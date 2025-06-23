from fastapi import APIRouter
import json
import logging

# Real Make.com and n8n module mappings
MAKE_MODULES = {
    "google_sheets": {
        "watch_rows": "google-sheets:watchRows",
        "get_values": "google-sheets:getValues", 
        "add_row": "google-sheets:addRow",
        "update_row": "google-sheets:updateRow"
    },
    "openai": {
        "chat_completion": "openai-gpt:createChatCompletion",
        "dalle_image": "openai-dall-e:createImage",
        "completion": "openai-gpt:createCompletion"
    },
    "wordpress": {
        "create_post": "wordpress:createPost",
        "update_post": "wordpress:updatePost",
        "get_post": "wordpress:getPost"
    },
    "instagram": {
        "create_post": "instagram:createMediaObject",
        "publish_post": "instagram:publishMedia"
    },
    "tiktok": {
        "upload_video": "tiktok:uploadVideo"
    },
    "youtube": {
        "upload_video": "youtube:uploadVideo",
        "create_playlist": "youtube:createPlaylist"
    },
    "webhook": {
        "receive": "webhook:webhook",
        "respond": "webhook:webhookResponse"
    },
    "tools": {
        "sleep": "tools:sleep",
        "set_variable": "tools:setVariable",
        "text_aggregator": "tools:textAggregator"
    },
    "http": {
        "make_request": "http:makeAnOAuth2APICall",
        "get": "http:makeAnAPICall"
    }
}

N8N_MODULES = {
    "google_sheets": {
        "watch_rows": "n8n-nodes-base.googleSheetsTrigger",
        "get_values": "n8n-nodes-base.googleSheets",
        "add_row": "n8n-nodes-base.googleSheets"
    },
    "openai": {
        "chat_completion": "n8n-nodes-base.openAi",
        "dalle_image": "n8n-nodes-base.openAi"
    },
    "wordpress": {
        "create_post": "n8n-nodes-base.wordpress",
        "update_post": "n8n-nodes-base.wordpress"
    },
    "webhook": {
        "receive": "n8n-nodes-base.webhook"
    },
    "http": {
        "make_request": "n8n-nodes-base.httpRequest"
    }
}

def generate_make_json(modules_data):
    """Generate accurate Make.com JSON structure"""
    flow = []
    
    for i, module in enumerate(modules_data, 1):
        module_config = {
            "id": i,
            "module": module["module"],
            "version": module.get("version", 1),
            "parameters": module.get("parameters", {}),
            "mapper": module.get("mapper", {}),
            "metadata": {
                "designer": {
                    "x": (i-1) * 300,
                    "y": 0
                }
            }
        }
        
        if "filter" in module:
            module_config["filter"] = module["filter"]
            
        flow.append(module_config)
    
    return {
        "name": modules_data[0].get("scenario_name", "Generated Automation"),
        "flow": flow,
        "metadata": {
            "instant": False,
            "version": 1,
            "scenario": {
                "roundtrips": 1,
                "maxErrors": 3,
                "autoCommit": True,
                "sequential": False,
                "confidential": False,
                "dataloss": False,
                "dlq": False,
                "freshVariables": False
            },
            "designer": {
                "orphans": []
            },
            "zone": "eu1.make.com"
        }
    }

def generate_n8n_json(nodes_data):
    """Generate accurate n8n JSON structure"""
    nodes = []
    connections = {}
    
    for i, node in enumerate(nodes_data):
        node_config = {
            "parameters": node.get("parameters", {}),
            "name": node.get("name", f"Node {i+1}"),
            "type": node["type"],
            "typeVersion": node.get("typeVersion", 1),
            "position": [
                node.get("position", [240 + i * 220, 300])[0],
                node.get("position", [240 + i * 220, 300])[1]
            ]
        }
        
        if "credentials" in node:
            node_config["credentials"] = node["credentials"]
            
        nodes.append(node_config)
        
        # Set up connections
        if i < len(nodes_data) - 1:  # Not the last node
            next_node_name = nodes_data[i + 1].get("name", f"Node {i+2}")
            connections[node.get("name", f"Node {i+1}")] = {
                "main": [[next_node_name]]
            }
    
    return {
        "name": nodes_data[0].get("workflow_name", "Generated Automation"),
        "nodes": nodes,
        "connections": connections,
        "active": False,
        "settings": {},
        "versionId": "1"
    }