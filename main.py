import sys
# 1. FORCE UTF-8 ENCODING (Fixes Windows Emoji issue)
sys.stdout.reconfigure(encoding='utf-8')
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
import re
import json
from datetime import datetime
from orchestrator import orchestrator
from exporters import export_test_cases
from pydantic import BaseModel
import hashlib # <--- NEW IMPORT

# --- FEEDBACK STORAGE 
FEEDBACK_FILE = "feedback.json"

# 2. INITIALIZE APP (Must happen before @app decorators)
app = FastAPI(title="AI Test Case Generator - Final Professional")

# 3. MOUNT STATIC FILES
app.mount("/static", StaticFiles(directory="static"), name="static")
os.makedirs("exports", exist_ok=True)

class FeedbackRequest(BaseModel):
    test_case_id: str
    description: str
    rating: str
    input_context: str # NEW FIELD (The code/text being tested)

@app.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    """Saves user feedback LINKED to the specific input context"""
    
    # Create a unique "fingerprint" for the code
    # We use MD5 to turn long code into a short string like "a1b2c3d4"
    context_hash = hashlib.md5(feedback.input_context.strip().encode('utf-8')).hexdigest()
    
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "id": feedback.test_case_id,
        "description": feedback.description,
        "rating": feedback.rating,
        "context_hash": context_hash # SAVING THE LINK
    }
    
    existing_data = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                existing_data = json.load(f)
        except:
            existing_data = []
    
    existing_data.append(data)
    
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(existing_data, f, indent=2)
        
    print(f"⭐ FEEDBACK RECEIVED: {feedback.rating.upper()} for {feedback.test_case_id}")
    return {"status": "success"}

# --- HISTORY CONFIG 
HISTORY_FILE = "history.json"

# --- HELPER FUNCTIONS ---
def save_to_history(input_text, input_type, test_cases, download_urls):
    """Saves a record of the generation to a JSON file"""
    record = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_preview": input_text[:50] + "..." if len(input_text) > 50 else input_text,
        "input_type": input_type,
        "count": len(test_cases),
        "download_urls": download_urls,
        "test_cases": test_cases 
    }
    
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except:
            history = []
            
    # Add new record to the TOP
    history.insert(0, record)
    
    # Keep only last 50 records
    if len(history) > 50:
        history = history[:50]
        
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def is_valid_python(code: str):
    code_lower = code.lower()
    if "#include" in code_lower or "std::" in code_lower: raise ValueError("❌ C/C++ Detected!")
    if "public class" in code_lower and "{" in code: raise ValueError("❌ Java Detected!")
    if "<html>" in code_lower or "</div>" in code_lower: raise ValueError("❌ HTML Detected!")
    if re.search(r'^\s*(int|void|double)\s+\w+\s*\(', code, re.MULTILINE): raise ValueError("❌ C-Style Function Detected!")
    if re.search(r'[^=]\s*\{\s*$', code, re.MULTILINE): raise ValueError("❌ Curly Braces '{' detected!")
    python_indicators = ["def ", "import ", "from ", "class ", "print(", "return", "if ", "pass", "list", "dict", "#"]
    if not any(k in code for k in python_indicators): raise ValueError("⚠️ No Python code detected.")
    return True

def is_valid_ui_description(text: str):
    text_lower = text.lower()
    if re.search(r'(.)\1{3,}', text_lower): raise ValueError("⚠️ Gibberish detected.")
    ui_keywords = ["form", "button", "input", "field", "text", "login", "page", "click", "submit", "error", "message", "display"]
    if not any(k in text_lower for k in ui_keywords): raise ValueError("⚠️ Invalid Description! Use UI keywords like 'button', 'form'.")
    return True

# --- ROUTES ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the main HTML page with UTF-8 encoding"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/history")
def get_history():
    """Returns the list of past generations"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

@app.post("/generate")
def generate_tests(
    input_text: str = Form(...),
    input_type: str = Form(...),
):
    try:
        if not input_text or len(input_text.strip()) < 5:
            raise HTTPException(status_code=400, detail="Input is too short")
        
        # VALIDATION
        if input_type == "code":
            try: is_valid_python(input_text)
            except ValueError as e: raise HTTPException(status_code=400, detail=str(e))
        elif input_type == "ui":
            try: is_valid_ui_description(input_text)
            except ValueError as e: raise HTTPException(status_code=400, detail=str(e))
        
        print(f"📥 REQUEST: {input_type.upper()} -> Generating ALL formats")
        
        # ORCHESTRATE
        test_cases = orchestrator.orchestrate(input_text, input_type)
        if not test_cases: raise HTTPException(status_code=500, detail="Failed to generate test cases")
        
        # EXPORT FILES
        unique_id = str(uuid.uuid4())[:8]
        base_filename = f"test_cases_{unique_id}"

        path_csv = export_test_cases(test_cases, "csv", base_filename)
        path_json = export_test_cases(test_cases, "json", base_filename)
        path_xlsx = export_test_cases(test_cases, "xlsx", base_filename)
        
        # DEFINE URLs
        download_urls = {
            "csv": f"/download/{os.path.basename(path_csv)}",
            "json": f"/download/{os.path.basename(path_json)}",
            "xlsx": f"/download/{os.path.basename(path_xlsx)}"
        }

        # SAVE TO HISTORY
        save_to_history(input_text, input_type, test_cases, download_urls)
        
        return {
            "status": "success",
            "message": f"Generated {len(test_cases)} test cases",
            "test_cases": test_cases,
            "orchestration_summary": orchestrator.get_summary(),
            "download_urls": download_urls
        }
    
    except HTTPException as he: raise he
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/download/{filename}")
def download_file(filename: str):
    filepath = f"exports/{filename}"
    if not os.path.exists(filepath): raise HTTPException(status_code=404, detail="File not found")
    
    media_type = "application/octet-stream"
    if filename.endswith(".csv"): media_type = "text/csv"
    elif filename.endswith(".json"): media_type = "application/json"
    elif filename.endswith(".xlsx"): media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return FileResponse(path=filepath, filename=filename, media_type=media_type)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Test Case Generator...")
    print("📱 Open browser at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)