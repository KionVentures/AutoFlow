from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt
import openai
import anthropic
import stripe
import json
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize external services
openai.api_key = os.environ['OPENAI_API_KEY']
anthropic_client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
stripe.api_key = os.environ['STRIPE_SECRET_KEY']

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT configuration
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Create the main app
app = FastAPI(title="AutoFlow AI", version="2.0.0")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Enums
class PlatformType(str, Enum):
    MAKE = "Make.com"
    N8N = "n8n"

class AIModel(str, Enum):
    GPT4 = "gpt-4"
    CLAUDE = "claude-3-5-sonnet-20241022"

class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    CREATOR = "creator"

# Enhanced Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    automations_used: int = 0
    automations_limit: int = 1
    stripe_customer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class AutomationRequest(BaseModel):
    task_description: str
    platform: PlatformType = PlatformType.MAKE
    ai_model: AIModel = AIModel.GPT4
    user_email: EmailStr  # Made required for lead capture

class AutomationTemplate(BaseModel):
    id: str
    name: str
    category: str
    description: str
    automation_summary: str
    required_tools: List[str]
    workflow_steps: List[str]
    make_json: str
    n8n_json: str
    setup_instructions: str
    bonus_content: Optional[str] = None
    tags: List[str] = []

class AutomationResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    task_description: str
    platform: PlatformType
    ai_model: AIModel = AIModel.GPT4
    automation_summary: str
    required_tools: List[str]
    workflow_steps: List[str]
    automation_json: str
    setup_instructions: str
    bonus_content: Optional[str] = None
    is_template: bool = False
    template_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StripeCheckoutRequest(BaseModel):
    tier: SubscriptionTier
    user_email: EmailStr

class BlueprintConversionRequest(BaseModel):
    blueprint_json: str
    source_platform: PlatformType
    target_platform: PlatformType
    ai_model: AIModel = AIModel.GPT4

class BlueprintConversionResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    source_platform: PlatformType
    target_platform: PlatformType
    ai_model: AIModel
    original_json: str
    converted_json: str
    conversion_notes: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pre-built Automation Templates
