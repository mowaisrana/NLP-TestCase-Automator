import pandas as pd
from datetime import datetime

def export_to_excel(test_cases, filename="test_cases_output.xlsx"):
    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(test_cases)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_{filename}"

    # Save to Excel
    df.to_excel(file_name, index=False)

    print(f"✅ Test cases exported successfully: {file_name}")
    return file_name

def export_history_to_excel(history, filename="testcase_history.xlsx"):
    df = pd.DataFrame(history)
    df.to_excel(filename, index=False)
    return filename

