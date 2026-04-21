import kagglehub, os, shutil, json, time
from pathlib import Path
from collections import defaultdict
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

def download_with_retry(slug):
    max_retries = 50 # Increased for unstable connections
    for i in range(max_retries):
        try:
            print(f"Attempting download of {slug} (Try {i+1})...")
            return kagglehub.dataset_download(slug)
        except Exception as e:
            # Handle DNS/Network drops by waiting longer
            wait = min(60 * (i + 1), 600) 
            print(f"Network Issue: {e}. Retrying in {wait} seconds...")
            time.sleep(wait)
    raise Exception(f"Failed to download {slug} after {max_retries} attempts.")

print("Starting Turbo-Optimized Dataset Forge...")
# Reordered: Small, high-velocity datasets first to enable early build
p2 = download_with_retry("warcoder/indian-medicinal-plant-image-dataset")
p3 = download_with_retry("mdfahimbinalam/leaf-dataset")
p1 = download_with_retry("aryashah2k/indian-medicinal-leaves-dataset")

SOURCES = [p1, p2, p3, "dataset/unified_dataset"]
OUT = "dataset/master_dataset"
MIN_IMAGES = 200
MAX_IMAGES = 800
EXTS = {'.jpg','.jpeg','.png','.webp','.bmp'}

# Remove these — crops and diseases, not medicinal plants
EXCLUDE = {
    'tomato','potato','corn','maize','rice','wheat','soybean',
    'soyabean','pepper','bell_pepper','apple','grape','peach',
    'cherry','blueberry','raspberry','strawberry','orange',
    'cucumber','squash','cassava','coffee','banana','jackfruit',
    'background','test','train','valid','leaf-dataset',
    'rizkikecek','plant leaf freshness','bangladesh','healthy',
    'unhealthy','bacterial','blight','scab','rust','spot','rot',
    'mold','mildew','virus','cercospora','hauglongbing'
}

# Merge variant spellings into one canonical name
CANONICAL = {
    'tulsi':'Tulsi','holy_basil':'Tulsi','tulasi':'Tulsi',
    'ocimum_tenuiflorum':'Tulsi','sacred_basil':'Tulsi',
    'neem':'Neem','azadirachta':'Neem','indian_lilac':'Neem',
    'aloe':'Aloe Vera','aloe_vera':'Aloe Vera',
    'turmeric':'Turmeric','curcuma':'Turmeric','haldi':'Turmeric',
    'ginger':'Ginger','zingiber':'Ginger','adrak':'Ginger',
    'ashwagandha':'Ashwagandha','withania':'Ashwagandha',
    'brahmi':'Brahmi','bacopa':'Brahmi',
    'amla':'Amla','phyllanthus_emblica':'Amla','gooseberry':'Amla',
    'giloy':'Giloy','guduchi':'Giloy','tinospora':'Giloy',
    'moringa':'Moringa','drumstick':'Moringa','sahjan':'Moringa',
    'hibiscus':'Hibiscus','gurhal':'Hibiscus','japa':'Hibiscus',
    'curry_leaf':'Curry Leaf','murraya':'Curry Leaf','kadi_patta':'Curry Leaf',
    'papaya':'Papaya','carica':'Papaya','papita':'Papaya',
    'guava':'Guava','psidium':'Guava','amrood':'Guava',
    'jamun':'Jamun','java_plum':'Jamun','syzygium':'Jamun',
    'mango':'Mango','mangifera':'Mango','aam':'Mango',
    'lemon':'Lemon','nimbu':'Lemon','citrus':'Lemon',
    'pomegranate':'Pomegranate','anar':'Pomegranate','punica':'Pomegranate',
    'arjun':'Arjun','arjuna':'Arjun','terminalia_arjuna':'Arjun',
    'bael':'Bael','bilva':'Bael','aegle':'Bael',
    'pongamia':'Pongamia Pinnata','karanja':'Pongamia Pinnata',
    'alstonia':'Alstonia Scholaris','saptaparni':'Alstonia Scholaris',
    'chinar':'Chinar','platanus':'Chinar',
    'jatropha':'Jatropha','ratanjot':'Jatropha',
    'tea':'Tea','camellia':'Tea','chai':'Tea',
    'mint':'Mint','mentha':'Mint','pudina':'Mint',
    'basil':'Basil','sweet_basil':'Basil',
}

def process_single_image(img_path, target_dir, index):
    try:
        shutil.copy2(img_path, target_dir/f"{index:05d}{img_path.suffix}")
        return True
    except: return False

def norm(raw):
    k = raw.lower().strip().replace(' ','_').replace('-','_')
    for key, val in CANONICAL.items():
        if key in k: return val
    return raw.strip().title()

def is_excluded(name):
    n = name.lower().replace(' ','_')
    return any(bad in n for bad in EXCLUDE)

buckets = defaultdict(list)
for src in SOURCES:
    if not os.path.exists(src): continue
    for root, dirs, files in os.walk(src):
        for f in files:
            fp = Path(root)/f
            if fp.suffix.lower() not in EXTS: continue
            label = norm(Path(root).name)
            if not is_excluded(label):
                buckets[label].append(fp)

print(f"\nRaw species found: {len(buckets)}")

shutil.rmtree(OUT, ignore_errors=True)
kept = []
dropped = []

with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    for species, images in sorted(buckets.items()):
        if len(images) < MIN_IMAGES:
            dropped.append((species, len(images)))
            continue
            
        d = Path(OUT)/species.replace(' ','_')
        d.mkdir(parents=True, exist_ok=True)
        
        # Parallel image copy
        futures = []
        for i, img in enumerate(images[:MAX_IMAGES]):
            futures.append(executor.submit(process_single_image, img, d, i))
        
        success_count = sum(1 for f in futures if f.result())
        kept.append((species, success_count))
        print(f"  ASSEMBLING: {species} ({success_count} images)")

print(f"\nKept:    {len(kept)} species")
print(f"Dropped: {len(dropped)} (under {MIN_IMAGES} images)")
print(f"Dropped list: {[d[0] for d in dropped]}")

index = [{'id':i,'name':s,'count':n} for i,(s,n) in enumerate(kept)]
with open(f"{OUT}/class_index.json",'w') as f:
    json.dump(index, f, indent=2)

print(f"\nDataset ready: {OUT}")
print(f"Total species: {len(kept)}")
print(f"Total images:  {sum(n for _,n in kept)}")
print("\nFinal species list:")
for s,n in kept: print(f"  {s}: {n}")
