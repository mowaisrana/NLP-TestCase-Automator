import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

def export_to_csv(test_cases: List[Dict[str, Any]], filename: str) -> str:
    """Export test cases to CSV"""
    df = pd.DataFrame(test_cases)
    filepath = f"exports/{filename}.csv"
    df.to_csv(filepath, index=False)
    return filepath


def export_to_json(test_cases: List[Dict[str, Any]], filename: str) -> str:
    """Export test cases to JSON"""
    data = {
        'generated_at': datetime.now().isoformat(),
        'total_test_cases': len(test_cases),
        'test_cases': test_cases
    }
    filepath = f"exports/{filename}.json"
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    return filepath


def export_to_xlsx(test_cases: List[Dict[str, Any]], filename: str) -> str:
    """Export test cases to Excel"""
    df = pd.DataFrame(test_cases)
    filepath = f"exports/{filename}.xlsx"
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Test Cases', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Test Cases']
        
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    return filepath


def export_test_cases(test_cases: List[Dict[str, Any]], format_type: str, filename: str) -> str:
    """Main export function"""
    if format_type == "csv":
        return export_to_csv(test_cases, filename)
    elif format_type == "json":
        return export_to_json(test_cases, filename)
    elif format_type == "xlsx":
        return export_to_xlsx(test_cases, filename)
    else:
        raise ValueError(f"Unsupported format: {format_type}")
