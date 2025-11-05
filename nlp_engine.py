import spacy
from test_case_generator import generate_test_cases


nlp = spacy.load("en_core_web_sm")

def analyze_requirement(text):
    doc = nlp(text)
    
    # Standardized action mapping
    action_mapping = {
        "register": "register",
        "signup": "register",
        "log": "login",
        "signin": "login",
        "create": "create",
        "add": "create",
        "make": "create",
        "edit": "update",
        "update": "update",
        "modify": "update",
        "delete": "delete",
        "remove": "delete",
        "search": "search",
        "find": "search",
        "view": "read",
        "see": "read",
        "display": "read",
        "get": "read",
        "should": "general_requirement" # For general statements
    }

    extracted_actions = []
    for token in doc:
        if token.pos_ == "VERB":
            lemma = token.lemma_.lower()
            if lemma in action_mapping:
                extracted_actions.append(action_mapping[lemma])
            else:
                # If not in mapping, use the lemma itself as a generic action
                extracted_actions.append(lemma)

    # Remove duplicates and maintain order (if order is important, otherwise a set would be faster)
    actions = list(dict.fromkeys(extracted_actions))

    objects = [chunk.text for chunk in doc.noun_chunks]

    result = {
        "original_text": text,
        "actions": actions,
        "objects": objects
    }
    
    return result

def process_requirement(text):
    nlp_result = analyze_requirement(text)
    test_cases = generate_test_cases(nlp_result)
    
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