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
import stripe
import json
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize external services
openai.api_key = os.environ['OPENAI_API_KEY']
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
app = FastAPI(title="AutoFlow AI", version="1.0.0")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Enums
class PlatformType(str, Enum):
    MAKE = "Make.com"
    N8N = "n8n"

class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    CREATOR = "creator"

# Models
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
    platform: PlatformType
    user_email: Optional[EmailStr] = None

class AutomationResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    task_description: str
    platform: PlatformType
    automation_summary: str
    required_tools: List[str]
    workflow_steps: List[str]
    automation_json: str
    setup_instructions: str
    bonus_content: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StripeCheckoutRequest(BaseModel):
    tier: SubscriptionTier
    user_email: EmailStr

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

def get_tier_limits(tier: SubscriptionTier) -> int:
    limits = {
        SubscriptionTier.FREE: 1,
        SubscriptionTier.PRO: 5,
        SubscriptionTier.CREATOR: 50
    }
    return limits[tier]

async def generate_automation_with_openai(task_description: str, platform: PlatformType) -> dict:
    """Generate automation using OpenAI GPT-4"""
    
    prompt = f"""You are AutoFlow AI – an expert automation builder that creates working automation templates for {platform}.

The user wants to automate: "{task_description}"

You must respond in this EXACT format:

🚀 Automation Summary: [Brief summary of what this automation does and why it's useful]

🧩 Platform: {platform}

📦 Required Tools:
- [Tool 1: Purpose + setup note]
- [Tool 2: Purpose + setup note]

📊 Automation Workflow Steps:
1. [Step 1: Trigger]
2. [Step 2: Action]
3. [Step 3: Continue until complete]

🧠 JSON Automation Template:
[Provide valid JSON for {platform} that can be imported]

📋 Setup Instructions:
[Step-by-step instructions for beginners to import and set up this automation]

🎁 Bonus Assets:
[If relevant, include email templates, captions, or other helpful content]

Generate a complete, working automation that a beginner can use immediately."""

    try:
        client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert automation builder. Always provide complete, functional automation templates."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
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
        
        for line in lines:
            line = line.strip()
            if line.startswith('🚀 Automation Summary:'):
                automation_summary = line.replace('🚀 Automation Summary:', '').strip()
                current_section = "summary"
            elif line.startswith('📦 Required Tools:'):
                current_section = "tools"
            elif line.startswith('📊 Automation Workflow Steps:'):
                current_section = "steps"
            elif line.startswith('🧠 JSON Automation Template:'):
                current_section = "json"
                json_started = True
            elif line.startswith('📋 Setup Instructions:'):
                current_section = "instructions"
                json_started = False
            elif line.startswith('🎁 Bonus Assets:'):
                current_section = "bonus"
            elif current_section == "tools" and line.startswith('- '):
                required_tools.append(line[2:])
            elif current_section == "steps" and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.') or line.startswith('6.') or line.startswith('7.') or line.startswith('8.') or line.startswith('9.')):
                workflow_steps.append(line)
            elif current_section == "json" and json_started:
                if line and not line.startswith('📋'):
                    automation_json += line + '\n'
            elif current_section == "instructions":
                if line and not line.startswith('🎁'):
                    setup_instructions += line + '\n'
            elif current_section == "bonus":
                bonus_content += line + '\n'
        
        return {
            "automation_summary": automation_summary,
            "required_tools": required_tools,
            "workflow_steps": workflow_steps,
            "automation_json": automation_json.strip(),
            "setup_instructions": setup_instructions.strip(),
            "bonus_content": bonus_content.strip() if bonus_content.strip() else None,
            "full_response": content
        }
        
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate automation: {str(e)}")

# Routes
@api_router.get("/")
async def root():
    return {"message": "AutoFlow AI API", "version": "1.0.0"}

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
    # Check usage limits
    if current_user.automations_used >= current_user.automations_limit:
        raise HTTPException(status_code=403, detail="Automation limit reached. Please upgrade your subscription.")
    
    # Generate automation using OpenAI
    automation_data = await generate_automation_with_openai(request.task_description, request.platform)
    
    # Create automation record
    automation = AutomationResponse(
        user_id=current_user.id,
        task_description=request.task_description,
        platform=request.platform,
        automation_summary=automation_data["automation_summary"],
        required_tools=automation_data["required_tools"],
        workflow_steps=automation_data["workflow_steps"],
        automation_json=automation_data["automation_json"],
        setup_instructions=automation_data["setup_instructions"],
        bonus_content=automation_data["bonus_content"]
    )
    
    # Save to database
    await db.automations.insert_one(automation.dict())
    
    # Update user's usage count
    await db.users.update_one(
        {"id": current_user.id},
        {"$inc": {"automations_used": 1}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    return automation

@api_router.post("/generate-automation-guest", response_model=AutomationResponse)
async def generate_automation_guest(request: AutomationRequest):
    """Generate automation for guest users (free tier, no auth required)"""
    
    # Generate automation using OpenAI
    automation_data = await generate_automation_with_openai(request.task_description, request.platform)
    
    # Create automation record (no user_id for guests)
    automation = AutomationResponse(
        user_id=None,
        task_description=request.task_description,
        platform=request.platform,
        automation_summary=automation_data["automation_summary"],
        required_tools=automation_data["required_tools"],
        workflow_steps=automation_data["workflow_steps"],
        automation_json=automation_data["automation_json"],
        setup_instructions=automation_data["setup_instructions"],
        bonus_content=automation_data["bonus_content"]
    )
    
    # Save to database (for analytics)
    await db.automations.insert_one(automation.dict())
    
    return automation

@api_router.get("/my-automations", response_model=List[AutomationResponse])
async def get_my_automations(current_user: User = Depends(get_current_user)):
    automations = await db.automations.find({"user_id": current_user.id}).sort("created_at", -1).to_list(100)
    return [AutomationResponse(**automation) for automation in automations]

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