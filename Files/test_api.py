import requests
import json
import time
import sys

# Fix Windows console encoding for emojis
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://13.53.39.78"
API_URL = f"{BASE_URL}/api"

def print_header(title):
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)

def run_api_tests():
    print_header("Running API Integration Tests")
    
    passed = 0
    failed = 0
    start_time = time.time()
    
    # 1. Test Stats Endpoint (Public)
    try:
        print("Test 1: GET /api/stats (Public endpoint)")
        response = requests.get(f"{API_URL}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and "recruiters" in data:
                print("  ✅ Passed. Valid JSON response received.")
                passed += 1
            else:
                print("  ❌ Failed. Missing keys in response.")
                failed += 1
        else:
            print(f"  ❌ Failed. Status code: {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"  ❌ Failed with exception: {e}")
        failed += 1

    # 2. Test Auth Endpoint (Unauthorized access)
    try:
        print("Test 2: GET /api/auth/me (Unauthorized access)")
        response = requests.get(f"{API_URL}/auth/me", timeout=5)
        if response.status_code == 401:
            print("  ✅ Passed. Correctly blocked unauthorized user.")
            passed += 1
        else:
            print(f"  ❌ Failed. Expected 401, got {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"  ❌ Failed with exception: {e}")
        failed += 1

    # 3. Test Profile Endpoint (Unauthorized access)
    try:
        print("Test 3: GET /api/profile/me (Unauthorized access)")
        response = requests.get(f"{API_URL}/profile/me", timeout=5)
        if response.status_code == 401:
            print("  ✅ Passed. Correctly blocked unauthorized user.")
            passed += 1
        else:
            print(f"  ❌ Failed. Expected 401, got {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"  ❌ Failed with exception: {e}")
        failed += 1
        
    # 4. Test Backend Health
    try:
        print("Test 4: Backend Service Health")
        # Since we know /api/stats works and connects to DB, we use it as health check
        response = requests.get(f"{API_URL}/stats", timeout=5)
        if response.status_code == 200:
            print("  ✅ Passed. Backend is up and connected to DB.")
            passed += 1
        else:
            print(f"  ❌ Failed. Backend returned {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"  ❌ Failed with exception: {e}")
        failed += 1

    end_time = time.time()
    
    print_header("TEST SUMMARY")
    print(f"Total Tests Run: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! The API is stable.")
    else:
        print("\n⚠️ SOME TESTS FAILED. Please check the logs.")

if __name__ == "__main__":
    run_api_tests()
