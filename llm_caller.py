import requests
import json
from typing import Dict, Any

class LLMCaller:
    """Calls Ollama/Mistral directly"""
    
    def __init__(self, model: str = "mistral:latest", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.endpoint = f"{host}/api/generate"
    
    def call_llm(self, prompt: str, system_prompt: str = None) -> str:
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "temperature": 0.3,
                "top_k": 40,
                "top_p": 0.9,
                "repeat_penalty": 1.1 # Stops loops!
            }

            # 600s timeout for Mistral
            response = requests.post(self.endpoint, json=payload, timeout=600)
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                raise Exception(f"LLM Error: {response.status_code}")
        except Exception as e:
            raise Exception(f"LLM Call Failed: {str(e)}")
    
    def build_code_analysis_prompt(self, code: str, analysis: Dict[str, Any]) -> str:
        return f"Analyze this code:\n{code}\nWhat are the main test scenarios?"
    
    def build_test_generation_prompt(self, analysis: Dict[str, Any], input_type: str) -> str:
        
        original_code = analysis.get('original_code', '')
        
        if input_type == "code":
            functions = analysis.get('functions', [])
            func_name = functions[0]["name"] if functions else "function_name"

            prompt = f"""Generate PYTHON (Pytest/Unittest) test cases for this code:
----------------
{original_code}
----------------

STRICT OUTPUT FORMAT (Use | separator):
TC-XXX | Description | Input Data | Expected Output | Test Type

EXAMPLES:
TC-001 | Valid Input | {func_name}(5) | 10 | Happy Path
TC-002 | Invalid Input | {func_name}(-1) | ValueError | Error Handling

RULES:
1. Use Python syntax (None, True, False, Exceptions).
2. Ensure every line has exactly 4 vertical bars (|).

Generate Python test cases:"""
        
        else: # UI
            prompt = f"""Generate test cases for this UI Description:
----------------
{original_code}
----------------
STRICT OUTPUT FORMAT (Use | separator):
TC-XXX | Description | Action | Result | Test Type

Generate test cases:"""
        
        return prompt
    
    def build_system_prompt(self) -> str:
        """
        Robust system prompt to enforce persona and formatting.
        """
        return """You are an expert QA Automation Engineer. 
Your task is to analyze code or requirements and generate structured test cases.
You must:
1. Focus on edge cases, validation errors, and happy paths.
2. STRICTLY follow the requested output format (CSV-style with | separators).
3. Do not output markdown tables, conversational filler, or intro text.
4. Just provide the data rows."""

llm = LLMCaller(model="mistral:latest")