AUTOMATION_TEMPLATES = {
    "Instagram Video Poster": {
        "id": "template_001",
        "name": "Instagram Video Poster",
        "category": "Social Media",
        "description": "Automatically post videos from Google Drive to Instagram when new files are added",
        "automation_summary": "Automatically posts new videos from Google Drive to Instagram with custom captions and hashtags",
        "required_tools": [
            "Google Drive - Monitor for new video files",
            "Instagram Basic Display API - Post videos to feed",
            "OpenAI GPT-4 - Generate engaging captions",
            "Image/Video Processing - Optimize format for Instagram"
        ],
        "workflow_steps": [
            "1. Monitor Google Drive folder for new video files (.mp4, .mov)",
            "2. When new video detected, download and validate format",
            "3. Generate engaging caption using AI based on filename/metadata",
            "4. Add relevant hashtags for maximum reach",
            "5. Upload video to Instagram with generated caption",
            "6. Send confirmation notification via email/Slack"
        ],
        "make_json": """{
  "name": "Instagram Video Poster",
  "flow": [
    {
      "id": 1,
      "module": "google-drive:watchFiles",
      "version": 1,
      "parameters": {
        "drive": "{{connection.drive}}",
        "folderId": "your-folder-id",
        "fileTypes": ["video/mp4", "video/quicktime"]
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 0, "y": 0}
      }
    },
    {
      "id": 2,
      "module": "openai-gpt:createCompletion",
      "version": 1,
      "parameters": {
        "model": "gpt-4",
        "prompt": "Create an engaging Instagram caption for a video titled: {{1.name}}. Include relevant hashtags.",
        "max_tokens": 150
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 300, "y": 0}
      }
    },
    {
      "id": 3,
      "module": "instagram-basic-display:uploadVideo",
      "version": 1,
      "parameters": {
        "videoUrl": "{{1.webContentLink}}",
        "caption": "{{2.choices[0].text}}"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 600, "y": 0}
      }
    }
  ],
  "metadata": {
    "version": 1,
    "scenario": "Instagram Video Poster",
    "isExecutionDisabled": false
  }
}""",
        "n8n_json": """{
  "name": "Instagram Video Poster",
  "nodes": [
    {
      "parameters": {
        "folderId": "your-folder-id",
        "fileTypes": "video"
      },
      "name": "Google Drive Trigger",
      "type": "n8n-nodes-base.googleDriveTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "model": "gpt-4",
        "prompt": "Create an engaging Instagram caption for: {{ $json.name }}. Include hashtags.",
        "maxTokens": 150
      },
      "name": "Generate Caption",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "videoUrl": "{{ $node['Google Drive Trigger'].json.webContentLink }}",
        "caption": "{{ $node['Generate Caption'].json.choices[0].text }}"
      },
      "name": "Post to Instagram",
      "type": "n8n-nodes-base.instagram",
      "typeVersion": 1,
      "position": [680, 300]
    }
  ],
  "connections": {
    "Google Drive Trigger": {
      "main": [["Generate Caption"]]
    },
    "Generate Caption": {
      "main": [["Post to Instagram"]]
    }
  }
}""",
        "setup_instructions": """**Step-by-Step Setup Guide:**

**For Make.com:**
1. Go to Make.com and click "Create a new scenario"
2. Click the "..." menu and select "Import Blueprint"
3. Copy and paste the JSON template above
4. Connect your Google Drive account when prompted
5. Set your target Google Drive folder ID
6. Connect your Instagram account using Instagram Basic Display API
7. Connect OpenAI for caption generation
8. Test the scenario with a sample video
9. Turn on the scenario to run automatically

**For n8n:**
1. Open your n8n instance and create a new workflow
2. Click "Import from JSON" and paste the template
3. Configure Google Drive credentials and folder ID
4. Set up Instagram API credentials
5. Add your OpenAI API key for caption generation
6. Test the workflow with a sample video file
7. Activate the workflow

**Required App Connections:**
- Google Drive (for file monitoring)
- Instagram Basic Display API (for posting)
- OpenAI API (for caption generation)

**Testing:**
1. Add a test video to your monitored Google Drive folder
2. Check that the automation triggers
3. Verify the caption is generated properly
4. Confirm the video posts to Instagram successfully""",
        "bonus_content": """**📱 Instagram Optimization Tips:**

**Video Format Guidelines:**
- Aspect ratio: 1:1 (square) or 4:5 (portrait) works best
- Resolution: 1080x1080 (square) or 1080x1350 (portrait)
- Length: 15-60 seconds for optimal engagement
- File size: Under 100MB

**Caption Best Practices:**
- Start with a hook in the first line
- Use 5-10 relevant hashtags
- Include a call-to-action
- Tag relevant accounts when appropriate

**Hashtag Research:**
- Mix popular (#entrepreneurship) and niche (#automationhacks) hashtags
- Use location-based hashtags for local reach
- Create a branded hashtag for your content

**Content Ideas:**
- Behind-the-scenes footage
- Tutorial snippets
- Product demonstrations
- Customer testimonials""",
        "tags": ["social media", "instagram", "video", "content creation", "google drive"]
    },
    
    "Lead Capture Flow": {
        "id": "template_002",
        "name": "Lead Capture Flow",
        "category": "Marketing",
        "description": "Capture leads from website forms and automatically add them to CRM with follow-up sequence",
        "automation_summary": "Captures website form submissions, adds contacts to CRM, sends welcome email, and triggers follow-up sequence",
        "required_tools": [
            "Webhook - Receive form submissions from website",
            "HubSpot/Salesforce CRM - Store lead information",
            "Email Service (Mailchimp/SendGrid) - Send welcome emails",
            "Slack - Notify sales team of new leads"
        ],
        "workflow_steps": [
            "1. Receive form submission via webhook from website",
            "2. Validate and clean the lead data (email format, required fields)",
            "3. Check if lead already exists in CRM to avoid duplicates",
            "4. Add new lead to CRM with proper tags and source tracking",
            "5. Send personalized welcome email with lead magnet",
            "6. Notify sales team via Slack with lead details",
            "7. Add lead to automated email nurture sequence"
        ],
        "make_json": """{
  "name": "Lead Capture Flow",
  "flow": [
    {
      "id": 1,
      "module": "webhook:webhook",
      "version": 1,
      "parameters": {
        "hookUrl": "auto-generated-webhook-url"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 0, "y": 0}
      }
    },
    {
      "id": 2,
      "module": "tools:emailValidator",
      "version": 1,
      "parameters": {
        "email": "{{1.email}}"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 300, "y": 0}
      }
    },
    {
      "id": 3,
      "module": "hubspot:searchContacts",
      "version": 1,
      "parameters": {
        "email": "{{1.email}}"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 600, "y": 0}
      }
    },
    {
      "id": 4,
      "module": "hubspot:createContact",
      "version": 1,
      "parameters": {
        "firstName": "{{1.firstName}}",
        "lastName": "{{1.lastName}}",
        "email": "{{1.email}}",
        "source": "Website Form",
        "leadStatus": "New"
      },
      "filter": {
        "name": "Contact doesn't exist",
        "conditions": [
          {
            "a": "{{3.total}}",
            "b": 0,
            "o": "equal"
          }
        ]
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 900, "y": 0}
      }
    },
    {
      "id": 5,
      "module": "mailchimp:addMember",
      "version": 1,
      "parameters": {
        "listId": "your-list-id",
        "emailAddress": "{{1.email}}",
        "status": "subscribed",
        "mergeFields": {
          "FNAME": "{{1.firstName}}",
          "LNAME": "{{1.lastName}}"
        }
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 1200, "y": 0}
      }
    },
    {
      "id": 6,
      "module": "slack:sendMessage",
      "version": 1,
      "parameters": {
        "channel": "#sales",
        "text": "🎯 New lead captured!\\nName: {{1.firstName}} {{1.lastName}}\\nEmail: {{1.email}}\\nSource: Website Form"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 1500, "y": 0}
      }
    }
  ],
  "metadata": {
    "version": 1,
    "scenario": "Lead Capture Flow",
    "isExecutionDisabled": false
  }
}""",
        "n8n_json": """{
  "name": "Lead Capture Flow",
  "nodes": [
    {
      "parameters": {},
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300],
      "webhookId": "auto-generated"
    },
    {
      "parameters": {
        "email": "={{ $json.email }}"
      },
      "name": "Validate Email",
      "type": "n8n-nodes-base.emailValidator",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "filterType": "manual",
        "query": "email={{ $json.email }}"
      },
      "name": "Search Contact",
      "type": "n8n-nodes-base.hubspot",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "properties": {
          "firstName": "={{ $node.Webhook.json.firstName }}",
          "lastName": "={{ $node.Webhook.json.lastName }}",
          "email": "={{ $node.Webhook.json.email }}"
        }
      },
      "name": "Create Contact",
      "type": "n8n-nodes-base.hubspot",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "listId": "your-list-id",
        "email": "={{ $node.Webhook.json.email }}",
        "subscribeStatus": "subscribed",
        "mergeFields": {
          "FNAME": "={{ $node.Webhook.json.firstName }}",
          "LNAME": "={{ $node.Webhook.json.lastName }}"
        }
      },
      "name": "Add to Email List",
      "type": "n8n-nodes-base.mailchimp",
      "typeVersion": 1,
      "position": [1120, 300]
    },
    {
      "parameters": {
        "channel": "#sales",
        "text": "🎯 New lead: {{ $node.Webhook.json.firstName }} {{ $node.Webhook.json.lastName }} ({{ $node.Webhook.json.email }})"
      },
      "name": "Notify Sales Team",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 1,
      "position": [1340, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [["Validate Email"]]
    },
    "Validate Email": {
      "main": [["Search Contact"]]
    },
    "Search Contact": {
      "main": [["Create Contact"]]
    },
    "Create Contact": {
      "main": [["Add to Email List"]]
    },
    "Add to Email List": {
      "main": [["Notify Sales Team"]]
    }
  }
}""",
        "setup_instructions": """**Step-by-Step Setup Guide:**

**For Make.com:**
1. Create new scenario in Make.com
2. Import the JSON template provided above
3. Configure the webhook URL and copy it to your website form
4. Connect your CRM (HubSpot, Salesforce, or Pipedrive)
5. Set up email service integration (Mailchimp, SendGrid, etc.)
6. Connect Slack for team notifications
7. Test with a sample form submission
8. Activate the scenario

**For n8n:**
1. Import workflow JSON into n8n
2. Configure webhook node and get the URL
3. Add webhook URL to your website contact form
4. Set up CRM credentials and list IDs
5. Configure email service connection
6. Add Slack workspace and channel details
7. Test the complete flow
8. Activate the workflow

**Website Integration:**
Add this code to your contact form's action:
```html
<form action="YOUR_WEBHOOK_URL" method="POST">
  <input name="firstName" placeholder="First Name" required>
  <input name="lastName" placeholder="Last Name" required>
  <input name="email" type="email" placeholder="Email" required>
  <input name="company" placeholder="Company">
  <button type="submit">Submit</button>
</form>
```

**Testing:**
1. Submit a test form on your website
2. Check CRM for new contact creation
3. Verify welcome email was sent
4. Confirm Slack notification appeared""",
        "bonus_content": """**🎯 Lead Scoring Enhancement:**

**Advanced Lead Qualification:**
Add these fields to score leads automatically:
- Company size (employees)
- Annual revenue 
- Industry/vertical
- Budget range
- Timeline to purchase

**Email Template Examples:**

**Welcome Email:**
Subject: "Welcome to [Company]! Here's your free guide"
"Hi {{firstName}}, thanks for downloading our guide. Here are 3 ways we can help you grow your business..."

**Follow-up Sequence:**
- Day 1: Welcome + Lead Magnet Delivery
- Day 3: Case Study Email  
- Day 7: Product Demo Invitation
- Day 14: Special Offer/Discount

**CRM Tag Strategy:**
- Source tags: "Website", "Social Media", "Paid Ads"
- Interest tags: "Pricing Page", "Demo Request", "Case Studies"
- Engagement tags: "High", "Medium", "Low"

**Conversion Optimization:**
- A/B test form length (3 vs 5 fields)
- Test different lead magnets
- Optimize thank you page with social proof
- Add exit-intent popup for cart abandoners""",
        "tags": ["marketing", "lead generation", "crm", "email marketing", "sales"]
    },

    "Email Follow-Up Sequence": {
        "id": "template_003",
        "name": "Email Follow-Up Sequence",
        "category": "Marketing",
        "description": "Automated email nurture sequence for new subscribers with behavioral triggers",
        "automation_summary": "Sends a series of timed, personalized emails to nurture new subscribers based on their actions and engagement",
        "required_tools": [
            "Email Service Provider (Mailchimp, ConvertKit, SendGrid) - Send emails",
            "CRM/Database - Track subscriber behavior",
            "Analytics Tool - Monitor email performance",
            "Conditional Logic - Trigger based on actions"
        ],
        "workflow_steps": [
            "1. New subscriber added to email list via signup form",
            "2. Send immediate welcome email with lead magnet",
            "3. Wait 2 days, then send educational content email",
            "4. Track email opens and clicks for engagement scoring",
            "5. Send social proof email after 5 days if engaged",
            "6. Offer product demo/consultation after 1 week",
            "7. Send special offer email after 2 weeks if no conversion"
        ],
        "make_json": """{
  "name": "Email Follow-Up Sequence",
  "flow": [
    {
      "id": 1,
      "module": "mailchimp:watchNewMembers",
      "version": 1,
      "parameters": {
        "listId": "your-list-id"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 0, "y": 0}
      }
    },
    {
      "id": 2,
      "module": "mailchimp:sendEmail",
      "version": 1,
      "parameters": {
        "to": "{{1.emailAddress}}",
        "subject": "Welcome! Here's your free guide",
        "htmlContent": "<h1>Welcome {{1.mergeFields.FNAME}}!</h1><p>Thanks for joining us. Here's your promised guide...</p>"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 300, "y": 0}
      }
    },
    {
      "id": 3,
      "module": "tools:sleep",
      "version": 1,
      "parameters": {
        "delay": 172800
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 600, "y": 0}
      }
    },
    {
      "id": 4,
      "module": "mailchimp:sendEmail",
      "version": 1,
      "parameters": {
        "to": "{{1.emailAddress}}",
        "subject": "The #1 mistake businesses make with automation",
        "htmlContent": "<h1>Hi {{1.mergeFields.FNAME}},</h1><p>Yesterday I helped a client avoid this costly automation mistake...</p>"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 900, "y": 0}
      }
    },
    {
      "id": 5,
      "module": "tools:sleep",
      "version": 1,
      "parameters": {
        "delay": 259200
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 1200, "y": 0}
      }
    },
    {
      "id": 6,
      "module": "mailchimp:sendEmail",
      "version": 1,
      "parameters": {
        "to": "{{1.emailAddress}}",
        "subject": "How [Customer] saved 20 hours per week",
        "htmlContent": "<h1>Real Results:</h1><p>See how {{1.mergeFields.FNAME}} our client transformed their business...</p>"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 1500, "y": 0}
      }
    }
  ],
  "metadata": {
    "version": 1,
    "scenario": "Email Follow-Up Sequence",
    "isExecutionDisabled": false
  }
}""",
        "n8n_json": """{
  "name": "Email Follow-Up Sequence",
  "nodes": [
    {
      "parameters": {
        "listId": "your-list-id"
      },
      "name": "New Subscriber Trigger",
      "type": "n8n-nodes-base.mailchimpTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "to": "={{ $json.email_address }}",
        "subject": "Welcome! Here's your free guide",
        "emailFormat": "html",
        "html": "<h1>Welcome {{ $json.merge_fields.FNAME }}!</h1><p>Thanks for joining us...</p>"
      },
      "name": "Send Welcome Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "amount": 2,
        "unit": "days"
      },
      "name": "Wait 2 Days",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "to": "={{ $node['New Subscriber Trigger'].json.email_address }}",
        "subject": "The #1 automation mistake",
        "emailFormat": "html",
        "html": "<h1>Hi {{ $node['New Subscriber Trigger'].json.merge_fields.FNAME }},</h1><p>Educational content here...</p>"
      },
      "name": "Send Educational Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "amount": 3,
        "unit": "days"
      },
      "name": "Wait 3 More Days",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [1120, 300]
    },
    {
      "parameters": {
        "to": "={{ $node['New Subscriber Trigger'].json.email_address }}",
        "subject": "Case study: 20 hours saved per week",
        "emailFormat": "html",
        "html": "<h1>Real Results</h1><p>Social proof content here...</p>"
      },
      "name": "Send Case Study",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [1340, 300]
    }
  ],
  "connections": {
    "New Subscriber Trigger": {
      "main": [["Send Welcome Email"]]
    },
    "Send Welcome Email": {
      "main": [["Wait 2 Days"]]
    },
    "Wait 2 Days": {
      "main": [["Send Educational Email"]]
    },
    "Send Educational Email": {
      "main": [["Wait 3 More Days"]]
    },
    "Wait 3 More Days": {
      "main": [["Send Case Study"]]
    }
  }
}""",
        "setup_instructions": """**Step-by-Step Setup Guide:**

**For Make.com:**
1. Create new scenario in Make.com
2. Import the JSON template above
3. Connect your email service provider (Mailchimp recommended)
4. Set your email list ID in the trigger module
5. Customize email content with your branding
6. Set up proper delays between emails (2 days, 3 days, etc.)
7. Test the sequence with a test email address
8. Activate the scenario

**For n8n:**
1. Import the workflow JSON into n8n
2. Configure your email service credentials
3. Set the correct list ID for new subscriber trigger
4. Customize email templates with your content
5. Adjust timing delays as needed
6. Test the complete sequence
7. Activate the workflow

**Email Content Customization:**
- Replace placeholder content with your actual copy
- Add your company branding and logo
- Include unsubscribe links (required by law)
- Personalize with subscriber's name and preferences

**Best Practices:**
- Keep emails focused on one main message
- Use clear, compelling subject lines
- Include clear call-to-action buttons
- Monitor open rates and adjust timing if needed""",
        "bonus_content": """**📧 Email Sequence Optimization:**

**Email Performance Benchmarks:**
- Welcome emails: 50-86% open rates
- Educational content: 20-25% open rates  
- Case studies: 15-20% open rates
- Sales emails: 10-15% open rates

**Subject Line Templates:**
- Welcome: "Welcome to [Company]! Here's what's next..."
- Educational: "The [Number] [Thing] that [Outcome]"
- Social Proof: "How [Customer] achieved [Result] in [Timeframe]"
- Sales: "[Benefit] inside + [Urgency/Scarcity]"

**Content Templates:**

**Welcome Email Structure:**
1. Thank you for subscribing
2. Set expectations (what they'll receive)
3. Deliver promised lead magnet
4. Introduce yourself/company briefly
5. Clear next steps

**Educational Email Structure:**
1. Hook with problem or question
2. Tell a relevant story or example
3. Provide actionable tip or insight
4. Soft CTA to relevant resource

**Advanced Segmentation:**
- Segment by lead source
- Behavioral triggers (clicked link, visited pricing)
- Engagement level (opens, clicks)
- Industry or company size
- Geographic location

**Testing Ideas:**
- A/B test send times (Tuesday 10 AM vs Thursday 2 PM)
- Test email length (short vs detailed)
- Test CTA button colors and text
- Test personal vs company sender name""",
        "tags": ["email marketing", "nurturing", "automation", "lead conversion", "drip campaign"]
    },

    "E-commerce Order Processing": {
        "id": "template_004",
        "name": "E-commerce Order Processing",
        "category": "E-commerce",
        "description": "Automatically process new orders, update inventory, send confirmations, and notify fulfillment team",
        "automation_summary": "Streamlines order processing from payment to fulfillment with automatic inventory updates and customer notifications",
        "required_tools": [
            "E-commerce Platform (Shopify, WooCommerce) - Order source",
            "Inventory Management System - Stock tracking",
            "Email Service - Customer notifications",
            "Accounting Software (QuickBooks) - Financial records",
            "Fulfillment Service - Shipping notifications"
        ],
        "workflow_steps": [
            "1. New order received from e-commerce platform",
            "2. Validate payment status and order details",
            "3. Check inventory levels for ordered items",
            "4. Update inventory counts and flag low stock items",
            "5. Send order confirmation email to customer",
            "6. Create invoice in accounting software",
            "7. Notify fulfillment team with order details",
            "8. Generate shipping label and tracking number"
        ],
        "make_json": """{
  "name": "E-commerce Order Processing",
  "flow": [
    {
      "id": 1,
      "module": "shopify:watchOrders",
      "version": 1,
      "parameters": {
        "webhook": "orders/create"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 0, "y": 0}
      }
    },
    {
      "id": 2,
      "module": "shopify:getOrder",
      "version": 1,
      "parameters": {
        "orderId": "{{1.id}}"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 300, "y": 0}
      }
    },
    {
      "id": 3,
      "module": "airtable:updateRecord",
      "version": 1,
      "parameters": {
        "baseId": "your-inventory-base",
        "tableId": "Inventory",
        "recordId": "{{2.line_items[].variant_id}}",
        "fields": {
          "Stock_Count": "{{subtract(get(inventory.stock), 2.line_items[].quantity)}}"
        }
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 600, "y": 0}
      }
    },
    {
      "id": 4,
      "module": "email:sendEmail",
      "version": 1,
      "parameters": {
        "to": "{{2.email}}",
        "subject": "Order Confirmation #{{2.order_number}}",
        "html": "<h1>Thanks for your order!</h1><p>Hi {{2.shipping_address.first_name}}, your order #{{2.order_number}} has been confirmed...</p>"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 900, "y": 0}
      }
    },
    {
      "id": 5,
      "module": "quickbooks:createInvoice",
      "version": 1,
      "parameters": {
        "customerId": "{{2.customer.id}}",
        "lineItems": "{{2.line_items}}",
        "totalAmount": "{{2.total_price}}"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 1200, "y": 0}
      }
    },
    {
      "id": 6,
      "module": "slack:sendMessage",
      "version": 1,
      "parameters": {
        "channel": "#fulfillment",
        "text": "📦 New Order #{{2.order_number}}\\nCustomer: {{2.shipping_address.first_name}} {{2.shipping_address.last_name}}\\nItems: {{2.line_items[].name}}\\nTotal: ${{2.total_price}}"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 1500, "y": 0}
      }
    }
  ],
  "metadata": {
    "version": 1,
    "scenario": "E-commerce Order Processing",
    "isExecutionDisabled": false
  }
}""",
        "n8n_json": """{
  "name": "E-commerce Order Processing",
  "nodes": [
    {
      "parameters": {
        "topic": "orders/create"
      },
      "name": "Shopify Order Webhook",
      "type": "n8n-nodes-base.shopifyTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "orderId": "={{ $json.id }}"
      },
      "name": "Get Order Details",
      "type": "n8n-nodes-base.shopify",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "operation": "update",
        "base": "your-inventory-base",
        "table": "Inventory",
        "id": "={{ $json.line_items[0].variant_id }}",
        "fields": {
          "Stock_Count": "={{ $json.inventory_quantity - $json.line_items[0].quantity }}"
        }
      },
      "name": "Update Inventory",
      "type": "n8n-nodes-base.airtable",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "to": "={{ $node['Get Order Details'].json.email }}",
        "subject": "Order Confirmation #{{ $node['Get Order Details'].json.order_number }}",
        "emailFormat": "html",
        "html": "<h1>Order Confirmed!</h1><p>Thanks {{ $node['Get Order Details'].json.shipping_address.first_name }}...</p>"
      },
      "name": "Send Confirmation Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "resource": "invoice",
        "operation": "create",
        "customer": "={{ $node['Get Order Details'].json.customer.id }}",
        "items": "={{ $node['Get Order Details'].json.line_items }}"
      },
      "name": "Create Invoice",
      "type": "n8n-nodes-base.quickbooks",
      "typeVersion": 1,
      "position": [1120, 300]
    },
    {
      "parameters": {
        "channel": "#fulfillment",
        "text": "📦 New Order #{{ $node['Get Order Details'].json.order_number }}\\nTotal: ${{ $node['Get Order Details'].json.total_price }}"
      },
      "name": "Notify Fulfillment",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 1,
      "position": [1340, 300]
    }
  ],
  "connections": {
    "Shopify Order Webhook": {
      "main": [["Get Order Details"]]
    },
    "Get Order Details": {
      "main": [["Update Inventory"]]
    },
    "Update Inventory": {
      "main": [["Send Confirmation Email"]]
    },
    "Send Confirmation Email": {
      "main": [["Create Invoice"]]
    },
    "Create Invoice": {
      "main": [["Notify Fulfillment"]]
    }
  }
}""",
        "setup_instructions": """**Step-by-Step Setup Guide:**

**For Make.com:**
1. Create new scenario in Make.com
2. Import the JSON template above
3. Connect your Shopify store using API credentials
4. Set up inventory management system (Airtable recommended)
5. Configure email service for customer notifications
6. Connect accounting software (QuickBooks or Xero)
7. Set up Slack for team notifications
8. Test with a sample order
9. Activate the scenario

**For n8n:**
1. Import workflow JSON into n8n
2. Configure Shopify webhook and API credentials
3. Set up inventory database connection
4. Configure email service for confirmations
5. Connect accounting software integration
6. Set up team notification channels
7. Test the complete workflow
8. Activate the automation

**Shopify Setup:**
1. Go to Settings > Notifications in Shopify admin
2. Set up webhook for "Order created" events
3. Point webhook to your automation URL
4. Enable necessary API permissions for order access

**Inventory Management:**
- Create Airtable base with product variants and stock counts
- Include fields: SKU, Product Name, Stock Count, Reorder Level
- Set up low stock alerts when inventory drops below threshold

**Testing:**
1. Place a test order in your store
2. Verify inventory is updated correctly
3. Check customer receives confirmation email
4. Confirm invoice is created in accounting software
5. Validate team notification appears""",
        "bonus_content": """**🛒 E-commerce Optimization Tips:**

**Inventory Management Best Practices:**
- Set reorder points for each product (usually 10-20% of max stock)
- Track seasonal demand patterns
- Implement ABC analysis (A=high value, B=medium, C=low)
- Use safety stock for popular items

**Order Confirmation Email Template:**
```html
<h1>🎉 Order Confirmed!</h1>
<p>Hi {{customer_name}},</p>
<p>Thanks for your order #{{order_number}}. Here's what you ordered:</p>
<ul>{{#each items}}
  <li>{{name}} x {{quantity}} - ${{price}}</li>
{{/each}}</ul>
<p><strong>Total: ${{total}}</strong></p>
<p>We'll send you tracking info once your order ships!</p>
```

**Advanced Features to Add:**
- Automatic discount codes for next purchase
- Loyalty points calculation and update
- Abandoned cart recovery sequences
- Product review request emails (sent 7 days after delivery)
- Cross-sell/upsell recommendations

**Performance Metrics to Track:**
- Order processing time (goal: < 2 hours)
- Inventory accuracy (goal: 99%+)
- Customer satisfaction scores
- Return/refund rates
- Revenue per customer

**Integration Ideas:**
- SMS notifications for high-value customers
- Social media posting about new orders
- Supplier auto-reordering when stock is low
- Customer service ticket creation for issues""",
        "tags": ["e-commerce", "order processing", "inventory", "shopify", "fulfillment"]
    },

    "Social Media Scheduler": {
        "id": "template_005",
        "name": "Social Media Scheduler",
        "category": "Social Media",
        "description": "Schedule and post content across multiple social media platforms with optimal timing",
        "automation_summary": "Automatically schedules and posts content to Facebook, Twitter, LinkedIn, and Instagram at optimal times for maximum engagement",
        "required_tools": [
            "Google Sheets/Airtable - Content calendar storage",
            "Facebook Pages API - Post to Facebook",
            "Twitter API - Tweet scheduling",
            "LinkedIn API - Professional posts",
            "Instagram Basic Display API - Photo posts",
            "AI Content Generator - Create captions"
        ],
        "workflow_steps": [
            "1. Monitor content calendar for scheduled posts",
            "2. Retrieve post content, images, and target platforms",
            "3. Generate platform-specific captions and hashtags",
            "4. Optimize image format for each platform",
            "5. Post content to selected social media platforms",
            "6. Track posting success and engagement metrics",
            "7. Update content calendar with post performance data"
        ],
        "make_json": """{
  "name": "Social Media Scheduler",
  "flow": [
    {
      "id": 1,
      "module": "airtable:watchRecords",
      "version": 1,
      "parameters": {
        "baseId": "your-content-base",
        "tableId": "Content_Calendar",
        "filterFormula": "AND(IS_AFTER({Post_Date}, TODAY()), {Status} = 'Scheduled')"
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 0, "y": 0}
      }
    },
    {
      "id": 2,
      "module": "openai:createCompletion",
      "version": 1,
      "parameters": {
        "model": "gpt-4",
        "prompt": "Create platform-specific social media captions for: {{1.content}}. Make versions for Facebook, Twitter, LinkedIn, and Instagram.",
        "max_tokens": 300
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 300, "y": 0}
      }
    },
    {
      "id": 3,
      "module": "facebook:createPost",
      "version": 1,
      "parameters": {
        "pageId": "your-facebook-page-id",
        "message": "{{2.choices[0].text.facebook}}",
        "imageUrl": "{{1.image_url}}"
      },
      "filter": {
        "name": "Facebook selected",
        "conditions": [
          {
            "a": "{{1.platforms}}",
            "b": "Facebook",
            "o": "contains"
          }
        ]
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 600, "y": 0}
      }
    },
    {
      "id": 4,
      "module": "twitter:createTweet",
      "version": 1,
      "parameters": {
        "text": "{{2.choices[0].text.twitter}}",
        "mediaUrl": "{{1.image_url}}"
      },
      "filter": {
        "name": "Twitter selected",
        "conditions": [
          {
            "a": "{{1.platforms}}",
            "b": "Twitter",
            "o": "contains"
          }
        ]
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 600, "y": 200}
      }
    },
    {
      "id": 5,
      "module": "linkedin:shareUpdate",
      "version": 1,
      "parameters": {
        "text": "{{2.choices[0].text.linkedin}}",
        "imageUrl": "{{1.image_url}}"
      },
      "filter": {
        "name": "LinkedIn selected",
        "conditions": [
          {
            "a": "{{1.platforms}}",
            "b": "LinkedIn",
            "o": "contains"
          }
        ]
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 600, "y": 400}
      }
    },
    {
      "id": 6,
      "module": "airtable:updateRecord",
      "version": 1,
      "parameters": {
        "baseId": "your-content-base",
        "tableId": "Content_Calendar",
        "recordId": "{{1.id}}",
        "fields": {
          "Status": "Posted",
          "Posted_Date": "{{formatDate(now, 'YYYY-MM-DD HH:mm:ss')}}"
        }
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 900, "y": 200}
      }
    }
  ],
  "metadata": {
    "version": 1,
    "scenario": "Social Media Scheduler",
    "isExecutionDisabled": false
  }
}""",
        "n8n_json": """{
  "name": "Social Media Scheduler",
  "nodes": [
    {
      "parameters": {
        "base": "your-content-base",
        "table": "Content_Calendar",
        "filterByFormula": "AND(IS_AFTER({Post_Date}, TODAY()), {Status} = 'Scheduled')"
      },
      "name": "Check Content Calendar",
      "type": "n8n-nodes-base.airtable",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "model": "gpt-4",
        "prompt": "Create social media captions for: {{ $json.content }}. Format for Facebook, Twitter, LinkedIn, Instagram.",
        "maxTokens": 300
      },
      "name": "Generate Captions",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "pageId": "your-facebook-page-id",
        "postType": "photo",
        "message": "={{ $node['Generate Captions'].json.choices[0].text }}",
        "imageUrl": "={{ $node['Check Content Calendar'].json.image_url }}"
      },
      "name": "Post to Facebook",
      "type": "n8n-nodes-base.facebook",
      "typeVersion": 1,
      "position": [680, 200]
    },
    {
      "parameters": {
        "text": "={{ $node['Generate Captions'].json.choices[0].text }}",
        "mediaUrls": "={{ $node['Check Content Calendar'].json.image_url }}"
      },
      "name": "Post to Twitter",
      "type": "n8n-nodes-base.twitter",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "text": "={{ $node['Generate Captions'].json.choices[0].text }}",
        "imageUrl": "={{ $node['Check Content Calendar'].json.image_url }}"
      },
      "name": "Post to LinkedIn",
      "type": "n8n-nodes-base.linkedin",
      "typeVersion": 1,
      "position": [680, 400]
    },
    {
      "parameters": {
        "operation": "update",
        "base": "your-content-base",
        "table": "Content_Calendar",
        "id": "={{ $node['Check Content Calendar'].json.id }}",
        "fields": {
          "Status": "Posted",
          "Posted_Date": "={{ new Date().toISOString() }}"
        }
      },
      "name": "Update Calendar",
      "type": "n8n-nodes-base.airtable",
      "typeVersion": 1,
      "position": [900, 300]
    }
  ],
  "connections": {
    "Check Content Calendar": {
      "main": [["Generate Captions"]]
    },
    "Generate Captions": {
      "main": [["Post to Facebook"], ["Post to Twitter"], ["Post to LinkedIn"]]
    },
    "Post to Facebook": {
      "main": [["Update Calendar"]]
    },
    "Post to Twitter": {
      "main": [["Update Calendar"]]
    },
    "Post to LinkedIn": {
      "main": [["Update Calendar"]]
    }
  }
}""",
        "setup_instructions": """**Step-by-Step Setup Guide:**

**For Make.com:**
1. Create new scenario in Make.com
2. Import the JSON template above
3. Set up Airtable base for content calendar
4. Connect social media platform APIs:
   - Facebook Pages API
   - Twitter API v2
   - LinkedIn API
   - Instagram Basic Display API
5. Configure OpenAI for caption generation
6. Set schedule to run every hour
7. Test with sample content
8. Activate the scenario

**For n8n:**
1. Import workflow JSON into n8n
2. Create content calendar in Airtable with fields:
   - Content (text)
   - Post_Date (date/time)
   - Platforms (multi-select)
   - Status (single select)
   - Image_URL (URL)
3. Connect all social media accounts
4. Set up OpenAI API for caption generation
5. Schedule workflow to run hourly
6. Test the complete flow
7. Activate the workflow

**Content Calendar Setup:**
Create Airtable base with these fields:
- Content: Long text field for post content
- Post_Date: Date field with time
- Platforms: Multiple select (Facebook, Twitter, LinkedIn, Instagram)
- Status: Single select (Scheduled, Posted, Failed)
- Image_URL: URL field for media
- Campaign: Text field for organizing content

**Social Media API Setup:**
1. **Facebook**: Create app in Facebook Developers, get Page Access Token
2. **Twitter**: Apply for Twitter API, get Bearer Token and API keys
3. **LinkedIn**: Create LinkedIn app, get authorization code
4. **Instagram**: Use Facebook's Instagram Basic Display API

**Testing:**
1. Add test content to your calendar
2. Set post date to current time + 5 minutes
3. Run automation manually
4. Check that posts appear on selected platforms
5. Verify calendar status updates to "Posted" """,
        "bonus_content": """**📱 Social Media Best Practices:**

**Optimal Posting Times:**
- **Facebook**: Tuesday-Thursday, 9 AM - 3 PM
- **Twitter**: Monday-Friday, 8 AM - 4 PM  
- **LinkedIn**: Tuesday-Thursday, 8 AM - 2 PM
- **Instagram**: Monday-Friday, 11 AM - 1 PM

**Platform-Specific Content Guidelines:**

**Facebook:**
- Use engaging questions to drive comments
- Post videos for higher engagement
- Include calls-to-action
- Optimal length: 1-80 characters

**Twitter:**
- Use relevant hashtags (2-3 max)
- Tweet threads for longer content
- Engage with replies quickly
- Optimal length: 71-100 characters

**LinkedIn:**
- Share industry insights and professional tips
- Use professional tone
- Include relevant industry hashtags
- Optimal length: 150-300 characters

**Instagram:**
- Use high-quality, visually appealing images
- Include 5-10 relevant hashtags
- Post Stories for behind-the-scenes content
- Optimal caption length: 125-150 characters

**Content Ideas:**
- Behind-the-scenes content
- User-generated content
- Industry news and trends
- How-to tutorials
- Customer testimonials
- Company culture posts
- Product spotlights
- Team member features

**Hashtag Research:**
- Use mix of popular and niche hashtags
- Research competitor hashtags
- Create branded hashtags
- Track hashtag performance
- Update hashtag strategy monthly

**Analytics to Track:**
- Engagement rate (likes, comments, shares)
- Reach and impressions
- Click-through rates
- Follower growth
- Best performing content types
- Optimal posting times for your audience""",
        "tags": ["social media", "scheduling", "content marketing", "automation", "facebook", "twitter", "linkedin", "instagram"]
    }
}

