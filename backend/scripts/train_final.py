import os, json, sys, torch, torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
import timm, numpy as np
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
import albumentations as A
from albumentations.pytorch import ToTensorV2
from PIL import Image

# Force unbuffered output for real-time monitoring
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

# --- ABSOLUTE PATH HARDENING ---
_HERE = os.path.dirname(os.path.abspath(__file__)) # scripts/
_BACKEND = os.path.dirname(_HERE) # backend/
_ROOT = os.path.dirname(_BACKEND) # project root/

DATASET_DIR = os.path.join(_ROOT, "dataset", "master_dataset")
MODEL_OUT   = os.path.join(_BACKEND, "ml_models")
DATA_OUT    = os.path.join(_BACKEND, "app", "data")

IMG_SIZE    = 224 # Optimized for speed
BATCH       = 32
EPOCHS      = 25
LR          = 3e-4
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"

class DS(torch.utils.data.Dataset):
    def __init__(self,base_imgs,idx,tfm):
        self.base_imgs=base_imgs;self.idx=idx;self.tfm=tfm
    def __len__(self): return len(self.idx)
    def __getitem__(self,i):
        path,lbl=self.base_imgs[self.idx[i]]
        img = np.array(Image.open(path).convert("RGB"))
        if self.tfm:
            img = self.tfm(image=img)["image"]
        return img,lbl

train_aug = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(0.2, 0.2, p=0.5),
    A.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
    ToTensorV2()
])

tfm_vl = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
    ToTensorV2()
])

if __name__ == '__main__':
    os.makedirs(MODEL_OUT, exist_ok=True)
    os.makedirs(DATA_OUT, exist_ok=True)

    print("--- PLANTOAI NEURAL FORGE STARTING ---")
    print(f"Device: {DEVICE} | Resolution: {IMG_SIZE}")

    if not os.path.exists(DATASET_DIR):
        print(f"ABORT: Dataset directory {DATASET_DIR} not found.")
        sys.exit(1)

    print(f"Scanning medicinal images at: {DATASET_DIR}...")
    raw = datasets.ImageFolder(DATASET_DIR)
    NUM = len(raw.classes)
    print(f"Extraction Complete: {len(raw)} images in {NUM} clinical classes.")
    
    with open(os.path.join(DATA_OUT, "class_names.json"), "w") as f: 
        json.dump(raw.classes, f, indent=2)

    n=len(raw); g=torch.Generator().manual_seed(42)
    idx=torch.randperm(n,generator=g).tolist()
    nv=max(int(n*.15),NUM); nt=max(int(n*.10),NUM); ntr=n-nv-nt
    
    # num_workers=0 is mandatory for Windows stability
    tl=DataLoader(DS(raw.imgs,idx[:ntr],train_aug),BATCH,shuffle=True,num_workers=0)
    vl=DataLoader(DS(raw.imgs,idx[ntr:ntr+nv],tfm_vl),BATCH,num_workers=0)
    tel=DataLoader(DS(raw.imgs,idx[ntr+nv:],tfm_vl),BATCH,num_workers=0)

    print(f"Dataset Split: Train={ntr} | Val={nv} | Test={nt}")

    print("Initializing Weights...")
    model=timm.create_model("tf_efficientnetv2_s.in21k",pretrained=True,num_classes=NUM).to(DEVICE)
    opt=torch.optim.AdamW(model.parameters(),lr=LR)
    crit=nn.CrossEntropyLoss(label_smoothing=0.1)
    best=0.0

    print("Starting Learning Phase (Baseline)...")
    for ep in range(EPOCHS):
        model.train()
        losses = []
        for i, (imgs,lbls) in enumerate(tl):
            imgs,lbls=imgs.to(DEVICE),lbls.to(DEVICE)
            opt.zero_grad(); loss=crit(model(imgs),lbls)
            loss.backward(); opt.step()
            losses.append(loss.item())
            if i % 50 == 0: 
                print(f"  Epoch {ep+1} | Batch {i}/{len(tl)} | Loss: {loss.item():.4f}", flush=True)
        
        avg_loss = sum(losses)/len(losses)
        model.eval(); vc=vt=0
        with torch.no_grad():
            for imgs,lbls in vl:
                vc+=(model(imgs.to(DEVICE)).argmax(1).cpu()==lbls).sum().item(); vt+=len(lbls)
        vacc = vc/vt if vt > 0 else 0
        print(f"DONE Epoch {ep+1:02d}/{EPOCHS} | Avg Loss: {avg_loss:.4f} | Val Acc: {vacc:.4f}", flush=True)
        
        if vacc>best:
            best=vacc; torch.save(model.state_dict(),f"{MODEL_OUT}/best.pt")
            print(f"  [SAVED] New best accuracy: {vacc:.4f}", flush=True)

    print("\n--- FORGE COMPLETE ---")
    with open(f"{MODEL_OUT}/training_report.json","w") as f:
        json.dump({"top1_accuracy":round(best*100,2),"num_classes":NUM,"train_images":ntr},f,indent=2)
