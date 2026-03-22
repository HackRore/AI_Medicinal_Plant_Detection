import glob
import os
import sys

def build_model():
    print("Initializing EfficientNetV2 H5 tensor reconstruction...")
    chunks = sorted(glob.glob('ml_models/efficientnetv2_best.h5.part*'), key=lambda x: int(x.split('part')[-1]))
    if not chunks:
        print("No binary chunks found. Skipping reconstruction.")
        return
        
    out_path = 'ml_models/efficientnetv2_best.h5'
    with open(out_path, 'wb') as outfile:
        for chunk in chunks:
            print(f"Reading chunk: {chunk}")
            with open(chunk, 'rb') as infile:
                outfile.write(infile.read())
                
    print(f"Successfully reconstructed {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    build_model()
