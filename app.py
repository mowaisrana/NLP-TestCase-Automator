import streamlit as st
from nlp_engine import analyze_requirement
from test_case_generator import generate_test_cases
import pandas as pd
from exporter import export_to_excel
from db import get_all_testcases, save_testcase
import sqlite3
from nlp_engine import process_requirement

st.set_page_config(
    page_title="NLP Test Case Automator",
    page_icon="🧠",
    layout="wide"
)


st.title("🧠 NLP Test Case Generator")
menu = ["Add Test Case", "View History", "Dashboard"]
choice = st.sidebar.selectbox("Menu", menu)

# Get history once
history = get_all_testcases()

# ------------------- ADD TEST CASE PAGE -------------------
if choice == "Add Test Case":
    st.subheader("📝 Add Test Case")
    st.write("Enter a software requirement below, and I will generate comprehensive test cases using NLP.")

    # Input section
    with st.container():
        requirement = st.text_area(
            "**Your Requirement:**",
            placeholder="e.g., The user shall be able to log in with a valid username and password.",
            height=150
        )
        if st.button("Generate Test Cases", use_container_width=True):
            if requirement.strip() == "":
                st.warning("⚠ Please enter a requirement")
            else:
                # Run NLP processing
                result = process_requirement(requirement)

                # Extract data properly
                nlp_result = result["nlp_result"]
                actions = nlp_result["actions"]
                objects = nlp_result["objects"]

                # Generate test cases (result already has them too)
                test_cases = result["test_cases"]
                
                st.success("✅ Test cases generated and saved!")

                # Output section
                st.subheader("--- Output --- ")

                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("🧠 View NLP Extraction Details"):
                        st.json(nlp_result)
                with col2:
                    st.subheader("📜 Generated Test Cases")
                    df = pd.DataFrame(test_cases)
                    st.table(df)

                # Save to DB
                save_testcase(requirement, actions, objects)
                # st.success("💾 Saved to database!") # Moved to main success message

                # Export & Download
                st.divider()
                filename = export_to_excel(test_cases, filename="generated_testcases.xlsx")
                with open(filename, "rb") as f:
                    st.download_button(
                        label="📥 Download Generated Test Cases (Excel)",
                        data=f,
                        file_name=filename,
                        use_container_width=True
                    )


# ------------------- VIEW HISTORY PAGE -------------------

elif choice == "View History":
    st.subheader("📜 Test Case History")

    conn = sqlite3.connect("testcases.db")
    c = conn.cursor()
    c.execute("SELECT id, requirement, actions, objects, created_at FROM testcases ORDER BY created_at DESC")
    data = c.fetchall()

    if data:
        # Convert data to a list of dictionaries for easier DataFrame creation
        df = pd.DataFrame(data, columns=["ID", "Requirement", "Actions", "Objects", "Created At"])
        
        # Convert 'Actions' and 'Objects' from string representation of lists to actual lists
        # This is needed for proper display and potential future filtering/searching
        df["Actions"] = df["Actions"].apply(eval)
        df["Objects"] = df["Objects"].apply(eval)

        st.dataframe(df, use_container_width=True)

        # Add a section to view individual test cases from history
        st.divider()
        st.subheader("🔎 View & Delete Individual Test Cases")
        # st.write("**View and Delete Individual Test Cases:**")
        test_case_ids = [str(row[0]) for row in data]
        selected_test_case_id = st.selectbox("Select a Test Case ID to view details or delete:", test_case_ids)

        if selected_test_case_id:
            # Find the selected row data
            selected_row = next((row for row in data if str(row[0]) == selected_test_case_id), None)
            if selected_row:
                test_id, requirement, actions_str, objects_str, created_at = selected_row
                actions = eval(actions_str)
                objects = eval(objects_str)

                st.write(f"### 🧾 Test Case ID: `{test_id}`")
                st.write(f"**📌 Requirement:** {requirement}")
                st.write(f"**⚙ Actions:** {', '.join(actions)}")
                st.write(f"**🎯 Objects:** {', '.join(objects)}")
                st.write(f"🕒 _Created: {created_at}_")

                with st.expander("📂 View Generated Test Cases for this Requirement"):
                    nlp_result = {"actions": actions, "objects": objects}
                    test_cases = generate_test_cases(nlp_result)
                    df_individual = pd.DataFrame(test_cases)
                    st.table(df_individual)
                
                if st.button(f"🗑️ Delete Test Case {test_id}"):
                    c.execute("DELETE FROM testcases WHERE id = ?", (test_id,))
                    conn.commit()
                    st.success(f"✅ Deleted Test Case {test_id}")
                    st.experimental_rerun()

    else:
        st.info("No test cases found")

    conn.close()




# ------------------- DASHBOARD PAGE -------------------
elif choice == "Dashboard":
    st.subheader("📊 Dashboard")
    st.write("Here's an overview of your test case generation activity.")

    if history:
        import pandas as pd
        from ast import literal_eval
        df = pd.DataFrame(history)
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["date"] = df["created_at"].dt.date

        st.subheader("--- Key Metrics ---")
        col1, col2 = st.columns(2)
        col1.metric("🧪 Total Test Cases Generated", len(df))
        col2.metric("📅 Active Days", df["date"].nunique())

        st.divider()
        st.subheader("--- Activity Trends ---")
        with st.expander("📈 View Test Cases Per Day"):
            st.line_chart(df.groupby("date").size())

        # Actions Frequency
        all_actions = []
        for a in df["actions"]:
            all_actions.extend(literal_eval(a))
        action_counts = pd.Series(all_actions).value_counts()

        with st.expander("🔎 View Most Common Actions (NLP Keywords)"):
            st.bar_chart(action_counts)

        # Excel download
        st.divider()
        st.subheader("--- Data Export ---")
        from exporter import export_history_to_excel
        file_name = export_history_to_excel(history)
        with open(file_name, "rb") as f:
            st.download_button(
                label="📥 Download All Test Cases (Excel)",
                data=f,
                file_name=file_name,
            )
    else:
        st.info("No data yet! Add test cases first ✅")