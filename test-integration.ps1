# Integration test script for Purity Vision Lab

Write-Host "🧬 Testing Purity Vision Lab Integration..." -ForegroundColor Green

# Test ML Service Health
Write-Host "`n1. Testing ML Service Health..." -ForegroundColor Yellow
try {
    $mlHealth = docker exec purity_ml curl -s http://localhost:8001/api/ml/health | ConvertFrom-Json
    if ($mlHealth.status -eq "healthy") {
        Write-Host "   ✅ ML Service is healthy" -ForegroundColor Green
        Write-Host "   📊 Model: $($mlHealth.model_type)" -ForegroundColor Cyan
        Write-Host "   ⏱️  Uptime: $([math]::Round($mlHealth.uptime_seconds, 2)) seconds" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ ML Service is not healthy" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Failed to connect to ML Service" -ForegroundColor Red
}

# Test Backend Health
Write-Host "`n2. Testing Backend Health..." -ForegroundColor Yellow
try {
    $backendResponse = docker exec purity-vision-backend curl -s http://localhost:3000/health
    if ($backendResponse -eq "OK") {
        Write-Host "   ✅ Backend is healthy" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Backend health check failed" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Failed to connect to Backend" -ForegroundColor Red
}

# Test Frontend
Write-Host "`n3. Testing Frontend..." -ForegroundColor Yellow
try {
    $frontendStatus = docker exec purity-vision-frontend curl -s -o /dev/null -w "%{http_code}" http://localhost:80
    if ($frontendStatus -eq "200") {
        Write-Host "   ✅ Frontend is serving content" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Frontend returned status: $frontendStatus" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Failed to connect to Frontend" -ForegroundColor Red
}

# Test ML Analysis (through ML service directly)
Write-Host "`n4. Testing ML Analysis..." -ForegroundColor Yellow
try {
    $testData = @{
        wavelengths = @(200, 300, 400, 500, 600)
        intensities = @(0.1, 0.2, 0.15, 0.3, 0.25)
    } | ConvertTo-Json -Compress

    $analysisResult = docker exec purity_ml curl -s -X POST http://localhost:8001/api/ml/analyze -H "Content-Type: application/json" -d $testData | ConvertFrom-Json
    
    if ($analysisResult.purity_percentage) {
        Write-Host "   ✅ ML Analysis successful" -ForegroundColor Green
        Write-Host "   🧪 Purity: $($analysisResult.purity_percentage)%" -ForegroundColor Cyan
        Write-Host "   🎯 Confidence: $($analysisResult.confidence_score)" -ForegroundColor Cyan
        Write-Host "   🤖 Model: $($analysisResult.model_used)" -ForegroundColor Cyan
        Write-Host "   ⚡ Processing time: $($analysisResult.processing_time_ms)ms" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ ML Analysis failed" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Failed to perform ML analysis" -ForegroundColor Red
}

Write-Host "`n🎉 Integration Test Complete!" -ForegroundColor Green
Write-Host "`n📊 Services Status:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n🌐 Access URLs:" -ForegroundColor Yellow
Write-Host "   Frontend:   http://localhost:80" -ForegroundColor Cyan
Write-Host "   Backend:    http://localhost:3000" -ForegroundColor Cyan
Write-Host "   ML Service: http://localhost:8001" -ForegroundColor Cyan

Write-Host "`n📚 API Documentation:" -ForegroundColor Yellow
Write-Host "   ML API:     http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "   Health:     http://localhost:8001/api/ml/health" -ForegroundColor Cyan