# Utility functions
def create_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

async def convert_blueprint_with_ai(blueprint_json: str, source_platform: PlatformType, target_platform: PlatformType, ai_model: AIModel) -> dict:
    """Convert blueprint from one platform to another using AI"""
    
    prompt = f"""You are an expert no-code automation converter. 

Convert this {source_platform} automation blueprint to {target_platform} format.

SOURCE PLATFORM: {source_platform}
TARGET PLATFORM: {target_platform}

SOURCE JSON:
{blueprint_json}

Requirements:
1. Maintain the same workflow logic and functionality
2. Map equivalent modules/nodes between platforms
3. Preserve all data transformations and connections
4. Generate valid {target_platform} JSON that can be imported
5. Include detailed conversion notes explaining any changes

Respond in this EXACT format:

🔄 **CONVERTED {target_platform.upper()} BLUEPRINT:**

```json
[Provide the complete converted JSON here]
```

📝 **CONVERSION NOTES:**
- List any module mappings that were changed
- Note any functionality differences
- Explain any manual adjustments needed
- Highlight any platform-specific features used

The converted JSON must be valid and importable into {target_platform}."""

    try:
        if ai_model == AIModel.GPT4:
            client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert automation platform converter. Always provide complete, functional blueprint conversions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            content = response.choices[0].message.content
            
        elif ai_model == AIModel.CLAUDE:
            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.content[0].text
        
        # Parse the response to extract converted JSON and notes
        lines = content.split('\n')
        converted_json = ""
        conversion_notes = ""
        
        in_json_block = False
        in_notes_section = False
        
        for line in lines:
            if '```json' in line:
                in_json_block = True
                continue
            elif '```' in line and in_json_block:
                in_json_block = False
                continue
            elif '📝 **CONVERSION NOTES:**' in line:
                in_notes_section = True
                continue
            elif in_json_block:
                converted_json += line + '\n'
            elif in_notes_section:
                conversion_notes += line + '\n'
        
        return {
            "converted_json": converted_json.strip(),
            "conversion_notes": conversion_notes.strip(),
            "full_response": content
        }
        
    except Exception as e:
        logging.error(f"Blueprint conversion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to convert blueprint: {str(e)}")

