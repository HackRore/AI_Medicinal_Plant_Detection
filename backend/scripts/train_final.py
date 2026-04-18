import os, json, sys, torch, torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
import timm, numpy as np
from sklearn.metrics import classification_report, top_k_accuracy_score
from PIL import Image

DATASET_DIR = "dataset/unified_dataset"
MODEL_OUT   = "backend/ml_models"
DATA_OUT    = "backend/app/data"
IMG_SIZE    = 224
BATCH       = 16
EPOCHS      = 25
LR          = 3e-4
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"

if __name__ == '__main__':
    os.makedirs(MODEL_OUT, exist_ok=True)
    os.makedirs(DATA_OUT, exist_ok=True)

    # Remove crop/disease folders before training
    import shutil
    CROP_WORDS = ["banana","bell_pepper","cassava","cherry","corn",
                  "cucumber","grape","orange","peach","potato","rice",
                  "soybean","squash","strawberry","tomato","wheat",
                  "blueberry","apple","coffee","chili","background"]
    for folder in os.listdir(DATASET_DIR):
        fp = os.path.join(DATASET_DIR, folder)
        if os.path.isdir(fp):
            name = folder.lower().replace(" ","_")
            if any(w in name for w in CROP_WORDS):
                try:
                    shutil.rmtree(fp)
                    print(f"REMOVED crop folder: {folder}")
                except:
                    pass

    raw = datasets.ImageFolder(DATASET_DIR)
    NUM = len(raw.classes)
    print(f"Medicinal classes to train: {NUM}")
    for i,c in enumerate(raw.classes): print(f"  {i}: {c}")

    if NUM < 3:
        print("ERROR: Too few classes. Check dataset.")
        sys.exit(1)

    tfm_tr = transforms.Compose([
        transforms.Resize((IMG_SIZE,IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.ColorJitter(0.3,0.3,0.3,0.1),
        transforms.RandomRotation(30),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
        transforms.RandomErasing(p=0.2)
    ])
    tfm_vl = transforms.Compose([
        transforms.Resize((IMG_SIZE,IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])

    class DS(torch.utils.data.Dataset):
        def __init__(self,base,idx,tfm):
            self.base=base;self.idx=idx;self.tfm=tfm
        def __len__(self): return len(self.idx)
        def __getitem__(self,i):
            path,lbl=self.base.imgs[self.idx[i]]
            return self.tfm(Image.open(path).convert("RGB")),lbl

    n=len(raw); g=torch.Generator().manual_seed(42)
    idx=torch.randperm(n,generator=g).tolist()
    nv=max(int(n*.15),NUM); nt=max(int(n*.10),NUM); ntr=n-nv-nt
    tl=DataLoader(DS(raw,idx[:ntr],tfm_tr),BATCH,shuffle=True,num_workers=0)
    vl=DataLoader(DS(raw,idx[ntr:ntr+nv],tfm_vl),BATCH,num_workers=0)
    tel=DataLoader(DS(raw,idx[ntr+nv:],tfm_vl),BATCH,num_workers=0)

    cnames=[{"id":i,"name":c.replace("_"," ")} for i,c in enumerate(raw.classes)]
    with open(f"{DATA_OUT}/class_names.json","w") as f: json.dump(cnames,f,indent=2)

    model=timm.create_model("tf_efficientnetv2_s.in21k",pretrained=True,num_classes=NUM).to(DEVICE)
    for p in model.parameters(): p.requires_grad=False
    for p in model.classifier.parameters(): p.requires_grad=True
    opt=torch.optim.AdamW(filter(lambda p:p.requires_grad,model.parameters()),lr=LR,weight_decay=1e-4)
    sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,EPOCHS)
    crit=nn.CrossEntropyLoss(label_smoothing=0.1)
    best=0.0

    for ep in range(EPOCHS):
        if ep==5:
            for p in model.parameters(): p.requires_grad=True
            opt=torch.optim.AdamW(model.parameters(),lr=LR/10,weight_decay=1e-4)
            sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,EPOCHS-5)
        model.train()
        for imgs,lbls in tl:
            imgs,lbls=imgs.to(DEVICE),lbls.to(DEVICE)
            opt.zero_grad(); loss=crit(model(imgs),lbls)
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
        sched.step()
        model.eval(); vc=vt=0
        with torch.no_grad():
            for imgs,lbls in vl:
                vc+=(model(imgs.to(DEVICE)).argmax(1).cpu()==lbls).sum().item(); vt+=len(lbls)
        vacc=vc/vt
        print(f"Epoch {ep+1:02d}/{EPOCHS} val={vacc:.4f}")
        if vacc>best:
            best=vacc; torch.save(model.state_dict(),f"{MODEL_OUT}/best.pt")
            print(f"  saved val={vacc:.4f}")

    model.load_state_dict(torch.load(f"{MODEL_OUT}/best.pt",map_location=DEVICE))
    model.eval()
    preds,labels,probs=[],[],[]
    with torch.no_grad():
        for imgs,lbls in tel:
            o=model(imgs.to(DEVICE)); p=torch.softmax(o,1)
            preds+=o.argmax(1).cpu().tolist()
            labels+=lbls.tolist()
            probs+=p.cpu().tolist()
    pa=np.array(probs)
    top1=float(np.mean(np.array(preds)==np.array(labels)))
    top3=float(top_k_accuracy_score(labels,pa,k=min(3,NUM)))
    print(f"\nTOP-1: {top1*100:.2f}%  TOP-3: {top3*100:.2f}%  CLASSES: {NUM}")
    print(classification_report(labels,preds,target_names=[c.replace("_"," ") for c in raw.classes]))

    with open(f"{MODEL_OUT}/training_report.json","w") as f:
        json.dump({"top1_accuracy":round(top1*100,2),"top3_accuracy":round(top3*100,2),
                   "num_classes":NUM,"train_images":ntr,"val_images":nv,"test_images":nt,
                   "model_arch":"tf_efficientnetv2_s.in21k","img_size":IMG_SIZE},f,indent=2)

    dummy=torch.randn(1,3,IMG_SIZE,IMG_SIZE).to(DEVICE)
    onnx=f"{MODEL_OUT}/plantoai_model.onnx"
    torch.onnx.export(model,dummy,onnx,input_names=["input"],output_names=["output"],
        dynamic_axes={"input":{0:"batch"},"output":{0:"batch"}},opset_version=17)
    sz=os.path.getsize(onnx)/1e6
    print(f"\nONNX: {onnx} ({sz:.1f}MB)")
    assert sz>50, f"FAIL: model only {sz:.1f}MB — training did not complete properly"
    print(f"\nTRAINING COMPLETE. Top-1={top1*100:.2f}% Classes={NUM} Size={sz:.1f}MB")
    print("COPY THESE NUMBERS. They go on the website.")
