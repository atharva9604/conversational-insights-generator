Here’s a simple `README.md` in the same style as your example, tailored to **your code + structure**:

````markdown
# Conversational Insights Generator  
FastAPI + Gemini + PostgreSQL (Single-File Submission)

This project is a complete end-to-end pipeline that analyzes **debt-collection call transcripts** using Google’s Gemini API and stores **structured insights** in PostgreSQL.

---

## 🚀 What the API Does

- Accepts a raw **Hinglish customer service call transcript**
- Sends it to **Gemini 2.0 Flash** using a strict JSON schema
- Extracts:
  - `customer_intent`
  - `sentiment` (`"Negative" | "Neutral" | "Positive"`)
  - `action_required` (boolean)
  - `summary`
- Validates everything via **Pydantic**
- Stores insights in PostgreSQL table **`call_records`**
- Returns a JSON response:

```json
{
  "id": 1,
  "unique_id": "uuid",
  "customer_intent": "...",
  "sentiment": "Positive",
  "action_required": false,
  "summary": "...",
  "raw_transcript": "...",
  "processed_at": "2025-12-01T10:30:45.123456",
  "processing_time_ms": 1234.56
}
````

All main logic is inside **`main.py`**.

---

## ⚙️ Technology Stack

| Layer    | Technology                         |
| -------- | ---------------------------------- |
| API      | FastAPI                            |
| LLM      | Google Gemini (`gemini-2.0-flash`) |
| Database | PostgreSQL + `asyncpg`             |
| Models   | Pydantic                           |
| Runtime  | Uvicorn                            |
| Env Mgmt | `python-dotenv`                    |

---

## 🔧 Setup Instructions

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Create PostgreSQL database

Example:

```sql
CREATE DATABASE insights_db;
```

### 3️⃣ Configure `.env`

Create a file named `.env` in the project root (you can use `.env.example` as a template):

```env
DATABASE_URL=postgresql://postgres:<yourpassword>@localhost:5432/insights_db
GEMINI_API_KEY=<your-gemini-api-key>
```

> Both `GEMINI_API_KEY` and `DATABASE_URL` are **required**.
> The app will fail fast if they are missing.

---

## ▶️ Run the API

Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

If startup is successful, you’ll see logs like:

```text
✓ LLM service initialized
✓ Database connected and schema initialized
✅ Application Ready!
```

---

## 🧪 Test Using Swagger UI / curl

Swagger UI:

> 👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Using Swagger

1. Open `POST /analyze_call`
2. Click **Try it out**
3. Example body:

```json
{
  "transcript": "Agent: Hello, main Maya bol rahi hoon, Apex Finance se. Kya main Mr. Sharma se baat kar sakti hoon? Customer: Haan, main bol raha hoon. Salary aayegi next week, tab payment karunga."
}
```

4. Click **Execute**
5. You should see a structured JSON response with `customer_intent`, `sentiment`, `action_required`, and `summary`.

### Using curl

```bash
curl -X POST "http://127.0.0.1:8000/analyze_call" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Agent: Hello... Customer: I will pay next week when salary comes."
  }'
```

---

## 🗃 View Stored Insights in SQL

The app creates a table called `call_records` (if not present) and inserts one row per analyzed call.

Example query:

```sql
SELECT
  id,
  unique_id,
  transcript,
  intent,
  sentiment,
  action_required,
  summary,
  created_at
FROM call_records
ORDER BY created_at DESC;
```

This is the same data used if you later export to a CSV like:

> `call_records_insights_samples.csv`

---

## 📁 Project Structure (Local)

```text
.
├── .env                # Local environment variables (not committed)
├── .env.example        # Sample env file
├── .gitignore
├── main.py             # Main FastAPI + Gemini + DB code
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── Predixion AI Assignment Report.pdf  # Final report (optional)
└── .venv / __pycache__ etc.           # Local environment / cache
```

---

## 🎥 Video Demonstration

YouTube link (demo of API + DB pipeline):

> ▶️ [https://youtu.be/](https://youtu.be/)<your-video-id>

*(Replace with your actual link once uploaded.)*

---

## 📘 Final Project Report

* Detailed explanation of design, prompts, DB schema, and sample outputs is included in:
  **`Predixion AI Assignment Report.pdf`**

```

If you want, I can also give you a **tiny version** (like 10–12 lines) for classroom portals that limit README size.
```
