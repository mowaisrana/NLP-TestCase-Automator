import re
from typing import List, Dict, Any

def parse_test_cases(raw_text: str) -> List[Dict[str, Any]]:
    """Parse raw LLM response into structured test cases (Robust Version)"""
    test_cases = []
    lines = raw_text.split('\n')
    
    # Regex to find table rows (lines starting with | or containing multiple |)
    # This matches format: | val1 | val2 | val3 |
    table_row_pattern = r'\|?([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|?([^|]*)?\|?'
    
    current_id = 1
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines or separator lines (e.g. |---|---|)
        if not line or '---' in line:
            continue
            
        # Try to parse as a pipe-separated line
        if line.count('|') >= 3:
            # Remove leading/trailing pipes for cleaner splitting
            content = line.strip('|')
            parts = [p.strip() for p in content.split('|')]
            
            # We need at least 3 parts (Description, Input, Output)
            if len(parts) >= 3:
                # Check if the first part looks like an ID (TC-xxx)
                if 'TC-' in parts[0].upper():
                    tc_id = parts[0]
                    desc = parts[1] if len(parts) > 1 else ""
                    inp = parts[2] if len(parts) > 2 else ""
                    out = parts[3] if len(parts) > 3 else ""
                    type_ = parts[4] if len(parts) > 4 else "Happy Path"
                else:
                    # AI forgot the ID? No problem, we generate one.
                    tc_id = f"TC-{current_id:03d}"
                    desc = parts[0]
                    inp = parts[1] if len(parts) > 1 else ""
                    out = parts[2] if len(parts) > 2 else ""
                    type_ = parts[3] if len(parts) > 3 else "Happy Path"
                    current_id += 1

                # Clean up "Type" field if it has extra junk
                if 'Type' in type_ or 'Test' in type_: # Skip header row
                    continue
                    
                test_cases.append({
                    'Test Case ID': tc_id,
                    'Description': desc,
                    'Input': inp,
                    'Expected Output': out,
                    'Test Type': type_
                })
    
    # If standard parsing failed completely, use fallback
    if not test_cases:
        return fallback_parse(raw_text)
    
    return test_cases

def fallback_parse(response: str) -> List[Dict[str, Any]]:
    """Fallback if LLM returns unstructured text"""
    test_cases = []
    lines = response.split('\n')
    current_id = 1
    
    for line in lines:
        line = line.strip()
        # Capture numbered lists or bullet points
        if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
            # Clean the line
            clean_line = re.sub(r'^[\d\-\*\.]+\s*', '', line)
            
            test_cases.append({
                'Test Case ID': f'TC-{current_id:03d}',
                'Description': clean_line,
                'Input': 'Manual Review Required',
                'Expected Output': 'Manual Review Required',
                'Test Type': 'Manual'
            })
            current_id += 1
            
    return test_cases