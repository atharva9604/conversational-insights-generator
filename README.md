📋 Overview
This production-grade API analyzes customer service call transcripts (in Hinglish) and automatically extracts:

Customer Intent: What the customer wants to achieve
Sentiment: Positive, Neutral, or Negative classification
Action Required: Whether follow-up is needed
Summary: Concise overview of the conversation

Built for debt collection scenarios with support for PTPs, disputes, hardship requests, and more.

✨ Features

🤖 AI-Powered Analysis using Google Gemini (gemini-2.0-flash)
📊 Structured JSON Output with Pydantic validation
💾 PostgreSQL Persistence with transaction safety
🔄 Automatic Retry Logic (3 attempts) for reliability
⚡ Fully Asynchronous using asyncio and AsyncPG
🔐 Connection Pooling for high performance
📈 Health Check Endpoint for monitoring
📚 Interactive API Documentation (Swagger UI)
✅ Comprehensive Validation at every layer


🛠 Tech Stack
ComponentTechnologyPurposeFrameworkFastAPI 0.100+High-performance async web frameworkDatabasePostgreSQL 12+Reliable data persistenceDB DriverAsyncPG 0.28+Async PostgreSQL clientAIGoogle Gemini APILLM for insight extractionValidationPydantic 2.0+Data validation and settingsServerUvicornASGI serverLanguagePython 3.9+Backend implementation

📦 Installation
Prerequisites

Python 3.9 or higher
PostgreSQL 12 or higher
Google Gemini API key (Get one here)

Setup

Clone the repository

bash   git clone https://github.com/yourusername/conversational-insights-generator.git
   cd conversational-insights-generator

Create virtual environment

bash   python -m venv venv
   
   # Activate it
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows

Install dependencies

bash   pip install -r requirements.txt

Create PostgreSQL database

bash   psql -U postgres -c "CREATE DATABASE insights_db;"

Configure environment variables

bash   # Copy example file
   cp .env.example .env
   
   # Edit with your credentials
   nano .env
Add your credentials:
bash   GEMINI_API_KEY=your_gemini_api_key_here
   DATABASE_URL=postgresql://postgres:password@localhost:5432/insights_db

Run the application

bash   uvicorn main:app --reload

Access the API

API Docs: http://localhost:8000/docs
Health Check: http://localhost:8000/health




🚀 Usage
Example Request
bashcurl -X POST "http://localhost:8000/analyze_call" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Agent: Hello, main Maya bol rahi hoon, Apex Finance se. Kya main Mr. Sharma se baat kar sakti hoon? Customer: Haan, main bol raha hoon. Kya hua? Agent: Sir, aapka personal loan ka EMI due date 3rd of next month hai. Just calling for a friendly reminder. Aapka payment ready hai na? Customer: Oh, okay. Haan, salary aa jayegi tab tak. I will definitely pay it on time, don't worry. Agent: Thank you, sir. Payment time pe ho jaye toh aapka credit score bhi maintain rahega. Have a good day!"
  }'
Example Response
json{
  "id": 1,
  "unique_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "customer_intent": "Payment Commitment - Salary Date",
  "sentiment": "Positive",
  "action_required": false,
  "summary": "Pre-due reminder for personal loan EMI due on 3rd of next month. Customer confirmed payment will be made on time when salary arrives. No further action needed.",
  "raw_transcript": "Agent: Hello, main Maya...",
  "processed_at": "2025-12-01T10:30:45.123456",
  "processing_time_ms": 1247.52
}

📊 API Endpoints
POST /analyze_call
Analyze a call transcript and extract structured insights.
Request Body:
json{
  "transcript": "Agent: ... Customer: ...",
  "metadata": {  // Optional
    "call_id": "CALL_001",
    "agent_id": "AGT_123"
  }
}
GET /health
Check system health status.
Response:
json{
  "status": "healthy",
  "database": "connected",
  "llm_client": "initialized",
  "timestamp": "2025-12-01T10:30:45.123456"
}
GET /
Get API information and available endpoints.
GET /docs
Interactive API documentation (Swagger UI).

🗄 Database Schema
sqlCREATE TABLE call_records (
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

-- Performance indexes
CREATE INDEX idx_call_records_sentiment ON call_records(sentiment);
CREATE INDEX idx_call_records_action_required ON call_records(action_required);
CREATE INDEX idx_call_records_created_at ON call_records(created_at DESC);

🧪 Testing
Health Check
bashcurl http://localhost:8000/health
Test with Sample Transcript
bash# Positive Sentiment
curl -X POST "http://localhost:8000/analyze_call" \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Agent: Payment reminder. Customer: Yes, will pay on time!"}'

# Neutral Sentiment (PTP)
curl -X POST "http://localhost:8000/analyze_call" \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Agent: Payment overdue. Customer: Emergency tha, Wednesday ko pakka karunga."}'

# Negative Sentiment (Hardship)
curl -X POST "http://localhost:8000/analyze_call" \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Agent: 75 days overdue. Customer: Financial hardship hai, restructuring chahiye."}'
Verify Database
sql-- Connect to database
psql -U postgres -d insights_db

-- View records
SELECT id, sentiment, action_required, created_at 
FROM call_records 
ORDER BY created_at DESC;

-- Sentiment distribution
SELECT sentiment, COUNT(*) 
FROM call_records 
GROUP BY sentiment;

🏗 Project Structure
conversational-insights-generator/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── venv/               # Virtual environment (not committed)

🔒 Security

✅ API keys stored in .env file (never committed)
✅ Environment variables loaded via python-dotenv
✅ Database credentials secured
✅ SQL injection prevention via parameterized queries
✅ Input validation at multiple layers
✅ CORS can be configured for production

⚠️ Important: Never commit .env file or expose API keys!

🐛 Troubleshooting
"Module not found" error
bashpip install -r requirements.txt
"Connection refused" to PostgreSQL
bash# Start PostgreSQL
sudo service postgresql start  # Linux
brew services start postgresql  # Mac
"Invalid API key"

Get a new key from https://ai.google.dev/
Update .env file with correct key

"Database does not exist"
bashpsql -U postgres -c "CREATE DATABASE insights_db;"

📈 Performance

Average Processing Time: 1-3 seconds per transcript
Concurrent Requests: Supported via connection pooling
Retry Logic: 3 attempts for LLM failures
Database Connections: Pool of 5-20 connections


