import streamlit as st
from nlp_engine import analyze_requirement
from test_case_generator import generate_test_cases
import pandas as pd
from exporter import export_to_excel
from db import get_all_testcases
import sqlite3
from db import save_testcase, get_all_testcases
from nlp_engine import process_requirement





st.title("🧠 NLP Test Case Generator")
# st.write("Enter a requirement and the system will generate test cases automatically.")
# user_input = st.text_area("Enter Requirement:", placeholder="e.g., User should be able to register using email and password.")
# if st.button("Generate Test Cases"):
#     if user_input.strip():
#         nlp_result = analyze_requirement(user_input)
#         test_cases = generate_test_cases(nlp_result)
#         if test_cases:
#             df = pd.DataFrame(test_cases)
#             st.success("✅ Test cases generated successfully!")
#             st.table(df)
#         else:
#             st.warning("⚠ No valid action detected. Try another requirement.")
#     else:
#         st.error("Please enter a requirement")



# st.set_page_config(page_title="NLP Test Case Automator", layout="wide")

# st.title("🧠 NLP Test Case Automator")
# st.write("Generate test cases from natural language requirements using AI & NLP")

# # Requirement input box
# user_input = st.text_area("Enter Requirement:", placeholder="e.g., User should be able to register using email and password")

# if st.button("Generate Test Cases"):
#     if user_input.strip() == "":
#         st.warning("Please enter a requirement.")
#     else:
#         # Run NLP Analysis
#         nlp_result = analyze_requirement(user_input)
#         test_cases = generate_test_cases(nlp_result)

#         st.subheader("✅ Generated Test Cases")
#         st.table(test_cases)

#         # Export button
#         if st.button("Export to Excel"):
#             export_to_excel(test_cases)
#             st.success("Excel exported successfully!")

# st.subheader("📂 Test Case History")
# history = get_all_testcases()

# if history:
#     st.dataframe(history)
# else:
#     st.info("No test case history found in database yet.")


#st.subheader("📊 Dashboard")


menu = ["Add Test Case", "View History", "Dashboard"]
choice = st.sidebar.selectbox("Menu", menu)

# Get history once
history = get_all_testcases()

# ------------------- ADD TEST CASE PAGE -------------------
# if choice == "Add Test Case":
#     st.subheader("📝 Add Test Case")

#     requirement = st.text_area("Enter requirement text:")
    
#     if st.button("Generate Test Cases"):
#         if requirement.strip() == "":
#             st.warning("⚠ Please enter a requirement")
#         else:
#             result = process_requirement(requirement)
#             st.success("✅ Test cases generated!")

#             for tc in result:
#                 st.write(tc)

#             save_testcase( requirement,result["nlp_result"]["actions"],result["nlp_result"]["objects"])
#             st.success("💾 Saved to database!")
if choice == "Add Test Case":
    st.subheader("📝 Add Test Case")

    requirement = st.text_area("Enter requirement text:")

    if st.button("Generate Test Cases"):
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

            # ✅ Display NLP output
            st.subheader("🧠 NLP Extraction")
            st.json(nlp_result)

            # ✅ Display test cases in table
            st.subheader("✅ Generated Test Cases")
            df = pd.DataFrame(test_cases)
            st.table(df)

            # ✅ Save to DB
            save_testcase(requirement, actions, objects)
            st.success("💾 Saved to database!")

            # ✅ Export & Download
            filename = export_to_excel(test_cases, filename="generated_testcases.xlsx")
            with open(filename, "rb") as f:
                st.download_button(
                    label="📥 Download Generated Test Cases (Excel)",
                    data=f,
                    file_name=filename,
                )


# ------------------- VIEW HISTORY PAGE -------------------

