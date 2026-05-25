# app.py

import streamlit as st
import pandas as pd
import sqlite3
import re
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Employee Payroll System",
    page_icon="💼",
    layout="wide"
)

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("employees.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    email TEXT,
    gender TEXT,
    working_days INTEGER,
    leaves INTEGER,
    salary REAL,
    bonus REAL,
    net_salary REAL,
    created_at TEXT
)
""")

conn.commit()

# =========================================================
# FUNCTIONS
# =========================================================

def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)


def calculate_net_salary(salary, bonus, leaves):
    deduction = (salary / 30) * leaves
    return salary + bonus - deduction


def employee_exists(emp_id):
    cursor.execute(
        "SELECT * FROM employees WHERE id=?",
        (emp_id,)
    )
    return cursor.fetchone()


def add_employee(data):
    cursor.execute("""
    INSERT INTO employees VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
    """, data)
    conn.commit()


def get_all_employees():
    query = "SELECT * FROM employees"
    return pd.read_sql_query(query, conn)


def update_employee(data):
    cursor.execute("""
    UPDATE employees
    SET
        name=?,
        address=?,
        email=?,
        gender=?,
        working_days=?,
        leaves=?,
        salary=?,
        bonus=?,
        net_salary=?
    WHERE id=?
    """, data)

    conn.commit()


def delete_employee(emp_id):
    cursor.execute(
        "DELETE FROM employees WHERE id=?",
        (emp_id,)
    )
    conn.commit()


# =========================================================
# TITLE
# =========================================================

st.title("💼 Employee Payroll Management System")

st.markdown("---")

# =========================================================
# SIDEBAR MENU
# =========================================================

st.sidebar.title("📌 Navigation")

if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

if st.sidebar.button("📊 Dashboard"):
    st.session_state.menu = "Dashboard"

if st.sidebar.button("➕ Add Employee"):
    st.session_state.menu = "Add Employee"

if st.sidebar.button("📋 View Employees"):
    st.session_state.menu = "View Employees"

if st.sidebar.button("🔍 Search Employee"):
    st.session_state.menu = "Search Employee"

if st.sidebar.button("✏ Update Employee"):
    st.session_state.menu = "Update Employee"

if st.sidebar.button("🗑 Delete Employee"):
    st.session_state.menu = "Delete Employee"

menu = st.session_state.menu

# =========================================================
# DASHBOARD
# =========================================================

if menu == "Dashboard":

    st.header("📊 Dashboard")

    df = get_all_employees()

    if not df.empty:

        total_emp = len(df)
        total_salary = df["net_salary"].sum()
        avg_salary = df["net_salary"].mean()
        highest_salary = df["net_salary"].max()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Employees", total_emp)
        col2.metric("Total Payroll", f"₹ {total_salary:,.2f}")
        col3.metric("Average Salary", f"₹ {avg_salary:,.2f}")
        col4.metric("Highest Salary", f"₹ {highest_salary:,.2f}")

        st.markdown("---")

        st.subheader("Salary Distribution")

        st.bar_chart(df.set_index("name")["net_salary"])

    else:
        st.info("No employee data available.")

# =========================================================
# ADD EMPLOYEE
# =========================================================

elif menu == "Add Employee":

    st.header("➕ Add Employee")

    with st.form("add_form"):

        col1, col2 = st.columns(2)

        with col1:
            emp_id = st.text_input("Employee ID")
            name = st.text_input("Name")
            email = st.text_input("Email")
            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )

        with col2:
            address = st.text_area("Address")
            working_days = st.number_input(
                "Working Days",
                min_value=0,
                max_value=31,
                value=30
            )

            leaves = st.number_input(
                "Leaves",
                min_value=0,
                max_value=31,
                value=0
            )

        salary = st.number_input(
            "Salary",
            min_value=0.0,
            value=0.0
        )

        bonus = st.number_input(
            "Bonus",
            min_value=0.0,
            value=0.0
        )

        submit = st.form_submit_button("Add Employee")

        if submit:

            if not emp_id or not name:
                st.error("Employee ID and Name are required.")

            elif employee_exists(emp_id):
                st.error("Employee ID already exists.")

            elif not validate_email(email):
                st.error("Invalid email address.")

            else:

                net_salary = calculate_net_salary(
                    salary,
                    bonus,
                    leaves
                )

                data = (
                    emp_id,
                    name,
                    address,
                    email,
                    gender,
                    working_days,
                    leaves,
                    salary,
                    bonus,
                    net_salary,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                add_employee(data)

                st.success(
                    "✅ Employee added successfully."
                )

# =========================================================
# VIEW EMPLOYEES
# =========================================================

elif menu == "View Employees":

    st.header("📋 Employee Records")

    df = get_all_employees()

    if not df.empty:

        st.dataframe(
            df,
            use_container_width=True
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇ Download CSV",
            data=csv,
            file_name="employees.csv",
            mime="text/csv"
        )

    else:
        st.info("No employee records found.")

# =========================================================
# SEARCH EMPLOYEE
# =========================================================

# =========================================================
# SEARCH EMPLOYEE
# =========================================================

elif menu == "Search Employee":

    st.header("🔍 Search Employee")

    search_type = st.radio(
        "Search By",
        ["Employee ID", "Name"]
    )

    search_value = st.text_input(
        "Enter Search Value"
    )

    if st.button("Search"):

        if search_type == "Employee ID":

            query = """
            SELECT * FROM employees
            WHERE id = ?
            """

            df = pd.read_sql_query(
                query,
                conn,
                params=(search_value,)
            )

        else:

            query = """
            SELECT * FROM employees
            WHERE name LIKE ?
            """

            df = pd.read_sql_query(
                query,
                conn,
                params=(f"%{search_value}%",)
            )

        if not df.empty:

            st.success(
                f"{len(df)} employee(s) found."
            )

            st.dataframe(
                df,
                use_container_width=True
            )

        else:
            st.error("No employee found.")

# =========================================================
# UPDATE EMPLOYEE
# =========================================================

elif menu == "Update Employee":

    st.header("✏ Update Employee")

    update_id = st.text_input(
        "Enter Employee ID"
    )

    if st.button("Load Employee"):

        employee = employee_exists(update_id)

        if employee:

            st.session_state.employee_data = employee

        else:
            st.error("Employee not found.")

    if "employee_data" in st.session_state:

        emp = st.session_state.employee_data

        with st.form("update_form"):

            name = st.text_input(
                "Name",
                value=emp[1]
            )

            address = st.text_area(
                "Address",
                value=emp[2]
            )

            email = st.text_input(
                "Email",
                value=emp[3]
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"],
                index=["Male", "Female", "Other"].index(emp[4])
            )

            working_days = st.number_input(
                "Working Days",
                min_value=0,
                max_value=31,
                value=emp[5]
            )

            leaves = st.number_input(
                "Leaves",
                min_value=0,
                max_value=31,
                value=emp[6]
            )

            salary = st.number_input(
                "Salary",
                min_value=0.0,
                value=float(emp[7])
            )

            bonus = st.number_input(
                "Bonus",
                min_value=0.0,
                value=float(emp[8])
            )

            update_btn = st.form_submit_button(
                "Update Employee"
            )

            if update_btn:

                if not validate_email(email):
                    st.error("Invalid email.")

                else:

                    net_salary = calculate_net_salary(
                        salary,
                        bonus,
                        leaves
                    )

                    data = (
                        name,
                        address,
                        email,
                        gender,
                        working_days,
                        leaves,
                        salary,
                        bonus,
                        net_salary,
                        update_id
                    )

                    update_employee(data)

                    st.success(
                        "✅ Employee updated successfully."
                    )

# =========================================================
# DELETE EMPLOYEE
# =========================================================

elif menu == "Delete Employee":

    st.header("🗑 Delete Employee")

    delete_id = st.text_input(
        "Enter Employee ID"
    )

    if st.button("Delete"):

        if employee_exists(delete_id):

            delete_employee(delete_id)

            st.success(
                "✅ Employee deleted successfully."
            )

        else:
            st.error("Employee not found.")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Built with Python, SQLite, Pandas and Streamlit"
)