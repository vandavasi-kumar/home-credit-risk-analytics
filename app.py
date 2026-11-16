import streamlit as st
import pandas as pd
import importlib.util
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="Home Credit Risk Analytics",
    layout="wide"
)

# Cached function to load dataset
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("data/application_train.csv")
        return data
    except Exception as error:
        st.error(f"Error loading dataset: {error}")
        return None

# Load the data
df = load_data()

# 1. Sidebar Navigation
st.sidebar.title("Navigation", anchor=False)

navigation_options = [
    "Executive Overview",
    "Customer Demographics",
    "Loan Application Analysis",
    "Default Risk Analysis",
    "Income & Employment",
    "Credit Bureau Analysis",
    "Previous Loan Applications",
    "Repayment & Installments",
    "ML Default Prediction",
    "Reports & Data Download"
]

# Track selected page in session state
if "current_page" not in st.session_state:
    st.session_state["current_page"] = navigation_options[0]

# Render each page as a clickable navigation item in a vertical list
for page_name in navigation_options:
    is_active = (st.session_state["current_page"] == page_name)
    if st.sidebar.button(
        page_name,
        key=f"nav_btn_{page_name}",
        use_container_width=True,
        type="primary" if is_active else "secondary"
    ):
        if st.session_state["current_page"] != page_name:
            st.session_state["current_page"] = page_name
            st.rerun()

selected_section = st.session_state["current_page"]

# 2. Global Filter State Management
if df is not None:
    # Safely determine minimum and maximum values for range sliders
    if "AMT_INCOME_TOTAL" in df.columns and not df["AMT_INCOME_TOTAL"].dropna().empty:
        min_income = float(df["AMT_INCOME_TOTAL"].min())
        max_income = float(df["AMT_INCOME_TOTAL"].max())
    else:
        min_income = 0.0
        max_income = 1000000.0

    if min_income >= max_income:
        max_income = min_income + 1000.0

    if "AMT_CREDIT" in df.columns and not df["AMT_CREDIT"].dropna().empty:
        min_credit = float(df["AMT_CREDIT"].min())
        max_credit = float(df["AMT_CREDIT"].max())
    else:
        min_credit = 0.0
        max_credit = 1000000.0

    if min_credit >= max_credit:
        max_credit = min_credit + 1000.0

    st.session_state["global_bounds"] = {
        "min_income": min_income,
        "max_income": max_income,
        "min_credit": min_credit,
        "max_credit": max_credit,
    }

    default_filters = {
        "gender": "All",
        "contract": "All",
        "target": "All",
        "income": (min_income, max_income),
        "credit": (min_credit, max_credit),
    }

    if "global_applied_filters" not in st.session_state:
        st.session_state["global_applied_filters"] = default_filters

    # 3. Apply Filters to Dataset
    applied = st.session_state["global_applied_filters"]
    filtered_df = df

    if applied.get("gender", "All") != "All" and "CODE_GENDER" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["CODE_GENDER"] == applied["gender"]]

    if applied.get("contract", "All") != "All" and "NAME_CONTRACT_TYPE" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["NAME_CONTRACT_TYPE"] == applied["contract"]]

    if applied.get("target", "All") == "0 - No Payment Difficulties" and "TARGET" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["TARGET"] == 0]
    elif applied.get("target", "All") == "1 - Payment Difficulties" and "TARGET" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["TARGET"] == 1]

    if "income" in applied and "AMT_INCOME_TOTAL" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["AMT_INCOME_TOTAL"].notna() &
            (filtered_df["AMT_INCOME_TOTAL"] >= applied["income"][0]) &
            (filtered_df["AMT_INCOME_TOTAL"] <= applied["income"][1])
        ]

    if "credit" in applied and "AMT_CREDIT" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["AMT_CREDIT"].notna() &
            (filtered_df["AMT_CREDIT"] >= applied["credit"][0]) &
            (filtered_df["AMT_CREDIT"] <= applied["credit"][1])
        ]

    # Show warning if no records match
    if filtered_df.empty:
        st.warning("No records match the selected filter criteria. Please adjust your filters or click Reset Filters.")

# Mapping of section names to page filenames
page_mapping = {
    "Executive Overview": "01_Executive_Overview.py",
    "Customer Demographics": "02_Customer_Demographics.py",
    "Loan Application Analysis": "03_Loan_Application_Analysis.py",
    "Default Risk Analysis": "04_Default_Risk_Analysis.py",
    "Income & Employment": "05_Income_Employment.py",
    "Credit Bureau Analysis": "06_Credit_Bureau_Analysis.py",
    "Previous Loan Applications": "07_Previous_Loan_Applications.py",
    "Repayment & Installments": "08_Repayment_Installments.py",
    "ML Default Prediction": "09_ML_Default_Prediction.py",
    "Reports & Data Download": "10_Reports_Data_Download.py"
}

# Function to dynamically load and display a page
def load_page(page_name, data):
    file_name = page_mapping.get(page_name)
    page_path = Path(__file__).parent / "dashboard_pages" / file_name

    # Check if page file exists
    if not page_path.exists():
        st.error(f"Page file not found: {page_path}")
        return

    # Dynamically import and run page
    try:
        spec = importlib.util.spec_from_file_location(page_name, page_path)
        if spec is None or spec.loader is None:
            st.error(f"Could not load specification for {file_name}")
            return

        page_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(page_module)

        # Call app(data) function
        if hasattr(page_module, "app"):
            page_module.app(data)
        else:
            st.error(f"Function 'app(data)' not found in {file_name}")
    except Exception as error:
        st.error(f"Error loading page '{page_name}': {error}")

# Run the selected page if dataset loaded safely
if df is not None:
    load_page(selected_section, filtered_df)
else:
    st.error("Cannot display page because the dataset could not be loaded. Please ensure data/application_train.csv is present.")