def get_tier_limits(tier: SubscriptionTier) -> int:
    limits = {
        SubscriptionTier.FREE: 1,
        SubscriptionTier.PRO: 5,
        SubscriptionTier.CREATOR: 50
    }
    return limits[tier]

def is_template_request(task_description: str) -> tuple[bool, str]:
    """Check if the request is for a specific template"""
    task_lower = task_description.lower().strip()
    
    # Direct template name matches
    for template_name, template_data in AUTOMATION_TEMPLATES.items():
        if template_name.lower() in task_lower or task_lower in template_name.lower():
            return True, template_name
    
    # "Use template:" prefix
    if task_lower.startswith("use template:"):
        template_name = task_description[13:].strip()
        for name in AUTOMATION_TEMPLATES.keys():
            if name.lower() in template_name.lower():
                return True, name
    
    return False, ""

def get_platform_specific_json(template_data: dict, platform: PlatformType) -> str:
    """Get the appropriate JSON for the specified platform"""
    if platform == PlatformType.MAKE:
        return template_data.get("make_json", "")
    else:  # n8n
        return template_data.get("n8n_json", "")

def enhance_setup_instructions(base_instructions: str, platform: PlatformType) -> str:
    """Add platform-specific setup instructions"""
    platform_guide = ""
    
    if platform == PlatformType.MAKE:
        platform_guide = """
**Make.com Import Instructions:**
1. Log in to your Make.com account
2. Click "Create a new scenario"
3. Click the "..." menu in the top right
4. Select "Import Blueprint"
5. Copy the JSON template above
6. Paste it into the import dialog
7. Click "Save" to import the blueprint
8. Follow the connection prompts for each app
9. Test the scenario before activating
10. Turn on the scenario to run automatically

**Connecting Apps in Make.com:**
- Each module will show a "Create a connection" button
- Click it and follow the OAuth flow for each service
- Grant necessary permissions when prompted
- Test connections before proceeding
"""
    else:  # n8n
        platform_guide = """
**n8n Import Instructions:**
1. Open your n8n instance
2. Click the "+" to create a new workflow
3. Click the "..." menu in the top right
4. Select "Import from JSON"
5. Copy the JSON template above
6. Paste it into the import dialog
7. Click "Import" to load the workflow
8. Configure credentials for each node
9. Test the workflow execution
10. Activate the workflow

**Setting Up Credentials in n8n:**
- Click on each node that requires authentication
- Click "Create New" under credentials
- Follow the setup wizard for each service
- Test the connection before saving
- Save and activate the workflow
"""
    
    return base_instructions + "\n\n" + platform_guide

