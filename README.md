# Vehicle Inspection Analyzer

Vehicle Inspection Analyzer is an AI-powered backend service that analyzes **vehicle inspection reports** (PDFs or images) using **OpenAI GPT-4o**.  
It automatically detects whether the file contains searchable text or scanned images, then extracts insights such as condition summary, risks, and maintenance recommendations.

---

## System Overview

Below is the flowchart representing the process pipeline of **Vehicle Inspection Analyzer**:

<img width="200" alt="System Flowchart" src="https://github.com/user-attachments/assets/89f3fb49-e688-43e3-ba11-64f46177a90c" />

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

#### Example Uploads (PDF & Images)

| **PDF Report** | **Scanned Image** |
|----------------|-------------------|
| <img width="180" alt="PDF Example" src="https://github.com/user-attachments/assets/432f7853-b012-417a-9fde-e4ffe64680d4" /> | <img width="180" alt="Scanned Image" src="https://github.com/user-attachments/assets/8742d487-fadb-48f4-a3b5-a9ef851fce19" /> |

## Notes 

- Only main.py, requirements.txt, and .env are required for backend deployment.
- Example reports folder has both pdf and images of Vehicle Inspection reports. Use it for testing.
- generate_report.py can be used for testing or debugging without FastAPI.
- Logs are saved automatically to scanno_ai.log in the root folder.
- Logging can be modified or disabled via logging.basicConfig in main.py.

## Limitations

Scanno AI is optimized for accuracy and performance, but the following limitations apply:
- Supported Files: Only .pdf, .jpg, .jpeg, and .png files are accepted.
- File Size: Large reports (≈50 MB +) may fail or timeout due to API limits.
- Token Limit: gpt-4o supports up to ~128k tokens (~300 pages). Very long reports should be summarized in chunks.
- Retries: Each request retries up to 3 times on network/API failure.
- No Memory: Every request is stateless; Scanno does not store or recall previous uploads.
- Fixed Personality: Scanno always speaks as “your smart car inspection expert in Qatar.” Behavior and tone are not configurable.
- Local Logging: Logs are written to scanno_ai.log; persistent storage depends on your hosting environment.

## Summary:
- AI backend is production-ready.
- Just run uvicorn backend_ai.py:app --reload and integrate.
