"""
AutoFlow AI - Advanced Workflow Conversion and Debugging System
Core Functions: Make↔n8n Conversion, Troubleshooting, Auto-Debug, Prompt Engine
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class WorkflowPlatform(str, Enum):
    MAKE = "make"
    N8N = "n8n"

class ErrorType(str, Enum):
    MODULE_NOT_FOUND = "module_not_found"
    CONNECTION_ERROR = "connection_error"
    PARAMETER_MISSING = "parameter_missing"
    CREDENTIAL_ERROR = "credential_error"
    TYPE_MISMATCH = "type_mismatch"
    LOGIC_ERROR = "logic_error"

@dataclass
class WorkflowError:
    error_type: ErrorType
    module_id: str
    module_name: str
    description: str
    suggested_fix: str
    severity: str  # "critical", "warning", "info"

@dataclass
class ConversionResult:
    success: bool
    converted_json: str
    warnings: List[str]
    fallback_modules: List[str]
    comments: List[str]

# MAKE.COM TO N8N MODULE MAPPING
MAKE_TO_N8N_MAPPING = {
    # Google Services
    "google-sheets:WatchRows": "n8n-nodes-base.googleSheetsTrigger",
    "google-sheets:SearchRows": "n8n-nodes-base.googleSheets",
    "google-sheets:AddRow": "n8n-nodes-base.googleSheets", 
    "google-sheets:UpdateRow": "n8n-nodes-base.googleSheets",
    "google-drive:WatchFiles": "n8n-nodes-base.googleDriveTrigger",
    "google-drive:UploadFile": "n8n-nodes-base.googleDrive",
    
    # OpenAI
    "openai:CreateChatCompletion": "n8n-nodes-base.openAi",
    "openai:CreateImage": "n8n-nodes-base.openAi",
    "openai:CreateCompletion": "n8n-nodes-base.openAi",
    
    # HTTP & Webhooks
    "http:ActionSendData": "n8n-nodes-base.httpRequest",
    "http:ActionSendDataOAuth2": "n8n-nodes-base.httpRequest",
    "webhook:CustomWebHook": "n8n-nodes-base.webhook",
    
    # WordPress
    "wordpress:CreatePost": "n8n-nodes-base.wordpress",
    "wordpress:UpdatePost": "n8n-nodes-base.wordpress",
    "wordpress:GetPost": "n8n-nodes-base.wordpress",
    
    # Social Media
    "instagram:CreateMedia": "n8n-nodes-base.httpRequest",  # Fallback to HTTP
    "facebook:CreatePost": "n8n-nodes-base.facebookGraphApi",
    "twitter:CreateTweet": "n8n-nodes-base.twitter",
    "youtube:UploadVideo": "n8n-nodes-base.youTube",
    
    # Tools
    "builtin:Sleep": "n8n-nodes-base.wait",
    "builtin:SetVariable": "n8n-nodes-base.set",
    "builtin:TextAggregator": "n8n-nodes-base.merge",
    "json:ParseJSON": "n8n-nodes-base.code",
    
    # Email
    "email:ActionSendEmail": "n8n-nodes-base.emailSend",
    "gmail:ActionSendEmail": "n8n-nodes-base.gmail",
    "gmail:TriggerWatchEmails": "n8n-nodes-base.gmail",
    
    # CRM
    "hubspot:CreateContact": "n8n-nodes-base.hubspot",
    "hubspot:UpdateContact": "n8n-nodes-base.hubspot",
    "hubspot:SearchContacts": "n8n-nodes-base.hubspot"
}

# N8N TO MAKE.COM MODULE MAPPING
N8N_TO_MAKE_MAPPING = {v: k for k, v in MAKE_TO_N8N_MAPPING.items()}

# Add specific n8n nodes that don't have direct Make equivalents
N8N_TO_MAKE_MAPPING.update({
    "n8n-nodes-base.start": "webhook:CustomWebHook",
    "n8n-nodes-base.set": "builtin:SetVariable",
    "n8n-nodes-base.code": "json:ParseJSON",
    "n8n-nodes-base.if": "builtin:Router",
    "n8n-nodes-base.merge": "builtin:TextAggregator",
    "n8n-nodes-base.wait": "builtin:Sleep"
})

class WorkflowConverter:
    """Handles conversion between Make.com and n8n workflows"""
    
    def __init__(self):
        self.make_to_n8n = MAKE_TO_N8N_MAPPING
        self.n8n_to_make = N8N_TO_MAKE_MAPPING
    
    def convert_make_to_n8n(self, make_json: Dict[str, Any]) -> ConversionResult:
        """Convert Make.com scenario to n8n workflow"""
        try:
            warnings = []
            fallback_modules = []
            comments = []
            
            # Extract scenario info
            scenario_name = make_json.get("name", "Converted Workflow")
            flow = make_json.get("flow", [])
            
            # Convert modules to nodes
            nodes = []
            connections = {}
            node_positions = {}
            
            for i, module in enumerate(flow):
                module_id = module.get("id", i + 1)
                module_name = module.get("module", "")
                module_params = module.get("parameters", {})
                module_mapper = module.get("mapper", {})
                
                # Find n8n equivalent
                n8n_node_type = self.make_to_n8n.get(module_name)
                
                if not n8n_node_type:
                    # Fallback to HTTP request
                    n8n_node_type = "n8n-nodes-base.httpRequest"
                    fallback_modules.append(f"Module '{module_name}' converted to HTTP Request")
                    warnings.append(f"No direct n8n equivalent for '{module_name}', using HTTP Request")
                
                # Convert parameters
                node_params = self._convert_make_params_to_n8n(module_name, module_params, module_mapper)
                
                # Create n8n node
                node = {
                    "parameters": node_params,
                    "name": f"Step {module_id}",
                    "type": n8n_node_type,
                    "typeVersion": 1,
                    "position": [240 + i * 220, 300]
                }
                
                # Add credentials if needed
                if self._requires_credentials(n8n_node_type):
                    node["credentials"] = self._get_n8n_credentials(n8n_node_type)
                
                nodes.append(node)
                node_positions[str(module_id)] = f"Step {module_id}"
            
            # Convert connections
            connections = self._convert_make_connections_to_n8n(flow, node_positions)
            
            # Build n8n workflow
            n8n_workflow = {
                "name": scenario_name,
                "nodes": nodes,
                "connections": connections,
                "active": False,
                "settings": {"executionOrder": "v1"},
                "versionId": "1",
                "meta": {"templateCredsSetupCompleted": False},
                "id": scenario_name.lower().replace(" ", "-")
            }
            
            comments.append("Converted from Make.com scenario")
            if fallback_modules:
                comments.extend(fallback_modules)
            
            return ConversionResult(
                success=True,
                converted_json=json.dumps(n8n_workflow, indent=2),
                warnings=warnings,
                fallback_modules=fallback_modules,
                comments=comments
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                converted_json="",
                warnings=[f"Conversion failed: {str(e)}"],
                fallback_modules=[],
                comments=[]
            )
    
    def convert_n8n_to_make(self, n8n_json: Dict[str, Any]) -> ConversionResult:
        """Convert n8n workflow to Make.com scenario"""
        try:
            warnings = []
            fallback_modules = []
            comments = []
            
            # Extract workflow info
            workflow_name = n8n_json.get("name", "Converted Scenario")
            nodes = n8n_json.get("nodes", [])
            connections = n8n_json.get("connections", {})
            
            # Convert nodes to modules
            flow = []
            module_mapping = {}
            
            for i, node in enumerate(nodes):
                node_type = node.get("type", "")
                node_name = node.get("name", f"Node {i}")
                node_params = node.get("parameters", {})
                
                # Find Make.com equivalent
                make_module = self.n8n_to_make.get(node_type)
                
                if not make_module:
                    # Fallback to HTTP module
                    make_module = "http:ActionSendData"
                    fallback_modules.append(f"Node '{node_type}' converted to HTTP module")
                    warnings.append(f"No direct Make.com equivalent for '{node_type}', using HTTP module")
                
                # Convert parameters
                make_params = self._convert_n8n_params_to_make(node_type, node_params)
                
                # Create Make.com module
                module = {
                    "id": i + 1,
                    "module": make_module,
                    "version": 1,
                    "parameters": make_params,
                    "mapper": {},
                    "metadata": {
                        "designer": {
                            "x": i * 300,
                            "y": 0
                        }
                    }
                }
                
                flow.append(module)
                module_mapping[node_name] = i + 1
            
            # Build Make.com scenario
            make_scenario = {
                "name": workflow_name,
                "flow": flow,
                "metadata": {
                    "instant": False,
                    "version": 1,
                    "scenario": {
                        "roundtrips": 1,
                        "maxErrors": 3,
                        "autoCommit": True,
                        "sequential": False
                    },
                    "designer": {"orphans": []},
                    "zone": "eu1.make.com"
                }
            }
            
            comments.append("Converted from n8n workflow")
            if fallback_modules:
                comments.extend(fallback_modules)
            
            return ConversionResult(
                success=True,
                converted_json=json.dumps(make_scenario, indent=2),
                warnings=warnings,
                fallback_modules=fallback_modules,
                comments=comments
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                converted_json="",
                warnings=[f"Conversion failed: {str(e)}"],
                fallback_modules=[],
                comments=[]
            )
    
    def _convert_make_params_to_n8n(self, module_name: str, params: Dict, mapper: Dict) -> Dict:
        """Convert Make.com parameters to n8n format"""
        converted = {}
        
        # Google Sheets specific conversions
        if "google-sheets" in module_name:
            if "spreadsheetId" in params:
                converted["sheetId"] = params["spreadsheetId"]
            if "worksheetId" in params:
                converted["range"] = "A:Z"  # Convert worksheet to range
        
        # OpenAI specific conversions
        elif "openai" in module_name:
            if "model" in params:
                converted["model"] = params["model"]
            if "max_tokens" in params:
                converted["maxTokens"] = params["max_tokens"]
            if "messages" in mapper:
                converted["messages"] = {"values": mapper["messages"]}
        
        # HTTP specific conversions
        elif "http" in module_name:
            if "url" in mapper:
                converted["url"] = mapper["url"]
            if "method" in params:
                converted["method"] = params["method"].upper()
        
        # Default: copy all parameters
        else:
            converted.update(params)
            converted.update(mapper)
        
        return converted
    
    def _convert_n8n_params_to_make(self, node_type: str, params: Dict) -> Dict:
        """Convert n8n parameters to Make.com format"""
        converted = {}
        
        # Google Sheets specific conversions
        if "googleSheets" in node_type:
            if "sheetId" in params:
                converted["spreadsheetId"] = params["sheetId"]
            if "range" in params:
                converted["worksheetId"] = "gid=0"
        
        # OpenAI specific conversions
        elif "openAi" in node_type:
            if "model" in params:
                converted["model"] = params["model"]
            if "maxTokens" in params:
                converted["max_tokens"] = params["maxTokens"]
        
        # HTTP specific conversions
        elif "httpRequest" in node_type:
            if "url" in params:
                converted["url"] = params["url"]
            if "method" in params:
                converted["method"] = params["method"].lower()
        
        # Default: copy all parameters
        else:
            converted.update(params)
        
        return converted
    
    def _convert_make_connections_to_n8n(self, flow: List[Dict], node_positions: Dict) -> Dict:
        """Convert Make.com flow connections to n8n connections"""
        connections = {}
        
        for i, module in enumerate(flow):
            if i < len(flow) - 1:  # Not the last module
                current_name = node_positions.get(str(module.get("id", i + 1)))
                next_name = node_positions.get(str(flow[i + 1].get("id", i + 2)))
                
                if current_name and next_name:
                    connections[current_name] = {
                        "main": [[next_name]]
                    }
        
        return connections
    
    def _requires_credentials(self, node_type: str) -> bool:
        """Check if n8n node type requires credentials"""
        credential_nodes = [
            "n8n-nodes-base.googleSheets",
            "n8n-nodes-base.googleSheetsTrigger",
            "n8n-nodes-base.openAi",
            "n8n-nodes-base.wordpress",
            "n8n-nodes-base.gmail"
        ]
        return node_type in credential_nodes
    
    def _get_n8n_credentials(self, node_type: str) -> Dict:
        """Get credential configuration for n8n node"""
        credential_map = {
            "n8n-nodes-base.googleSheets": {"googleSheetsOAuth2Api": {"id": "google_sheets", "name": "Google Sheets"}},
            "n8n-nodes-base.googleSheetsTrigger": {"googleSheetsOAuth2Api": {"id": "google_sheets", "name": "Google Sheets"}},
            "n8n-nodes-base.openAi": {"openAiApi": {"id": "openai", "name": "OpenAI"}},
            "n8n-nodes-base.wordpress": {"wordpressApi": {"id": "wordpress", "name": "WordPress"}},
            "n8n-nodes-base.gmail": {"gmailOAuth2": {"id": "gmail", "name": "Gmail"}}
        }
        return credential_map.get(node_type, {})

class WorkflowDebugger:
    """Handles workflow debugging and error detection"""
    
    def __init__(self):
        self.common_errors = {
            "missing_spreadsheet_id": "Spreadsheet ID is required for Google Sheets modules",
            "invalid_openai_model": "Invalid OpenAI model specified",
            "missing_credentials": "Authentication credentials not configured",
            "invalid_url": "Invalid or malformed URL",
            "type_mismatch": "Data type mismatch between modules"
        }
    
    def analyze_workflow(self, workflow_json: Dict[str, Any], platform: WorkflowPlatform) -> List[WorkflowError]:
        """Analyze workflow for potential errors"""
        errors = []
        
        if platform == WorkflowPlatform.MAKE:
            errors.extend(self._analyze_make_workflow(workflow_json))
        else:
            errors.extend(self._analyze_n8n_workflow(workflow_json))
        
        return errors
    
    def _analyze_make_workflow(self, make_json: Dict[str, Any]) -> List[WorkflowError]:
        """Analyze Make.com workflow for errors"""
        errors = []
        flow = make_json.get("flow", [])
        
        for module in flow:
            module_id = str(module.get("id", "unknown"))
            module_name = module.get("module", "")
            parameters = module.get("parameters", {})
            
            # Check for missing spreadsheet ID
            if "google-sheets" in module_name:
                if not parameters.get("spreadsheetId"):
                    errors.append(WorkflowError(
                        error_type=ErrorType.PARAMETER_MISSING,
                        module_id=module_id,
                        module_name=module_name,
                        description="Missing required spreadsheet ID",
                        suggested_fix="Add spreadsheet ID: {{connection.drive.spreadsheetId}}",
                        severity="critical"
                    ))
            
            # Check OpenAI parameters
            elif "openai" in module_name:
                if not parameters.get("model"):
                    errors.append(WorkflowError(
                        error_type=ErrorType.PARAMETER_MISSING,
                        module_id=module_id,
                        module_name=module_name,
                        description="Missing required model parameter",
                        suggested_fix="Add model parameter: 'gpt-4' or 'gpt-3.5-turbo'",
                        severity="critical"
                    ))
            
            # Check HTTP modules
            elif "http" in module_name:
                mapper = module.get("mapper", {})
                if not mapper.get("url") and not parameters.get("url"):
                    errors.append(WorkflowError(
                        error_type=ErrorType.PARAMETER_MISSING,
                        module_id=module_id,
                        module_name=module_name,
                        description="Missing required URL parameter",
                        suggested_fix="Add URL in mapper or parameters",
                        severity="critical"
                    ))
        
        return errors
    
    def _analyze_n8n_workflow(self, n8n_json: Dict[str, Any]) -> List[WorkflowError]:
        """Analyze n8n workflow for errors"""
        errors = []
        nodes = n8n_json.get("nodes", [])
        
        for node in nodes:
            node_name = node.get("name", "unknown")
            node_type = node.get("type", "")
            parameters = node.get("parameters", {})
            
            # Check Google Sheets nodes
            if "googleSheets" in node_type:
                if not parameters.get("sheetId"):
                    errors.append(WorkflowError(
                        error_type=ErrorType.PARAMETER_MISSING,
                        module_id=node_name,
                        module_name=node_type,
                        description="Missing required sheet ID",
                        suggested_fix="Add sheetId parameter with spreadsheet ID",
                        severity="critical"
                    ))
            
            # Check OpenAI nodes
            elif "openAi" in node_type:
                if not parameters.get("model"):
                    errors.append(WorkflowError(
                        error_type=ErrorType.PARAMETER_MISSING,
                        module_id=node_name,
                        module_name=node_type,
                        description="Missing required model parameter",
                        suggested_fix="Add model parameter: 'gpt-4' or 'gpt-3.5-turbo'",
                        severity="critical"
                    ))
            
            # Check HTTP nodes
            elif "httpRequest" in node_type:
                if not parameters.get("url"):
                    errors.append(WorkflowError(
                        error_type=ErrorType.PARAMETER_MISSING,
                        module_id=node_name,
                        module_name=node_type,
                        description="Missing required URL parameter",
                        suggested_fix="Add url parameter with target endpoint",
                        severity="critical"
                    ))
        
        return errors
    
    def generate_fix(self, workflow_json: Dict[str, Any], errors: List[WorkflowError], platform: WorkflowPlatform) -> Dict[str, Any]:
        """Generate a fixed version of the workflow"""
        fixed_workflow = workflow_json.copy()
        
        if platform == WorkflowPlatform.MAKE:
            fixed_workflow = self._fix_make_workflow(fixed_workflow, errors)
        else:
            fixed_workflow = self._fix_n8n_workflow(fixed_workflow, errors)
        
        return fixed_workflow
    
    def _fix_make_workflow(self, workflow: Dict[str, Any], errors: List[WorkflowError]) -> Dict[str, Any]:
        """Apply fixes to Make.com workflow"""
        flow = workflow.get("flow", [])
        
        for error in errors:
            for module in flow:
                if str(module.get("id")) == error.module_id:
                    # Fix missing parameters
                    if error.error_type == ErrorType.PARAMETER_MISSING:
                        if "spreadsheet" in error.description.lower():
                            module.setdefault("parameters", {})["spreadsheetId"] = "{{connection.drive.spreadsheetId}}"
                        elif "model" in error.description.lower():
                            module.setdefault("parameters", {})["model"] = "gpt-4"
                        elif "url" in error.description.lower():
                            module.setdefault("mapper", {})["url"] = "https://api.example.com"
        
        return workflow
    
    def _fix_n8n_workflow(self, workflow: Dict[str, Any], errors: List[WorkflowError]) -> Dict[str, Any]:
        """Apply fixes to n8n workflow"""
        nodes = workflow.get("nodes", [])
        
        for error in errors:
            for node in nodes:
                if node.get("name") == error.module_id:
                    # Fix missing parameters
                    if error.error_type == ErrorType.PARAMETER_MISSING:
                        if "sheet" in error.description.lower():
                            node.setdefault("parameters", {})["sheetId"] = "your-spreadsheet-id"
                        elif "model" in error.description.lower():
                            node.setdefault("parameters", {})["model"] = "gpt-4"
                        elif "url" in error.description.lower():
                            node.setdefault("parameters", {})["url"] = "https://api.example.com"
        
        return workflow

class WorkflowTroubleshooter:
    """Handles troubleshooting conversations with users"""
    
    def __init__(self):
        self.debugger = WorkflowDebugger()
        self.conversation_state = {}
    
    def ask_diagnostic_questions(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Ask smart questions to diagnose workflow issues"""
        
        # Initialize conversation state
        if session_id not in self.conversation_state:
            self.conversation_state[session_id] = {
                "platform": None,
                "error_message": None,
                "failing_module": None,
                "workflow_json": None,
                "step": "initial"
            }
        
        state = self.conversation_state[session_id]
        
        # Determine next question based on what we know
        if state["step"] == "initial":
            if "make" in user_input.lower() or "make.com" in user_input.lower():
                state["platform"] = "make"
                state["step"] = "get_error"
                return {
                    "question": "What error message are you seeing? Please copy and paste the exact error from Make.com.",
                    "options": ["Connection error", "Module error", "Data error", "Authentication error"]
                }
            elif "n8n" in user_input.lower():
                state["platform"] = "n8n"
                state["step"] = "get_error"
                return {
                    "question": "What error message are you seeing? Please copy and paste the exact error from n8n.",
                    "options": ["Node execution failed", "Connection error", "Credential error", "Workflow error"]
                }
            else:
                return {
                    "question": "Which platform are you using?",
                    "options": ["Make.com", "n8n"]
                }
        
        elif state["step"] == "get_error":
            state["error_message"] = user_input
            state["step"] = "get_module"
            return {
                "question": f"Which module/node is failing? You can paste your workflow JSON here, or tell me the specific module name.",
                "options": ["Google Sheets", "OpenAI", "HTTP Request", "WordPress", "Other"]
            }
        
        elif state["step"] == "get_module":
            # Try to parse workflow JSON
            try:
                workflow_json = json.loads(user_input)
                state["workflow_json"] = workflow_json
                state["step"] = "analyze"
                return self._analyze_and_suggest_fix(state)
            except json.JSONDecodeError:
                state["failing_module"] = user_input
                state["step"] = "get_input"
                return {
                    "question": "What input data triggered this error? Please share the specific values that caused the failure.",
                    "options": ["Empty data", "Wrong format", "Missing field", "Invalid URL"]
                }
        
        elif state["step"] == "get_input":
            state["input_data"] = user_input
            state["step"] = "analyze"
            return self._analyze_and_suggest_fix(state)
        
        return {"question": "I need more information to help you.", "options": []}
    
    def _analyze_and_suggest_fix(self, state: Dict) -> Dict[str, Any]:
        """Analyze the issue and provide a fix"""
        platform = WorkflowPlatform.MAKE if state["platform"] == "make" else WorkflowPlatform.N8N
        
        if state.get("workflow_json"):
            # Analyze the actual workflow
            errors = self.debugger.analyze_workflow(state["workflow_json"], platform)
            
            if errors:
                # Generate fixed workflow
                fixed_workflow = self.debugger.generate_fix(state["workflow_json"], errors, platform)
                
                error_explanations = []
                for error in errors:
                    error_explanations.append(f"• {error.description} - {error.suggested_fix}")
                
                return {
                    "analysis": f"Found {len(errors)} issues in your workflow:",
                    "errors": error_explanations,
                    "fixed_workflow": json.dumps(fixed_workflow, indent=2),
                    "has_fix": True
                }
            else:
                return {
                    "analysis": "Your workflow structure looks correct. The issue might be:",
                    "suggestions": [
                        "Check your API credentials and permissions",
                        "Verify input data format matches expected schema",
                        "Test with simpler data first",
                        "Check rate limits on external APIs"
                    ],
                    "has_fix": False
                }
        else:
            # Provide general troubleshooting based on description
            common_solutions = {
                "google sheets": [
                    "Ensure spreadsheet is shared with the service account",
                    "Check that the spreadsheet ID is correct",
                    "Verify the worksheet name/range is valid"
                ],
                "openai": [
                    "Check your OpenAI API key is valid and has credits",
                    "Verify the model name (use 'gpt-4' or 'gpt-3.5-turbo')",
                    "Check if input text exceeds token limits"
                ],
                "http": [
                    "Verify the URL is accessible and correct",
                    "Check authentication headers and API keys",
                    "Ensure request format matches API requirements"
                ]
            }
            
            module_lower = state.get("failing_module", "").lower()
            suggestions = []
            
            for key, solutions in common_solutions.items():
                if key in module_lower:
                    suggestions.extend(solutions)
            
            if not suggestions:
                suggestions = [
                    "Check module configuration and required parameters",
                    "Verify authentication and permissions",
                    "Test with simpler input data"
                ]
            
            return {
                "analysis": f"Based on your description, here are the most likely solutions:",
                "suggestions": suggestions,
                "has_fix": False
            }