async def generate_complex_automation(task_description: str, platform: PlatformType, ai_model: AIModel) -> dict:
    """Generate complex automation with accurate, importable JSON using real module names"""
    
    # Enhanced system prompt for accurate JSON generation
    system_prompt = f"""You are an expert {platform} automation engineer. You must generate REAL, IMPORTABLE JSON that works in {platform}.

CRITICAL REQUIREMENTS:
1. Use ONLY real {platform} module names from the official documentation
2. Generate complete, valid JSON that can be imported directly
3. Include proper connections, parameters, and metadata
4. Use actual field names and structures that {platform} expects
5. Ensure all modules exist and are correctly configured

REAL MODULE NAMES TO USE:
For Make.com: google-sheets:watchRows, openai-gpt:createChatCompletion, openai-dall-e:createImage, wordpress:createPost, instagram:createMediaObject, tiktok:uploadVideo, youtube:uploadVideo
For n8n: n8n-nodes-base.googleSheetsTrigger, n8n-nodes-base.openAi, n8n-nodes-base.wordpress, n8n-nodes-base.httpRequest

RESPOND WITH WORKING JSON ONLY - NO EXPLANATIONS."""

    if platform == PlatformType.MAKE:
        user_prompt = f"""Generate a complete Make.com scenario JSON for: {task_description}

Structure required:
{{
  "name": "Scenario Name",
  "flow": [
    {{
      "id": 1,
      "module": "google-sheets:watchRows",
      "version": 1,
      "parameters": {{
        "spreadsheetId": "{{{{connection.spreadsheetId}}}}",
        "worksheetId": "gid=0",
        "includeEmptyRows": false
      }},
      "mapper": {{}},
      "metadata": {{
        "designer": {{"x": 0, "y": 0}}
      }}
    }}
  ],
  "metadata": {{
    "instant": false,
    "version": 1,
    "scenario": {{
      "roundtrips": 1,
      "maxErrors": 3,
      "autoCommit": true,
      "sequential": false
    }}
  }}
}}

Generate the complete workflow with proper module IDs (1, 2, 3...), real module names, and proper connections."""

    else:  # n8n
        user_prompt = f"""Generate a complete n8n workflow JSON for: {task_description}

Structure required:
{{
  "name": "Workflow Name",
  "nodes": [
    {{
      "parameters": {{
        "spreadsheetId": "{{{{ $credentials.spreadsheetId }}}}",
        "sheetName": "Sheet1"
      }},
      "name": "Google Sheets Trigger",
      "type": "n8n-nodes-base.googleSheetsTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    }}
  ],
  "connections": {{
    "Google Sheets Trigger": {{
      "main": [["Next Node"]]
    }}
  }},
  "active": false,
  "settings": {{}}
}}

Generate the complete workflow with real node types and proper connections."""

    try:
        if ai_model == AIModel.GPT4:
            client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4000,
                temperature=0.1  # Very low temperature for consistent, accurate output
            )
            raw_json = response.choices[0].message.content.strip()
            
        else:  # Claude
            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                ]
            )
            raw_json = response.content[0].text.strip()
        
        # Clean and validate JSON
        raw_json = raw_json.replace('```json', '').replace('```', '').strip()
        
        # Validate JSON structure
        try:
            parsed_json = json.loads(raw_json)
            
            # Validate platform-specific structure
            if platform == PlatformType.MAKE and "flow" not in parsed_json:
                raise ValueError("Make.com JSON must have 'flow' property")
            elif platform == PlatformType.N8N and "nodes" not in parsed_json:
                raise ValueError("n8n JSON must have 'nodes' property")
                
            # Re-serialize with proper formatting
            validated_json = json.dumps(parsed_json, indent=2)
            
            return {
                "automation_json": validated_json,
                "is_valid": True
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Generated JSON validation failed: {e}")
            
            # Return fallback JSON structure
            if platform == PlatformType.MAKE:
                fallback_json = {
                    "name": "Generated Automation",
                    "flow": [
                        {
                            "id": 1,
                            "module": "webhook:webhook",
                            "version": 1,
                            "parameters": {},
                            "mapper": {},
                            "metadata": {"designer": {"x": 0, "y": 0}}
                        }
                    ],
                    "metadata": {
                        "instant": False,
                        "version": 1,
                        "scenario": {
                            "roundtrips": 1,
                            "maxErrors": 3,
                            "autoCommit": True,
                            "sequential": False
                        }
                    }
                }
            else:  # n8n
                fallback_json = {
                    "name": "Generated Automation",
                    "nodes": [
                        {
                            "parameters": {},
                            "name": "Start",
                            "type": "n8n-nodes-base.start",
                            "typeVersion": 1,
                            "position": [240, 300]
                        }
                    ],
                    "connections": {},
                    "active": False,
                    "settings": {}
                }
            
            return {
                "automation_json": json.dumps(fallback_json, indent=2),
                "is_valid": False
            }
            
    except Exception as e:
        logging.error(f"Error generating complex automation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate automation: {str(e)}")

async def generate_automation_with_ai(task_description: str, platform: PlatformType, ai_model: AIModel) -> dict:
    """Generate automation using specified AI model with accurate importable JSON"""
    
    # Check if this is a template request first
    is_template, template_name = is_template_request(task_description)
    if is_template and template_name in AUTOMATION_TEMPLATES:
        template_data = AUTOMATION_TEMPLATES[template_name]
        return {
            "automation_summary": template_data["automation_summary"],
            "required_tools": template_data["required_tools"],
            "workflow_steps": template_data["workflow_steps"],
            "automation_json": get_platform_specific_json(template_data, platform),
            "setup_instructions": enhance_setup_instructions(template_data["setup_instructions"], platform),
            "bonus_content": template_data.get("bonus_content"),
            "is_template": True,
            "template_id": template_data["id"]
        }
    
    # For complex automations, use the specialized function for JSON generation
    platform_examples = {
        PlatformType.MAKE: '''Example Make.com JSON format with REAL working modules:
{
  "name": "Content Automation Workflow",
  "flow": [
    {
      "id": 1,
      "module": "google-sheets:WatchNewRows",
      "version": 1,
      "parameters": {
        "spreadsheetId": "your-spreadsheet-id",
        "sheetName": "Sheet1",
        "tableFirstRow": "A1",
        "includeEmptyRows": false
      },
      "mapper": {},
      "metadata": {
        "designer": {"x": 0, "y": 0},
        "restore": {}
      }
    },
    {
      "id": 2,
      "module": "openai-gpt:CreateCompletion",
      "version": 1,
      "parameters": {
        "model": "gpt-4",
        "maxTokens": 1000
      },
      "mapper": {
        "prompt": "Analyze this article: {{1.url}}"
      },
      "metadata": {
        "designer": {"x": 300, "y": 0},
        "restore": {}
      }
    },
    {
      "id": 3,
      "module": "builtin:BasicRouter",
      "version": 1,
      "parameters": {},
      "mapper": {},
      "metadata": {
        "designer": {"x": 600, "y": 0},
        "restore": {}
      }
    },
    {
      "id": 4,
      "module": "wordpress:CreatePost",
      "version": 1,
      "parameters": {
        "status": "publish"
      },
      "mapper": {
        "title": "{{2.title}}",
        "content": "{{2.content}}"
      },
      "metadata": {
        "designer": {"x": 900, "y": -100},
        "restore": {}
      }
    },
    {
      "id": 5,
      "module": "instagram:CreatePost",
      "version": 1,
      "parameters": {},
      "mapper": {
        "caption": "{{2.instagram_caption}}"
      },
      "metadata": {
        "designer": {"x": 900, "y": 0},
        "restore": {}
      }
    }
  ],
  "metadata": {
    "instant": false,
    "version": 1,
    "scenario": {
      "roundtrips": 1,
      "maxErrors": 3,
      "autoCommit": true,
      "sequential": false
    },
    "zone": "us1.make.com"
  }
}

CRITICAL: Use ONLY these verified Make.com modules:
- google-sheets:WatchNewRows (watch for new Google Sheets rows)
- google-sheets:GetRange (get data from Google Sheets)
- openai-gpt:CreateCompletion (GPT-4 text generation)
- openai-dalle:GenerateImage (DALL-E image generation)
- wordpress:CreatePost (create WordPress posts)
- wordpress:UploadMedia (upload media to WordPress)
- instagram:CreatePost (post to Instagram)
- tiktok:UploadVideo (upload to TikTok)
- youtube:UploadVideo (upload to YouTube)
- slack:PostMessage (post to Slack)
- twitter:CreateTweet (post to Twitter)
- builtin:BasicRouter (route to multiple paths)
- http:ActionSendData (HTTP requests)
- tools:SetVariable (set variables)
- tools:Sleep (add delays)
- json:ParseJSON (parse JSON data)''',
        
        PlatformType.N8N: '''Example n8n JSON format with REAL working nodes:
{
  "name": "Content Automation Workflow",
  "nodes": [
    {
      "parameters": {
        "spreadsheetId": "your-spreadsheet-id",
        "range": "Sheet1!A:Z"
      },
      "id": "sheets-1",
      "name": "Google Sheets Trigger",
      "type": "n8n-nodes-base.googleSheetsTrigger",
      "typeVersion": 2,
      "position": [240, 300]
    },
    {
      "parameters": {
        "model": "gpt-4",
        "prompt": "Analyze this article: {{ $json.url }}",
        "maxTokens": 1000
      },
      "id": "openai-1",
      "name": "OpenAI GPT-4",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [{"value1": "{{ $json.platform }}", "value2": "wordpress"}]
        }
      },
      "id": "if-1",
      "name": "Route Content",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [680, 300]
    }
  ],
  "connections": {
    "Google Sheets Trigger": {
      "main": [["OpenAI GPT-4"]]
    },
    "OpenAI GPT-4": {
      "main": [["Route Content"]]
    }
  }
}

CRITICAL: Use ONLY these verified n8n nodes:
- n8n-nodes-base.googleSheetsTrigger (watch Google Sheets)
- n8n-nodes-base.googleSheets (read/write Google Sheets)
- n8n-nodes-base.openAi (OpenAI GPT-4 and DALL-E)
- n8n-nodes-base.wordpress (WordPress operations)
- n8n-nodes-base.httpRequest (HTTP requests)
- n8n-nodes-base.if (conditional routing)
- n8n-nodes-base.set (set data values)
- n8n-nodes-base.function (custom JavaScript)
- n8n-nodes-base.merge (merge data streams)
- n8n-nodes-base.wait (add delays)'''
    }

    prompt = f"""You are AutoFlow AI — an expert no-code automation generator. You MUST provide a complete, working JSON template using REAL modules that exist in {platform}.

CRITICAL REQUIREMENTS:
1. You must generate actual, functional JSON code using verified module names
2. Create a COMPLEX workflow that matches the user's request exactly
3. Use the correct modules for the services mentioned (Google Sheets, OpenAI, WordPress, etc.)
4. Include proper routing/branching for multiple outputs
5. Do NOT use simple webhook + HTTP fallbacks for complex requests

Task: "{task_description}"
Target Platform: {platform}

ANALYSIS: This request needs these key components:
- Google Sheets trigger (not webhook)
- OpenAI/ChatGPT integration for content processing
- Multiple social media endpoints
- WordPress publishing
- Image generation
- Proper routing/branching

{platform_examples[platform]}

You must respond in this EXACT format with a COMPLEX, MULTI-STEP workflow:

🚀 Automation Summary: [Brief summary of what this automation does and why it's useful]

🧩 Platform: {platform}

📦 Required Apps:
- [App 1: Purpose + setup note]
- [App 2: Purpose + setup note]
- [Continue for ALL apps mentioned in the request]

📊 Automation Workflow Steps:
1. [Step 1: Trigger description - should match the user's trigger request]
2. [Step 2: Action description - should match the processing needed]
3. [Step 3: Continue for ALL steps mentioned in the user request]
4. [Include routing/branching steps]
5. [Include all social media and publishing steps]

🧠 JSON Automation Template:
```json
[PROVIDE COMPLETE, COMPLEX WORKFLOW JSON using the SPECIFIC modules for each service mentioned. This should be 5+ modules for a complex request like this, NOT just webhook + HTTP]
```

📋 Beginner Setup Instructions:
[Detailed step-by-step instructions for importing JSON, connecting ALL the required apps, and testing]

🎁 Bonus Assets:
[Optional templates, tips, or additional resources]

CRITICAL: For a complex request like this, you MUST use modules like:
- google-sheets:WatchNewRows (for Google Sheets trigger)
- openai-gpt:CreateCompletion (for ChatGPT/GPT-4)
- openai-dalle:GenerateImage (for DALL-E)
- wordpress:CreatePost (for WordPress)
- builtin:BasicRouter (for routing to multiple platforms)
- And specific modules for each social media platform mentioned

DO NOT create a simple webhook + HTTP workflow for complex requests. Create the full multi-step automation the user requested."""

    try:
        if ai_model == AIModel.GPT4:
            client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert automation builder. You MUST always provide complete, functional JSON automation templates. Never say you cannot provide JSON. Always generate working code."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.5
            )
            content = response.choices[0].message.content
            
        elif ai_model == AIModel.CLAUDE:
            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                temperature=0.5,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.content[0].text
        
        # Parse the response to extract components
        lines = content.split('\n')
        automation_summary = ""
        required_tools = []
        workflow_steps = []
        automation_json = ""
        setup_instructions = ""
        bonus_content = ""
        
        current_section = ""
        json_started = False
        json_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith('🚀 Automation Summary:'):
                automation_summary = line_stripped.replace('🚀 Automation Summary:', '').strip()
                current_section = "summary"
            elif line_stripped.startswith('📦 Required Apps:'):
                current_section = "tools"
            elif line_stripped.startswith('📊 Automation Workflow Steps:'):
                current_section = "steps"
            elif line_stripped.startswith('🧠 JSON Automation Template:'):
                current_section = "json"
            elif '```json' in line_stripped:
                json_started = True
                continue
            elif '```' in line_stripped and json_started:
                json_started = False
                automation_json = '\n'.join(json_lines)
                break
            elif line_stripped.startswith('📋 Beginner Setup Instructions:'):
                current_section = "instructions"
                json_started = False
            elif line_stripped.startswith('🎁 Bonus Assets:'):
                current_section = "bonus"
            elif current_section == "tools" and line_stripped.startswith('- '):
                required_tools.append(line_stripped[2:])
            elif current_section == "steps" and any(line_stripped.startswith(f'{i}.') for i in range(1, 10)):
                workflow_steps.append(line_stripped)
            elif json_started:
                json_lines.append(line)
            elif current_section == "instructions":
                if line_stripped and not line_stripped.startswith('🎁'):
                    setup_instructions += line + '\n'
            elif current_section == "bonus":
                bonus_content += line + '\n'
        
        # Fallback JSON if AI didn't provide proper JSON
        if not automation_json or "not possible" in automation_json.lower() or "limitations" in automation_json.lower():
            automation_json = generate_fallback_json(task_description, platform)
            logging.warning(f"AI failed to generate JSON, using fallback for: {task_description}")
        
        # Validate JSON
        try:
            json.loads(automation_json)
        except json.JSONDecodeError:
            automation_json = generate_fallback_json(task_description, platform)
            logging.warning(f"Invalid JSON generated, using fallback for: {task_description}")
        
        # Enhance setup instructions with platform-specific guidance
        enhanced_instructions = enhance_setup_instructions(setup_instructions.strip(), platform)
        
        return {
            "automation_summary": automation_summary or f"Custom automation for: {task_description}",
            "required_tools": required_tools or ["Webhook - Trigger automation", "HTTP Request - Send data"],
            "workflow_steps": workflow_steps or ["1. Trigger: Receive webhook data", "2. Process: Transform data", "3. Action: Send to destination"],
            "automation_json": automation_json,
            "setup_instructions": enhanced_instructions,
            "bonus_content": bonus_content.strip() if bonus_content.strip() else None,
            "is_template": False,
            "template_id": None
        }
        
    except Exception as e:
        logging.error(f"AI API error: {str(e)}")
        # Return fallback automation on any error
        return {
            "automation_summary": f"Basic automation for: {task_description}",
            "required_tools": ["Webhook - Trigger automation", "HTTP Request - Send data"],
            "workflow_steps": ["1. Trigger: Receive webhook data", "2. Process: Transform data", "3. Action: Send to destination"],
            "automation_json": generate_fallback_json(task_description, platform),
            "setup_instructions": enhance_setup_instructions("Follow platform-specific import instructions below.", platform),
            "bonus_content": None,
            "is_template": False,
            "template_id": None
        }

