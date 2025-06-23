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

TEST_USER = {
    "email": generate_random_email(),
    "password": "TestPassword123!"
}

TEST_AUTOMATION_REQUEST = {
    "task_description": "When someone fills out my contact form, send them a welcome email",
    "platform": "Make.com",
    "ai_model": "gpt-4",
    "user_email": generate_random_email()
}

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

# Test functions for email validation and lead capture
def test_generate_automation_with_valid_email():
    """Test generating an automation with a valid email"""
    print_test_header("Generate Automation With Valid Email")
    
    # Create request with valid email
    valid_request = {
        "task_description": "When someone fills out my contact form, send them a welcome email",
        "platform": "Make.com",
        "ai_model": "gpt-4",
        "user_email": generate_random_email()
    }
    
    response = requests.post(f"{API_URL}/generate-automation-guest", json=valid_request)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        # Check for all expected fields
        required_fields = [
            "id", "task_description", "platform", "automation_summary", 
            "required_tools", "workflow_steps", "automation_json", "setup_instructions"
        ]
        for field in required_fields:
            success = assert_field_exists(response_json, field) and success
        
        # Verify task description matches our request
        success = assert_field_equals(response_json, "task_description", valid_request["task_description"]) and success
        success = assert_field_equals(response_json, "platform", valid_request["platform"]) and success
    
    return success, valid_request["user_email"] if success else None

def test_generate_automation_without_email():
    """Test generating an automation without an email (should fail)"""
    print_test_header("Generate Automation Without Email")
    
    # Create request without email field
    invalid_request = {
        "task_description": "When someone fills out my contact form, send them a welcome email",
        "platform": "Make.com",
        "ai_model": "gpt-4"
        # Missing user_email
    }
    
    response = requests.post(f"{API_URL}/generate-automation-guest", json=invalid_request)
    print_response(response)
    
    # We expect a validation error
    success = response.status_code in [400, 422]
    if success:
        print(f"✅ Status code is {response.status_code} (validation error) as expected")
    else:
        print(f"❌ Expected validation error status code, got {response.status_code}")
    
    return success

def test_generate_automation_with_empty_email():
    """Test generating an automation with an empty email (should fail)"""
    print_test_header("Generate Automation With Empty Email")
    
    # Create request with empty email
    invalid_request = {
        "task_description": "When someone fills out my contact form, send them a welcome email",
        "platform": "Make.com",
        "ai_model": "gpt-4",
        "user_email": ""
    }
    
    response = requests.post(f"{API_URL}/generate-automation-guest", json=invalid_request)
    print_response(response)
    
    # We expect a validation error
    success = response.status_code in [400, 422]
    if success:
        print(f"✅ Status code is {response.status_code} (validation error) as expected")
    else:
        print(f"❌ Expected validation error status code, got {response.status_code}")
    
    return success

def test_generate_automation_with_invalid_email():
    """Test generating an automation with an invalid email format (should fail)"""
    print_test_header("Generate Automation With Invalid Email")
    
    # Create request with invalid email format
    invalid_request = {
        "task_description": "When someone fills out my contact form, send them a welcome email",
        "platform": "Make.com",
        "ai_model": "gpt-4",
        "user_email": "not-an-email"
    }
    
    response = requests.post(f"{API_URL}/generate-automation-guest", json=invalid_request)
    print_response(response)
    
    # We expect a validation error
    success = response.status_code in [400, 422]
    if success:
        print(f"✅ Status code is {response.status_code} (validation error) as expected")
    else:
        print(f"❌ Expected validation error status code, got {response.status_code}")
    
    return success

def test_stats_endpoint():
    """Test the stats endpoint"""
    print_test_header("Stats Endpoint")
    
    response = requests.get(f"{API_URL}/")
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        # Check for all expected fields
        required_fields = [
            "total_automations", "total_leads", "total_users", "satisfaction_rate"
        ]
        for field in required_fields:
            success = assert_field_exists(response_json, field) and success
    
    return success

def test_backward_compatibility(token):
    """Test that authenticated user automation generation still works"""
    print_test_header("Backward Compatibility")
    
    # Test authenticated automation generation
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/generate-automation", json=TEST_AUTOMATION_REQUEST, headers=headers)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        # Check for all expected fields
        required_fields = [
            "id", "user_id", "task_description", "platform", "automation_summary", 
            "required_tools", "workflow_steps", "automation_json", "setup_instructions"
        ]
        for field in required_fields:
            success = assert_field_exists(response_json, field) and success
        
        # Verify task description matches our request
        success = assert_field_equals(response_json, "task_description", TEST_AUTOMATION_REQUEST["task_description"]) and success
        success = assert_field_equals(response_json, "platform", TEST_AUTOMATION_REQUEST["platform"]) and success
    
    return success

def run_email_validation_tests():
    """Run all email validation tests"""
    print_test_header("EMAIL VALIDATION TESTS")
    
    results = {}
    
    # Test without email
    results["generate_automation_without_email"] = test_generate_automation_without_email()
    
    # Test with empty email
    results["generate_automation_with_empty_email"] = test_generate_automation_with_empty_email()
    
    # Test with invalid email
    results["generate_automation_with_invalid_email"] = test_generate_automation_with_invalid_email()
    
    # Test with valid email
    success, email = test_generate_automation_with_valid_email()
    results["generate_automation_with_valid_email"] = success
    
    # Test stats endpoint
    results["stats_endpoint"] = test_stats_endpoint()
    
    # Test backward compatibility
    # First register a user
    registration_success, registration_data = register_test_user()
    results["user_registration"] = registration_success
    
    if registration_success:
        token = registration_data["access_token"]
        # Test backward compatibility
        results["backward_compatibility"] = test_backward_compatibility(token)
    
    # Print summary
    print("\n" + "=" * 80)
    print("EMAIL VALIDATION TEST SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        if not result:
            all_passed = False
        print(f"{status} - {test_name}")
    
    print("\nOverall Result:", "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED")
    
    return all_passed, results

def register_test_user():
    """Register a test user and return the token"""
    print_test_header("Register Test User")
    
    response = requests.post(f"{API_URL}/auth/register", json=TEST_USER)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        success = assert_field_exists(response_json, "access_token") and success
        success = assert_field_exists(response_json, "token_type") and success
        success = assert_field_exists(response_json, "user") and success
        
        if "user" in response_json:
            user = response_json["user"]
            success = assert_field_exists(user, "id") and success
            success = assert_field_exists(user, "email") and success
            success = assert_field_equals(user, "email", TEST_USER["email"]) and success
    
    return success, response.json() if success else None

if __name__ == "__main__":
    run_email_validation_tests()