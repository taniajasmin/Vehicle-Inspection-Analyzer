import os
import io
import json
import time
import logging
from pathlib import Path
from PIL import Image
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('scanno_ai.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()

try:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    client = OpenAI(api_key=openai_api_key)
    logging.info("OpenAI API configured successfully.")
except Exception as e:
    logging.error(f"Error loading OpenAI API key: {str(e)}")
    exit(1)

def pick_file() -> Path:
    logging.info("Opening file picker...")
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        title="Select Vehicle Inspection Report (PDF / Image)",
        filetypes=[
            ("PDF & Images", "*.pdf *.jpg *.jpeg *.png"),
            ("PDF", "*.pdf"),
            ("Images", "*.jpg *.jpeg *.png")
        ]
    )
    root.destroy()
    if not file_path:
        logging.info("No file selected – exiting.")
        exit(0)
    return Path(file_path)


def extract_text_from_pdf(pdf_path: Path) -> str | None:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        if text.strip():
            logging.info("Extracted searchable text from PDF.")
            return text
        else:
            logging.info("PDF is scanned – will use GPT-4o Vision.")
            return None
    except Exception as e:
        logging.error(f"PDF reading failed: {e}")
        return None

# GPT-4o VISION (IMAGE / SCANNED PDF)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def analyze_with_gpt_vision(image_bytes: bytes) -> str:
    """Send image to GPT-4o (vision) and get JSON report."""
    try:
        logging.info("Sending image to GPT-4o Vision...")
        start = time.time()

        # Convert to base64
        import base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
You are Scanno, a senior vehicle inspection engineer in Qatar.
Use English or Arabic based on user preference.
Analyze the vehicle inspection report in the image and return ONLY valid JSON:

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
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800,
            temperature=0.2
        )
        elapsed = time.time() - start
        result = response.choices[0].message.content.strip()
        logging.info(f"GPT-4o Vision responded in {elapsed:.2f}s")
        return result
    except Exception as e:
        logging.error(f"GPT-4o Vision error: {e}")
        raise

# GPT-4o TEXT (Searchable PDF)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def analyze_with_gpt_text(text: str) -> str:
    try:
        logging.info("Sending extracted text to GPT-4o...")
        start = time.time()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Scanno, a senior vehicle inspection engineer in Qatar."},
                {"role": "user", "content": f"""
Analyze this vehicle inspection report and return ONLY valid JSON:

{{
  "summary": "1-line car condition",
  "risk_level": "Low|Medium|High|Critical",
  "issues": ["bullet points"],
  "maintenance": ["action items"],
  "recommendation": "final advice"
}}

Report:
{text}
"""}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        elapsed = time.time() - start
        result = response.choices[0].message.content.strip()
        logging.info(f"GPT-4o Text responded in {elapsed:.2f}s")
        return result
    except Exception as e:
        logging.error(f"GPT-4o Text error: {e}")
        raise

# SAVE REPORT 
def save_report(result: dict, source_file: Path):
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "car_condition_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    logging.info(f"Report saved: {out_file}")


def main():
    logging.info("Scanno AI – Vehicle Inspection Analyzer")
    file_path = pick_file()
    logging.info(f"Selected file: {file_path}")

    result = None

    # PDF 
    if file_path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(file_path)
        if text:
            raw_response = analyze_with_gpt_text(text)
        else:
            # Scanned PDF → use vision
            with open(file_path, "rb") as f:
                image_bytes = f.read()
            raw_response = analyze_with_gpt_vision(image_bytes)

    # IMAGE
    else:
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        raw_response = analyze_with_gpt_vision(image_bytes)

    # Parse JSON
    try:
        # Clean response (remove markdown if any)
        start = raw_response.find("{")
        end = raw_response.rfind("}") + 1
        json_str = raw_response[start:end]
        result = json.loads(json_str)
    except Exception as e:
        logging.error(f"Failed to parse JSON: {e}\nRaw:\n{raw_response}")
        result = {"error": "Invalid JSON", "raw_response": raw_response}

    save_report(result, file_path)
    print("\n" + "="*60)
    print("AI CAR CONDITION REPORT:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("="*60)

if __name__ == "__main__":
    main()