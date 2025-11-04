# 🤖 NLP-TestCase-Automator
AI-powered tool that automatically generates software test cases from **plain English requirements** using **Natural Language Processing (NLP)** and basic rule‑based AI.

## 📌 Overview
NLP-TestCase-Automator converts user stories or requirement statements like:
> "User should be able to log in using email and password"
into structured **test cases** with steps, inputs, and expected results.
This helps QA engineers **save time**, **reduce manual effort**, and **improve test coverage**.

## 🚀 Features
* Understand natural language requirement text
* Extract actions, inputs, and expected behavior
* Generate structured test cases automatically
* Display results in a simple **web UI** (Streamlit)

## 🧠 Tech Used
| Component   | Technology |
| ----------- | ---------- |
| Language    | Python     |
| NLP Library | spaCy      |
| UI          | Streamlit  |
| Data        | Pandas     |

## 🗂️ Folder Structure
```
NLP-TestCase-Automator/
 ├── app.py
 ├── test_generator.py
 ├── requirements.txt
 └── README.md
```

## ⚙️ Installation
```bash
pip install spacy
pip install nltk
pip install pandas
pip install streamlit
pip install transformers
python -m spacy download en_core_web_sm
```

## ▶️ Run the App
```bash
streamlit run app.py
```

## 🎯 Example Input
> "User should be able to register using email and password"

### ✅ Output (Test Case Table)
| Step | Action                     | Input                | Expected Result |
| ---- | -------------------------- | -------------------- | --------------- |
| 1    | Open registration page     | —                    | Page loads      |
| 2    | Enter valid email/password | email, password      | Account created |
| 3    | Enter invalid values       | wrong email/password | Error message   |


## 📚 Future Enhancements
* Gherkin (Given‑When‑Then) output
* ML model for smarter test case generation
* Export to Excel / JSON
* Integration with Selenium

👥 Team
Developed by:
Muhammad Owais & Muhammad Asim
Course: Artificial Intelligence (Semester Project)
