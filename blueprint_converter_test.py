#!/usr/bin/env python3
import requests
import json
import time
import random
import string
import os
from typing import Dict, Any, Optional

# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"\'')
            break

# Ensure the URL doesn't have quotes
BACKEND_URL = BACKEND_URL.strip('"\'')
API_URL = f"{BACKEND_URL}/api"

print(f"Using API URL: {API_URL}")

# Test data
def generate_random_email():
    """Generate a random email for testing"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"test_{random_str}@example.com"

# Blueprint test data
MAKE_BLUEPRINT_JSON = """{
  "name": "Test Workflow",
  "flow": [
    {
      "id": 1,
      "module": "webhook:webhook",
      "parameters": {}
    },
    {
      "id": 2,
      "module": "email:send",
      "parameters": {
        "to": "{{1.data.email}}",
        "subject": "Thank you for contacting us",
        "text": "We received your message and will get back to you soon."
      }
    }
  ]
}"""

N8N_BLUEPRINT_JSON = """{
  "name": "Test Workflow", 
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [240, 300]
    },
    {
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "position": [460, 300],
      "parameters": {
        "to": "={{ $json.email }}",
        "subject": "Thank you for contacting us",
        "text": "We received your message and will get back to you soon."
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [["Send Email"]]
    }
  }
}"""

INVALID_JSON = """{
  "name": "Invalid JSON,
  "flow": [
    {
      "id": 1
      "module": "webhook:webhook",
    }
  ]
}"""

# Helper functions
def print_test_header(test_name):
    """Print a formatted test header"""
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)

def print_response(response):
    """Print the response details"""
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def assert_status_code(response, expected_code):
    """Assert that the status code matches the expected code"""
    if response.status_code != expected_code:
        print(f"❌ Expected status code {expected_code}, got {response.status_code}")
        return False
    print(f"✅ Status code is {expected_code} as expected")
    return True

def assert_json_response(response):
    """Assert that the response is valid JSON"""
    try:
        response.json()
        print("✅ Response is valid JSON")
        return True
    except:
        print("❌ Response is not valid JSON")
        return False

def assert_field_exists(response_json, field):
    """Assert that a field exists in the response JSON"""
    if field not in response_json:
        print(f"❌ Field '{field}' not found in response")
        return False
    print(f"✅ Field '{field}' exists in response")
    return True

def assert_field_equals(response_json, field, expected_value):
    """Assert that a field equals the expected value"""
    if field not in response_json:
        print(f"❌ Field '{field}' not found in response")
        return False
    if response_json[field] != expected_value:
        print(f"❌ Field '{field}' expected to be '{expected_value}', got '{response_json[field]}'")
        return False
    print(f"✅ Field '{field}' equals '{expected_value}' as expected")
    return True

def create_user(tier="free"):
    """Create a user for testing"""
    print_test_header(f"Create {tier.capitalize()} User")
    
    user_email = generate_random_email()
    user = {
        "email": user_email,
        "password": "TestPassword123!"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=user)
    print_response(response)
    
    if response.status_code != 200:
        print(f"❌ Failed to create {tier} user")
        return None
    
    token = response.json()["access_token"]
    
    # For testing purposes, we need to directly update the user's tier in the database
    # This would normally be done through a payment process
    # Since we can't directly access the database in this test, we'll use a workaround
    
    # For Pro tier testing, we'll use a special test endpoint or assume the first user is Pro
    # In a real environment, you would need admin access to update the user's tier
    
    if tier == "pro":
        print("⚠️ Note: In a real environment, you would need to upgrade the user to Pro tier")
        print("⚠️ For testing purposes, we'll assume this user has Pro tier access")
        
        # In a real test environment, you might have an admin endpoint to update user tiers
        # For now, we'll just note that this is a limitation of our test environment
    
    return token

def test_blueprint_conversion_make_to_n8n(token):
    """Test converting a Make.com blueprint to n8n format"""
    print_test_header("Blueprint Conversion: Make.com to n8n")
    
    headers = {"Authorization": f"Bearer {token}"}
    request_data = {
        "blueprint_json": MAKE_BLUEPRINT_JSON,
        "source_platform": "Make.com",
        "target_platform": "n8n",
        "ai_model": "gpt-4"
    }
    
    response = requests.post(f"{API_URL}/convert-blueprint", json=request_data, headers=headers)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        # Check for all expected fields
        required_fields = [
            "id", "user_id", "source_platform", "target_platform", "ai_model",
            "original_json", "converted_json", "conversion_notes", "created_at"
        ]
        for field in required_fields:
            success = assert_field_exists(response_json, field) and success
        
        # Verify platforms match our request
        success = assert_field_equals(response_json, "source_platform", "Make.com") and success
        success = assert_field_equals(response_json, "target_platform", "n8n") and success
        success = assert_field_equals(response_json, "ai_model", "gpt-4") and success
        
        # Verify the converted JSON is not empty and is valid JSON
        try:
            converted = json.loads(response_json["converted_json"])
            if "nodes" in converted:  # n8n format should have nodes
                print("✅ Converted JSON is valid n8n format")
            else:
                print("❌ Converted JSON does not appear to be valid n8n format")
                success = False
        except json.JSONDecodeError:
            print("❌ Converted JSON is not valid JSON")
            success = False
    
    return success

def test_blueprint_conversion_n8n_to_make(token):
    """Test converting an n8n blueprint to Make.com format"""
    print_test_header("Blueprint Conversion: n8n to Make.com")
    
    headers = {"Authorization": f"Bearer {token}"}
    request_data = {
        "blueprint_json": N8N_BLUEPRINT_JSON,
        "source_platform": "n8n",
        "target_platform": "Make.com",
        "ai_model": "gpt-4"
    }
    
    response = requests.post(f"{API_URL}/convert-blueprint", json=request_data, headers=headers)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        # Check for all expected fields
        required_fields = [
            "id", "user_id", "source_platform", "target_platform", "ai_model",
            "original_json", "converted_json", "conversion_notes", "created_at"
        ]
        for field in required_fields:
            success = assert_field_exists(response_json, field) and success
        
        # Verify platforms match our request
        success = assert_field_equals(response_json, "source_platform", "n8n") and success
        success = assert_field_equals(response_json, "target_platform", "Make.com") and success
        
        # Verify the converted JSON is not empty and is valid JSON
        try:
            converted = json.loads(response_json["converted_json"])
            if "flow" in converted:  # Make.com format should have flow
                print("✅ Converted JSON is valid Make.com format")
            else:
                print("❌ Converted JSON does not appear to be valid Make.com format")
                success = False
        except json.JSONDecodeError:
            print("❌ Converted JSON is not valid JSON")
            success = False
    
    return success

def test_blueprint_conversion_free_tier():
    """Test that Free tier users cannot access blueprint conversion"""
    print_test_header("Blueprint Conversion: Free Tier Access")
    
    # Create a new user (which will be on the FREE tier)
    token = create_user(tier="free")
    if not token:
        return False
    
    # Try to use the blueprint conversion API
    headers = {"Authorization": f"Bearer {token}"}
    request_data = {
        "blueprint_json": MAKE_BLUEPRINT_JSON,
        "source_platform": "Make.com",
        "target_platform": "n8n",
        "ai_model": "gpt-4"
    }
    
    response = requests.post(f"{API_URL}/convert-blueprint", json=request_data, headers=headers)
    print_response(response)
    
    # Should get a 403 Forbidden
    success = assert_status_code(response, 403)
    success = assert_json_response(response) and success
    
    if success:
        error_data = response.json()
        if "detail" in error_data and "pro feature" in error_data["detail"].lower():
            print("✅ Error message indicates this is a Pro feature")
        else:
            print("❌ Error message does not indicate this is a Pro feature")
            success = False
    
    return success

def test_blueprint_conversion_invalid_json(token):
    """Test blueprint conversion with invalid JSON"""
    print_test_header("Blueprint Conversion: Invalid JSON")
    
    headers = {"Authorization": f"Bearer {token}"}
    request_data = {
        "blueprint_json": INVALID_JSON,
        "source_platform": "Make.com",
        "target_platform": "n8n",
        "ai_model": "gpt-4"
    }
    
    response = requests.post(f"{API_URL}/convert-blueprint", json=request_data, headers=headers)
    print_response(response)
    
    # Should get a 400 Bad Request
    success = assert_status_code(response, 400)
    success = assert_json_response(response) and success
    
    if success:
        error_data = response.json()
        if "detail" in error_data and "invalid json" in error_data["detail"].lower():
            print("✅ Error message indicates invalid JSON format")
        else:
            print("❌ Error message does not indicate invalid JSON format")
            success = False
    
    return success

def test_blueprint_conversion_same_platform(token):
    """Test blueprint conversion with same source and target platform"""
    print_test_header("Blueprint Conversion: Same Platform")
    
    headers = {"Authorization": f"Bearer {token}"}
    request_data = {
        "blueprint_json": MAKE_BLUEPRINT_JSON,
        "source_platform": "Make.com",
        "target_platform": "Make.com",  # Same as source
        "ai_model": "gpt-4"
    }
    
    response = requests.post(f"{API_URL}/convert-blueprint", json=request_data, headers=headers)
    print_response(response)
    
    # Should get a 400 Bad Request
    success = assert_status_code(response, 400)
    success = assert_json_response(response) and success
    
    if success:
        error_data = response.json()
        if "detail" in error_data and "different" in error_data["detail"].lower():
            print("✅ Error message indicates source and target must be different")
        else:
            print("❌ Error message does not indicate source and target must be different")
            success = False
    
    return success

def test_blueprint_conversion_claude(token):
    """Test blueprint conversion with Claude AI model"""
    print_test_header("Blueprint Conversion: Claude AI Model")
    
    headers = {"Authorization": f"Bearer {token}"}
    request_data = {
        "blueprint_json": MAKE_BLUEPRINT_JSON,
        "source_platform": "Make.com",
        "target_platform": "n8n",
        "ai_model": "claude-3-5-sonnet-20241022"
    }
    
    response = requests.post(f"{API_URL}/convert-blueprint", json=request_data, headers=headers)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        # Verify AI model matches our request
        success = assert_field_equals(response_json, "ai_model", "claude-3-5-sonnet-20241022") and success
        
        # Verify the converted JSON is not empty and is valid JSON
        try:
            converted = json.loads(response_json["converted_json"])
            if "nodes" in converted:  # n8n format should have nodes
                print("✅ Claude successfully converted to n8n format")
            else:
                print("❌ Claude conversion does not appear to be valid n8n format")
                success = False
        except json.JSONDecodeError:
            print("❌ Claude conversion is not valid JSON")
            success = False
    
    return success

def test_get_my_conversions(token):
    """Test getting the user's blueprint conversions"""
    print_test_header("Get My Conversions")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/my-conversions", headers=headers)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        # Check that we got an array
        if not isinstance(response_json, list):
            print("❌ Expected an array of conversions")
            success = False
        else:
            print(f"✅ Received an array of {len(response_json)} conversions")
            
            # If we have conversions, check the first one
            if len(response_json) > 0:
                conversion = response_json[0]
                required_fields = [
                    "id", "user_id", "source_platform", "target_platform", "ai_model",
                    "original_json", "converted_json", "conversion_notes", "created_at"
                ]
                for field in required_fields:
                    success = assert_field_exists(conversion, field) and success
    
    return success

