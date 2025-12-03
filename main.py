import os
import json
import uuid
from typing import Literal, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
import asyncpg
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not GEMINI_API_KEY or not DATABASE_URL:
    raise RuntimeError("FATAL: GEMINI_API_KEY and DATABASE_URL must be set in environment.")

# 2. PYDANTIC MODELS
# ============================================================================

class CallInsight(BaseModel):
    """Core structured output model for LLM extraction."""
    customer_intent: str = Field(
        ..., min_length=5, max_length=200,
        description="Primary customer intent"
    )
    sentiment: Literal['Negative', 'Neutral', 'Positive'] = Field(
        ..., description="Customer sentiment classification"
    )
    action_required: bool = Field(
        ..., description="True if follow-up action needed"
    )
    summary: str = Field(
        ..., min_length=20, max_length=500,
        description="Concise summary of the call"
    )
    
    @validator('customer_intent', 'summary')
    def validate_non_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()


class CallRequest(BaseModel):
    """Model for incoming API requests."""
    transcript: str = Field(
        ..., min_length=20, max_length=10000,
        description="Raw customer service call transcript"
    )
    metadata: Optional[dict] = Field(
        default=None, description="Optional metadata"
    )
    
    @validator('transcript')
    def validate_transcript(cls, v):
        if not v or not v.strip():
            raise ValueError("Transcript cannot be empty")
        if 'Agent:' not in v or 'Customer:' not in v:
            raise ValueError("Transcript must contain both Agent and Customer dialogue")
        return v.strip()


class CallResponse(BaseModel):
    """Model for API response."""
    id: int
    unique_id: str
    customer_intent: str
    sentiment: Literal['Negative', 'Neutral', 'Positive']
    action_required: bool
    summary: str
    raw_transcript: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    llm_client: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# 3. LLM SERVICE
# ============================================================================

class LLMInsightExtractor:
    """Handles all LLM interaction with retry logic."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        return """You are an expert financial and debt collection analyst. Analyze customer service call transcripts (often in Hinglish) and extract structured insights with EXTREME PRECISION.

=== CRITICAL INSTRUCTIONS ===
1. Output ONLY valid JSON matching the exact schema provided
2. NO additional text, commentary, or markdown formatting
3. Analyze from the CUSTOMER's perspective for intent and sentiment

=== FIELD DEFINITIONS ===

**customer_intent** (String):
- Be SPECIFIC and ACTION-ORIENTED
- Examples: "Promise to Pay (PTP) - Wednesday", "Dispute Fraudulent Transaction", "Request Loan Restructuring due to Hardship"

**sentiment** (Must be EXACTLY one of: Negative, Neutral, Positive):
- **Positive**: Customer is cooperative, proactive, confirms timely payment
- **Neutral**: Customer agrees after explanation, sets clear PTP, responds calmly
- **Negative**: Customer is confrontational, disputes debt, expresses distress/hardship

**action_required** (Boolean):
- **true** if: PTP set, dispute raised, hardship request, legal action mentioned, form to be sent
- **false** if: Simple reminder with vague response, no concrete commitment

**summary** (Text):
- Structure: [Debt Status] + [Customer Response] + [Outcome]
- Length: 1-3 concise sentences

Return ONLY the JSON object."""
    
    async def extract_insights(self, transcript: str, max_retries: int = 3) -> CallInsight:
        schema = CallInsight.model_json_schema()
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=transcript,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        response_mime_type="application/json",
                        response_schema=schema,
                        temperature=0.1,
                    )
                )
                
                insight_data = json.loads(response.text)
                insight = CallInsight(**insight_data)
                
                if insight.sentiment not in ['Negative', 'Neutral', 'Positive']:
                    raise ValueError(f"Invalid sentiment: {insight.sentiment}")
                
                return insight
                
            except Exception as e:
                last_error = f"Attempt {attempt + 1} failed: {e}"
                print(f"  ✗ {last_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract insights after {max_retries} attempts. Last error: {last_error}"
        )

# 4. DATABASE SERVICE
# ============================================================================

class DatabaseService:
    """Handles all database operations with connection pooling."""
    
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS call_records (
        id SERIAL PRIMARY KEY,
        unique_id UUID UNIQUE NOT NULL,
        transcript TEXT NOT NULL,
        intent TEXT NOT NULL,
        sentiment TEXT NOT NULL CHECK (sentiment IN ('Negative', 'Neutral', 'Positive')),
        action_required BOOLEAN NOT NULL,
        summary TEXT NOT NULL,
        metadata JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_call_records_sentiment ON call_records(sentiment);
    CREATE INDEX IF NOT EXISTS idx_call_records_action_required ON call_records(action_required);
    CREATE INDEX IF NOT EXISTS idx_call_records_created_at ON call_records(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_call_records_unique_id ON call_records(unique_id);
    """
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self, database_url: str):
        try:
            self.pool = await asyncpg.create_pool(
                database_url, min_size=5, max_size=20, command_timeout=60
            )
            async with self.pool.acquire() as conn:
                await conn.execute(self.SCHEMA)
            print("✓ Database connected and schema initialized")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            print("✓ Database connection closed")
    
    async def health_check(self) -> bool:
        if not self.pool:
            return False
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False
    
    async def insert_call_record(
        self, transcript: str, insights: CallInsight, metadata: Optional[dict] = None
    ) -> tuple[int, str]:
        if not self.pool:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not available"
            )
        
        unique_id = str(uuid.uuid4())
        insert_query = """
        INSERT INTO call_records 
            (unique_id, transcript, intent, sentiment, action_required, summary, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id;
        """
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    record_id = await conn.fetchval(
                        insert_query, unique_id, transcript,
                        insights.customer_intent, insights.sentiment,
                        insights.action_required, insights.summary,
                        json.dumps(metadata) if metadata else None
                    )
            return record_id, unique_id
            
        except asyncpg.UniqueViolationError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate record detected"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to persist data: {str(e)}"
            )

