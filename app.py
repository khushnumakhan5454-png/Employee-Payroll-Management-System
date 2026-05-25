# app.py

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Employee Payroll", layout="centered")

st.title("💼 Employee Payroll Management System")

# Store Data
if "employees" not in st.session_state:
    st.session_state.employees = []

# ================= ADD EMPLOYEE =================

st.header("➕ Add Employee")

emp_id = st.text_input("Employee ID")
name = st.text_input("Name")
address = st.text_input("Address")
email = st.text_input("Email")

gender = st.selectbox(
    "Gender",
    ["Male", "Female", "Other"]
)

working_days = st.number_input(
    "Working Days",
    min_value=0,
    max_value=31
)

leave = st.number_input(
    "Leave",
    min_value=0,
    max_value=31
)

salary = st.number_input(
    "Salary",
    min_value=0
)

bonus = st.number_input(
    "Bonus",
    min_value=0
)

# Salary Calculation
deduction = (salary / 30) * leave
net_salary = salary + bonus - deduction

# Add Button
if st.button("Add Employee"):

    employee = {
        "ID": emp_id,
        "Name": name,
        "Address": address,
        "Email": email,
        "Gender": gender,
        "Working Days": working_days,
        "Leave": leave,
        "Salary": salary,
        "Bonus": bonus,
        "Net Salary": net_salary
    }

    st.session_state.employees.append(employee)

    st.success("✅ Employee Added Successfully")

# ================= VIEW EMPLOYEE =================

st.header("📋 Employee Records")

if st.session_state.employees:

    df = pd.DataFrame(st.session_state.employees)

    st.dataframe(df, use_container_width=True)

else:
    st.info("No Employee Data Available")

# ================= SEARCH EMPLOYEE =================

st.header("🔍 Search Employee")

search_id = st.text_input("Enter Employee ID")

if st.button("Search"):

    found = False

    for emp in st.session_state.employees:

        if emp["ID"] == search_id:

            st.write(emp)

            found = True

    if not found:
        st.error("Employee Not Found")

# ================= UPDATE EMPLOYEE =================

st.header("✏ Update Employee")

update_id = st.text_input("Employee ID For Update")

new_name = st.text_input("New Name")
new_address = st.text_input("New Address")
new_email = st.text_input("New Email")

new_salary = st.number_input(
    "New Salary",
    min_value=0
)

new_bonus = st.number_input(
    "New Bonus",
    min_value=0
)

if st.button("Update Employee"):

    found = False

    for emp in st.session_state.employees:

        if emp["ID"] == update_id:

            emp["Name"] = new_name
            emp["Address"] = new_address
            emp["Email"] = new_email
            emp["Salary"] = new_salary
            emp["Bonus"] = new_bonus

            deduction = (new_salary / 30) * emp["Leave"]

            emp["Net Salary"] = (
                new_salary + new_bonus - deduction
            )

            found = True

            st.success("✅ Employee Updated Successfully")

    if not found:
        st.error("Employee ID Not Found")

# ================= DELETE EMPLOYEE =================

st.header("🗑 Delete Employee")

delete_id = st.text_input("Employee ID For Delete")

if st.button("Delete Employee"):

    new_list = []

    found = False

    for emp in st.session_state.employees:

        if emp["ID"] != delete_id:
            new_list.append(emp)

        else:
            found = True

    st.session_state.employees = new_list

    if found:
        st.success("✅ Employee Deleted Successfully")

    else:
        st.error("Employee ID Not Found")

# ================= DOWNLOAD CSV =================

st.header("⬇ Download Data")

if st.session_state.employees:

    df = pd.DataFrame(st.session_state.employees)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="employee_payroll.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Made with Python + Streamlit")