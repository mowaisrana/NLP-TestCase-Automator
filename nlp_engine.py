import spacy
from test_case_generator import generate_test_cases
from db import save_testcase
from exporter import export_to_excel


nlp = spacy.load("en_core_web_sm")

def analyze_requirement(text):
    doc = nlp(text)
    
    actions = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    objects = [chunk.text for chunk in doc.noun_chunks]

    result = {
        "original_text": text,
        "actions": actions,
        "objects": objects
    }
    print(result)
    # Save to DB
    save_testcase(text, actions, objects)
    # Export test cases to Excel
    
    return result  # ✅ Correct indentation & return

def process_requirement(text):
    nlp_result = analyze_requirement(text)
    test_cases = generate_test_cases(nlp_result)
    export_to_excel(test_cases)
    
    return {
        "nlp_result": nlp_result,
        "test_cases": test_cases
    }

if __name__ == "__main__":
    sample = "User should be able to register using email and password."
    
    nlp_result = analyze_requirement(sample)
    print("NLP Output:", nlp_result)

    if nlp_result:  # ✅ Safety check
        test_cases = generate_test_cases(nlp_result)
        print("\nGenerated Test Cases:")
        for tc in test_cases:
            print(tc)
    else:
        print("NLP analysis returned None — error.")
    
    export_to_excel(test_cases)