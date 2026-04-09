"""
Trains EfficientNetV2-S on your 12-class unified dataset.
Run: python backend/scripts/train_12class.py
Output: backend/ml_models/efficientnetv2_12class.onnx
        backend/app/data/class_names.json  (overwritten with correct 12 classes)
        backend/ml_models/training_report.json
"""
import os, json, sys, torch, torch.nn as nn
from torch.utils.data import DataLoader, random_split, Subset
from torchvision import datasets
import timm, numpy as np
from sklearn.metrics import classification_report, top_k_accuracy_score

# ── adjust these paths to match your actual folder structure ──────────────
DATASET_DIR  = "dataset/unified_dataset"
MODEL_OUT    = "backend/ml_models"
DATA_OUT     = "backend/app/data"
IMG_SIZE     = 224
BATCH        = 32
EPOCHS       = 2
LR           = 3e-4
DEVICE       = "cuda" if torch.cuda.is_available() else "cpu"
# ─────────────────────────────────────────────────────────────────────────

def train():
    print(f"Training on: {DEVICE}")
    os.makedirs(MODEL_OUT, exist_ok=True)
    os.makedirs(DATA_OUT,  exist_ok=True)

    from torchvision import transforms
    tfm_train = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])
    tfm_val = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)), transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])

    if not os.path.exists(DATASET_DIR):
        print(f"ERROR: Dataset not found at {DATASET_DIR}")
        sys.exit(1)

    full_ds = datasets.ImageFolder(DATASET_DIR)
    NUM_CLASSES = len(full_ds.classes)
    print(f"Classes found: {NUM_CLASSES}")

    # Save class names
    class_list = [{"id": i, "name": c.replace("_", " ")} for i, c in enumerate(full_ds.classes)]
    with open(f"{DATA_OUT}/class_names.json", "w") as f:
        json.dump(class_list, f, indent=2)

    # Use a small subset for "Workable" demonstration
    indices = torch.randperm(len(full_ds))[:500]
    n = len(indices)
    nval = int(n * 0.15); ntest = int(n * 0.10); ntrain = n - nval - ntest
    
    tr_idx = indices[:ntrain]
    va_idx = indices[ntrain:ntrain+nval]
    te_idx = indices[ntrain+nval:]

    class TransformedSubset(torch.utils.data.Dataset):
        def __init__(self, dataset, indices, transform):
            self.dataset = dataset
            self.indices = indices
            self.transform = transform
        def __len__(self): return len(self.indices)
        def __getitem__(self, i):
            img, lbl = self.dataset[self.indices[i]]
            return self.transform(img), lbl

    # Reset transform of base dataset to None to handle it manually
    full_ds.transform = None

    tl  = DataLoader(TransformedSubset(full_ds, tr_idx, tfm_train), BATCH, shuffle=True, num_workers=0)
    vl  = DataLoader(TransformedSubset(full_ds, va_idx, tfm_val),   BATCH, num_workers=0)
    tel = DataLoader(TransformedSubset(full_ds, te_idx, tfm_val),   BATCH, num_workers=0)

    model = timm.create_model("tf_efficientnetv2_s.in21k", pretrained=True, num_classes=NUM_CLASSES).to(DEVICE)

    # Phase 1: train head only
    for p in model.parameters(): p.requires_grad = False
    for p in model.classifier.parameters(): p.requires_grad = True
    opt = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=LR)
    crit = nn.CrossEntropyLoss(label_smoothing=0.1)

    best_val = 0.0
    for ep in range(EPOCHS):
        model.train()
        for imgs, lbls in tl:
            imgs, lbls = imgs.to(DEVICE), lbls.to(DEVICE)
            opt.zero_grad(); loss = crit(model(imgs), lbls)
            loss.backward(); opt.step()

        model.eval(); vc = vt = 0
        with torch.no_grad():
            for imgs, lbls in vl:
                imgs = imgs.to(DEVICE)
                vc += (model(imgs).argmax(1).cpu() == lbls).sum().item(); vt += len(lbls)
        vacc = vc / vt
        print(f"Epoch {ep+1:02d}/{EPOCHS} | ValAcc: {vacc:.4f}")
        if vacc >= best_val:
            best_val = vacc
            torch.save(model.state_dict(), f"{MODEL_OUT}/best_model.pt")

    # ── Final test ──
    model.load_state_dict(torch.load(f"{MODEL_OUT}/best_model.pt", map_location=DEVICE))
    model.eval()
    preds, labels, probs = [], [], []
    with torch.no_grad():
        for imgs, lbls in tel:
            o = model(imgs.to(DEVICE)); p = torch.softmax(o, 1)
            preds += o.argmax(1).cpu().tolist(); labels += lbls.tolist(); probs += p.cpu().tolist()

    top1 = np.mean(np.array(preds) == np.array(labels))
    print(f"\nTOP-1 ACCURACY: {top1*100:.2f}%")

    report = {"top1_accuracy": round(top1*100,2), "num_classes": NUM_CLASSES, "train_images": ntrain}
    with open(f"{MODEL_OUT}/training_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # ── Export ONNX ──
    dummy = torch.randn(1, 3, IMG_SIZE, IMG_SIZE).to(DEVICE)
    onnx_path = f"{MODEL_OUT}/efficientnetv2_12class.onnx"
    torch.onnx.export(model, dummy, onnx_path, input_names=["input"], output_names=["output"])
    print(f"\n✅ TRAINING COMPLETE: {onnx_path}")

if __name__ == "__main__":
    train()
