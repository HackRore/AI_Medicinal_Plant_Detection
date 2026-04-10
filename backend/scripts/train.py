"""
Trains EfficientNetV2-S (ImageNet-21k pretrained).
Optimized for Speed: Samples dataset to ~6,000 images for CPU feasibility.
"""
import os, json, sys, torch, torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
import timm, numpy as np
from PIL import Image

DATASET_DIR = "dataset/unified_dataset"
MODEL_OUT   = "backend/ml_models"
DATA_OUT    = "backend/app/data"
IMG_SIZE    = 224
BATCH       = 32
EPOCHS      = 15       # Reduced epochs for CPU speed, more than enough with ImageNet-21k weights
LR          = 5e-4
DEVICE      = "cpu"

class TDS(torch.utils.data.Dataset):
    def __init__(self, base, indices, tfm):
        self.base=base; self.idx=indices; self.tfm=tfm
    def __len__(self): return len(self.idx)
    def __getitem__(self,i):
        path, lbl = self.base.imgs[self.idx[i]]
        return self.tfm(Image.open(path).convert("RGB")), lbl

def train_model():
    print(f"Neural Forge: Optimized CPU Training Flow")

    if not os.path.isdir(DATASET_DIR):
        print("ERROR: Dataset missing."); sys.exit(1)

    tfm_tr = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])
    tfm_vl = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)), transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])

    raw = datasets.ImageFolder(DATASET_DIR)
    NUM = len(raw.classes)
    
    # ── Dataset Sampling for CPU feasible speed ────────────────────────
    # Limits each class to 180 images. Total ~6000 images.
    final_indices = []
    class_counts = {}
    indices = torch.randperm(len(raw)).tolist()
    for idx in indices:
        _, lbl = raw.imgs[idx]
        class_counts[lbl] = class_counts.get(lbl, 0) + 1
        if class_counts[lbl] <= 180:
            final_indices.append(idx)
    
    print(f"Dataset Sampled: {len(final_indices)} images from {NUM} classes")
    
    os.makedirs(MODEL_OUT, exist_ok=True)
    os.makedirs(DATA_OUT, exist_ok=True)

    cnames = [{"id":i,"name":c.replace("_"," ")} for i,c in enumerate(raw.classes)]
    with open(f"{DATA_OUT}/class_names.json","w") as f: json.dump(cnames,f,indent=2)

    n = len(final_indices)
    nval = int(n*.15); ntr = n - nval
    tr_idx, va_idx = final_indices[:ntr], final_indices[ntr:]

    tl = DataLoader(TDS(raw, tr_idx, tfm_tr), BATCH, shuffle=True, num_workers=0)
    vl = DataLoader(TDS(raw, va_idx, tfm_vl), BATCH, num_workers=0)

    print("Building EfficientNetV2-S (G9 Scientific Configuration)...")
    # Load ImageNet weights first
    model = timm.create_model("tf_efficientnetv2_s.in21k", pretrained=True, num_classes=NUM)

    checkpoint_path = os.path.join(MODEL_OUT, "best.pt")
    if os.path.exists(checkpoint_path):
        print(f"Loading Base Intelligence from: {checkpoint_path}")
        try:
            # Load old weights (33 classes) into a 33-class model to extract base features
            base_model = timm.create_model("tf_efficientnetv2_s.in21k", num_classes=33)
            base_model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
            
            # Transfer all weights except the classifier head
            msg = model.load_state_dict(base_model.state_dict(), strict=False)
            print(f"  Finetuning Sync: {msg}")
        except Exception as e:
            print(f"  Warning: Could not perform full intelligence transfer: {e}")

    for p in model.parameters(): p.requires_grad = False
    for p in model.classifier.parameters(): p.requires_grad = True
    
    # Use balanced learning rate for finetuning
    opt   = torch.optim.AdamW(filter(lambda p:p.requires_grad, model.parameters()), lr=LR)
    crit  = nn.CrossEntropyLoss(label_smoothing=0.1)
    best  = 0.0

    print("Running Neural Forge Epochs (Fine-Tuning Mode)...")
    for ep in range(EPOCHS):
        if ep == 3:
            print("  Phase 2: Unfreezing all layers for convergence...")
            for p in model.parameters(): p.requires_grad = True
            opt = torch.optim.AdamW(model.parameters(), lr=LR/5)

        model.train()
        for i, (imgs, lbls) in enumerate(tl):
            opt.zero_grad(); crit(model(imgs), lbls).backward(); opt.step()
            if i % 20 == 0: print(f"  Ep {ep+1} | Batch {i}/{len(tl)}")

        model.eval(); vc=vt=0
        with torch.no_grad():
            for imgs, lbls in vl:
                vc += (model(imgs).argmax(1) == lbls).sum().item(); vt += len(lbls)
        
        vacc = vc/vt
        print(f"Epoch {ep+1} | Val Acc: {vacc:.4f}")
        
        if vacc > best:
            best = vacc
            torch.save(model.state_dict(), f"{MODEL_OUT}/best.pt")
            print(f"  Saved Best")

    print("\nTraining complete. Exporting ONNX...")
    model.load_state_dict(torch.load(f"{MODEL_OUT}/best.pt"))
    torch.onnx.export(model, torch.randn(1, 3, IMG_SIZE, IMG_SIZE), f"{MODEL_OUT}/plantoai_model.onnx")
    
    report = {"top1_accuracy": round(best*100, 2), "num_classes": NUM, "train_images": ntr, "model_arch": "EfficientNetV2-S"}
    with open(f"{MODEL_OUT}/training_report.json", "w") as f: json.dump(report, f, indent=3)
    
    print(f"\n✅ SYSTEM READY | Final Accuracy: {best*100:.2f}%")

if __name__ == "__main__":
    train_model()
