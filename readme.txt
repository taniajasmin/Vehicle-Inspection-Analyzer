# Scanno AI Backend  
**Secure, JSON-only AI Analysis Engine for Vehicle Inspection Reports**

---

## Overview
This is the **AI backend** for Scanno — a vehicle inspection assistant.  
It receives **extracted report text** (from PDF or image OCR) via JSON and returns **structured professional analysis** using **GPT-4o**.

**No files are uploaded. No data is stored. 100% privacy.**

---
## Flowchart






---

## File Structure
```bash
├── backend_ai.py          ← Main FastAPI server (single file)
├── .env                   ← Your OpenAI key (never commit!)
└──requirements.txt       ← Python dependencies

text---

## Features
| Feature | Status |
|-------|--------|
| JSON Input/Output | Yes |
| GPT-4o Analysis | Yes |
| Fixed Professional Prompt | Yes |
| No File Storage | Yes |
| CORS Enabled | Yes |
| `.env` Key Loading | Yes |
| cURL / Frontend Ready | Yes |

---

## Setup (One-Time)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
2. Create .env
```bash
OPENAI_API_KEY=sk-your-real-key-here

## Run the Server
```bash
uvicorn backend_ai.py:app --reload --port=8000

**Server runs at:** http://localhost:8000
Interactive docs: http://localhost:8000/docs

## API Endpoint
### POST /analyze
**Request (JSON)**
```json
{
  "report_text": "Engine oil low. Brake pads 20%. Tire tread 3mm.",
  "user_query": "Should I buy this car?"
}
```
**Response (JSON)**
```json
{
  "summary": "Engine oil is low and brakes are worn.",
  "risk_level": "Medium",
  "issues": [
    "Engine oil level is below recommended.",
    "Brake pads are at 20% efficiency."
  ],
  "maintenance": [
    "Refill engine oil to the appropriate level.",
    "Replace brake pads to ensure optimal braking performance."
  ],
  "recommendation": "Address the issues before driving long distances; short trips may be manageable with caution."
}
```

**Test with cURL**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "report_text": "Engine oil low. Brakes 20%.",
    "user_query": "Is it safe?"
  }'
```

## For Frontend Developers

- Send only text — no files.
- Use fetch or axios:
```js
const res = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    report_text: extractedText,
    user_query: 'Analyze this'
  })
});
const data = await res.json();
```

## Security & Privacy

| Feature                     | Implemented |
|----------------------------|-------------|
| No file upload to server   | Yes         |
| No report text logging     | Yes         |
| API key stored in `.env`   | Yes         |
| CORS enabled (`*`)         | Yes (restrict in production) |
| Client-side OCR & PDF processing | Yes (handled by frontend) |
| No persistent storage      | Yes         |

> **Privacy by Design**: Only extracted **text** is sent. Nothing is saved.


## Summary:
- AI backend is production-ready.
- Just run uvicorn backend_ai.py:app --reload and integrate.
