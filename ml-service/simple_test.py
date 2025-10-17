#!/usr/bin/env python3
"""
Simple test for the ML service
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_basic_endpoints():
    """Test basic endpoints that should work"""
    
    print("🧪 Testing Basic ML Service Endpoints")
    print("=" * 40)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test 2: Health check
    try:
        response = requests.get(f"{BASE_URL}/api/ml/health")
        print(f"✅ Health check: {response.status_code}")
        result = response.json()
        print(f"   Status: {result.get('status')}")
        print(f"   Model: {result.get('model_type')}")
        print(f"   Uptime: {result.get('uptime_seconds', 0):.1f}s")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: Single spectrum analysis
    try:
        test_spectrum = {
            "wavelengths": list(range(400, 1800, 10)),
            "intensities": [100 + i * 0.1 for i in range(140)]
        }
        
        response = requests.post(f"{BASE_URL}/api/ml/analyze", json=test_spectrum)
        print(f"✅ Spectrum analysis: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Purity: {result.get('purity_percentage', 0):.1f}%")
            print(f"   Confidence: {result.get('confidence_score', 0):.3f}")
            print(f"   Contaminants: {len(result.get('contaminants', []))} detected")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Spectrum analysis failed: {e}")
    
    # Test 4: Available models
    try:
        response = requests.get(f"{BASE_URL}/api/ml/models")
        print(f"✅ Models endpoint: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print(f"   Available models: {len(models)}")
            for model in models:
                print(f"     - {model.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Models endpoint failed: {e}")
    
    print("\n🎉 Basic testing completed!")
    print("\n📱 Next steps:")
    print("   1. Open http://localhost:8001/static/index.html")
    print("   2. Open http://localhost:8001/docs")
    print("   3. Try the web interface for 2D scanning")

if __name__ == "__main__":
    test_basic_endpoints()
