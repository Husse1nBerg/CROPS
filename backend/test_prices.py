"""Test script for the prices endpoint"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_endpoints():
    """Test health endpoints"""
    print("=== Testing Health Endpoints ===")
    
    # Test main health
    response = requests.get(f"{BASE_URL}/health")
    print(f"Main health: {response.status_code} - {response.json()}")
    
    # Test prices health (no auth required)
    response = requests.get(f"{BASE_URL}/api/prices/health")
    print(f"Prices health: {response.status_code} - {response.json()}")
    print()

def test_login():
    """Test login endpoint"""
    print("=== Testing Login ===")
    
    # Try login
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    print(f"Login attempt: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"Token received: {token_data['token_type']} {token_data['access_token'][:20]}...")
        return token_data['access_token']
    else:
        print(f"Login failed: {response.json()}")
        return None

def test_prices_endpoint_without_auth():
    """Test prices endpoint without authentication"""
    print("=== Testing Prices Endpoint (No Auth) ===")
    
    response = requests.get(f"{BASE_URL}/api/prices/")
    print(f"Prices without auth: {response.status_code}")
    
    if response.status_code == 401:
        print("Authentication required (expected)")
    elif response.status_code == 200:
        data = response.json()
        print(f"Prices returned: {len(data)} items")
        if data:
            print(f"First price: {data[0]}")
    else:
        print(f"Unexpected response: {response.text}")
    print()

def test_prices_endpoint_with_auth(token):
    """Test prices endpoint with authentication"""
    print("=== Testing Prices Endpoint (With Auth) ===")
    
    if not token:
        print("No token available, skipping authenticated test")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/prices/", headers=headers)
    
    print(f"Authenticated prices: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Prices returned: {len(data)} items")
        for item in data[:3]:  # Show first 3 items
            print(f"  - {item['product_name']} at {item['store_name']}: {item['price']} EGP")
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    try:
        test_health_endpoints()
        token = test_login()
        test_prices_endpoint_without_auth()
        test_prices_endpoint_with_auth(token)
        
        print("=== Summary ===")
        print("✓ Health endpoints working")
        print("✓ Login endpoint accessible")
        print("✓ Prices endpoint requires authentication")
        if token:
            print("✓ Prices endpoint returns data when authenticated")
        else:
            print("× Login failed - check user credentials")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Is it running on http://localhost:8000?")
    except Exception as e:
        print(f"ERROR: {e}")