def generate_fallback_json(task_description: str, platform: PlatformType) -> str:
    """Generate fallback JSON with REAL working modules"""
    if platform == PlatformType.MAKE:
        return json.dumps({
            "name": f"Automation - {task_description[:30]}",
            "flow": [
                {
                    "id": 1,
                    "module": "gateway:CustomWebHook",
                    "version": 1,
                    "parameters": {
                        "hook": 151971,
                        "maxResults": 1
                    },
                    "mapper": {},
                    "metadata": {
                        "designer": {
                            "x": 0,
                            "y": 0
                        },
                        "restore": {
                            "hook": {
                                "data": {
                                    "editable": "true"
                                },
                                "label": "My webhook"
                            }
                        },
                        "expect": [
                            {
                                "name": "data",
                                "type": "collection",
                                "label": "Data",
                                "spec": []
                            }
                        ]
                    }
                },
                {
                    "id": 2,
                    "module": "http:ActionSendData",
                    "version": 3,
                    "parameters": {
                        "handleErrors": False,
                        "useNewZLibDeCompress": True
                    },
                    "mapper": {
                        "url": "https://httpbin.org/post",
                        "method": "POST",
                        "headers": [],
                        "qs": [],
                        "bodyType": "application/json",
                        "body": '{{"task": "{}", "data": "{{1.data}}" }}'.format(task_description)
                    },
                    "metadata": {
                        "designer": {
                            "x": 300,
                            "y": 0
                        },
                        "restore": {
                            "method": {
                                "label": "POST"
                            },
                            "bodyType": {
                                "label": "JSON (application/json)"
                            }
                        },
                        "expect": [
                            {
                                "name": "url",
                                "type": "url",
                                "label": "URL",
                                "required": True
                            }
                        ]
                    }
                }
            ],
            "metadata": {
                "instant": False,
                "version": 1,
                "scenario": {
                    "roundtrips": 1,
                    "maxErrors": 3,
                    "autoCommit": True,
                    "autoCommitTriggerLast": True,
                    "sequential": False,
                    "slots": None,
                    "confidential": False,
                    "dataloss": False,
                    "dlq": False,
                    "freshVariables": False
                },
                "designer": {
                    "orphans": []
                },
                "zone": "us1.make.com"
            }
        }, indent=2)
    else:  # n8n
        return json.dumps({
            "name": f"Automation - {task_description[:30]}",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "webhook",
                        "options": {}
                    },
                    "id": "webhook-node-1",
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "webhookId": "auto-generated"
                },
                {
                    "parameters": {
                        "url": "https://httpbin.org/post",
                        "sendBody": True,
                        "bodyContentType": "json",
                        "jsonBody": '{{"task": "{}", "data": "{{ $json }}" }}'.format(task_description),
                        "options": {}
                    },
                    "id": "http-node-1",
                    "name": "HTTP Request",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 3,
                    "position": [460, 300]
                }
            ],
            "connections": {
                "Webhook": {
                    "main": [
                        [
                            {
                                "node": "HTTP Request",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            "pinData": {}
        }, indent=2)

# Routes
@api_router.get("/")
async def root():
    try:
        # Get actual stats from database
        total_automations = await db.automations.count_documents({})
        total_leads = await db.leads.count_documents({})
        total_users = await db.users.count_documents({})
        
        # Calculate satisfaction rate (implement your own logic)
        satisfaction_rate = 4.9  # Placeholder
        
        return {
            "total_automations": total_automations,
            "total_leads": total_leads,
            "total_users": total_users,
            "satisfaction_rate": satisfaction_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/create-checkout-session")
async def create_checkout_session(request: StripeCheckoutRequest):
    try:
        prices = {
            SubscriptionTier.PRO: "price_1QxxxxxxxxxxxxxxxxxxxPro",  # Replace with actual Stripe price ID
            SubscriptionTier.CREATOR: "price_1QxxxxxxxxxxxxxxxxxxxCreator"  # Replace with actual Stripe price ID
        }
        
        if request.tier not in prices:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': prices[request.tier],
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://your-domain.com/pricing',
            customer_email=request.user_email,
            metadata={
                'tier': request.tier,
                'user_email': request.user_email
            }
        )
        
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/templates")
async def get_templates():
    """Get all available automation templates"""
    templates = []
    for name, data in AUTOMATION_TEMPLATES.items():
        templates.append({
            "id": data["id"],
            "name": name,
            "category": data["category"],
            "description": data["description"],
            "tags": data["tags"]
        })
    return {"templates": templates}

@api_router.get("/templates/{template_name}")
async def get_template(template_name: str, platform: PlatformType = PlatformType.MAKE):
    """Get a specific template by name"""
    if template_name not in AUTOMATION_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template_data = AUTOMATION_TEMPLATES[template_name]
    
    return AutomationResponse(
        task_description=f"Use template: {template_name}",
        platform=platform,
        automation_summary=template_data["automation_summary"],
        required_tools=template_data["required_tools"],
        workflow_steps=template_data["workflow_steps"],
        automation_json=get_platform_specific_json(template_data, platform),
        setup_instructions=enhance_setup_instructions(template_data["setup_instructions"], platform),
        bonus_content=template_data.get("bonus_content"),
        is_template=True,
        template_id=template_data["id"]
    )

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    password_hash = create_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        subscription_tier=SubscriptionTier.FREE,
        automations_limit=get_tier_limits(SubscriptionTier.FREE)
    )
    
    await db.users.insert_one(user.dict())
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "subscription_tier": user.subscription_tier,
            "automations_used": user.automations_used,
            "automations_limit": user.automations_limit
        }
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user["id"],
            "email": user["email"],
            "subscription_tier": user["subscription_tier"],
            "automations_used": user["automations_used"],
            "automations_limit": user["automations_limit"]
        }
    )

