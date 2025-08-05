import requests
import time
import json

def test_web_app():
    """Test the web application endpoints"""
    
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Trading Signal Web App")
    print("-" * 40)
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print("   ❌ Health check failed")
            return
        
        # Test main page
        print("2. Testing main page...")
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Main page loads successfully")
        else:
            print("   ❌ Main page failed to load")
            return
        
        # Test analysis endpoint (this will take a while)
        print("3. Testing analysis endpoint...")
        print("   ⏳ This may take 1-2 minutes...")
        
        start_time = time.time()
        response = requests.post(f"{base_url}/analyze", 
                               json={}, 
                               timeout=300)  # 5 minute timeout
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Analysis completed in {end_time - start_time:.1f} seconds")
            print(f"   📊 Signal: {result.get('signal', 'Unknown')}")
            print(f"   📈 Confidence: {result.get('confidence', 0):.1%}")
            print(f"   📰 Articles: {result.get('total_articles', 0)}")
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web app. Make sure it's running on http://localhost:5001")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Analysis may take longer than expected.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_web_app()