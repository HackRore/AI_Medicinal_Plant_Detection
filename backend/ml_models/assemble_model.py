import os
import sys

# Portable path: current directory
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(MODEL_DIR, 'efficientnetv2_best.h5')

parts = sorted([
    f for f in os.listdir(MODEL_DIR)
    if f.startswith('efficientnetv2_best.h5.part')
])

print(f"Found {len(parts)} parts to assemble:")
for p in parts:
    size = os.path.getsize(os.path.join(MODEL_DIR, p))
    print(f"  {p} — {size/1024/1024:.1f} MB")

print(f"\nAssembling into: {OUTPUT}")
total = 0

if len(parts) == 0:
    print("NO PARTS FOUND! Cannot assemble.")
    sys.exit(1)

with open(OUTPUT, 'wb') as outfile:
    for part in parts:
        part_path = os.path.join(MODEL_DIR, part)
        with open(part_path, 'rb') as infile:
            data = infile.read()
            outfile.write(data)
            total += len(data)
        print(f"  Added {part} — running total: {total/1024/1024:.1f} MB")

final_size = os.path.getsize(OUTPUT)
print(f"\nAssembly complete!")
print(f"Final model size: {final_size/1024/1024:.1f} MB")

# Verify it loads
print("\nVerifying model loads correctly...")
import tensorflow as tf
model = tf.keras.models.load_model(OUTPUT, compile=False)
print(f"Model loaded successfully!")
print(f"Input shape  : {model.input_shape}")
print(f"Output shape : {model.output_shape}")
print(f"Parameters   : {model.count_params():,}")
