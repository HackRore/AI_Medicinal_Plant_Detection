import os

file_path = r"d:\PROJECT STAGE 1\backend\ml_models\efficientnetv2_best.h5"
chunk_size = 15 * 1024 * 1024  # 15 MB

with open(file_path, "rb") as f:
    data = f.read()

total_chunks = (len(data) // chunk_size) + (1 if len(data) % chunk_size != 0 else 0)

for i in range(total_chunks):
    chunk_data = data[i * chunk_size : (i + 1) * chunk_size]
    with open(f"{file_path}.part{i}", "wb") as chunk_file:
        chunk_file.write(chunk_data)

print(f"Successfully split into {total_chunks} parts.")
