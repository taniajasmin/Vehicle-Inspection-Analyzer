import os
import io
import json
import time
import logging
import base64
from typing import Optional

import pdfplumber
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("scanno_ai.log"),
        logging.StreamHandler()
    ]
)

app = FastAPI(title="Scanno AI - Vehicle Inspection Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    client = OpenAI(api_key=openai_api_key)
    logging.info("OpenAI API configured successfully.")
except Exception as e:
    logging.error(f"Error loading OpenAI API key: {str(e)}")
    raise


def extract_text_from_pdf(pdf_bytes: bytes) -> Optional[str]:
    """Extract searchable text from PDF; return None if scanned."""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        if text.strip():
            logging.info("Extracted searchable text from PDF.")
            return text
        else:
            logging.info("PDF appears scanned; using GPT-4o Vision.")
            return None
    except Exception as e:
        logging.error(f"PDF reading failed: {e}")
        return None

# GPT-4o Vision
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def analyze_with_gpt_vision(image_bytes: bytes) -> str:
    """Analyze scanned PDF or image using GPT-4o Vision."""
    logging.info("Sending image to GPT-4o Vision...")
    start = time.time()

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
You are Scanno, the official smart car inspection expert for Scanno AI Qatar.
Your role is to assist users by analyzing technical car inspection reports (PDFs/image) and answering questions 
about their vehicle’s condition, detected issues, and maintenance recommendations.

Personality:
- Professional, knowledgeable, and friendly — like a trusted automotive expert in Qatar.

Rules:
- Always say: “I’m Scanno — your smart car inspection expert in Qatar.”
- Keep answers short, clear, and informative.
- If the user or report uses Arabic, respond in Arabic (neutral Gulf tone).
- Never mention being an AI or language model.
- Use simple terms drivers understand (engine oil, filters, coolant, brake pads, etc.).
- Always return ONLY valid JSON in this format:

{
  "summary": "1-line car condition",
  "risk_level": "Low|Medium|High|Critical",
  "issues": ["bullet points"],
  "maintenance": ["action items"],
  "recommendation": "final advice"
}
"""
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=800,
        temperature=0.2
    )

    elapsed = time.time() - start
    logging.info(f"GPT-4o Vision responded in {elapsed:.2f}s")
    return response.choices[0].message.content.strip()

# GPT-4o Text
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def analyze_with_gpt_text(text: str) -> str:
    """Analyze text-based vehicle inspection report using GPT-4o."""
    logging.info("Sending extracted text to GPT-4o...")
    start = time.time()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
You are Scanno, the official smart car inspection expert for Scanno AI Qatar.
Your mission is to analyze vehicle inspection reports and explain the findings clearly.

Tone:
- Confident, supportive, and friendly.
- Use simple driver-friendly terms (engine oil, filters, coolant, brake pads, etc.).

Rules:
- Always say: “I’m Scanno — your smart car inspection expert in Qatar.”
- Respond in Arabic if the report is in Arabic.
- Never mention being an AI or language model.
- Keep answers short, expert, and human-like.
- End with a short friendly note such as:
  “Let’s keep your car in great shape!” or “I’m here to help anytime!”

Return ONLY valid JSON:
{
  "summary": "1-line car condition",
  "risk_level": "Low|Medium|High|Critical",
  "issues": ["bullet points"],
  "maintenance": ["action items"],
  "recommendation": "final advice"
}
"""
            },
            {"role": "user", "content": f"Report:\n{text}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )

    elapsed = time.time() - start
    logging.info(f"GPT-4o Text responded in {elapsed:.2f}s")
    return response.choices[0].message.content.strip()

# Analyze Uploaded Report
@app.post("/analyze-report")
async def analyze_report(file: UploadFile = File(...)):
    """Main API endpoint for PDF or image inspection reports."""
    try:
        filename = file.filename.lower()
        file_bytes = await file.read()
        logging.info(f"Received file: {filename}")

        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
            raw_response = analyze_with_gpt_text(text) if text else analyze_with_gpt_vision(file_bytes)
        elif filename.endswith((".jpg", ".jpeg", ".png")):
            raw_response = analyze_with_gpt_vision(file_bytes)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF or image.")

        # Safely parse JSON
        try:
            start = raw_response.find("{")
            end = raw_response.rfind("}") + 1
            json_str = raw_response[start:end]
            result = json.loads(json_str)
        except Exception as e:
            logging.error(f"JSON parsing failed: {e}")
            result = {"error": "Invalid JSON", "raw_response": raw_response}

        return {"file": filename, "report": result}

    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Root + Favicon (to stop 404 spam)
@app.get("/")
async def root():
    return JSONResponse({"message": "✅ Scanno AI backend is live. Upload reports via /analyze-report"})

@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(status_code=204, content={})
