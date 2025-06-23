# Real Make.com and n8n Module/Node Mappings

## MAKE.COM REAL MODULES
MAKE_MODULES = {
    # Google Services
    "google_sheets": {
        "watch_rows": "google-sheets:WatchRows",
        "search_rows": "google-sheets:SearchRows", 
        "add_row": "google-sheets:AddRow",
        "update_row": "google-sheets:UpdateRow",
        "get_range": "google-sheets:GetRange",
        "clear_range": "google-sheets:ClearRange"
    },
    "google_drive": {
        "watch_files": "google-drive:WatchFiles",
        "upload_file": "google-drive:UploadFile",
        "download_file": "google-drive:DownloadFile"
    },
    
    # OpenAI
    "openai": {
        "chat_completion": "openai:CreateChatCompletion",
        "completion": "openai:CreateCompletion", 
        "create_image": "openai:CreateImage",
        "create_transcription": "openai:CreateTranscription"
    },
    
    # HTTP & Webhooks
    "http": {
        "make_request": "http:ActionSendData",
        "oauth_request": "http:ActionSendDataOAuth2"
    },
    "webhook": {
        "custom_webhook": "webhook:CustomWebHook"
    },
    
    # WordPress
    "wordpress": {
        "create_post": "wordpress:CreatePost",
        "update_post": "wordpress:UpdatePost",
        "get_post": "wordpress:GetPost"
    },
    
    # Social Media
    "instagram": {
        "create_media": "instagram:CreateMedia",
        "publish_media": "instagram:PublishMedia"
    },
    "facebook": {
        "create_post": "facebook:CreatePost",
        "create_photo": "facebook:CreatePhoto"
    },
    "twitter": {
        "create_tweet": "twitter:CreateTweet"
    },
    "youtube": {
        "upload_video": "youtube:UploadVideo"
    },
    "tiktok": {
        "upload_video": "tiktok:UploadVideo"
    },
    
    # Tools
    "tools": {
        "sleep": "builtin:Sleep",
        "set_variable": "builtin:SetVariable", 
        "text_aggregator": "builtin:TextAggregator",
        "array_aggregator": "builtin:ArrayAggregator"
    },
    
    # Email
    "email": {
        "send_email": "email:ActionSendEmail"
    },
    "gmail": {
        "send_email": "gmail:ActionSendEmail",
        "watch_emails": "gmail:TriggerWatchEmails"
    },
    
    # CRM
    "hubspot": {
        "create_contact": "hubspot:CreateContact",
        "update_contact": "hubspot:UpdateContact",
        "search_contacts": "hubspot:SearchContacts"
    },
    
    # E-commerce
    "shopify": {
        "watch_orders": "shopify:TriggerWatchOrders",
        "create_product": "shopify:CreateProduct"
    },
    
    # File Processing
    "json": {
        "parse_json": "json:ParseJSON",
        "create_json": "json:CreateJSON"
    },
    "csv": {
        "parse_csv": "csv:ParseCSV"
    }
}

## N8N REAL NODES  
N8N_NODES = {
    # Google Services
    "google_sheets": {
        "trigger": "n8n-nodes-base.googleSheetsTrigger",
        "sheets": "n8n-nodes-base.googleSheets"
    },
    "google_drive": {
        "trigger": "n8n-nodes-base.googleDriveTrigger", 
        "drive": "n8n-nodes-base.googleDrive"
    },
    
    # OpenAI
    "openai": {
        "openai": "n8n-nodes-base.openAi"
    },
    
    # HTTP & Webhooks
    "http": {
        "request": "n8n-nodes-base.httpRequest"
    },
    "webhook": {
        "webhook": "n8n-nodes-base.webhook"
    },
    
    # WordPress
    "wordpress": {
        "wordpress": "n8n-nodes-base.wordpress"
    },
    
    # Social Media  
    "instagram": {
        "instagram": "n8n-nodes-base.instagram"
    },
    "facebook": {
        "facebook": "n8n-nodes-base.facebookGraphApi"
    },
    "twitter": {
        "twitter": "n8n-nodes-base.twitter"
    },
    "youtube": {
        "youtube": "n8n-nodes-base.youTube"
    },
    
    # Core Tools
    "tools": {
        "start": "n8n-nodes-base.start",
        "set": "n8n-nodes-base.set",
        "code": "n8n-nodes-base.code",
        "wait": "n8n-nodes-base.wait",
        "if": "n8n-nodes-base.if",
        "merge": "n8n-nodes-base.merge"
    },
    
    # Email
    "email": {
        "send": "n8n-nodes-base.emailSend"
    },
    "gmail": {
        "gmail": "n8n-nodes-base.gmail"
    },
    
    # CRM
    "hubspot": {
        "hubspot": "n8n-nodes-base.hubspot"
    },
    
    # E-commerce
    "shopify": {
        "shopify": "n8n-nodes-base.shopify"
    }
}