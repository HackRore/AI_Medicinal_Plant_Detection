import zipfile
src = r"C:\Users\HackRore\.cache\kagglehub\datasets\rizkikecek\dataset-herbal-leaves\1.zip"
try:
    with zipfile.ZipFile(src, 'r') as z:
        print(f"Total files: {len(z.namelist())}")
        for name in z.namelist()[:10]:
            print(name)
except Exception as e:
    print(e)
