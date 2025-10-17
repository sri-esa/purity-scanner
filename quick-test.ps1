Write-Host "🧬 Testing Purity Vision Lab..." -ForegroundColor Green

Write-Host "`n📊 Container Status:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n🔍 Testing ML Service Health..." -ForegroundColor Yellow
$mlResult = docker exec purity_ml curl -s http://localhost:8001/api/ml/health
Write-Host "ML Health Response: $mlResult" -ForegroundColor Cyan

Write-Host "`n🌐 Services are available at:" -ForegroundColor Green
Write-Host "   Frontend:   http://localhost:80" -ForegroundColor Cyan
Write-Host "   Backend:    http://localhost:3000" -ForegroundColor Cyan  
Write-Host "   ML Service: http://localhost:8001" -ForegroundColor Cyan
Write-Host "   ML API Docs: http://localhost:8001/docs" -ForegroundColor Cyan
