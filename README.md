# 📋 Conversational Insights Generator

A **production-grade** API that analyzes customer service call transcripts (in Hinglish) and automatically extracts:

- **Customer Intent** – What the customer wants to achieve  
- **Sentiment** – `Positive`, `Neutral`, or `Negative`  
- **Action Required** – Whether follow-up is needed  
- **Summary** – Concise overview of the conversation  

Optimized for **debt collection scenarios** with support for:

- Promise to Pay (PTP)
- Disputes
- Hardship / restructuring requests
- General pre-due and post-due reminder calls

---

## ✨ Features

- 🤖 **AI-Powered Analysis** using Google Gemini (`gemini-2.0-flash`)
- 📊 **Structured JSON Output** with Pydantic validation
- 💾 **PostgreSQL Persistence** with transaction safety
- 🔄 **Automatic Retry Logic** (3 attempts) for reliability
- ⚡ Fully **asynchronous** using `asyncio` and `asyncpg`
- 🔐 **Connection Pooling** for high performance
- 📈 `/health` **Health Check Endpoint** for monitoring
- 📚 **Interactive API Documentation** (Swagger UI via FastAPI)
- ✅ **Comprehensive validation** at every layer

---

## 🛠 Tech Stack

| Component  | Technology         | Purpose                               |
|-----------|--------------------|---------------------------------------|
| Framework | FastAPI 0.100+     | High-performance async web framework  |
| Database  | PostgreSQL 12+     | Reliable data persistence             |
| DB Driver | AsyncPG 0.28+      | Async PostgreSQL client               |
| AI        | Google Gemini API  | LLM for insight extraction            |
| Validation| Pydantic 2.0+      | Data validation and settings          |
| Server    | Uvicorn            | ASGI server                           |
| Language  | Python 3.9+        | Backend implementation                |

---

## 📦 Installation

### Prerequisites

- Python **3.9+**
- PostgreSQL **12+**
- Google Gemini API key

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/atharva9604/conversational-insights-generator.git
cd conversational-insights-generator
2️⃣ Create Virtual Environment
bash
Copy code
python -m venv venv
Activate it:

bash
Copy code
# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Create PostgreSQL Database
bash
Copy code
psql -U postgres -c "CREATE DATABASE insights_db;"
5️⃣ Configure Environment Variables
Copy the example env file:

bash
Copy code
cp .env.example .env
Edit .env:

bash
Copy code
nano .env
Add your credentials:

env
Copy code
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/insights_db
6️⃣ Run the Application
bash
Copy code
uvicorn main:app --reload
🌐 API Access
Once the server is running:

API Docs (Swagger UI): http://localhost:8000/docs

Health Check: http://localhost:8000/health

Root Info: http://localhost:8000/

🚀 Usage
Example Request
bash
Copy code
curl -X POST "http://localhost:8000/analyze_call" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Agent: Hello, main Maya bol rahi hoon, Apex Finance se. Kya main Mr. Sharma se baat kar sakti hoon? Customer: Haan, main bol raha hoon. Kya hua? Agent: Sir, aapka personal loan ka EMI due date 3rd of next month hai. Just calling for a friendly reminder. Aapka payment ready hai na? Customer: Oh, okay. Haan, salary aa jayegi tab tak. I will definitely pay it on time, dont worry. Agent: Thank you, sir. Payment time pe ho jaye toh aapka credit score bhi maintain rahega. Have a good day!"
  }'
Example Response
json
Copy code
{
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

json
Copy code
{
  "transcript": "Agent: ... Customer: ...",
  "metadata": {
    "call_id": "CALL_001",
    "agent_id": "AGT_123"
  }
}
metadata is optional and stored as JSONB in the database.

GET /health
Check system health status.

Response:

json
Copy code
{
  "status": "healthy",
  "database": "connected",
  "llm_client": "initialized",
  "timestamp": "2025-12-01T10:30:45.123456"
}
Other Endpoints
GET / – Basic API information

GET /docs – Interactive API documentation (Swagger UI)

🗄 Database Schema
sql
Copy code
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

-- Performance indexes
CREATE INDEX idx_call_records_sentiment
    ON call_records (sentiment);

CREATE INDEX idx_call_records_action_required
    ON call_records (action_required);

CREATE INDEX idx_call_records_created_at
    ON call_records (created_at DESC);
🧪 Testing
Health Check
bash
Copy code
curl http://localhost:8000/health
Sample Transcripts
Positive Sentiment

bash
Copy code
curl -X POST "http://localhost:8000/analyze_call" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Agent: Payment reminder. Customer: Yes, will pay on time!"
  }'
Neutral (PTP)

bash
Copy code
curl -X POST "http://localhost:8000/analyze_call" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Agent: Payment overdue. Customer: Emergency tha, Wednesday ko pakka karunga."
  }'
Negative (Hardship)

bash
Copy code
curl -X POST "http://localhost:8000/analyze_call" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Agent: 75 days overdue. Customer: Financial hardship hai, restructuring chahiye."
  }'
Verify Database Records
sql
Copy code
-- View records
SELECT id, sentiment, action_required, created_at
FROM call_records
ORDER BY created_at DESC;

-- Sentiment distribution
SELECT sentiment, COUNT(*)
FROM call_records
GROUP BY sentiment;
🏗 Project Structure
text
Copy code
conversational-insights-generator/
├── main.py          # Main application file
├── requirements.txt # Python dependencies
├── .env.example     # Environment variables template
├── .gitignore       # Git ignore rules
├── README.md        # Project documentation
└── venv/            # Virtual environment (not committed)
🔒 Security
✅ API keys stored in .env (never committed)

✅ Environment variables loaded via python-dotenv

✅ Database credentials not hard-coded

✅ SQL injection prevention via parameterized queries

✅ Input validation at multiple layers

✅ CORS can be configured for production

⚠️ Important: Never commit .env file or expose API keys.

🐛 Troubleshooting
1. "Module not found"

bash
Copy code
pip install -r requirements.txt
2. "Connection refused" to PostgreSQL

bash
Copy code
# Linux
sudo service postgresql start

# macOS (Homebrew)
brew services start postgresql
3. "Invalid API key"

Get a new key from: https://ai.google.dev/

Update .env with the correct key.

4. "Database does not exist"

bash
Copy code
psql -U postgres -c "CREATE DATABASE insights_db;"
📈 Performance
⏱ Average processing time: 1–3 seconds per transcript

🔁 Retry Logic: 3 attempts for LLM failures

🔗 Database connections via connection pooling (e.g. 5–20 connections)

🌐 Supports concurrent requests via async I/O
