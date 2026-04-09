import re
from typing import Dict, List, Any

class CodeAnalyzer:
    """
    Analyzes code snippets to extract metadata AND generates heuristic testing strategies.
    (Heuristic Pre-processing Layer)
    """
    
    def __init__(self):
        self.analysis = {}
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze a Python code snippet"""
        self.analysis = {
            "code": code,
            "type": "code",
            "functions": self._extract_functions(code),
            "classes": self._extract_classes(code),
            "imports": self._extract_imports(code),
            "error_handling": self._check_error_handling(code),
            "parameters": self._extract_parameters(code),
            "potential_test_types": self._identify_test_types(code),
            # NEW: Generate Strategy Advice based on heuristics
            "test_strategy": self._generate_test_strategy(code)
        }
        return self.analysis
    
    def analyze_ui(self, ui_description: str) -> Dict[str, Any]:
        """Analyze a UI/form description"""
        # For UI, we treat the description itself as the "strategy context"
        return {
            "description": ui_description,
            "type": "ui",
            "form_fields": self._extract_form_fields(ui_description),
            "buttons": self._extract_buttons(ui_description),
            "validations": self._extract_validations(ui_description),
            "flows": self._extract_user_flows(ui_description),
            "potential_test_types": self._identify_ui_test_types(ui_description),
            "test_strategy": "Focus on Usability, Input Validation, and Responsive Design."
        }

    # --- 🧠 HEURISTIC STRATEGY GENERATOR 
    def _generate_test_strategy(self, code: str) -> str:
        """
        Applies rule-based heuristics to suggest specific testing angles.
        Justification: Combines symbolic AI (Rules) with generative AI (LLM).
        """
        strategies = []
        code_lower = code.lower()
        
        # 1. Database Interactions
        if any(x in code_lower for x in ['sqlite', 'sqlalchemy', 'cursor', 'execute', 'db.']):
            strategies.append("⚠️ DATABASE DETECTED: Mock all database connections. Do not use real DB.")
            
        # 2. API / Network Calls
        if any(x in code_lower for x in ['requests.', 'urllib', 'http', 'api', 'fetch']):
            strategies.append("🌐 NETWORK CALLS: Mock external API responses (200 OK, 404 Not Found, 500 Server Error).")
            
        # 3. File Systems
        if any(x in code_lower for x in ['open(', 'read', 'write', 'path', 'os.']):
            strategies.append("📂 FILE I/O: Use temporary files or mocks. Test permission errors and missing files.")
            
        # 4. Math Operations
        if '/' in code or '%' in code:
            strategies.append("➗ MATH OPS: Strictly test for ZeroDivisionError and overflow scenarios.")
            
        # 5. Loops / Recursion
        if 'while' in code_lower or 'recursion' in code_lower:
            strategies.append("🔄 LOOPS: Test for infinite loops and exceeding recursion depth.")

        if not strategies:
            strategies.append("✅ STANDARD: Focus on Input Validation, Boundary Values, and Happy Paths.")
            
        return "\n".join(strategies)

    # --- EXISTING EXTRACTION METHODS 
    def _extract_functions(self, code: str) -> List[Dict[str, Any]]:
        functions = []
        matches = re.finditer(r'def\s+(\w+)\s*\((.*?)\):', code)
        for match in matches:
            functions.append({
                "name": match.group(1),
                "args": match.group(2)
            })
        return functions
    
    def _extract_classes(self, code: str) -> List[str]:
        return re.findall(r'class\s+(\w+)', code)
    
    def _extract_imports(self, code: str) -> List[str]:
        return re.findall(r'^(?:from|import)\s+(\w+)', code, re.MULTILINE)
    
    def _check_error_handling(self, code: str) -> bool:
        return 'try:' in code and 'except' in code
    
    def _extract_parameters(self, code: str) -> List[str]:
        params = []
        matches = re.search(r'def\s+\w+\s*\((.*?)\):', code)
        if matches:
            raw_params = matches.group(1).split(',')
            params = [p.strip() for p in raw_params if p.strip()]
        return params

    def _identify_test_types(self, code: str) -> List[str]:
        types = ["Happy Path", "Edge Cases"]
        if self._check_error_handling(code):
            types.append("Error Handling")
        if "if" in code or "else" in code:
            types.append("Condition Testing")
        return types

    # --- UI HELPERS 
    def _extract_form_fields(self, description: str) -> List[str]:
        fields = []
        keywords = ['field', 'input', 'checkbox', 'radio', 'dropdown', 'area']
        desc_lower = description.lower()
        if any(k in desc_lower for k in keywords):
            words = desc_lower.split()
            for i, word in enumerate(words):
                if word in keywords and i > 0:
                    fields.append(f"{words[i-1]} {word}")
        return fields if fields else ["generic_field"]
    
    def _extract_buttons(self, description: str) -> List[str]:
        buttons = []
        if 'button' in description.lower():
            buttons.append("Submit/Action Button")
        return buttons
    
    def _extract_validations(self, description: str) -> List[str]:
        validations = []
        desc_lower = description.lower()
        if 'required' in desc_lower: validations.append("required")
        if 'email' in desc_lower: validations.append("email_format")
        return validations
    
    def _extract_user_flows(self, description: str) -> List[str]:
        flows = []
        if 'submit' in description.lower(): flows.append("form_submission")
        if 'login' in description.lower(): flows.append("authentication")
        return flows
    
    def _identify_ui_test_types(self, description: str) -> List[str]:
        return ["Happy Path", "Validation Testing", "UI Responsiveness"]

analyzer = CodeAnalyzer()