# 5. FASTAPI APPLICATION
# ============================================================================

llm_service: Optional[LLMInsightExtractor] = None
db_service = DatabaseService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm_service
    
    print("\n" + "="*60)
    print("Starting Conversational Insights Generator")
    print("="*60 + "\n")
    
    try:
        llm_service = LLMInsightExtractor(api_key=GEMINI_API_KEY)
        print("✓ LLM service initialized")
    except Exception as e:
        print(f"✗ LLM initialization failed: {e}")
        raise
    
    try:
        await db_service.connect(DATABASE_URL)
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise
    
    print("\n✅ Application Ready!")
    print("📍 API Docs: http://localhost:8000/docs")
    print("📍 Health:   http://localhost:8000/health\n")
    
    yield
    
    print("\nShutting down...")
    await db_service.disconnect()
    print("✅ Shutdown complete\n")


app = FastAPI(
    title="Conversational Insights Generator",
    description="Production-grade API for analyzing debt collection call transcripts",
    version="2.0.0",
    lifespan=lifespan
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"⚠️  Unhandled exception: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred", "type": type(exc).__name__}
    )


@app.get("/", tags=["Info"])
async def root():
    return {
        "name": "Conversational Insights Generator",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {"docs": "/docs", "health": "/health", "analyze": "/analyze_call"}
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    db_healthy = await db_service.health_check()
    return HealthResponse(
        status="healthy" if (db_healthy and llm_service) else "degraded",
        database="connected" if db_healthy else "disconnected",
        llm_client="initialized" if llm_service else "not_initialized"
    )


@app.post("/analyze_call", response_model=CallResponse, status_code=status.HTTP_201_CREATED, tags=["Analysis"])
async def analyze_call(request: CallRequest):
    """
    Analyze customer service call transcript and persist structured insights.
    
    Pipeline:
    1. Validate input transcript
    2. Extract insights using LLM with retry logic
    3. Persist to database with transaction safety
    4. Return complete response with metadata
    """
    if not llm_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service not available"
        )
    
    start_time = datetime.utcnow()
    
    try:
        # Extract insights
        insights = await llm_service.extract_insights(request.transcript)
        
        # Persist to database
        record_id, unique_id = await db_service.insert_call_record(
            transcript=request.transcript,
            insights=insights,
            metadata=request.metadata
        )
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return CallResponse(
            id=record_id,
            unique_id=unique_id,
            customer_intent=insights.customer_intent,
            sentiment=insights.sentiment,
            action_required=insights.action_required,
            summary=insights.summary,
            raw_transcript=request.transcript,
            processing_time_ms=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )



# =============================================================================
# TESTING WITH SAMPLE TRANSCRIPTS
# =============================================================================

# Transcript #1 (Pre-Due, Positive)
# curl -X POST "http://localhost:8000/analyze_call" \\
#   -H "Content-Type: application/json" \\
#   -d '{"transcript": "Agent: Hello, main Maya bol rahi hoon, Apex Finance se. Kya main Mr. Sharma se baat kar sakti hoon? Customer: Haan, main bol raha hoon. Kya hua? Agent: Sir, aapka personal loan ka EMI due date 3rd of next month hai. Just calling for a friendly reminder. Aapka payment ready hai na? Customer: Oh, okay. Haan, salary aa jayegi tab tak. I will definitely pay it on time, don't worry. Agent: Thank you, sir. Payment time pe ho jaye toh aapka credit score bhi maintain rahega. Have a good day!"}'

# Transcript #3 (Post-Due, PTP)
# curl -X POST "http://localhost:8000/analyze_call" \\
#   -H "Content-Type: application/json" \\
#   -d '{"transcript": "Agent: Hello Mr. Verma, main Aman bol raha hoon. Aapka personal loan EMI 7 days se overdue hai. Aapne payment kyun nahi kiya? Customer: Dekhiye, thoda emergency aa gaya tha. Mera bonus expected hai next week. Agent: Sir, aapko pata hai ki is par penalty lag rahi hai. Aap exact date bataiye, kab tak confirm payment ho jayega? Customer: Wednesday ko pakka kar dunga. Promise to Pay (PTP) le lo Wednesday ka. Agent: Okay, main aapka PTP book kar raha hoon next Wednesday ke liye. Please ensure payment is done to stop further charges."}'

# Transcript #10 (Hardship)
# curl -X POST "http://localhost:8000/analyze_call" \\
#   -H "Content-Type: application/json" \\
#   -d '{"transcript": "Agent: Ms. Pooja, hum aapko 75 days se call kar rahe hain. Aap cooperate nahi kar rahe. Customer: Meri mother hospital mein hain. Serious financial hardship hai. I am requesting a restructuring of the loan. Agent: Ma'am, we understand the situation. Lekin restructuring ke liye aapko hardship application fill karni hogi aur last 3 months ka bank statement dena hoga. Customer: Okay, send me the form."}'