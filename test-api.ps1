# Test script for Docker backend API
$body = @{
    wavelengths = @(400,500,600,700,800)
    intensities = @(1000,1500,1200,800,600)
} | ConvertTo-Json

Write-Host "Testing Docker backend API..."
Write-Host "Body: $body"

try {
    $response = Invoke-RestMethod -Uri "http://localhost/api/analyze" -Method POST -ContentType "application/json" -Body $body
    Write-Host "Success! Response:"
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