@api_router.post("/generate-automation", response_model=AutomationResponse)
async def generate_automation(request: AutomationRequest, current_user: User = Depends(get_current_user)):
    # Check if this is a template request first
    is_template, template_name = is_template_request(request.task_description)
    
    # Only check usage limits for custom automations, not templates
    if not is_template and current_user.automations_used >= current_user.automations_limit:
        raise HTTPException(status_code=403, detail="Automation limit reached. Please upgrade your subscription.")
    
    # Generate automation using specified AI
    automation_data = await generate_automation_with_ai(request.task_description, request.platform, request.ai_model)
    
    # Create automation record
    automation = AutomationResponse(
        user_id=current_user.id,
        task_description=request.task_description,
        platform=request.platform,
        ai_model=request.ai_model,
        automation_summary=automation_data["automation_summary"],
        required_tools=automation_data["required_tools"],
        workflow_steps=automation_data["workflow_steps"],
        automation_json=automation_data["automation_json"],
        setup_instructions=automation_data["setup_instructions"],
        bonus_content=automation_data["bonus_content"],
        is_template=automation_data["is_template"],
        template_id=automation_data["template_id"]
    )
    
    # Save to database
    await db.automations.insert_one(automation.dict())
    
    # Update user's usage count (only for custom automations, templates don't count)
    if not automation_data["is_template"]:
        await db.users.update_one(
            {"id": current_user.id},
            {"$inc": {"automations_used": 1}, "$set": {"updated_at": datetime.utcnow()}}
        )
    
    return automation

