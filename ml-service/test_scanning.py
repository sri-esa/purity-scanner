#!/usr/bin/env python3
"""
Quick test script for the 2D scanning system
"""
import requests
import time
import json

# API base URL
BASE_URL = "http://localhost:8001/api/ml"

def test_health():
    """Test if the service is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_hardware_status():
    """Test hardware status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/scan/hardware/status")
        print(f"✅ Hardware status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Hardware status failed: {e}")
        return False

def test_small_scan():
    """Test a small 2x2 scan"""
    print("\n🔬 Starting small test scan (2x2 grid)...")
    
    # Scan parameters for a quick test
    scan_params = {
        "x_start": 0.0,
        "y_start": 0.0,
        "x_end": 1.0,
        "y_end": 1.0,
        "step_x": 1.0,
        "step_y": 1.0,
        "integration_time": 0.01,  # Very fast for testing
        "model_id": "mock",
        "serpentine": True,
        "batch_size": 1
    }
    
    try:
        # Start scan
        response = requests.post(f"{BASE_URL}/scan/start", json=scan_params)
        print(f"✅ Scan started: {response.status_code}")
        scan_result = response.json()
        print(f"   Scan ID: {scan_result.get('scan_id')}")
        
        # Monitor progress
        print("\n📊 Monitoring scan progress...")
        for i in range(10):  # Max 10 checks
            time.sleep(1)
            
            status_response = requests.get(f"{BASE_URL}/scan/status")
            status = status_response.json()
            
            progress = status.get('progress', 0) * 100
            print(f"   Progress: {progress:.1f}% ({status.get('completed_points', 0)}/{status.get('total_points', 0)} points)")
            
            if status.get('status') in ['completed', 'error', 'cancelled']:
                print(f"✅ Scan finished with status: {status.get('status')}")
                break
        
        # Get results if completed
        if status.get('status') == 'completed':
            print("\n📈 Getting scan results...")
            
            # Get summary
            summary_response = requests.get(f"{BASE_URL}/scan/result/summary")
            if summary_response.status_code == 200:
                summary = summary_response.json()
                stats = summary.get('statistics', {})
                print(f"   Grid shape: {summary.get('grid_shape')}")
                print(f"   Mean purity: {stats.get('mean', 0):.1f}%")
                print(f"   Min purity: {stats.get('min', 0):.1f}%")
                print(f"   Max purity: {stats.get('max', 0):.1f}%")
            
            # Save heatmap
            heatmap_response = requests.get(f"{BASE_URL}/scan/result/heatmap?format=png")
            if heatmap_response.status_code == 200:
                with open("test_heatmap.png", "wb") as f:
                    f.write(heatmap_response.content)
                print("   💾 Heatmap saved as 'test_heatmap.png'")
            
            # Get raw data
            data_response = requests.get(f"{BASE_URL}/scan/result/data?format=json")
            if data_response.status_code == 200:
                with open("test_scan_data.json", "w") as f:
                    json.dump(data_response.json(), f, indent=2)
                print("   💾 Raw data saved as 'test_scan_data.json'")
        
        return True
        
    except Exception as e:
        print(f"❌ Scan test failed: {e}")
        return False

def test_single_analysis():
    """Test single spectrum analysis"""
    print("\n🧪 Testing single spectrum analysis...")
    
    # Mock spectrum data
    test_data = {
        "wavelengths": list(range(400, 1800, 10)),  # 400-1800 nm, 10nm steps
        "intensities": [100 + i * 0.1 for i in range(140)]  # Mock intensities
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=test_data)
        print(f"✅ Analysis completed: {response.status_code}")
        result = response.json()
        print(f"   Purity: {result.get('purity_percentage', 0):.1f}%")
        print(f"   Confidence: {result.get('confidence_score', 0):.3f}")
        print(f"   Contaminants: {result.get('contaminants', [])}")
        return True
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Purity Vision Lab 2D Scanning System")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("❌ Server not running. Please start with: uvicorn main:app --port 8001")
        return
    
    # Test 2: Hardware status
    test_hardware_status()
    
    # Test 3: Single analysis
    test_single_analysis()
    
    # Test 4: Small scan
    test_small_scan()
    
    print("\n🎉 Testing completed!")
    print("\n📱 Next steps:")
    print("   1. Open http://localhost:8001/static/index.html for the web interface")
    print("   2. Open http://localhost:8001/docs for API documentation")
    print("   3. Check generated files: test_heatmap.png, test_scan_data.json")

if __name__ == "__main__":
    main()
