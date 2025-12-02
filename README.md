📋 Conversational Insights Generator

A production-grade API that analyzes customer service call transcripts (in Hinglish) and automatically extracts:

Customer Intent — What the customer wants

Sentiment — Positive / Neutral / Negative classification

Action Required — Whether follow-up is needed

Summary — Short overview of the call

Optimized for debt collection workflows (PTPs, disputes, hardship, etc.)

✨ Features

🤖 AI-Powered insights using Google Gemini (gemini-2.0-flash)

📊 Structured JSON Output validated with Pydantic

💾 PostgreSQL persistence with transactions

🔄 Auto Retry Logic (3 attempts) for LLM calls

⚡ Fully asynchronous (asyncio + AsyncPG)

🔐 Connection Pooling for scalability

📈 /health endpoint for live monitoring

📚 Interactive Swagger UI

🧩 End-to-end validation

🛠 Tech Stack
Component	Technology	Purpose
Framework	FastAPI 0.100+	Async API framework
Database	PostgreSQL 12+	Data persistence
DB Driver	AsyncPG 0.28+	Async database operations
AI Model	Google Gemini API	Insight extraction
Validation	Pydantic 2.0+	Data model enforcement
Server	Uvicorn	ASGI server
Language	Python 3.9+	Backend implementation
📦 Installation
Prerequisites

Python 3.9+

PostgreSQL 12+

Gemini API Key

1️⃣ Clone the repository
git clone https://github.com/atharva9604/conversational-insights-generator.git
cd conversational-insights-generator

2️⃣ Create virtual environment
python -m venv venv


Activate it:

source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE insights_db;"

5️⃣ Configure Environment Variables
cp .env.example .env
nano .env


Add:

GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/insights_db

6️⃣ Run the Application
uvicorn main:app --reload

🌐 API Access
Resource	URL
Swagger Docs	http://localhost:8000/docs

Health Check	http://localhost:8000/health
🚀 Usage
Example Request
curl -X POST "http://localhost:8000/analyze_call" \
-H "Content-Type: application/json" \
-d '{
  "transcript": "Agent: Hello, main Maya bol rahi hoon..."
}'

Example Response
{
  "id": 1,
  "unique_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "customer_intent": "Payment Commitment - Salary Date",
  "sentiment": "Positive",
  "action_required": false,
  "summary": "Pre-due reminder for EMI...",
  "raw_transcript": "Agent: Hello...",
  "processed_at": "2025-12-01T10:30:45.123456",
  "processing_time_ms": 1247.52
}

📊 Endpoints
Method	Endpoint	Description
POST	/analyze_call	Analyze transcript & store results
GET	/health	System health
GET	/	Base info
GET	/docs	Swagger UI
🗄 Database Schema
CREATE TABLE call_records (
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

-- Indexes
CREATE INDEX idx_call_records_sentiment ON call_records(sentiment);
CREATE INDEX idx_call_records_action_required ON call_records(action_required);
CREATE INDEX idx_call_records_created_at ON call_records(created_at DESC);

🧪 Testing
Health Check
curl http://localhost:8000/health

Sample Inputs

Positive sentiment:

curl -X POST "http://localhost:8000/analyze_call" \
-H "Content-Type: application/json" \
-d '{"transcript": "Yes, will pay on time!"}'


PTP (Neutral):

-d '{"transcript": "Emergency tha, Wednesday ko pakka karunga."}'


Negative / Hardship:

-d '{"transcript": "Financial hardship hai, restructuring chahiye."}'


Check DB records:

SELECT id, sentiment, action_required FROM call_records ORDER BY created_at DESC;

🏗 Project Structure
conversational-insights-generator/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── venv/

🔒 Security

API keys secured via .env

SQL injection protection via parameterized queries

CORS support for production

Never commit .env

🐛 Troubleshooting
Issue	Fix
Module not found	pip install -r requirements.txt
PostgreSQL refusal	sudo service postgresql start / brew services start postgresql
Invalid API key	Generate new Gemini key
DB missing	CREATE DATABASE insights_db;
📈 Performance

⏱ 1–3 sec processing time per transcript

🔁 Automated retries

🔗 Connection pooling (5–20 connections)

⚙️ Supports concurrent requests
