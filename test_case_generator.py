def generate_test_cases(nlp_result):
    actions = nlp_result["actions"]
    objects = nlp_result["objects"]

    test_cases = []

    if "register" in actions:
        test_cases.append({
            "Step": 1,
            "Action": "Open registration page",
            "Input": "-",
            "Expected Result": "Registration page should load"
        })
        test_cases.append({
            "Step": 2,
            "Action": "Enter valid email and password",
            "Input": "email, password",
            "Expected Result": "Account should be created"
        })
        test_cases.append({
            "Step": 3,
            "Action": "Enter invalid email or password",
            "Input": "invalid email/password",
            "Expected Result": "Error message should appear"
        })

    return test_cases
