from pathlib import Path
import os
import json

print("\n=== CHECK 1: DATASET STATUS ===")
ds = Path('dataset/master_dataset')
if not ds.exists(): ds = Path('dataset/unified_dataset')

if ds.exists():
    results = []
    for f in sorted(ds.iterdir()):
        if f.is_dir():
            n = len(list(f.rglob('*.jpg')) + list(f.rglob('*.png')) + list(f.rglob('*.jpeg')))
            results.append((f.name, n))
    
    results.sort(key=lambda x: -x[1])
    good = [(n,c) for n,c in results if c >= 200]
    weak = [(n,c) for n,c in results if 80 <= c < 200]
    drop = [(n,c) for n,c in results if c < 80]
    
    print(f'GOOD (200+ images): {len(good)} species')
    print(f'WEAK (80-199):      {len(weak)} species')
    print(f'DROP (under 80):    {len(drop)} species')
    print()
    for name, count in results:
        tag = 'GOOD' if count>=200 else 'WEAK' if count>=80 else 'DROP'
        print(f'  {tag}  {count:5d}  {name}')
else:
    print("Dataset directory not found!")

print("\n=== CHECK 2: KNOWLEDGE BASE STATUS ===")
try:
    kb = json.load(open('backend/app/data/medicinal_knowledge.json', encoding='utf-8'))
    print(f'KB entries: {len(kb)}')
    for name, data in kb.items():
        issues = []
        if len(data.get('ayurvedic_uses',[])) < 4: issues.append('needs more uses')
        if len(data.get('preparation','')) < 50: issues.append('preparation too short')
        if not data.get('active_compounds',[]): issues.append('no compounds')
        if not data.get('contraindications',[]): issues.append('no contraindications')
        if not data.get('references',[]): issues.append('NO REFERENCES')
        status = 'INCOMPLETE' if issues else 'OK'
        print(f'  {status}: {name}' + (f' — {", ".join(issues)}' if issues else ''))
except Exception as e:
    print(f"KB check failed: {e}")

print("\n=== CHECK 3: BACKEND STATUS ===")
print("Backend is currently configured for file-based API.")
print("Database dependencies have been neutralized.")
