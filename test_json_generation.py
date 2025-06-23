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

# Helper functions
def generate_random_email():
    """Generate a random email for testing"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"test_{random_str}@example.com"

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

def test_json_generation_custom():
    """Test JSON generation for custom automations"""
    print_test_header("JSON Generation for Custom Automations")
    
    # Test with Make.com
    make_request = {
        "task_description": "Send email when form is submitted",
        "platform": "Make.com",
        "ai_model": "gpt-4",
        "user_email": generate_random_email()
    }
    
    make_response = requests.post(f"{API_URL}/generate-automation-guest", json=make_request)
    print("Make.com Response:")
    print_response(make_response)
    
    # Test with n8n
    n8n_request = {
        "task_description": "Send email when form is submitted",
        "platform": "n8n",
        "ai_model": "gpt-4",
        "user_email": generate_random_email()
    }
    
    n8n_response = requests.post(f"{API_URL}/generate-automation-guest", json=n8n_request)
    print("n8n Response:")
    print_response(n8n_response)
    
    success = assert_status_code(make_response, 200) and assert_status_code(n8n_response, 200)
    success = assert_json_response(make_response) and assert_json_response(n8n_response) and success
    
    if success:
        # Check Make.com response
        make_json = make_response.json()
        success = assert_field_exists(make_json, "automation_json") and success
        
        try:
            make_content = json.loads(make_json["automation_json"])
            print("✅ Make.com automation_json contains valid JSON")
            
            # Check that it's not an error message
            json_str = make_json["automation_json"].lower()
            if "due to the complexity" in json_str or "not possible" in json_str:
                print("❌ Make.com automation_json contains error messages instead of valid JSON")
                success = False
            else:
                print("✅ Make.com automation_json contains actual JSON content, not error messages")
                
            # Check for proper structure
            if "name" in make_content and "flow" in make_content and "metadata" in make_content:
                print("✅ Make.com JSON has proper structure (name, flow, metadata)")
            else:
                print("❌ Make.com JSON missing required structure elements")
                success = False
                
            # Check for realistic module names
            if "flow" in make_content and len(make_content["flow"]) > 0:
                has_modules = any("module" in item for item in make_content["flow"])
                if has_modules:
                    print("✅ Make.com JSON contains modules with names")
                else:
                    print("❌ Make.com JSON doesn't contain proper module names")
                    success = False
        except json.JSONDecodeError:
            print("❌ Make.com automation_json is not valid JSON")
            success = False
            
        # Check n8n response
        n8n_json = n8n_response.json()
        success = assert_field_exists(n8n_json, "automation_json") and success
        
        try:
            n8n_content = json.loads(n8n_json["automation_json"])
            print("✅ n8n automation_json contains valid JSON")
            
            # Check that it's not an error message
            json_str = n8n_json["automation_json"].lower()
            if "due to the complexity" in json_str or "not possible" in json_str:
                print("❌ n8n automation_json contains error messages instead of valid JSON")
                success = False
            else:
                print("✅ n8n automation_json contains actual JSON content, not error messages")
                
            # Check for proper structure
            if "name" in n8n_content and "nodes" in n8n_content and "connections" in n8n_content:
                print("✅ n8n JSON has proper structure (name, nodes, connections)")
            else:
                print("❌ n8n JSON missing required structure elements")
                success = False
                
            # Check for realistic node types
            if "nodes" in n8n_content and len(n8n_content["nodes"]) > 0:
                has_types = any("type" in item for item in n8n_content["nodes"])
                if has_types:
                    print("✅ n8n JSON contains nodes with types")
                else:
                    print("❌ n8n JSON doesn't contain proper node types")
                    success = False
        except json.JSONDecodeError:
            print("❌ n8n automation_json is not valid JSON")
            success = False
    
    return success

def test_template_json_verification():
    """Test JSON generation for templates with different platforms"""
    print_test_header("Template JSON Verification")
    
    # Test with Make.com
    make_request = {
        "task_description": "Use template: Instagram Video Poster",
        "platform": "Make.com",
        "ai_model": "gpt-4",
        "user_email": generate_random_email()
    }
    
    make_response = requests.post(f"{API_URL}/generate-automation-guest", json=make_request)
    print("Make.com Template Response:")
    print_response(make_response)
    
    # Test with n8n
    n8n_request = {
        "task_description": "Use template: Instagram Video Poster",
        "platform": "n8n",
        "ai_model": "gpt-4",
        "user_email": generate_random_email()
    }
    
    n8n_response = requests.post(f"{API_URL}/generate-automation-guest", json=n8n_request)
    print("n8n Template Response:")
    print_response(n8n_response)
    
    success = assert_status_code(make_response, 200) and assert_status_code(n8n_response, 200)
    success = assert_json_response(make_response) and assert_json_response(n8n_response) and success
    
    if success:
        # Check Make.com response
        make_json = make_response.json()
        success = assert_field_exists(make_json, "automation_json") and success
        success = assert_field_equals(make_json, "is_template", True) and success
        
        # Check n8n response
        n8n_json = n8n_response.json()
        success = assert_field_exists(n8n_json, "automation_json") and success
        success = assert_field_equals(n8n_json, "is_template", True) and success
        
        # Verify the JSON is different for each platform
        if make_json["automation_json"] != n8n_json["automation_json"]:
            print("✅ Template JSON is different for Make.com and n8n")
        else:
            print("❌ Template JSON is the same for both platforms")
            success = False
            
        # Verify both are valid JSON
        try:
            make_content = json.loads(make_json["automation_json"])
            n8n_content = json.loads(n8n_json["automation_json"])
            print("✅ Both template JSONs are valid")
            
            # Check for proper structure
            if "name" in make_content and "flow" in make_content:
                print("✅ Make.com template JSON has proper structure")
            else:
                print("❌ Make.com template JSON missing required structure elements")
                success = False
                
            if "name" in n8n_content and "nodes" in n8n_content and "connections" in n8n_content:
                print("✅ n8n template JSON has proper structure")
            else:
                print("❌ n8n template JSON missing required structure elements")
                success = False
        except json.JSONDecodeError:
            print("❌ One or both template JSONs are not valid")
            success = False
    
    return success

def test_ai_model_json_generation():
    """Test JSON generation with different AI models"""
    print_test_header("AI Model JSON Generation")
    
    # Test with GPT-4
    gpt4_request = {
        "task_description": "Send email when form is submitted",
        "platform": "Make.com",
        "ai_model": "gpt-4",
        "user_email": generate_random_email()
    }
    
    gpt4_response = requests.post(f"{API_URL}/generate-automation-guest", json=gpt4_request)
    print("GPT-4 Response:")
    print_response(gpt4_response)
    
    # Test with Claude
    claude_request = {
        "task_description": "Send email when form is submitted",
        "platform": "Make.com",
        "ai_model": "claude-3-5-sonnet-20241022",
        "user_email": generate_random_email()
    }
    
    claude_response = requests.post(f"{API_URL}/generate-automation-guest", json=claude_request)
    print("Claude Response:")
    print_response(claude_response)
    
    success = assert_status_code(gpt4_response, 200) and assert_status_code(claude_response, 200)
    success = assert_json_response(gpt4_response) and assert_json_response(claude_response) and success
    
    if success:
        # Check GPT-4 response
        gpt4_json = gpt4_response.json()
        success = assert_field_exists(gpt4_json, "automation_json") and success
        success = assert_field_equals(gpt4_json, "ai_model", "gpt-4") and success
        
        try:
            json.loads(gpt4_json["automation_json"])
            print("✅ GPT-4 automation_json contains valid JSON")
        except json.JSONDecodeError:
            print("❌ GPT-4 automation_json is not valid JSON")
            success = False
            
        # Check Claude response
        claude_json = claude_response.json()
        success = assert_field_exists(claude_json, "automation_json") and success
        success = assert_field_equals(claude_json, "ai_model", "claude-3-5-sonnet-20241022") and success
        
        try:
            json.loads(claude_json["automation_json"])
            print("✅ Claude automation_json contains valid JSON")
        except json.JSONDecodeError:
            print("❌ Claude automation_json is not valid JSON")
            success = False
    
    return success

if __name__ == "__main__":
    results = {}
    
    # Run the tests
    results["json_generation_custom"] = test_json_generation_custom()
    results["template_json_verification"] = test_template_json_verification()
    results["ai_model_json_generation"] = test_ai_model_json_generation()
    
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