import streamlit as st
import pandas as pd

def app(data):
    st.title("Default Risk Analysis", anchor=False)
    st.write("Analyze loan default patterns and identify high-risk customer segments.")
    st.divider()

    if data is None:
        st.error("No dataset available to display. Please verify that data/application_train.csv is loaded.")
        return

    if data.empty:
        return

    # Filters
    def reset_risk_filters():
        st.session_state["risk_sel_contract"] = "All"
        st.session_state["risk_sel_gender"] = "All"
        st.session_state["risk_sel_edu"] = "All"
        st.session_state["risk_sel_income"] = "All"
        st.session_state["risk_sel_age"] = "All"

    with st.container(border=True):
        st.subheader("Filter Options", anchor=False)
        col_f1, col_f2, col_f3, col_f4, col_f5, col_f6 = st.columns([2, 2, 2, 2, 2, 1.2])

        with col_f1:
            contract_options = ["All"] + sorted(data["NAME_CONTRACT_TYPE"].dropna().unique().tolist()) if "NAME_CONTRACT_TYPE" in data.columns else ["All"]
            if "risk_sel_contract" in st.session_state and st.session_state["risk_sel_contract"] not in contract_options:
                st.session_state["risk_sel_contract"] = "All"
            sel_contract = st.selectbox("Contract Type", contract_options, key="risk_sel_contract")

        with col_f2:
            gender_options = ["All"] + sorted(data["CODE_GENDER"].dropna().unique().tolist()) if "CODE_GENDER" in data.columns else ["All"]
            if "risk_sel_gender" in st.session_state and st.session_state["risk_sel_gender"] not in gender_options:
                st.session_state["risk_sel_gender"] = "All"
            sel_gender = st.selectbox("Gender", gender_options, key="risk_sel_gender")

        with col_f3:
            edu_options = ["All"] + sorted(data["NAME_EDUCATION_TYPE"].dropna().unique().tolist()) if "NAME_EDUCATION_TYPE" in data.columns else ["All"]
            if "risk_sel_edu" in st.session_state and st.session_state["risk_sel_edu"] not in edu_options:
                st.session_state["risk_sel_edu"] = "All"
            sel_edu = st.selectbox("Education", edu_options, key="risk_sel_edu")

        with col_f4:
            income_bands = ["All", "< 100K", "100K-150K", "150K-200K", "200K-300K", "300K+"]
            if "risk_sel_income" in st.session_state and st.session_state["risk_sel_income"] not in income_bands:
                st.session_state["risk_sel_income"] = "All"
            sel_income = st.selectbox("Income Band", income_bands, key="risk_sel_income")

        with col_f5:
            age_options = ["All", "< 30", "30-40", "40-50", "50-60", "60+"]
            if "risk_sel_age" in st.session_state and st.session_state["risk_sel_age"] not in age_options:
                st.session_state["risk_sel_age"] = "All"
            sel_age = st.selectbox("Age Group", age_options, key="risk_sel_age")

        with col_f6:
            st.write("")
            st.write("")
            st.button("Reset Filters", key="risk_reset_btn", on_click=reset_risk_filters, use_container_width=True)

    # Filtered data
    filtered_df = data

    if sel_contract != "All" and "NAME_CONTRACT_TYPE" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["NAME_CONTRACT_TYPE"] == sel_contract]

    if sel_gender != "All" and "CODE_GENDER" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["CODE_GENDER"] == sel_gender]

    if sel_edu != "All" and "NAME_EDUCATION_TYPE" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["NAME_EDUCATION_TYPE"] == sel_edu]

    if sel_income != "All" and "AMT_INCOME_TOTAL" in filtered_df.columns:
        inc = filtered_df["AMT_INCOME_TOTAL"]
        if sel_income == "< 100K":
            filtered_df = filtered_df[inc < 100000]
        elif sel_income == "100K-150K":
            filtered_df = filtered_df[(inc >= 100000) & (inc < 150000)]
        elif sel_income == "150K-200K":
            filtered_df = filtered_df[(inc >= 150000) & (inc < 200000)]
        elif sel_income == "200K-300K":
            filtered_df = filtered_df[(inc >= 200000) & (inc < 300000)]
        elif sel_income == "300K+":
            filtered_df = filtered_df[inc >= 300000]

    if sel_age != "All" and "DAYS_BIRTH" in filtered_df.columns:
        age_years = filtered_df["DAYS_BIRTH"].abs() / 365
        if sel_age == "< 30":
            filtered_df = filtered_df[age_years < 30]
        elif sel_age == "30-40":
            filtered_df = filtered_df[(age_years >= 30) & (age_years < 40)]
        elif sel_age == "40-50":
            filtered_df = filtered_df[(age_years >= 40) & (age_years < 50)]
        elif sel_age == "50-60":
            filtered_df = filtered_df[(age_years >= 50) & (age_years < 60)]
        elif sel_age == "60+":
            filtered_df = filtered_df[age_years >= 60]

    if filtered_df.empty:
        st.warning("No records match the selected default risk filter criteria.")
        return

    st.divider()

    # Metrics
    total_applications = len(filtered_df)
    payment_difficulties = int((filtered_df["TARGET"] == 1).sum()) if "TARGET" in filtered_df.columns else 0
    no_difficulties = int((filtered_df["TARGET"] == 0).sum()) if "TARGET" in filtered_df.columns else 0
    default_rate = (payment_difficulties / total_applications * 100) if total_applications > 0 else 0.0

    # High-risk applications proxy (low external risk scores: EXT_SOURCE_2 < 0.3)
    if "EXT_SOURCE_2" in filtered_df.columns:
        high_risk_count = int((filtered_df["EXT_SOURCE_2"].dropna() < 0.3).sum())
    else:
        high_risk_count = payment_difficulties

    # Defaulter averages
    defaulters_df = filtered_df[filtered_df["TARGET"] == 1] if "TARGET" in filtered_df.columns else pd.DataFrame()
    if not defaulters_df.empty:
        avg_credit_defaulters = float(defaulters_df["AMT_CREDIT"].dropna().mean()) if "AMT_CREDIT" in defaulters_df.columns else 0.0
        avg_income_defaulters = float(defaulters_df["AMT_INCOME_TOTAL"].dropna().mean()) if "AMT_INCOME_TOTAL" in defaulters_df.columns else 0.0
    else:
        avg_credit_defaulters = 0.0
        avg_income_defaulters = 0.0

    st.subheader("Key Performance Indicators (KPIs)", anchor=False)

    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7 = st.columns(7)
    with kpi1:
        with st.container(border=True):
            st.caption("Total Applications")
            st.markdown(f"##### {total_applications:,}")

    with kpi2:
        with st.container(border=True):
            st.caption("Total Defaults")
            st.markdown(f"##### {payment_difficulties:,}")

    with kpi3:
        with st.container(border=True):
            st.caption("Non-default Customers")
            st.markdown(f"##### {no_difficulties:,}")

    with kpi4:
        with st.container(border=True):
            st.caption("Overall Default Rate")
            st.markdown(f"##### {default_rate:.2f}%")

    with kpi5:
        with st.container(border=True):
            st.caption("High-risk Applications")
            st.markdown(f"##### {high_risk_count:,}")

    with kpi6:
        with st.container(border=True):
            st.caption("Avg Credit Defaulters")
            st.markdown(f"##### ${avg_credit_defaulters:,.2f}")

    with kpi7:
        with st.container(border=True):
            st.caption("Avg Income Defaulters")
            st.markdown(f"##### ${avg_income_defaulters:,.2f}")

    st.divider()

    # Charts
    st.subheader("Visual Analytics", anchor=False)

    # Row 1: Target Distribution & Default Rate by Gender
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Default vs Non-default**")
            if "TARGET" in filtered_df.columns and not filtered_df["TARGET"].dropna().empty:
                target_counts = filtered_df["TARGET"].value_counts()
                target_df = pd.DataFrame({
                    "Applications": [
                        int(target_counts.get(0, 0)),
                        int(target_counts.get(1, 0))
                    ]
                }, index=["Non-Default (0)", "Default (1)"])
                st.bar_chart(target_df, y="Applications", color="#1B365D")
            else:
                st.info("Target data not available.")

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Default Rate by Gender**")
            if "CODE_GENDER" in filtered_df.columns and "TARGET" in filtered_df.columns and not filtered_df.empty:
                gender_default = filtered_df.groupby("CODE_GENDER")["TARGET"].mean() * 100
                gender_default_df = pd.DataFrame({"Default Rate (%)": gender_default})
                st.bar_chart(gender_default_df, y="Default Rate (%)", color="#0D9488")
            else:
                st.info("Gender or target data not available.")

    # Row 2: Default Rate by Education & Default Rate by Income Band
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        with st.container(border=True):
            st.markdown("**Default Rate by Education**")
            if "NAME_EDUCATION_TYPE" in filtered_df.columns and "TARGET" in filtered_df.columns and not filtered_df.empty:
                edu_default = filtered_df.groupby("NAME_EDUCATION_TYPE")["TARGET"].mean() * 100
                edu_default_df = pd.DataFrame({"Default Rate (%)": edu_default})
                st.bar_chart(edu_default_df, y="Default Rate (%)", color="#1B365D")
            else:
                st.info("Education or target data not available.")

    with chart_col4:
        with st.container(border=True):
            st.markdown("**Default Rate by Income Band**")
            if "AMT_INCOME_TOTAL" in filtered_df.columns and "TARGET" in filtered_df.columns and not filtered_df.empty:
                inc_bins = pd.cut(
                    filtered_df["AMT_INCOME_TOTAL"].dropna(),
                    bins=[0, 100000, 150000, 200000, 300000, float("inf")],
                    labels=["< 100K", "100K-150K", "150K-200K", "200K-300K", "300K+"]
                )
                inc_default = filtered_df.groupby(inc_bins, observed=False)["TARGET"].mean() * 100
                inc_default_df = pd.DataFrame({"Default Rate (%)": inc_default})
                st.bar_chart(inc_default_df, y="Default Rate (%)", color="#0D9488")
            else:
                st.info("Income or target data not available.")

    # Row 3: Default Rate by Age Group & Default Rate by Contract Type
    chart_col5, chart_col6 = st.columns(2)

    with chart_col5:
        with st.container(border=True):
            st.markdown("**Default Rate by Age Group**")
            if "DAYS_BIRTH" in filtered_df.columns and "TARGET" in filtered_df.columns and not filtered_df.empty:
                age_years = filtered_df["DAYS_BIRTH"].abs() / 365
                age_bins = pd.cut(
                    age_years,
                    bins=[0, 30, 40, 50, 60, 100],
                    labels=["< 30", "30-40", "40-50", "50-60", "60+"]
                )
                age_default = filtered_df.groupby(age_bins, observed=False)["TARGET"].mean() * 100
                age_default_df = pd.DataFrame({"Default Rate (%)": age_default})
                st.bar_chart(age_default_df, y="Default Rate (%)", color="#0D9488")
            else:
                st.info("Age or target data not available.")

    with chart_col6:
        with st.container(border=True):
            st.markdown("**Default Rate by Contract Type**")
            if "NAME_CONTRACT_TYPE" in filtered_df.columns and "TARGET" in filtered_df.columns and not filtered_df.empty:
                contract_default = filtered_df.groupby("NAME_CONTRACT_TYPE")["TARGET"].mean() * 100
                contract_default_df = pd.DataFrame({"Default Rate (%)": contract_default})
                st.bar_chart(contract_default_df, y="Default Rate (%)", color="#1B365D")
            else:
                st.info("Contract type or target data not available.")

    # Show data
    st.divider()
    st.subheader("High-Risk Customer Segment", anchor=False)
    if "TARGET" in filtered_df.columns and not filtered_df[filtered_df["TARGET"] == 1].empty:
        high_risk_base = filtered_df[filtered_df["TARGET"] == 1]
    else:
        high_risk_base = filtered_df

    preview_columns = [
        "SK_ID_CURR",
        "TARGET",
        "CODE_GENDER",
        "DAYS_BIRTH",
        "NAME_EDUCATION_TYPE",
        "NAME_CONTRACT_TYPE",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "EXT_SOURCE_2"
    ]
    display_columns = [col for col in preview_columns if col in high_risk_base.columns]
    preview_df = high_risk_base[display_columns].head(20).copy() if display_columns else high_risk_base.head(20).copy()

    if "DAYS_BIRTH" in preview_df.columns:
        preview_df["AGE_YEARS"] = (preview_df["DAYS_BIRTH"].abs() / 365).round(1)
        preview_df = preview_df.drop(columns=["DAYS_BIRTH"])

    with st.container(border=True):
        st.dataframe(preview_df, use_container_width=True)

if __name__ == "__main__":
    try:
        sample_data = pd.read_csv("data/application_train.csv")
    except Exception:
        sample_data = None
    app(sample_data)
