import urllib.request
url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Tulsi_plant2.jpg/320px-Tulsi_plant2.jpg'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
with urllib.request.urlopen(req) as response, open(r'd:\PROJECT STAGE 1\tulsi_sample.jpg', 'wb') as out_file:
    data = response.read()
    out_file.write(data)
print("Image downloaded successfully to d:\\PROJECT STAGE 1\\tulsi_sample.jpg")