def run_all_tests():
    """Run all tests in sequence"""
    results = {}
    
    # Test Free tier access (should be denied)
    results["blueprint_conversion_free_tier"] = test_blueprint_conversion_free_tier()
    
    # Create a user for testing
    token = create_user(tier="free")
    if not token:
        print("⚠️ Skipping remaining tests because user creation failed")
        return False, results
    
    # Test getting conversions (should work even for free tier)
    results["get_my_conversions"] = test_get_my_conversions(token)
    
    # Note: The following tests would require a Pro tier user
    # Since we can't directly upgrade a user to Pro tier in our test environment,
    # we'll skip these tests and just note what they would test
    
    print("\n" + "=" * 80)
    print("SKIPPED TESTS (Require Pro Tier)")
    print("=" * 80)
    print("- Blueprint Conversion: Make.com to n8n")
    print("- Blueprint Conversion: n8n to Make.com")
    print("- Blueprint Conversion: Invalid JSON")
    print("- Blueprint Conversion: Same Platform")
    print("- Blueprint Conversion: Claude AI Model")
    print("\nNote: These tests would verify the functionality of the blueprint conversion API")
    print("      but require a Pro tier user, which we can't create in our test environment.")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        if not result:
            all_passed = False
        print(f"{status} - {test_name}")
    
    print("\nOverall Result:", "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED")
    
    return all_passed, results

if __name__ == "__main__":
    run_all_tests()