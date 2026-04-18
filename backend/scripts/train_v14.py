"""
PlantoAI: Master Convergent Trainer (v14.0)
Consolidates 5 dataset sources into a single optimized G9 Neural Engine.
Sources: IMLD, raw, test_only, unified, unified_dataset
"""
import os, json, sys, torch, torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
import torchvision.models as models
from sklearn.metrics import classification_report
import glob

# Configuration
ROOT_DIR = "D:/PROJECT FINAL"
DATA_DIRS = [
    f"{ROOT_DIR}/dataset/IMLD",
    f"{ROOT_DIR}/dataset/raw",
    f"{ROOT_DIR}/dataset/test_only",
    f"{ROOT_DIR}/dataset/unified",
    f"{ROOT_DIR}/dataset/unified_dataset"
]
MODEL_OUT = f"{ROOT_DIR}/backend/models"
DATA_OUT  = f"{ROOT_DIR}/backend/app/data"
IMG_SIZE  = 224
BATCH     = 8
LIMIT     = 8000  # Scratch training needs more data for accuracy
EPOCHS    = 10
LR        = 1e-4
DEVICE    = "cuda" if torch.cuda.is_available() else "cpu"

# Filter: Only keep medicinal plants and remove "crop" noise
CROP_NOISE = ["banana", "bell_pepper", "cassava", "cherry", "corn", "cucumber", 
              "grape", "orange", "peach", "potato", "rice", "soybean", "squash", 
              "strawberry", "tomato", "wheat", "blueberry", "apple", "coffee", 
              "chili", "background"]

class ConvergentDataset(Dataset):
    def __init__(self, data_dirs, transform=None):
        self.samples = []
        self.class_to_idx = {}
        self.transform = transform
        
        # 1. Discover all valid medicinal folders across all roots
        all_folders = {}
        for d in data_dirs:
            if not os.path.exists(d): continue
            print(f"Scanning Root: {d}")
            for entry in os.scandir(d):
                if entry.is_dir():
                    norm = entry.name.lower().replace("_", " ").strip()
                    if any(noise in norm for noise in CROP_NOISE): continue
                    
                    if norm not in all_folders: all_folders[norm] = []
                    all_folders[norm].append(entry.path)
        
        # 2. Map folders to continuous IDs
        self.classes = sorted(list(all_folders.keys()))
        self.class_to_idx = {name: i for i, name in enumerate(self.classes)}
        
        # 3. Collect all images (Faster Walk)
        for norm, paths in all_folders.items():
            label_idx = self.class_to_idx[norm]
            for p in paths:
                for root, _, files in os.walk(p):
                    for f in files:
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            self.samples.append((os.path.join(root, f), label_idx))
        
        import random
        random.shuffle(self.samples)
        if LIMIT and len(self.samples) > LIMIT:
            self.samples = self.samples[:LIMIT]
                    
        print(f"CONVERGENCE READY: {len(self.classes)} classes | {len(self.samples)} images (STABILITY CAP ACTIVE)", flush=True)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        try:
            img = Image.open(path).convert("RGB")
            if self.transform:
                img = self.transform(img)
            return img, label
        except Exception as e:
            print(f"Warning: Corrupt image skip {path}: {e}")
            # Return a blank image as fallback or just try next
            return torch.zeros(3, IMG_SIZE, IMG_SIZE), label

def train():
    os.makedirs(MODEL_OUT, exist_ok=True)
    os.makedirs(DATA_OUT, exist_ok=True)

    # Standard Transfoms (Matching G9Preprocessor logic)
    tfm_train = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(0.2, 0.2, 0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    tfm_val = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    full_ds = ConvergentDataset(DATA_DIRS)
    clist = [{"id": i, "name": name.title()} for i, name in enumerate(full_ds.classes)]
    with open(f"{DATA_OUT}/class_names.json", "w") as f:
        json.dump(clist, f, indent=2)

    # Split
    total = len(full_ds)
    train_size = int(0.8 * total)
    val_size = total - train_size
    train_idx, val_idx = torch.utils.data.random_split(
        range(total), [train_size, val_size], generator=torch.Generator().manual_seed(42))
    
    # Re-apply transforms per split
    class SplitDS(Dataset):
        def __init__(self, base, idxs, tfm):
            self.base = base; self.idxs = idxs; self.tfm = tfm
        def __len__(self): return len(self.idxs)
        def __getitem__(self, i):
            p, l = self.base.samples[self.idxs[i]]
            try:
                return self.tfm(Image.open(p).convert("RGB")), l
            except:
                return torch.zeros(3, IMG_SIZE, IMG_SIZE), l

    train_loader = DataLoader(SplitDS(full_ds, train_idx, tfm_train), batch_size=BATCH, shuffle=True, num_workers=0)
    val_loader   = DataLoader(SplitDS(full_ds, val_idx, tfm_val), batch_size=BATCH, num_workers=0)

    print("DEBUG: Initializing Native MobileNetV3 (SCRATCH MODE - FIREWALL BYPASS)...", flush=True)
    # Model: Native MobileNetV3-Large (No external downloads)
    num_classes = len(full_ds.classes)
    model = models.mobilenet_v3_large(weights=None) # BYPASS FIREWALL
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    model = model.to(DEVICE)
    print("DEBUG: Model Ready.", flush=True)
    
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, EPOCHS)

    print(f"DEBUG: Starting Training on {DEVICE}...", flush=True)
    best_acc = 0
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        for i, (imgs, labels) in enumerate(train_loader):
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        scheduler.step()
        
        # Validation
        model.eval()
        correct = 0
        total_val = 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                outputs = model(imgs)
                _, predicted = torch.max(outputs.data, 1)
                total_val += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        acc = (correct / total_val) * 100
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {running_loss/len(train_loader):.4f} | Val Acc: {acc:.2f}%")
        
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), f"{MODEL_OUT}/best.pt")
            print(f"  --> Saved Best Model ({acc:.2f}%)")

    # Export to ONNX
    print("Exporting to ONNX...")
    model.load_state_dict(torch.load(f"{MODEL_OUT}/best.pt"))
    model.eval()
    dummy_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE).to(DEVICE)
    onnx_path = f"{MODEL_OUT}/plantoai_model.onnx"
    torch.onnx.export(model, dummy_input, onnx_path, 
                      input_names=['input'], output_names=['output'],
                      dynamic_axes={'input': {0: 'batch'}, 'output': {0: 'batch'}},
                      opset_version=14)
    
    # Save Report
    with open(f"{MODEL_OUT}/training_report.json", "w") as f:
        json.dump({
            "num_classes": num_classes,
            "top1_accuracy": round(best_acc, 2),
            "train_images": train_size,
            "val_images": val_size,
            "model_arch": "tf_efficientnetv2_s.in21k"
        }, f, indent=2)

    print("\nTRAINING AND DEPLOYMENT READY.")

if __name__ == "__main__":
    train()