@api_router.post("/generate-automation-guest", response_model=AutomationResponse)
async def generate_automation_guest(request: AutomationRequest):
    """Generate automation for guest users with required email for lead capture"""
    
    # Store lead information for future marketing (you could add to a leads collection)
    lead_data = {
        "email": request.user_email,
        "task_description": request.task_description,
        "platform": request.platform,
        "ai_model": request.ai_model,
        "created_at": datetime.utcnow(),
        "source": "guest_automation"
    }
    
    # Optional: Save lead to database for marketing purposes
    try:
        await db.leads.insert_one(lead_data)
    except Exception as e:
        logging.warning(f"Failed to save lead data: {e}")
    
    # Generate automation using specified AI
    automation_data = await generate_automation_with_ai(request.task_description, request.platform, request.ai_model)
    
    # Create automation record (no user_id for guests, but include email)
    automation = AutomationResponse(
        user_id=None,
        task_description=request.task_description,
        platform=request.platform,
        ai_model=request.ai_model,
        automation_summary=automation_data["automation_summary"],
        required_tools=automation_data["required_tools"],
        workflow_steps=automation_data["workflow_steps"],
        automation_json=automation_data["automation_json"],
        setup_instructions=automation_data["setup_instructions"],
        bonus_content=automation_data["bonus_content"],
        is_template=automation_data["is_template"],
        template_id=automation_data["template_id"]
    )
    
    # Save to database (for analytics, include email in metadata)
    automation_dict = automation.dict()
    automation_dict["guest_email"] = request.user_email  # Track guest email
    await db.automations.insert_one(automation_dict)
    
    return automation

@api_router.get("/my-automations", response_model=List[AutomationResponse])
async def get_my_automations(current_user: User = Depends(get_current_user)):
    automations = await db.automations.find({"user_id": current_user.id}).sort("created_at", -1).to_list(100)
    return [AutomationResponse(**automation) for automation in automations]

@api_router.post("/convert-blueprint", response_model=BlueprintConversionResponse)
async def convert_blueprint(request: BlueprintConversionRequest, current_user: User = Depends(get_current_user)):
    """Convert blueprint between Make.com and n8n (Pro feature)"""
    
    # Check if user has Pro or Creator tier
    if current_user.subscription_tier == SubscriptionTier.FREE:
        raise HTTPException(status_code=403, detail="Blueprint conversion is a Pro feature. Please upgrade your subscription.")
    
    # Validate that source and target platforms are different
    if request.source_platform == request.target_platform:
        raise HTTPException(status_code=400, detail="Source and target platforms must be different")
    
    # Validate JSON format
    try:
        json.loads(request.blueprint_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in blueprint")
    
    # Convert blueprint using AI
    conversion_data = await convert_blueprint_with_ai(
        request.blueprint_json, 
        request.source_platform, 
        request.target_platform, 
        request.ai_model
    )
    
    # Create conversion record
    conversion = BlueprintConversionResponse(
        user_id=current_user.id,
        source_platform=request.source_platform,
        target_platform=request.target_platform,
        ai_model=request.ai_model,
        original_json=request.blueprint_json,
        converted_json=conversion_data["converted_json"],
        conversion_notes=conversion_data["conversion_notes"]
    )
    
    # Save to database
    await db.blueprint_conversions.insert_one(conversion.dict())
    
    return conversion

@api_router.get("/my-conversions", response_model=List[BlueprintConversionResponse])
async def get_my_conversions(current_user: User = Depends(get_current_user)):
    """Get user's blueprint conversions"""
    conversions = await db.blueprint_conversions.find({"user_id": current_user.id}).sort("created_at", -1).to_list(50)
    return [BlueprintConversionResponse(**conversion) for conversion in conversions]

@api_router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "subscription_tier": current_user.subscription_tier,
        "automations_used": current_user.automations_used,
        "automations_limit": current_user.automations_limit,
        "created_at": current_user.created_at
    }

@api_router.post("/create-checkout-session")
async def create_checkout_session(request: StripeCheckoutRequest):
    try:
        prices = {
            SubscriptionTier.PRO: "price_1QxxxxxxxxxxxxxxxxxxxPro",  # Replace with actual Stripe price ID
            SubscriptionTier.CREATOR: "price_1QxxxxxxxxxxxxxxxxxxxCreator"  # Replace with actual Stripe price ID
        }
        
        if request.tier not in prices:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': prices[request.tier],
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://your-domain.com/pricing',
            customer_email=request.user_email,
            metadata={
                'tier': request.tier,
                'user_email': request.user_email
            }
        )
        
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()