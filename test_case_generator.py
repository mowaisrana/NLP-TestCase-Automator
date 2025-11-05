def generate_test_cases(nlp_result):
    actions = nlp_result["actions"]
    objects = nlp_result["objects"]

    test_cases = []
    generated_steps = set()

    # Function to add a test case if it's not a duplicate
    def add_test_case(step, action, input_data, expected_result):
        step_key = (action, input_data, expected_result) # Unique identifier for a step
        if step_key not in generated_steps:
            test_cases.append({
                "Step": step,
                "Action": action,
                "Input": input_data,
                "Expected Result": expected_result
            })
            generated_steps.add(step_key)

    # Test case generation logic for specific actions
    if "register" in actions:
        add_test_case(1, "Open registration page", "-", "Registration page should load")
        add_test_case(2, "Enter valid email and password", "valid email, valid password", "Account should be created successfully")
        add_test_case(3, "Enter existing email and valid password", "existing email, valid password", "Error message for existing email should appear")
        add_test_case(4, "Enter invalid email format", "invalid email, valid password", "Error message for invalid email format should appear")
        add_test_case(5, "Enter password not meeting criteria", "valid email, weak password", "Error message for weak password should appear")
        add_test_case(6, "Submit with empty fields", "-", "Error messages for mandatory fields should appear")

    if "login" in actions:
        add_test_case(1, "Open login page", "-", "Login page should load")
        add_test_case(2, "Enter valid username and password", "valid username, valid password", "User should be logged in successfully")
        add_test_case(3, "Enter invalid username or password", "invalid username/password", "Error message for invalid credentials should appear")
        add_test_case(4, "Attempt login with empty fields", "-", "Error messages for mandatory fields should appear")

    if "create" in actions:
        # Generic create action, can be refined based on objects
        for obj in objects:
            add_test_case(1, f"Navigate to {obj} creation form", "-", f"{obj} creation form should load")
            add_test_case(2, f"Enter valid details for {obj}", f"valid {obj} data", f"{obj} should be created successfully")
            add_test_case(3, f"Enter invalid details for {obj}", f"invalid {obj} data", f"Error message for invalid {obj} data should appear")

    if "update" in actions:
        # Generic edit/update action
        for obj in objects:
            add_test_case(1, f"Navigate to {obj} edit page", "-", f"{obj} edit page should load")
            add_test_case(2, f"Modify {obj} with valid data", f"updated {obj} data", f"{obj} should be updated successfully")
            add_test_case(3, f"Attempt to modify {obj} with invalid data", f"invalid {obj} data", f"Error message for invalid {obj} data should appear")

    if "delete" in actions:
        # Generic delete action
        for obj in objects:
            add_test_case(1, f"Navigate to {obj} management page", "-", f"{obj} management page should load")
            add_test_case(2, f"Select {obj} to delete", f"{obj} ID", f"{obj} should be selected")
            add_test_case(3, f"Confirm deletion of {obj}", "confirmation", f"{obj} should be deleted successfully")
            add_test_case(4, f"Cancel deletion of {obj}", "cancellation", f"{obj} should not be deleted")

    if "search" in actions:
        # Generic search action
        for obj in objects:
            add_test_case(1, f"Navigate to {obj} search page", "-", f"{obj} search page should load")
            add_test_case(2, f"Enter valid search term for {obj}", f"valid {obj} search term", f"Relevant {obj} results should be displayed")
            add_test_case(3, f"Enter invalid search term for {obj}", f"invalid {obj} search term", f"No {obj} results or error message should be displayed")
            add_test_case(4, f"Perform empty search for {obj}", "-", f"All {obj} results or appropriate message should be displayed")

    if "read" in actions:
        # Generic read/view action
        for obj in objects:
            add_test_case(1, f"Navigate to {obj} list/view page", "-", f"{obj} list/view page should load")
            add_test_case(2, f"Verify {obj} are displayed correctly", "-", f"{obj} should be visible and correctly formatted")
            add_test_case(3, f"Attempt to view non-existent {obj}", f"non-existent {obj} ID", f"Error or 'not found' message should appear")

    if "general_requirement" in actions and not any(action in actions for action in ["register", "login", "create", "update", "delete", "search", "read"]):
        # Default test case if no specific action is found but a general requirement is present
        for action in actions:
            if action != "general_requirement":
                add_test_case(1, f"Verify system handles '{action}' as expected", "-", f"System should respond correctly to the '{action}'")
            elif not actions or len(actions) == 1 and "general_requirement" in actions: # Handles cases where only 'should' is detected
                add_test_case(1, "Analyze general system behavior", "-", "System should meet the general requirement.")

    # Fallback if no specific actions or general requirements were processed
    if not test_cases:
        add_test_case(1, "Review requirement manually", "-", "No specific automated test cases could be generated. Manual review needed.")

    # Ensure steps are ordered correctly and re-number if necessary
    final_test_cases = []
    step_counter = 1
    for tc in test_cases:
        tc["Step"] = step_counter
        final_test_cases.append(tc)
        step_counter += 1

    return final_test_cases
