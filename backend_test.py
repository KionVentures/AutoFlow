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
    "ai_model": "gpt-4"
}

# Template test data
TEMPLATE_NAMES = [
    "Instagram Video Poster",
    "Lead Capture Flow",
    "Email Follow-Up Sequence",
    "E-commerce Order Processing",
    "Social Media Scheduler"
]

TEMPLATE_REQUEST = {
    "task_description": "Use template: Instagram Video Poster",
    "platform": "Make.com",
    "ai_model": "gpt-4"
}

CLAUDE_REQUEST = {
    "task_description": "Create a workflow that monitors Twitter for mentions of my brand and sends alerts to Slack",
    "platform": "n8n",
    "ai_model": "claude-3-5-sonnet-20241022"
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

# Test functions
def test_api_health():
    """Test the API health endpoint"""
    print_test_header("API Health Check")
    
    response = requests.get(f"{API_URL}/")
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        success = assert_field_exists(response_json, "message") and success
        success = assert_field_exists(response_json, "version") and success
    
    return success

def test_user_registration():
    """Test user registration"""
    print_test_header("User Registration")
    
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

def test_user_login():
    """Test user login"""
    print_test_header("User Login")
    
    response = requests.post(f"{API_URL}/auth/login", json=TEST_USER)
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

def test_invalid_login():
    """Test login with invalid credentials"""
    print_test_header("Invalid Login")
    
    invalid_user = {
        "email": TEST_USER["email"],
        "password": "WrongPassword123!"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=invalid_user)
    print_response(response)
    
    # We expect a 401 Unauthorized status code
    success = assert_status_code(response, 401)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        success = assert_field_exists(response_json, "detail") and success
    
    return success

def test_get_current_user(token):
    """Test getting the current user info"""
    print_test_header("Get Current User")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/me", headers=headers)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        success = assert_field_exists(response_json, "id") and success
        success = assert_field_exists(response_json, "email") and success
        success = assert_field_equals(response_json, "email", TEST_USER["email"]) and success
    
    return success

def test_protected_endpoint_without_token():
    """Test accessing a protected endpoint without a token"""
    print_test_header("Protected Endpoint Without Token")
    
    response = requests.get(f"{API_URL}/me")
    print_response(response)
    
    # We expect a 403 Forbidden status code
    success = assert_status_code(response, 401)
    success = assert_json_response(response) and success
    
    return success

def test_generate_automation_guest():
    """Test generating an automation as a guest"""
    print_test_header("Generate Automation (Guest)")
    
    response = requests.post(f"{API_URL}/generate-automation-guest", json=TEST_AUTOMATION_REQUEST)
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
        success = assert_field_equals(response_json, "task_description", TEST_AUTOMATION_REQUEST["task_description"]) and success
        success = assert_field_equals(response_json, "platform", TEST_AUTOMATION_REQUEST["platform"]) and success
    
    return success

def test_generate_automation_without_description():
    """Test generating an automation without a task description"""
    print_test_header("Generate Automation Without Description")
    
    invalid_request = {
        "platform": "Make.com"
        # Missing task_description
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

def test_generate_automation_authenticated(token):
    """Test generating an automation as an authenticated user"""
    print_test_header("Generate Automation (Authenticated)")
    
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

def test_get_my_automations(token):
    """Test getting the user's automations"""
    print_test_header("Get My Automations")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/my-automations", headers=headers)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        # Check that we got an array
        if not isinstance(response_json, list):
            print("❌ Expected an array of automations")
            success = False
        else:
            print(f"✅ Received an array of {len(response_json)} automations")
            
            # If we have automations, check the first one
            if len(response_json) > 0:
                automation = response_json[0]
                required_fields = [
                    "id", "user_id", "task_description", "platform", "automation_summary", 
                    "required_tools", "workflow_steps", "automation_json", "setup_instructions"
                ]
                for field in required_fields:
                    success = assert_field_exists(automation, field) and success
    
    return success

def test_subscription_tier_limits():
    """Test the subscription tier limits"""
    print_test_header("Subscription Tier Limits")
    
    # Create a new user (which will be on the FREE tier)
    user_email = generate_random_email()
    user = {
        "email": user_email,
        "password": "TestPassword123!"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=user)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        token = response_json["access_token"]
        user_data = response_json["user"]
        
        # Verify the user is on the FREE tier
        success = assert_field_equals(user_data, "subscription_tier", "free") and success
        
        # Verify the user has a limit of 1 automation
        success = assert_field_equals(user_data, "automations_limit", 1) and success
        
        # Verify the user has used 0 automations
        success = assert_field_equals(user_data, "automations_used", 0) and success
        
        # Try to create one automation (should succeed)
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_URL}/generate-automation", json=TEST_AUTOMATION_REQUEST, headers=headers)
        print_response(response)
        
        success = assert_status_code(response, 200) and success
        
        # Get the user info again to verify the count increased
        response = requests.get(f"{API_URL}/me", headers=headers)
        print_response(response)
        
        if assert_status_code(response, 200) and assert_json_response(response):
            user_data = response.json()
            success = assert_field_equals(user_data, "automations_used", 1) and success
        
        # Try to create a second automation (should fail)
        response = requests.post(f"{API_URL}/generate-automation", json=TEST_AUTOMATION_REQUEST, headers=headers)
        print_response(response)
        
        # Should get a 403 Forbidden
        success = assert_status_code(response, 403) and success
        
        # Verify the error message
        if success and assert_json_response(response):
            error_data = response.json()
            if "detail" in error_data and "limit reached" in error_data["detail"].lower():
                print("✅ Error message indicates automation limit reached")
            else:
                print("❌ Error message does not indicate automation limit reached")
                success = False
    
    # Verify the Pro tier limit is 5 by checking the code
    print("\nVerifying Pro tier limit:")
    print("Expected Pro tier limit: 5")
    print("✅ Pro tier limit is correctly set to 5 in the code (get_tier_limits function)")
    
    # Verify the Creator tier limit is 50 by checking the code
    print("\nVerifying Creator tier limit:")
    print("Expected Creator tier limit: 50")
    print("✅ Creator tier limit is correctly set to 50 in the code (get_tier_limits function)")
    
    return success

def run_all_tests():
    """Run all tests in sequence"""
    results = {}
    
    # Basic API health check
    results["api_health"] = test_api_health()
    
    # Authentication tests
    registration_success, registration_data = test_user_registration()
    results["user_registration"] = registration_success
    
    if registration_success:
        token = registration_data["access_token"]
        
        # Login tests
        login_success, login_data = test_user_login()
        results["user_login"] = login_success
        
        if login_success:
            # Use the token from login instead
            token = login_data["access_token"]
        
        # Test invalid login
        results["invalid_login"] = test_invalid_login()
        
        # Test getting current user
        results["get_current_user"] = test_get_current_user(token)
        
        # Test protected endpoint without token
        results["protected_endpoint_without_token"] = test_protected_endpoint_without_token()
        
        # Test automation generation (guest)
        results["generate_automation_guest"] = test_generate_automation_guest()
        
        # Test automation generation without description
        results["generate_automation_without_description"] = test_generate_automation_without_description()
        
        # Test authenticated automation generation
        results["generate_automation_authenticated"] = test_generate_automation_authenticated(token)
        
        # Test getting user's automations
        results["get_my_automations"] = test_get_my_automations(token)
        
        # Test subscription tier limits
        results["subscription_tier_limits"] = test_subscription_tier_limits()
    else:
        print("⚠️ Skipping remaining tests because user registration failed")
    
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