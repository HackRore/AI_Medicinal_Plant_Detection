$imgPath = "D:\PROJECT FINAL\dataset\master_dataset\Tulsi\00155.jpg"
if (Test-Path $imgPath) {
    Write-Host "Found image at $imgPath"
    $response = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/predict" -Form @{file = Get-Item $imgPath}
    $response | ConvertTo-Json -Depth 10 | Out-File -Encoding utf8 "local_predict.json"
    Write-Host "Success! Results saved to local_predict.json"
} else {
    Write-Error "Image not found at $imgPath"
}
