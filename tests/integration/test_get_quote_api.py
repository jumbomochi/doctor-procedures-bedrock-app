#!/usr/bin/env python3

import requests
import json

# API Gateway endpoint
BASE_URL = "https://jj6skt98b3.execute-api.us-east-1.amazonaws.com/dev"

def test_get_quote_specific_procedure():
    """Test getting median cost for a specific procedure by a doctor"""
    print("🧪 Testing: Get quote for specific procedure...")
    
    url = f"{BASE_URL}/get-quote"
    params = {
        'doctorName': 'Dr. Alice Smith',
        'procedureCode': 'CONSULT001'
    }
    
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('message', '')}")
        print(f"📊 Median Cost: ${data.get('medianCost', 0):.2f}")
        print(f"🔬 Sample Count: {data.get('sampleCount', 0)}")
        if 'costRange' in data:
            print(f"📈 Cost Range: ${data['costRange']['min']:.2f} - ${data['costRange']['max']:.2f}")
    else:
        print(f"❌ Error: {response.text}")
    
    print("-" * 50)

def test_get_quote_all_procedures():
    """Test getting median cost for all procedures by a doctor"""
    print("🧪 Testing: Get quote for all procedures by doctor...")
    
    url = f"{BASE_URL}/get-quote"
    params = {
        'doctorName': 'Dr. Alice Smith'
        # No procedureCode parameter
    }
    
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('message', '')}")
        print(f"📊 Overall Median Cost: ${data.get('medianCost', 0):.2f}")
        print(f"🔬 Total Procedures: {data.get('sampleCount', 0)}")
        if 'procedureTypes' in data:
            print(f"🏥 Procedure Types: {', '.join(data['procedureTypes'])}")
        if 'costRange' in data:
            print(f"📈 Cost Range: ${data['costRange']['min']:.2f} - ${data['costRange']['max']:.2f}")
    else:
        print(f"❌ Error: {response.text}")
    
    print("-" * 50)

def test_get_quote_nonexistent_doctor():
    """Test error handling for nonexistent doctor"""
    print("🧪 Testing: Error handling for nonexistent doctor...")
    
    url = f"{BASE_URL}/get-quote"
    params = {
        'doctorName': 'Dr. Nonexistent Doctor'
    }
    
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 404:
        data = response.json()
        print(f"✅ Expected 404: {data.get('message', '')}")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    print("-" * 50)

def test_get_quote_missing_doctor():
    """Test error handling for missing doctor parameter"""
    print("🧪 Testing: Error handling for missing doctor parameter...")
    
    url = f"{BASE_URL}/get-quote"
    params = {}  # No parameters
    
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 400:
        data = response.json()
        print(f"✅ Expected 400: {data.get('message', '')}")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    print("-" * 50)

if __name__ == "__main__":
    print("🏥 Testing GetQuote Lambda Function")
    print("=" * 50)
    
    test_get_quote_specific_procedure()
    test_get_quote_all_procedures()
    test_get_quote_nonexistent_doctor()
    test_get_quote_missing_doctor()
    
    print("🎯 Test completed!")
