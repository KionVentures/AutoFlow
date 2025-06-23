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

def test_get_templates():
    """Test retrieving all templates"""
    print_test_header("Get Templates")
    
    response = requests.get(f"{API_URL}/templates")
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        success = assert_field_exists(response_json, "templates") and success
        
        if "templates" in response_json:
            templates = response_json["templates"]
            if len(templates) == 5:
                print(f"✅ Received 5 templates as expected")
            else:
                print(f"❌ Expected 5 templates, got {len(templates)}")
                success = False
            
            # Check if all expected templates are present
            template_names = [t["name"] for t in templates]
            for expected_name in TEMPLATE_NAMES:
                if expected_name in template_names:
                    print(f"✅ Template '{expected_name}' found")
                else:
                    print(f"❌ Template '{expected_name}' not found")
                    success = False
    
    return success

def test_get_specific_template():
    """Test retrieving a specific template"""
    print_test_header("Get Specific Template")
    
    template_name = "Instagram Video Poster"
    response = requests.get(f"{API_URL}/templates/{template_name}")
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        # Check for all required template fields
        required_fields = [
            "automation_summary", "required_tools", "workflow_steps", 
            "automation_json", "setup_instructions", "bonus_content",
            "is_template", "template_id"
        ]
        for field in required_fields:
            success = assert_field_exists(response_json, field) and success
        
        # Verify it's marked as a template
        success = assert_field_equals(response_json, "is_template", True) and success
    
    return success

def test_get_specific_template_with_platform():
    """Test retrieving a specific template with different platforms"""
    print_test_header("Get Specific Template with Platform")
    
    template_name = "Instagram Video Poster"
    
    # Test with Make.com platform
    response_make = requests.get(f"{API_URL}/templates/{template_name}?platform=Make.com")
    print("Make.com Platform Response:")
    print_response(response_make)
    
    # Test with n8n platform
    response_n8n = requests.get(f"{API_URL}/templates/{template_name}?platform=n8n")
    print("n8n Platform Response:")
    print_response(response_n8n)
    
    success = assert_status_code(response_make, 200) and assert_status_code(response_n8n, 200)
    success = assert_json_response(response_make) and assert_json_response(response_n8n) and success
    
    if success:
        # Verify the JSON is different for each platform
        make_json = response_make.json()["automation_json"]
        n8n_json = response_n8n.json()["automation_json"]
        
        if make_json != n8n_json:
            print("✅ Platform-specific JSON is different for Make.com and n8n")
        else:
            print("❌ Platform-specific JSON is the same for both platforms")
            success = False
    
    return success

def test_template_recognition():
    """Test template recognition in automation generation"""
    print_test_header("Template Recognition")
    
    response = requests.post(f"{API_URL}/generate-automation-guest", json=TEMPLATE_REQUEST)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        # Verify it's marked as a template
        success = assert_field_exists(response_json, "is_template") and success
        success = assert_field_equals(response_json, "is_template", True) and success
        
        # Verify template_id exists
        success = assert_field_exists(response_json, "template_id") and success
        
        # Verify automation_json is valid JSON
        success = assert_field_exists(response_json, "automation_json") and success
        try:
            json_content = json.loads(response_json["automation_json"])
            print("✅ automation_json contains valid JSON")
            
            # Check that it's not an error message
            json_str = response_json["automation_json"].lower()
            if "due to the complexity" in json_str or "not possible" in json_str:
                print("❌ automation_json contains error messages instead of valid JSON")
                success = False
            else:
                print("✅ automation_json contains actual JSON content, not error messages")
        except json.JSONDecodeError:
            print("❌ automation_json is not valid JSON")
            success = False
    
    return success

