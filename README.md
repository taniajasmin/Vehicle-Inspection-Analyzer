# Vehicle Inspection Analyzer

Vehicle Inspection Analyzer is an AI-powered backend service that analyzes **vehicle inspection reports** (PDFs or images) using **OpenAI GPT-4o**.  
It automatically detects whether the file contains searchable text or scanned images, then extracts insights such as condition summary, risks, and maintenance recommendations.

---

## System Overview

Below is the flowchart representing the process pipeline of **Vehicle Inspection Analyzer**:

<img width="373" height="724" alt="Image" src="https://github.com/user-attachments/assets/89f3fb49-e688-43e3-ba11-64f46177a90c" />

---

## Project Structure

```text
Vehicle Inspection Analyzer/
│
├── main.py                 # FastAPI backend for vehicle report analysis
├── generate_report.py      # Standalone script (non-API version)
│
├── output/
│   └── car_condition_report.json  # Saved AI report (if enabled)
│
├── .env                    # Environment variables (API keys, config)
├── requirements.txt        # Python dependencies
├── scanno_ai.log           # Log file for analysis activity
├── readme.txt
└── README.md               # This file
```


---

## Features

- Upload **PDF** or **image** (JPG, PNG) of vehicle inspection reports  
- Automatically detects **scanned vs. text PDFs**  
- Uses **GPT-4o Vision** for scanned reports and **GPT-4o Text** for searchable ones  
- Returns **structured JSON output**:

```json
{
  "summary": "1-line car condition",
  "risk_level": "Low|Medium|High|Critical",
  "issues": ["list of detected problems"],
  "maintenance": ["recommended actions"],
  "recommendation": "final verdict"
}
```
- Ready to integrate into web or mobile frontends
- Built-in retry, error logging, and JSON validation


---

## Backend Development Setup
###1. Install Dependencies
``` bash
pip install -r requirements.txt
```

### 2. Create .env File
Create a .env file in the project root:
```text
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run FastAPI Backend
```bash
uvicorn main:app --reload
```
The backend runs on: http://127.0.0.1:8000

---

### 4. Test the API
**Using Swagger UI**
Go to:
http://127.0.0.1:8000/docs
Upload your PDF or image under the /analyze-report endpoint and click Execute.

**Example of pdf upload and image uploads

|<img width="492" height="833" alt="Image" src="https://github.com/user-attachments/assets/432f7853-b012-417a-9fde-e4ffe64680d4" />|<img width="456" height="720" alt="Image" src="https://github.com/user-attachments/assets/8742d487-fadb-48f4-a3b5-a9ef851fce19" />|img width="492" height="840" alt="Image" src="https://github.com/user-attachments/assets/889800d6-8a13-4b8e-bcf4-734446e6410c" />|

## Notes 

- Only main.py, requirements.txt, and .env are required for backend deployment.
- generate_report.py can be used for offline testing or debugging without FastAPI.
- Logs are saved automatically to scanno_ai.log in the root folder.
- Logging can be modified or disabled via logging.basicConfig in main.py.


## Summary:
- AI backend is production-ready.
- Just run uvicorn backend_ai.py:app --reload and integrate.
