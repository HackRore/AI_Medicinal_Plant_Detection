import os, json, time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import transforms, datasets
import timm
import albumentations as A
from albumentations.pytorch import ToTensorV2
import numpy as np
from sklearn.metrics import classification_report, top_k_accuracy_score
from PIL import Image

# ── CONFIG ────────────────────────────────────────────────────────────────────
DATASET_DIR = "d:/PROJECT STAGE 1/dataset/unified_dataset"
OUTPUT_DIR  = "d:/PROJECT STAGE 1/backend/app/model"
MODEL_NAME  = "tf_efficientnetv2_s.in21k"   # ImageNet-21k pretrained
IMG_SIZE    = 384
BATCH_SIZE  = 16  # Reduced from 32 for lower GPU memory pressure
EPOCHS      = 10  # Rapid session for validation
LR          = 3e-4
WEIGHT_DECAY= 1e-4
VAL_SPLIT   = 0.15
TEST_SPLIT  = 0.10
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"
SEED        = 42

torch.manual_seed(SEED)
print(f"Training on: {DEVICE}")

# ── AUGMENTATION ──────────────────────────────────────────────────────────────
train_transform = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.3),
    A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.5),
    A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, p=0.5),
    A.Rotate(limit=45, p=0.5),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2()
])

val_transform = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2()
])

class AlbumentationsDataset(torch.utils.data.Dataset):
    def __init__(self, base_dataset, transform):
        self.base = base_dataset
        self.transform = transform
    def __len__(self): return len(self.base)
    def __getitem__(self, idx):
        img, label = self.base[idx]
        img_np = np.array(img)
        if img_np.ndim == 2:
            img_np = np.stack([img_np]*3, axis=-1)
        if img_np.shape[2] == 4:
            img_np = img_np[:,:,:3]
        augmented = self.transform(image=img_np)
        return augmented["image"], label

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
raw_dataset = datasets.ImageFolder(DATASET_DIR)
num_classes = len(raw_dataset.classes)

# Hardening: Filter missing files (Ghost Files)
valid_samples = []
for path, target in raw_dataset.samples:
    if os.path.exists(path):
        valid_samples.append((path, target))
raw_dataset.samples = valid_samples
raw_dataset.imgs = valid_samples # Sync internal list

print(f"Classes: {num_classes}")
print(f"Total valid images: {len(raw_dataset)}")

# Save class index
os.makedirs(OUTPUT_DIR, exist_ok=True)
class_index = [{"id": i, "name": c.replace("_", " ")} for i, c in enumerate(raw_dataset.classes)]
with open(f"{OUTPUT_DIR}/class_index.json", "w") as f:
    json.dump(class_index, f, indent=2)

# Split
n = len(raw_dataset)
n_test  = int(n * TEST_SPLIT)
n_val   = int(n * VAL_SPLIT)
n_train = n - n_val - n_test
train_ds, val_ds, test_ds = random_split(raw_dataset, [n_train, n_val, n_test],
    generator=torch.Generator().manual_seed(SEED))

train_loader = DataLoader(AlbumentationsDataset(train_ds, train_transform),
    batch_size=BATCH_SIZE, shuffle=True, num_workers=0)  # num_workers=0 for stability on Windows
val_loader   = DataLoader(AlbumentationsDataset(val_ds, val_transform),
    batch_size=BATCH_SIZE, num_workers=0)
test_loader  = DataLoader(AlbumentationsDataset(test_ds, val_transform),
    batch_size=BATCH_SIZE, num_workers=0)

# ── MODEL ─────────────────────────────────────────────────────────────────────
model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=num_classes)
model = model.to(DEVICE)

# Freeze base, train head for first 2 epochs
for param in model.parameters():
    param.requires_grad = False
for param in model.classifier.parameters():
    param.requires_grad = True

optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()),
    lr=LR, weight_decay=WEIGHT_DECAY)
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

# ── TRAINING LOOP ─────────────────────────────────────────────────────────────
best_val_acc = 0.0

for epoch in range(EPOCHS):
    # Unfreeze all layers after epoch 2
    if epoch == 2:
        for param in model.parameters():
            param.requires_grad = True
        optimizer = torch.optim.AdamW(model.parameters(), lr=LR/10, weight_decay=WEIGHT_DECAY)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS-2)
        print("  [Epoch 2] Unfreezing all layers, LR reduced to", LR/10)

    model.train()
    train_loss, train_correct = 0.0, 0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        train_loss += loss.item() * imgs.size(0)
        train_correct += (outputs.argmax(1) == labels).sum().item()
    scheduler.step()

    model.eval()
    val_correct, val_total = 0, 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            outputs = model(imgs)
            val_correct += (outputs.argmax(1) == labels).sum().item()
            val_total += labels.size(0)

    val_acc = val_correct / val_total
    train_acc = train_correct / n_train
    print(f"Epoch {epoch+1:02d}/{EPOCHS} | Train Acc: {train_acc:.4f} | Val Acc: {val_acc:.4f}")

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), f"{OUTPUT_DIR}/best_model.pt")
        print(f"  ✓ Saved best model (val_acc={val_acc:.4f})")

# ── FINAL EVALUATION ──
print("\n── Final Test Evaluation ──")
model.load_state_dict(torch.load(f"{OUTPUT_DIR}/best_model.pt"))
model.eval()

all_preds, all_labels, all_probs = [], [], []
with torch.no_grad():
    for imgs, labels in test_loader:
        imgs = imgs.to(DEVICE)
        outputs = model(imgs)
        probs = torch.softmax(outputs, dim=1)
        all_preds.extend(outputs.argmax(1).cpu().numpy())
        all_labels.extend(labels.numpy())
        all_probs.extend(probs.cpu().numpy())

all_probs_np = np.array(all_probs)
top1 = np.mean(np.array(all_preds) == np.array(all_labels))
top3 = top_k_accuracy_score(all_labels, all_probs_np, k=3)

print(f"\n  Top-1 Accuracy: {top1*100:.2f}%")
print(f"  Top-3 Accuracy: {top3*100:.2f}%")
print(f"\n  Per-class report:")
class_names = [c.replace("_"," ") for c in raw_dataset.classes]
print(classification_report(all_labels, all_preds, target_names=class_names))

# Save report
report = {
    "top1_accuracy": round(top1*100, 2),
    "top3_accuracy": round(top3*100, 2),
    "num_classes": num_classes,
    "train_images": n_train,
    "val_images": n_val,
    "test_images": n_test,
    "model_arch": MODEL_NAME,
    "epochs_trained": EPOCHS,
    "best_val_acc": round(best_val_acc*100, 2),
}
with open(f"{OUTPUT_DIR}/training_report.json", "w") as f:
    json.dump(report, f, indent=2)

# ── EXPORT TO ONNX ──
dummy = torch.randn(1, 3, IMG_SIZE, IMG_SIZE).to(DEVICE)
onnx_path = f"{OUTPUT_DIR}/efficientnetv2_medicinal.onnx"
torch.onnx.export(model, dummy, onnx_path,
    input_names=["input"], output_names=["output"],
    dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
    opset_version=17)

print(f"\n  ONNX model exported: {onnx_path}")
print("\n  ✅ TRAINING COMPLETE")