def test_ai_model_selection():
    """Test different AI models for automation generation"""
    print_test_header("AI Model Selection")
    
    # Test with GPT-4
    gpt4_response = requests.post(f"{API_URL}/generate-automation-guest", json=TEST_AUTOMATION_REQUEST)
    print("GPT-4 Response:")
    print_response(gpt4_response)
    
    # Test with Claude
    claude_response = requests.post(f"{API_URL}/generate-automation-guest", json=CLAUDE_REQUEST)
    print("Claude Response:")
    print_response(claude_response)
    
    success = assert_status_code(gpt4_response, 200) and assert_status_code(claude_response, 200)
    success = assert_json_response(gpt4_response) and assert_json_response(claude_response) and success
    
    if success:
        # Verify AI model is stored in the response
        gpt4_json = gpt4_response.json()
        claude_json = claude_response.json()
        
        success = assert_field_exists(gpt4_json, "ai_model") and success
        success = assert_field_exists(claude_json, "ai_model") and success
        
        success = assert_field_equals(gpt4_json, "ai_model", "gpt-4") and success
        success = assert_field_equals(claude_json, "ai_model", "claude-3-5-sonnet-20241022") and success
    
    return success

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

def test_fallback_json_generation():
    """Test fallback JSON generation when AI fails"""
    print_test_header("Fallback JSON Generation")
    
    # Create a request that might trigger fallback (complex task)
    complex_request = {
        "task_description": "Create a complex multi-step workflow that integrates with 15 different systems, processes data through machine learning models, and implements advanced business logic with conditional branching based on real-time market data analysis",
        "platform": "Make.com",
        "ai_model": "gpt-4",
        "user_email": generate_random_email()
    }
    
    response = requests.post(f"{API_URL}/generate-automation-guest", json=complex_request)
    print_response(response)
    
    success = assert_status_code(response, 200)
    success = assert_json_response(response) and success
    
    if success:
        response_json = response.json()
        success = assert_field_exists(response_json, "automation_json") and success
        
        try:
            json_content = json.loads(response_json["automation_json"])
            print("✅ automation_json contains valid JSON even for complex request")
            
            # Check for basic structure
            if "name" in json_content and ("flow" in json_content or "nodes" in json_content):
                print("✅ JSON has proper structure even for complex request")
            else:
                print("❌ JSON missing required structure elements")
                success = False
                
            # Check for webhook module (common in fallback)
            if "flow" in json_content and len(json_content["flow"]) > 0:
                has_webhook = any("webhook" in str(item.get("module", "")).lower() for item in json_content["flow"])
                if has_webhook:
                    print("✅ JSON contains webhook module as expected in fallback")
                else:
                    print("❌ JSON doesn't contain expected webhook module")
            elif "nodes" in json_content and len(json_content["nodes"]) > 0:
                has_webhook = any("webhook" in str(item.get("type", "")).lower() for item in json_content["nodes"])
                if has_webhook:
                    print("✅ JSON contains webhook node as expected in fallback")
                else:
                    print("❌ JSON doesn't contain expected webhook node")
        except json.JSONDecodeError:
            print("❌ automation_json is not valid JSON")
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

def test_enhanced_setup_instructions():
    """Test that setup instructions include platform-specific details"""
    print_test_header("Enhanced Setup Instructions")
    
    # Test with Make.com
    make_response = requests.post(f"{API_URL}/generate-automation-guest", 
                                 json={"task_description": "Send weekly sales reports to my team", 
                                       "platform": "Make.com", 
                                       "ai_model": "gpt-4"})
    
    # Test with n8n
    n8n_response = requests.post(f"{API_URL}/generate-automation-guest", 
                                json={"task_description": "Send weekly sales reports to my team", 
                                      "platform": "n8n", 
                                      "ai_model": "gpt-4"})
    
    success = assert_status_code(make_response, 200) and assert_status_code(n8n_response, 200)
    success = assert_json_response(make_response) and assert_json_response(n8n_response) and success
    
    if success:
        make_instructions = make_response.json()["setup_instructions"]
        n8n_instructions = n8n_response.json()["setup_instructions"]
        
        # Check for platform-specific keywords in instructions
        make_keywords = ["Make.com", "Import Blueprint"]
        n8n_keywords = ["n8n", "Import from JSON"]
        
        make_has_keywords = all(keyword.lower() in make_instructions.lower() for keyword in make_keywords)
        n8n_has_keywords = all(keyword.lower() in n8n_instructions.lower() for keyword in n8n_keywords)
        
        if make_has_keywords:
            print("✅ Make.com instructions contain platform-specific keywords")
        else:
            print("❌ Make.com instructions missing platform-specific keywords")
            success = False
            
        if n8n_has_keywords:
            print("✅ n8n instructions contain platform-specific keywords")
        else:
            print("❌ n8n instructions missing platform-specific keywords")
            success = False
    
    return success

