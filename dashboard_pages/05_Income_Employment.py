import streamlit as st
import pandas as pd

def app(data):
    st.title("Income & Employment", anchor=False)
    st.write("Analyze customer income levels, employment profile, and their relationship with loan default risk.")
    st.divider()

    if data is None:
        st.error("No dataset available to display. Please verify that data/application_train.csv is loaded.")
        return

    if data.empty:
        return

    # Filters
    def reset_inc_filters():
        st.session_state["inc_sel_contract"] = "All"
        st.session_state["inc_sel_type"] = "All"
        st.session_state["inc_sel_occ"] = "All"
        st.session_state["inc_sel_target"] = "All"

    with st.container(border=True):
        st.subheader("Filter Options", anchor=False)
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([2, 2, 2, 2, 1.2])

        with col_f1:
            contract_options = ["All"] + sorted(data["NAME_CONTRACT_TYPE"].dropna().unique().tolist()) if "NAME_CONTRACT_TYPE" in data.columns else ["All"]
            if "inc_sel_contract" in st.session_state and st.session_state["inc_sel_contract"] not in contract_options:
                st.session_state["inc_sel_contract"] = "All"
            sel_contract = st.selectbox("Contract Type", contract_options, key="inc_sel_contract")

        with col_f2:
            inc_types = ["All"] + sorted(data["NAME_INCOME_TYPE"].dropna().unique().tolist()) if "NAME_INCOME_TYPE" in data.columns else ["All"]
            if "inc_sel_type" in st.session_state and st.session_state["inc_sel_type"] not in inc_types:
                st.session_state["inc_sel_type"] = "All"
            sel_inc_type = st.selectbox("Income Type", inc_types, key="inc_sel_type")

        with col_f3:
            occ_types = ["All"] + sorted(data["OCCUPATION_TYPE"].dropna().unique().tolist()) if "OCCUPATION_TYPE" in data.columns else ["All"]
            if "inc_sel_occ" in st.session_state and st.session_state["inc_sel_occ"] not in occ_types:
                st.session_state["inc_sel_occ"] = "All"
            sel_occ_type = st.selectbox("Occupation Type", occ_types, key="inc_sel_occ")

        with col_f4:
            target_options = ["All", "0 - Non-Default", "1 - Default"]
            if "inc_sel_target" in st.session_state and st.session_state["inc_sel_target"] not in target_options:
                st.session_state["inc_sel_target"] = "All"
            sel_target = st.selectbox("Target (Default)", target_options, key="inc_sel_target")

        with col_f5:
            st.write("")
            st.write("")
            st.button("Reset Filters", key="inc_reset_btn", on_click=reset_inc_filters, use_container_width=True)

    # Filtered data
    filtered_df = data

    if sel_contract != "All" and "NAME_CONTRACT_TYPE" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["NAME_CONTRACT_TYPE"] == sel_contract]

    if sel_inc_type != "All" and "NAME_INCOME_TYPE" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["NAME_INCOME_TYPE"] == sel_inc_type]

    if sel_occ_type != "All" and "OCCUPATION_TYPE" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["OCCUPATION_TYPE"] == sel_occ_type]

    if sel_target != "All" and "TARGET" in filtered_df.columns:
        if sel_target == "0 - Non-Default":
            filtered_df = filtered_df[filtered_df["TARGET"] == 0]
        elif sel_target == "1 - Default":
            filtered_df = filtered_df[filtered_df["TARGET"] == 1]

    if filtered_df.empty:
        st.warning("No records match the selected income and employment filter criteria.")
        return

    st.divider()

    # Metrics
    if "AMT_INCOME_TOTAL" in filtered_df.columns and not filtered_df["AMT_INCOME_TOTAL"].dropna().empty:
        avg_income = float(filtered_df["AMT_INCOME_TOTAL"].dropna().mean())
        median_income = float(filtered_df["AMT_INCOME_TOTAL"].dropna().median())
        max_income = float(filtered_df["AMT_INCOME_TOTAL"].dropna().max())
    else:
        avg_income = 0.0
        median_income = 0.0
        max_income = 0.0

    if "DAYS_EMPLOYED" in filtered_df.columns:
        employed_df = filtered_df[filtered_df["DAYS_EMPLOYED"] != 365243]
        total_employed = len(employed_df)
        total_unemployed = len(filtered_df) - total_employed

        if not employed_df["DAYS_EMPLOYED"].dropna().empty:
            avg_employment_years = float((employed_df["DAYS_EMPLOYED"].abs() / 365).mean())
        else:
            avg_employment_years = 0.0

        if "TARGET" in employed_df.columns and total_employed > 0:
            default_rate_employed = float((employed_df["TARGET"] == 1).mean() * 100)
        else:
            default_rate_employed = 0.0
    else:
        total_employed = 0
        total_unemployed = 0
        avg_employment_years = 0.0
        default_rate_employed = 0.0

    st.subheader("Key Performance Indicators (KPIs)", anchor=False)

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        with st.container(border=True):
            st.caption("Average Income")
            st.markdown(f"##### ${avg_income:,.2f}")

    with col2:
        with st.container(border=True):
            st.caption("Median Income")
            st.markdown(f"##### ${median_income:,.2f}")

    with col3:
        with st.container(border=True):
            st.caption("Highest Annual Income")
            st.markdown(f"##### ${max_income:,.2f}")

    with col4:
        with st.container(border=True):
            st.caption("Avg Employment Duration")
            st.markdown(f"##### {avg_employment_years:.1f} years")

    with col5:
        with st.container(border=True):
            st.caption("Employed Customers")
            st.markdown(f"##### {total_employed:,}")

    with col6:
        with st.container(border=True):
            st.caption("Unemployed Customers")
            st.markdown(f"##### {total_unemployed:,}")

    with col7:
        with st.container(border=True):
            st.caption("Default Rate (Employed)")
            st.markdown(f"##### {default_rate_employed:.2f}%")

    # Employment data explanation note

    st.divider()

    # Charts
    st.subheader("Visual Analytics", anchor=False)

    # Row 1: Income Distribution & Average Income by Occupation
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Income Distribution**")
            if "AMT_INCOME_TOTAL" in filtered_df.columns and not filtered_df["AMT_INCOME_TOTAL"].dropna().empty:
                income_bins = pd.cut(
                    filtered_df["AMT_INCOME_TOTAL"].dropna(),
                    bins=[0, 100000, 150000, 200000, 300000, 500000, float("inf")],
                    labels=["< 100K", "100K-150K", "150K-200K", "200K-300K", "300K-500K", "500K+"]
                )
                income_dist = pd.DataFrame({"Applications": income_bins.value_counts().sort_index()})
                st.bar_chart(income_dist, y="Applications", color="#1B365D")
            else:
                st.info("Income data not available.")

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Average Income by Occupation**")
            if "OCCUPATION_TYPE" in filtered_df.columns and "AMT_INCOME_TOTAL" in filtered_df.columns:
                occ_df = filtered_df.dropna(subset=["OCCUPATION_TYPE", "AMT_INCOME_TOTAL"])
                if not occ_df.empty:
                    occ_income = occ_df.groupby("OCCUPATION_TYPE")["AMT_INCOME_TOTAL"].mean().sort_values(ascending=False).head(10)
                    occ_income_df = pd.DataFrame({"Average Income ($)": occ_income})
                    st.bar_chart(occ_income_df, y="Average Income ($)", color="#0D9488")
                else:
                    st.info("No occupation type records with valid income.")
            else:
                st.info("Occupation or income data not available.")

    # Row 2: Employment Duration Distribution & Default Rate by Occupation
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        with st.container(border=True):
            st.markdown("**Employment Duration Distribution**")
            if "DAYS_EMPLOYED" in filtered_df.columns:
                employed_records = filtered_df[filtered_df["DAYS_EMPLOYED"] != 365243]["DAYS_EMPLOYED"].dropna()
                if not employed_records.empty:
                    emp_years = employed_records.abs() / 365
                    emp_bins = pd.cut(
                        emp_years,
                        bins=[0, 2, 5, 10, 15, 100],
                        labels=["< 2 yrs", "2-5 yrs", "5-10 yrs", "10-15 yrs", "15+ yrs"]
                    )
                    emp_dist = pd.DataFrame({"Applications": emp_bins.value_counts().sort_index()})
                    st.bar_chart(emp_dist, y="Applications", color="#1B365D")
                else:
                    st.info("No actively employed applicants found in the filtered records.")
            else:
                st.info("Employment duration data not available.")

    with chart_col4:
        with st.container(border=True):
            st.markdown("**Default Rate by Occupation**")
            if "OCCUPATION_TYPE" in filtered_df.columns and "TARGET" in filtered_df.columns and not filtered_df.empty:
                occ_default = filtered_df.groupby("OCCUPATION_TYPE")["TARGET"].mean().sort_values(ascending=False).head(10) * 100
                occ_default_df = pd.DataFrame({"Default Rate (%)": occ_default})
                st.bar_chart(occ_default_df, y="Default Rate (%)", color="#0D9488")
            else:
                st.info("Occupation or target data not available.")

    # Row 3: Income vs Credit Amount (Full width)
    with st.container(border=True):
        st.markdown("**Income vs Credit Amount**")
        if "AMT_INCOME_TOTAL" in filtered_df.columns and "AMT_CREDIT" in filtered_df.columns:
            scatter_sample = filtered_df[["AMT_INCOME_TOTAL", "AMT_CREDIT"]].dropna()
            if len(scatter_sample) > 1000:
                scatter_sample = scatter_sample.sample(n=1000, random_state=42)
            if not scatter_sample.empty:
                st.scatter_chart(scatter_sample, x="AMT_INCOME_TOTAL", y="AMT_CREDIT", color="#0D9488")
            else:
                st.info("No records available to display scatter chart.")
        else:
            st.info("Income or credit amount data not available.")

    # Show data
    st.divider()
    st.subheader("Customer Income & Employment Details", anchor=False)
    preview_columns = [
        "SK_ID_CURR",
        "TARGET",
        "AMT_INCOME_TOTAL",
        "NAME_INCOME_TYPE",
        "OCCUPATION_TYPE",
        "ORGANIZATION_TYPE",
        "DAYS_EMPLOYED"
    ]
    display_columns = [col for col in preview_columns if col in filtered_df.columns]
    preview_df = filtered_df[display_columns].head(20).copy() if display_columns else filtered_df.head(20).copy()

    if "DAYS_EMPLOYED" in preview_df.columns:
        preview_df["EMPLOYMENT_YEARS"] = preview_df["DAYS_EMPLOYED"].apply(
            lambda d: f"{round(abs(d) / 365, 1)} yrs" if pd.notna(d) and d != 365243 else "Retired / N/A"
        )
        preview_df = preview_df.drop(columns=["DAYS_EMPLOYED"])

    with st.container(border=True):
        st.dataframe(preview_df, use_container_width=True)

if __name__ == "__main__":
    try:
        sample_data = pd.read_csv("data/application_train.csv")
    except Exception:
        sample_data = None
    app(sample_data)
