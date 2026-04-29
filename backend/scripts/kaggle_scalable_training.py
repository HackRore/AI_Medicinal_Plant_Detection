import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import urllib.request
import zipfile
import tarfile

# ==========================================
# 1. ROBUST DATASET DOWNLOADER
# ==========================================
def download_and_extract(url, dest_path, extract_to):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to, exist_ok=True)
        print(f"Downloading {url}...")
        try:
            urllib.request.urlretrieve(url, dest_path)
            print(f"Extracting {dest_path}...")
            if dest_path.endswith('.zip'):
                with zipfile.ZipFile(dest_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif dest_path.endswith('.tar.bz2'):
                with tarfile.open(dest_path, 'r:bz2') as tar_ref:
                    tar_ref.extractall(extract_to)
            print(f"✅ Successfully prepared {extract_to}")
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
    else:
        print(f"✅ Dataset already exists at {extract_to}. Skipping download.")

# Define datasets (Flavia as an example for baseline)
DATA_DIR = "./datasets"
os.makedirs(DATA_DIR, exist_ok=True)
download_and_extract(
    "https://sourceforge.net/projects/flavia/files/Leaf%20Image%20Dataset/1.0/Leaves.tar.bz2/download",
    os.path.join(DATA_DIR, "flavia_leaves.tar.bz2"),
    os.path.join(DATA_DIR, "flavia")
)

# ==========================================
# 2. DATA AUGMENTATION & PREPROCESSING
# ==========================================
# EfficientNetV2 expects 224x224 images and specific normalization
img_transforms = {
    'train': transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

# IMPORTANT: In a real scenario, you combine Flavia, Kaggle, etc., into a unified folder structure:
# datasets/train/class_1/... and datasets/val/class_1/...
# For this script, we assume you have structured them into './datasets/train' and './datasets/val'

# ==========================================
# 3. ADVANCED MODEL ARCHITECTURE (TRANSFER LEARNING)
# ==========================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Training on device: {device}")

# We use EfficientNetV2 - it's faster to train and highly accurate for fine-grained image classification (like leaves)
model = models.efficientnet_v2_s(weights=models.EfficientNet_V2_S_Weights.DEFAULT)

# Freeze early layers to save compute (only train the last layers)
for param in model.parameters():
    param.requires_grad = False

# Adapt the final classifier for our Target Species Count (e.g., scaling up to 1000)
TARGET_CLASSES = 1000  # Adjust this to 46, 200, or 1000 based on your current phase
model.classifier[1] = nn.Linear(model.classifier[1].in_features, TARGET_CLASSES)
model = model.to(device)

# ==========================================
# 4. CHECKPOINTING & RESUME LOGIC (CRITICAL FOR KAGGLE/COLAB)
# ==========================================
CHECKPOINT_PATH = "plantoai_checkpoint.pth"

optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()
start_epoch = 0

if os.path.exists(CHECKPOINT_PATH):
    print(f"🔄 Found checkpoint at {CHECKPOINT_PATH}. Resuming training...")
    checkpoint = torch.load(CHECKPOINT_PATH, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    start_epoch = checkpoint['epoch'] + 1
    print(f"✅ Resumed from Epoch {start_epoch}")
else:
    print("✨ Starting fresh training run.")

# ==========================================
# 5. ROBUST TRAINING LOOP
# ==========================================
EPOCHS = 25

def train_model():
    # Placeholder for dataloaders (replace with actual ImageFolder dataloaders)
    # dataloaders = {'train': train_loader, 'val': val_loader}
    
    print("⏳ Starting Training Loop...")
    for epoch in range(start_epoch, EPOCHS):
        print(f"Epoch {epoch}/{EPOCHS - 1}")
        print("-" * 10)
        
        # simulated training step...
        # for inputs, labels in dataloaders['train']:
        #     inputs, labels = inputs.to(device), labels.to(device)
        #     optimizer.zero_grad()
        #     outputs = model(inputs)
        #     loss = criterion(outputs, labels)
        #     loss.backward()
        #     optimizer.step()
            
        print(f"Epoch {epoch} complete. Saving Checkpoint...")
        
        # SAVE CHECKPOINT AFTER EVERY EPOCH
        # If Kaggle disconnects, you lose ZERO progress.
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': 0.0, # Save actual loss here
        }, CHECKPOINT_PATH)
        
        # Also save a production-ready model if validation accuracy improves
        # torch.save(model.state_dict(), "best_plantoai_model.pth")

if __name__ == '__main__':
    train_model()
    print("🎉 Training Complete! Export 'best_plantoai_model.pth' for deployment.")
