"""
Downloads 3 approved medicinal leaf datasets from Kaggle,
merges them, deduplicates class names, and outputs
dataset/unified_dataset/ ready for training.
PlantVillage is EXCLUDED — it contains crop diseases not plant species.
"""
import kagglehub, os, shutil, json
from pathlib import Path
from collections import defaultdict
from PIL import Image

# ── DOWNLOAD ─────────────────────────────────────────────────────
print("Downloading datasets...")
path_a = kagglehub.dataset_download("mdfahimbinalam/leaf-dataset")
path_b = kagglehub.dataset_download("rayush/plant-leaves")
path_c = kagglehub.dataset_download("hmohamedhussain/leaves-image-dataset")
# Test set only — never add to training
path_t = kagglehub.dataset_download("mahirdipto/plant-leaf-test")

DATASET_PATHS = [path_a, path_b, path_c]
OUT           = "dataset/unified_dataset"
TEST_OUT      = "dataset/test_only"
MIN           = 60
MAX           = 600
EXTS          = {'.jpg','.jpeg','.png','.webp','.bmp'}

# ── CANONICAL MAP — merges variant spellings ──────────────────────
# If you find more duplicates during Step 2.2, add them here
CANON = {
    "tulsi":"Basil","holy_basil":"Basil","ocimum_tenuiflorum":"Basil",
    "neem":"Neem","azadirachta_indica":"Neem","indian_lilac":"Neem",
    "aloe":"Aloe Vera","aloe_vera":"Aloe Vera",
    "turmeric":"Turmeric","curcuma_longa":"Turmeric",
    "ashwagandha":"Ashwagandha","withania_somnifera":"Ashwagandha",
    "giloy":"Giloy","guduchi":"Giloy","tinospora_cordifolia":"Giloy",
    "brahmi":"Brahmi","bacopa_monnieri":"Brahmi",
    "amla":"Amla","phyllanthus_emblica":"Amla",
    "moringa":"Moringa","moringa_oleifera":"Moringa",
    "arjun":"Arjun","arjuna":"Arjun","terminalia_arjuna":"Arjun",
    "bael":"Bael","aegle_marmelos":"Bael","bilva":"Bael",
    "chinar":"Chinar","platanus_orientalis":"Chinar",
    "guava":"Guava","psidium_guajava":"Guava","gauva":"Guava",
    "jamun":"Jamun","syzygium_cumini":"Jamun","java_plum":"Jamun",
    "jatropha":"Jatropha","jatropha_curcas":"Jatropha",
    "lemon":"Lemon","citrus_limon":"Lemon","nimbu":"Lemon",
    "mango":"Mango","mangifera_indica":"Mango",
    "pomegranate":"Pomegranate","punica_granatum":"Pomegranate","anar":"Pomegranate",
    "pongamia":"Pongamia Pinnata","pongamia_pinnata":"Pongamia Pinnata","karanja":"Pongamia Pinnata",
    "alstonia":"Alstonia Scholaris","alstonia_scholaris":"Alstonia Scholaris","saptaparni":"Alstonia Scholaris",
    "hibiscus":"Hibiscus","hibiscus_rosa_sinensis":"Hibiscus",
    "mint":"Mint","mentha":"Mint",
    "curry_leaf":"Curry Leaf","murraya_koenigii":"Curry Leaf",
    "papaya":"Papaya","carica_papaya":"Papaya",
}

def norm(raw):
    k = raw.lower().strip().replace(" ","_").replace("-","_")
    return CANON.get(k, raw.strip().title())

def ok(p):
    try: return Image.open(p).size[0] >= 64
    except: return False

buckets = defaultdict(list)
for dp in DATASET_PATHS:
    for root,_,files in os.walk(dp):
        for f in files:
            fp = Path(root)/f
            if fp.suffix.lower() in EXTS:
                buckets[norm(Path(root).name)].append(fp)

valid = {k:v for k,v in buckets.items() if len(v) >= MIN}
print(f"\nClasses kept : {len(valid)}")
print(f"Classes dropped (<{MIN} images): {sorted(set(buckets)-set(valid))}\n")

shutil.rmtree(OUT, ignore_errors=True)
index = []
for cls, imgs in sorted(valid.items()):
    safe = cls.replace(" ","_")
    d = Path(OUT)/safe; d.mkdir(parents=True, exist_ok=True)
    n = 0
    for img in imgs[:MAX]:
        if ok(img): shutil.copy2(img, d/f"{n:05d}{img.suffix}"); n+=1
    index.append({"id":len(index),"name":cls,"count":n})
    print(f"  {cls}: {n} images")

with open(f"{OUT}/class_index.json","w") as f:
    json.dump(index, f, indent=2)

# Copy test data separately — never touch during training
shutil.copytree(path_t, TEST_OUT, dirs_exist_ok=True)

print(f"\n✓ Dataset ready at {OUT}")
print(f"  Total classes: {len(index)}")
print(f"  Total images : {sum(c['count'] for c in index)}")
print(f"  Test data    : {TEST_OUT}")
print("\n  ↑ Save these numbers. They go on the About page after training.")
