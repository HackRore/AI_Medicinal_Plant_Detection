import torch, timm, os, json, sys
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
import torch.nn as nn
import numpy as np

DATASET = 'dataset/master_dataset'
OUT     = 'backend/ml_models'
SIZE    = 224
BATCH   = 16
EPOCHS  = 16
LR      = 3e-4
DEVICE  = 'cpu'
START_EP = 14  # RESUMING FROM HERE

os.makedirs(OUT, exist_ok=True)

tfm_tr = transforms.Compose([
    transforms.Resize((SIZE,SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.ColorJitter(0.3,0.3,0.3,0.1),
    transforms.RandomRotation(30),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
    transforms.RandomErasing(p=0.2)
])
tfm_vl = transforms.Compose([
    transforms.Resize((SIZE,SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

print('Loading dataset...', flush=True)
raw = datasets.ImageFolder(DATASET)
NUM = len(raw.classes)
print(f'Classes: {NUM}  Images: {len(raw)}', flush=True)
sys.stdout.flush()

cnames = [{'id':i,'name':c.replace('_',' ')} for i,c in enumerate(raw.classes)]
with open(f'{OUT}/../app/data/class_names.json','w') as f:
    json.dump(cnames, f, indent=2)

from sklearn.utils.class_weight import compute_class_weight
labels_all = [s[1] for s in raw.samples]
weights = compute_class_weight('balanced',
    classes=np.arange(NUM), y=labels_all)
weight_tensor = torch.tensor(weights, dtype=torch.float32)

n=len(raw); g=torch.Generator().manual_seed(42)
idx=torch.randperm(n,generator=g).tolist()
nv=max(int(n*.15),NUM); nt=max(int(n*.10),NUM); ntr=n-nv-nt

from PIL import Image
class DS(torch.utils.data.Dataset):
    def __init__(self,base,idx,tfm):
        self.base=base;self.idx=idx;self.tfm=tfm
    def __len__(self): return len(self.idx)
    def __getitem__(self,i):
        path,lbl=self.base.imgs[self.idx[i]]
        return self.tfm(Image.open(path).convert('RGB')),lbl

# num_workers=0 is critical on Windows to prevent crashes
tl=DataLoader(DS(raw,idx[:ntr],tfm_tr),BATCH,shuffle=True,num_workers=0)
vl=DataLoader(DS(raw,idx[ntr:ntr+nv],tfm_vl),BATCH,num_workers=0)
tel=DataLoader(DS(raw,idx[ntr+nv:],tfm_vl),BATCH,num_workers=0)

print('Loading model...', flush=True)
model=timm.create_model('tf_efficientnetv2_s.in21k',pretrained=True,num_classes=NUM)
for p in model.parameters(): p.requires_grad=False
for p in model.classifier.parameters(): p.requires_grad=True

opt=torch.optim.AdamW(filter(lambda p:p.requires_grad,model.parameters()),lr=LR,weight_decay=1e-4)
sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,EPOCHS)
crit=nn.CrossEntropyLoss(weight=weight_tensor,label_smoothing=0.1)

# RESUME LOGIC
best = 0.0
RESUME_PATH = f'{OUT}/best.pt'
if os.path.exists(RESUME_PATH):
    try:
        model.load_state_dict(torch.load(RESUME_PATH, map_location=DEVICE))
        print(f'>>> SUCCESS: Resumed from last known checkpoint ({RESUME_PATH})', flush=True)
        # Seed best with a high floor for Epoch 11
        best = 0.9964 
    except Exception as e:
        print(f'>>> WARNING: Checkpoint load failed, starting fresh: {e}', flush=True)

# FORCE UNFREEZE IF RESUMING AFTER EP 5
if START_EP > 5:
    for p in model.parameters(): p.requires_grad=True
    opt=torch.optim.AdamW(model.parameters(),lr=LR/10,weight_decay=1e-4)
    sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,EPOCHS-5)
    # Advanced: Step the scheduler to match the epoch
    for _ in range(START_EP - 6): sched.step()
    print(f'>>> PHASE SYNC: Unfrozen state activated for Epoch {START_EP}', flush=True)

print(f'Training resumed from Epoch {START_EP}. Each epoch shows progress.', flush=True)
for ep in range(START_EP - 1, EPOCHS):
    if ep==5:
        for p in model.parameters(): p.requires_grad=True
        opt=torch.optim.AdamW(model.parameters(),lr=LR/10,weight_decay=1e-4)
        sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,EPOCHS-5)
        print('[ep5] All layers unfrozen', flush=True)

    model.train()
    correct=total=0
    for batch_i,(imgs,lbls) in enumerate(tl):
        opt.zero_grad()
        loss=crit(model(imgs),lbls)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
        opt.step()
        correct+=(model(imgs).argmax(1)==lbls).sum().item()
        total+=len(lbls)
        if batch_i % 20 == 0:
            print(f'  Ep{ep+1} batch {batch_i}/{len(tl)} train_acc={correct/max(total,1):.3f}', flush=True)
    sched.step()

    model.eval(); vc=vt=0
    with torch.no_grad():
        for imgs,lbls in vl:
            vc+=(model(imgs).argmax(1)==lbls).sum().item(); vt+=len(lbls)
    vacc=vc/vt
    print(f'EPOCH {ep+1:02d}/{EPOCHS} val_acc={vacc:.4f}', flush=True)
    if vacc>best:
        best=vacc
        torch.save(model.state_dict(),f'{OUT}/best.pt')
        print(f'  SAVED best={vacc:.4f}', flush=True)

from sklearn.metrics import classification_report, top_k_accuracy_score
model.load_state_dict(torch.load(f'{OUT}/best.pt',map_location='cpu'))
model.eval()
preds,labels,probs=[],[],[]
with torch.no_grad():
    for imgs,lbls in tel:
        o=model(imgs); p=torch.softmax(o,1)
        preds+=o.argmax(1).tolist(); labels+=lbls.tolist(); probs+=p.tolist()
pa=np.array(probs)
top1=float(np.mean(np.array(preds)==np.array(labels)))
top3=float(top_k_accuracy_score(labels,pa,k=min(3,NUM)))
print(f'\nFINAL RESULTS:')
print(f'TOP-1 ACCURACY: {top1*100:.2f}%')
print(f'TOP-3 ACCURACY: {top3*100:.2f}%')
print(f'CLASSES: {NUM}')
print(classification_report(labels,preds,target_names=[c.replace("_"," ") for c in raw.classes]))

with open(f'{OUT}/training_report.json','w') as f:
    json.dump({'top1_accuracy':round(top1*100,2),'top3_accuracy':round(top3*100,2),
               'num_classes':NUM,'train_images':ntr,'val_images':nv,'test_images':nt,
               'model_arch':'tf_efficientnetv2_s.in21k','img_size':SIZE},f,indent=2)

dummy=torch.randn(1,3,SIZE,SIZE)
onnx=f'{OUT}/plantoai_model.onnx'
torch.onnx.export(model,dummy,onnx,input_names=['input'],output_names=['output'],
    dynamic_axes={'input':{0:'batch'},'output':{0:'batch'}},opset_version=17)
sz=os.path.getsize(onnx)/1e6
print(f'\nONNX saved: {onnx} ({sz:.1f}MB)')
assert sz>50, f'Model too small ({sz:.1f}MB) - training failed'
print('TRAINING COMPLETE')