elif choice == "View History":
    st.subheader("📜 Test Case History")

    import sqlite3
    conn = sqlite3.connect("testcases.db")
    c = conn.cursor()
    c.execute("SELECT id, requirement, actions, objects, created_at FROM testcases ORDER BY created_at DESC")
    data = c.fetchall()

    if data:
        for row in data:
            test_id = row[0]
            requirement = row[1]
            actions = eval(row[2])
            objects = eval(row[3])
            created = row[4]

            st.write(f"### 🧾 Test Case ID: `{test_id}`")
            st.write(f"**📌 Requirement:** {requirement}")
            st.write(f"**⚙ Actions:** {', '.join(actions)}")
            st.write(f"**🎯 Objects:** {', '.join(objects)}")
            st.write(f"🕒 _Created: {created}_")

            # ✅ Show generated test cases in a collapsible section
            with st.expander("📂 View Generated Test Cases"):
                result = {
                    "nlp_result": {"actions": actions, "objects": objects}
                }
                from test_case_generator import generate_test_cases
                test_cases = generate_test_cases(result["nlp_result"])

                df = pd.DataFrame(test_cases)
                st.table(df)

            # 🗑 Delete button
            if st.button(f"Delete {test_id}"):
                c.execute("DELETE FROM testcases WHERE id = ?", (test_id,))
                conn.commit()
                st.success(f"✅ Deleted Test Case {test_id}")
                st.experimental_rerun()

            st.divider()

    else:
        st.info("No test cases found")

    conn.close()




# elif choice == "View History":
#     st.subheader("📜 Test Case History")

#     import sqlite3
#     conn = sqlite3.connect("testcases.db")
#     c = conn.cursor()
#     c.execute("SELECT id, requirement, actions, objects, created_at FROM testcases ORDER BY created_at DESC")
#     data = c.fetchall()

#     if data:
#         for row in data:
#             st.write(f"**ID:** {row[0]}")
#             st.write(f"**Requirement:** {row[1]}")
#             st.write(f"**Actions:** {row[2]}")
#             st.write(f"**Objects:** {row[3]}")
#             st.write(f"**Created:** {row[4]}")

#             if st.button(f"🗑 Delete {row[0]}"):
#                 c.execute("DELETE FROM testcases WHERE id = ?", (row[0],))
#                 conn.commit()
#                 st.success(f"✅ Deleted Test Case {row[0]}")
#                 st.experimental_rerun()
#             st.divider()
#     else:
#         st.info("No test cases found")

#     conn.close()


# ------------------- DASHBOARD PAGE -------------------
elif choice == "Dashboard":
    st.subheader("📊 Dashboard")

    if history:
        import pandas as pd
        from ast import literal_eval
        df = pd.DataFrame(history)
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["date"] = df["created_at"].dt.date

        col1, col2 = st.columns(2)
        col1.metric("🧪 Total Test Cases", len(df))
        col2.metric("📅 Active Days", df["date"].nunique())

        st.write("### 📈 Test Cases Per Day")
        st.line_chart(df.groupby("date").size())

        # Actions Frequency
        all_actions = []
        for a in df["actions"]:
            all_actions.extend(literal_eval(a))
        action_counts = pd.Series(all_actions).value_counts()

        st.write("### 🔎 Most Common Actions")
        st.bar_chart(action_counts)

        # Excel download
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


# # Get all testcases again for dashboard
# history = get_all_testcases()

# # ------------------- View History Page -------------------
# if choice == "View History":
#     st.subheader("📜 Test Case History")

#     conn = sqlite3.connect("testcases.db")
#     c = conn.cursor()
#     c.execute("SELECT id, requirement, actions, objects, created_at FROM testcases ORDER BY created_at DESC")
#     data = c.fetchall()

#     if data:
#         for row in data:
#             st.write(f"**ID:** {row[0]}")
#             st.write(f"**Requirement:** {row[1]}")
#             st.write(f"**Actions:** {row[2]}")
#             st.write(f"**Objects:** {row[3]}")
#             st.write(f"**Created At:** {row[4]}")

#             if st.button(f"🗑️ Delete ID {row[0]}"):
#                 c.execute("DELETE FROM testcases WHERE id = ?", (row[0],))
#                 conn.commit()
#                 st.success(f"✅ Deleted Test Case {row[0]}")
#                 st.experimental_rerun()

