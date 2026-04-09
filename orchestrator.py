from analyzer import analyzer
from llm_caller import llm
from parser import parse_test_cases
from typing import Dict, List, Any
import time
import json
import os
import hashlib #NEW IMPORT for Context Hashing

# --- CONFIG 
FEEDBACK_FILE = "feedback.json"

class TestGenerationOrchestrator:
    """
    Orchestrates the AI Agents with:
    1. Heuristic Strategy (Analyzer)
    2. Agentic Self-Correction (Retry Loop)
    3. Reinforcement Learning Context (Feedback Injection)
    """
    
    def __init__(self):
        self.analyzer = analyzer
        self.llm = llm
        self.analysis_results = {}
        self.test_cases = []
    
    # 🟢 HELPER: Load Context-Aware Feedback
    def _get_feedback_context(self, current_input: str) -> str:
        """Reads user feedback SPECIFIC to the current code input"""
        if not os.path.exists(FEEDBACK_FILE):
            return ""
            
        try:
            # 1. Calculate Hash of current input (Fingerprint)
            current_hash = hashlib.md5(current_input.strip().encode('utf-8')).hexdigest()
            
            with open(FEEDBACK_FILE, "r") as f:
                history = json.load(f)
            
            # 2. Filter: Only keep feedback that matches this input's hash
            # (Matches the logic we added to main.py)
            relevant_history = [item for item in history if item.get('context_hash') == current_hash]
            
            if not relevant_history:
                return "" # No feedback for THIS specific code yet
            
            # Filter for "useless" (Negative Reinforcement)
            bad_examples = [item['description'] for item in relevant_history if item['rating'] == 'useless']
            
            # Filter for "useful" (Positive Reinforcement)
            good_examples = [item['description'] for item in relevant_history if item['rating'] == 'useful']
            
            context = []
            if bad_examples:
                context.append(f"⛔ AVOID these (Previously marked Useless for THIS code):\n" + "\n".join([f"- {desc}" for desc in bad_examples[-5:]]))
            
            if good_examples:
                context.append(f"✅ PREFERRED (Previously marked Useful for THIS code):\n" + "\n".join([f"- {desc}" for desc in good_examples[-5:]]))
                
            return "\n\n".join(context)
            
        except Exception as e:
            print(f"⚠️ Failed to load feedback: {e}")
            return ""

    def orchestrate(self, user_input: str, input_type: str) -> List[Dict[str, Any]]:
        print("\n" + "=" * 60)
        print("🤖 CUSTOM AI ORCHESTRATION STARTED (Agentic + RLHF Mode)")
        print("=" * 60)
        
        # STEP 1: ANALYZE & STRATEGIZE
        print("\n📊 STEP 1: Analyzing & Generating Heuristics...")
        self.analysis_results = self._analyze_step(user_input, input_type)
        
        # Extract the Heuristic Strategy
        strategy_advice = self.analysis_results.get("test_strategy", "Standard Strategy")
        print(f"🧠 Heuristic Strategy Detected:\n   👉 {strategy_advice}")
        
        # STEP 2: LOAD FEEDBACK (Context-Aware RLHF)
        print("\n🧠 STEP 2: Retrieving Context-Aware Feedback...")
        
        # Pass the user_input to get specific feedback
        feedback_context = self._get_feedback_context(user_input)
        
        if feedback_context:
            print("   ✅ Found relevant feedback for this specific code! Injecting...")
        else:
            print("   ℹ️ No feedback history found for this code. Starting fresh.")

        # STEP 3: BUILD PROMPT (With Injection)
        print("\n🧪 STEP 3: Building Context-Aware Prompt...")
        base_prompt = self.llm.build_test_generation_prompt(self.analysis_results, input_type)
        
        final_prompt = f"""
{base_prompt}

IMPORTANT TESTING STRATEGY (Heuristics):
{strategy_advice}

USER FEEDBACK HISTORY (Learned Rules from RLHF):
{feedback_context if feedback_context else "No history yet."}
"""
        # ---------------------------
        
        # STEP 4: AGENTIC GENERATION LOOP
        print("\n🚀 STEP 4: Entering Agentic Generation Loop...")
        
        max_attempts = 3
        attempt = 1
        self.test_cases = []
        
        while attempt <= max_attempts:
            print(f"\n   🔄 Attempt {attempt}/{max_attempts}...")
            
            try:
                # Call LLM
                llm_response = self.llm.call_llm(
                    prompt=final_prompt,
                    system_prompt=self.llm.build_system_prompt()
                )
                
                # Parse
                parsed_cases = parse_test_cases(llm_response)
                
                # VALIDATION CHECK
                if parsed_cases and len(parsed_cases) > 0:
                    print(f"   ✅ Success! Generated {len(parsed_cases)} valid test cases.")
                    self.test_cases = parsed_cases
                    break # Exit loop on success
                else:
                    print("   ⚠️ Parsing failed (0 cases). Agent detected invalid format.")
                    
                    # FEEDBACK LOOP: Modify prompt for next attempt
                    error_feedback = "The previous output was empty or invalid. You MUST use the | separator format."
                    final_prompt = f"{base_prompt}\n\nSYSTEM FEEDBACK: {error_feedback}\nRetry now:"
                    
                    attempt += 1
                    time.sleep(2) # Backoff
                    
            except Exception as e:
                print(f"   ❌ Error in attempt {attempt}: {str(e)}")
                attempt += 1
                time.sleep(2)
        
        # FINAL STATUS
        if not self.test_cases:
            print("\n❌ All attempts failed. Creating fallback manual review case.")
            self.test_cases = [{
                "Test Case ID": "TC-ERR", 
                "Description": "AI Failed to generate valid structure", 
                "Input": "N/A", 
                "Expected Output": "Manual Review", 
                "Test Type": "Error"
            }]

        print("\n" + "=" * 60)
        print("🎉 ORCHESTRATION COMPLETE!")
        print("=" * 60)
        
        return self.test_cases
    
    def _analyze_step(self, user_input: str, input_type: str) -> Dict[str, Any]:
        results = {}
        if input_type == "code":
            results = self.analyzer.analyze_code(user_input)
        else:
            results = self.analyzer.analyze_ui(user_input)
        
        results['original_code'] = user_input
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "analysis": self.analysis_results,
            "test_cases_generated": len(self.test_cases),
            "status": "success" if self.test_cases else "failed"
        }

orchestrator = TestGenerationOrchestrator()