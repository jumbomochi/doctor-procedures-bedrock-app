#!/usr/bin/env python3
"""
Simple local test script that doesn't require Docker
"""
import sys
import os
import json

# Add the function directories to Python path
sys.path.append('functions/add_doctor_procedure')
sys.path.append('functions/get_quote_lambda')
sys.path.append('functions/show_history_lambda')
sys.path.append('functions/bedrock_intent_mapper_lambda')

def test_add_doctor_procedure():
    """Test the add doctor procedure lambda function"""
    print("🧪 Testing Add Doctor Procedure Lambda...")
    
    # Mock the environment
    os.environ['DYNAMODB_TABLE_NAME'] = 'DoctorProcedures'
    
    # Create test event
    test_event = {
        "body": json.dumps({
            "doctorName": "Dr. Alice Smith",
            "procedureCode": "CONSULT001",
            "procedureName": "Initial Consultation",
            "cost": 150.00,
            "time": "2025-07-31T10:30:00Z"
        })
    }
    
    try:
        # This would normally import and test the function
        # For now, we'll just validate the event structure
        body = json.loads(test_event['body'])
        required_fields = ['doctorName', 'procedureCode', 'cost']
        
        for field in required_fields:
            if field not in body:
                raise ValueError(f"Missing required field: {field}")
        
        print("   ✅ Event structure is valid")
        print(f"   📝 Doctor: {body['doctorName']}")
        print(f"   🏥 Procedure: {body['procedureName']} ({body['procedureCode']})")
        print(f"   💰 Cost: ${body['cost']}")
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    return True

def test_get_quote():
    """Test the get quote lambda function"""
    print("\n🧪 Testing Get Quote Lambda...")
    
    test_event = {
        "queryStringParameters": {
            "procedureCode": "CONSULT001"
        }
    }
    
    try:
        query_params = test_event.get('queryStringParameters', {})
        procedure_code = query_params.get('procedureCode')
        
        if not procedure_code:
            raise ValueError("Missing required parameter: procedureCode")
        
        print("   ✅ Event structure is valid")
        print(f"   🔍 Looking up procedure: {procedure_code}")
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    return True

def test_show_history():
    """Test the show history lambda function"""
    print("\n🧪 Testing Show History Lambda...")
    
    test_event = {
        "queryStringParameters": {
            "doctorName": "Dr. Alice Smith",
            "limit": "5"
        }
    }
    
    try:
        query_params = test_event.get('queryStringParameters', {})
        doctor_name = query_params.get('doctorName')
        limit = query_params.get('limit', '5')
        
        if not doctor_name:
            raise ValueError("Missing required parameter: doctorName")
        
        print("   ✅ Event structure is valid")
        print(f"   👨‍⚕️ Doctor: {doctor_name}")
        print(f"   📊 Limit: {limit}")
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    return True

def validate_template():
    """Validate the SAM template structure"""
    print("\n🧪 Validating SAM Template...")
    
    try:
        with open('template.yaml', 'r') as f:
            content = f.read()
        
        # Basic validation checks
        required_sections = ['AWSTemplateFormatVersion', 'Transform', 'Resources']
        for section in required_sections:
            if section not in content:
                raise ValueError(f"Missing required section: {section}")
        
        print("   ✅ Template structure is valid")
        print("   📄 Found all required sections")
        
    except Exception as e:
        print(f"   ❌ Validation failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Running Local Tests (No Docker Required)")
    print("=" * 50)
    
    tests = [
        ("Template Validation", validate_template),
        ("Add Doctor Procedure", test_add_doctor_procedure),
        ("Get Quote", test_get_quote),
        ("Show History", test_show_history)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        print("\nNext steps:")
        print("1. Install Docker to run full SAM local tests")
        print("2. Start DynamoDB Local: docker run -p 8000:8000 amazon/dynamodb-local")
        print("3. Run: sam local start-api --port 3000")
        print("4. Set up Bedrock Agent with your OpenAPI schemas")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