#             st.markdown("---")
#     else:
#         st.info("No test cases found")

#     conn.close()

# # ------------------- Dashboard (Only On Add Test Case Screen) -------------------
# elif choice == "Add Test Case":

#     st.subheader("📊 Dashboard")

#     if history:
#         import pandas as pd
#         df = pd.DataFrame(history)

#         # Convert created_at to datetime
#         df["created_at"] = pd.to_datetime(df["created_at"])
#         total_testcases = len(df)
#         df["date"] = df["created_at"].dt.date
#         testcases_per_day = df.groupby("date").size()

#         col1, col2 = st.columns(2)
#         col1.metric("🧪 Total Test Cases", total_testcases)
#         col2.metric("📅 Active Days", testcases_per_day.count())

#         st.write("### 📈 Test Cases Created Per Day")
#         st.line_chart(testcases_per_day)

#         from ast import literal_eval
#         all_actions = []
#         for a in df["actions"]:
#             all_actions.extend(literal_eval(a))

#         action_counts = pd.Series(all_actions).value_counts()

#         st.write("### 🔎 Most Common Actions (NLP keywords)")
#         st.bar_chart(action_counts)

#         from exporter import export_history_to_excel
#         file_name = export_history_to_excel(history)
#         with open(file_name, "rb") as f:
#             st.download_button(
#                 label="📥 Download All Test Cases (Excel)",
#                 data=f,
#                 file_name=file_name,
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )

#     else:
#         st.info("No data available yet to display dashboard.")

# elif choice == "View History":
#     st.subheader("📜 Test Case History")
    
#     conn = sqlite3.connect("testcases.db")
#     c = conn.cursor()
#     c.execute("SELECT id, requirement, actions, objects, created_at FROM testcases ORDER BY created_at DESC")
#     data = c.fetchall()

#     if data:
#         for row in data:
#             st.write(f"**ID:** {row[0]}")
#             st.write(f"**Requirement:** {row[1]}")
#             st.write(f"**Actions:** {row[2]}")
#             st.write(f"**Objects:** {row[3]}")
#             st.write(f"**Created:** {row[4]}")
            
#             delete = st.button(f"Delete ID {row[0]}")
#             if delete:
#                 c.execute("DELETE FROM testcases WHERE id = ?", (row[0],))
#                 conn.commit()
#                 st.success(f"Deleted Test Case {row[0]}")
#                 st.experimental_rerun()

#             st.markdown("---")
#     else:
#         st.info("No test cases found")

#     conn.close()

# if history:
#     import pandas as pd
#     df = pd.DataFrame(history)

#     # Convert created_at to datetime
#     df["created_at"] = pd.to_datetime(df["created_at"])
#     # Count total test cases
#     total_testcases = len(df)
#     # Test cases per day
#     df["date"] = df["created_at"].dt.date
#     testcases_per_day = df.groupby("date").size()

#     col1, col2 = st.columns(2)
#     col1.metric("🧪 Total Test Cases", total_testcases)
#     col2.metric("📅 Active Days", testcases_per_day.count())

#     st.write("### 📈 Test Cases Created Per Day")
#     st.line_chart(testcases_per_day)

#     # Most frequent action keywords (NLP insight)
#     from ast import literal_eval
#     all_actions = []
#     for a in df["actions"]:
#         all_actions.extend(literal_eval(a))

#     action_counts = pd.Series(all_actions).value_counts()

#     st.write("### 🔎 Most Common Actions (NLP keywords)")
#     st.bar_chart(action_counts)

#     # ✅ Export full history to Excel
#     from exporter import export_history_to_excel
#     file_name = export_history_to_excel(history)
#     with open(file_name, "rb") as f:
#         st.download_button(
#             label="📥 Download All Test Cases (Excel)",
#             data=f,
#             file_name=file_name,
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

# else:
#     st.info("No data available yet to display dashboard.")