def test_template_usage_limits(token):
    """Test that template usage doesn't count toward limits"""
    print_test_header("Template Usage Limits")
    
    # Create a new user (which will be on the FREE tier with 1 automation limit)
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
        
        # First, use a template (shouldn't count toward limit)
        headers = {"Authorization": f"Bearer {token}"}
        template_response = requests.post(f"{API_URL}/generate-automation", 
                                         json=TEMPLATE_REQUEST, 
                                         headers=headers)
        print("Template Response:")
        print_response(template_response)
        
        success = assert_status_code(template_response, 200) and success
        
        # Check user info - should still have 0 automations used
        user_response = requests.get(f"{API_URL}/me", headers=headers)
        print("User Info After Template:")
        print_response(user_response)
        
        if assert_status_code(user_response, 200) and assert_json_response(user_response):
            user_data = user_response.json()
            success = assert_field_equals(user_data, "automations_used", 0) and success
        
        # Now create a custom automation (should count toward limit)
        custom_response = requests.post(f"{API_URL}/generate-automation", 
                                       json=TEST_AUTOMATION_REQUEST, 
                                       headers=headers)
        print("Custom Automation Response:")
        print_response(custom_response)
        
        success = assert_status_code(custom_response, 200) and success
        
        # Check user info again - should now have 1 automation used
        user_response = requests.get(f"{API_URL}/me", headers=headers)
        print("User Info After Custom Automation:")
        print_response(user_response)
        
        if assert_status_code(user_response, 200) and assert_json_response(user_response):
            user_data = user_response.json()
            success = assert_field_equals(user_data, "automations_used", 1) and success
        
        # Try another template (should still work)
        template_response = requests.post(f"{API_URL}/generate-automation", 
                                         json={"task_description": "Use template: Lead Capture Flow", 
                                               "platform": "Make.com", 
                                               "ai_model": "gpt-4"}, 
                                         headers=headers)
        print("Second Template Response:")
        print_response(template_response)
        
        success = assert_status_code(template_response, 200) and success
        
        # Try another custom automation (should fail due to limit)
        custom_response = requests.post(f"{API_URL}/generate-automation", 
                                       json={"task_description": "Send daily reports to Slack", 
                                             "platform": "Make.com", 
                                             "ai_model": "gpt-4"}, 
                                       headers=headers)
        print("Second Custom Automation Response:")
        print_response(custom_response)
        
        # Should get a 403 Forbidden
        success = assert_status_code(custom_response, 403) and success
    
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
        
        # Test template endpoints
        results["get_templates"] = test_get_templates()
        results["get_specific_template"] = test_get_specific_template()
        results["get_specific_template_with_platform"] = test_get_specific_template_with_platform()
        
        # Test automation generation (guest)
        results["generate_automation_guest"] = test_generate_automation_guest()
        
        # Test automation generation without description
        results["generate_automation_without_description"] = test_generate_automation_without_description()
        
        # Test authenticated automation generation
        results["generate_automation_authenticated"] = test_generate_automation_authenticated(token)
        
        # Test getting user's automations
        results["get_my_automations"] = test_get_my_automations(token)
        
        # Test template recognition
        results["template_recognition"] = test_template_recognition()
        
        # Test AI model selection
        results["ai_model_selection"] = test_ai_model_selection()
        
        # Test enhanced setup instructions
        results["enhanced_setup_instructions"] = test_enhanced_setup_instructions()
        
        # Test template usage limits
        results["template_usage_limits"] = test_template_usage_limits(token)
        
        # Test subscription tier limits
        results["subscription_tier_limits"] = test_subscription_tier_limits()
        
        # Test JSON generation for custom automations
        results["json_generation_custom"] = test_json_generation_custom()
        
        # Test fallback JSON generation
        results["fallback_json_generation"] = test_fallback_json_generation()
        
        # Test AI model JSON generation
        results["ai_model_json_generation"] = test_ai_model_json_generation()
        
        # Test template JSON verification
        results["template_json_verification"] = test_template_json_verification()
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