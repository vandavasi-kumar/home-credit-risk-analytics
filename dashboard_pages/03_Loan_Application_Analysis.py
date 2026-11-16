import streamlit as st
import pandas as pd

def app(data):
    # 1. Page Heading and Description
    st.title("Loan Application Analysis", anchor=False)
    st.write("Analyze loan amounts, contract types, and key ratios for Home Credit applications.")
    st.divider()

    if data is None:
        st.error("No dataset available to display. Please verify that data/application_train.csv is loaded.")
        return

    # Handle cases where no records match the filters
    if data.empty:
        return

    # Filters
    def reset_loan_filters():
        st.session_state["loan_sel_contract"] = "All"
        st.session_state["loan_sel_gender"] = "All"
        st.session_state["loan_sel_target"] = "All"
        st.session_state["loan_sel_income"] = "All"
        st.session_state["loan_sel_credit"] = "All"

    with st.container(border=True):
        st.subheader("Filter Options", anchor=False)
        col_f1, col_f2, col_f3, col_f4, col_f5, col_f6 = st.columns([2, 2, 2, 2, 2, 1.2])

        with col_f1:
            contract_options = ["All"] + sorted(data["NAME_CONTRACT_TYPE"].dropna().unique().tolist()) if "NAME_CONTRACT_TYPE" in data.columns else ["All"]
            if "loan_sel_contract" in st.session_state and st.session_state["loan_sel_contract"] not in contract_options:
                st.session_state["loan_sel_contract"] = "All"
            sel_contract = st.selectbox("Contract Type", contract_options, key="loan_sel_contract")

        with col_f2:
            gender_options = ["All"] + sorted(data["CODE_GENDER"].dropna().unique().tolist()) if "CODE_GENDER" in data.columns else ["All"]
            if "loan_sel_gender" in st.session_state and st.session_state["loan_sel_gender"] not in gender_options:
                st.session_state["loan_sel_gender"] = "All"
            sel_gender = st.selectbox("Gender", gender_options, key="loan_sel_gender")

        with col_f3:
            target_options = ["All", "0 - Non-Default", "1 - Default"]
            if "loan_sel_target" in st.session_state and st.session_state["loan_sel_target"] not in target_options:
                st.session_state["loan_sel_target"] = "All"
            sel_target = st.selectbox("Target (Default)", target_options, key="loan_sel_target")

        with col_f4:
            income_bands = ["All", "< 100K", "100K-150K", "150K-200K", "200K-300K", "300K+"]
            if "loan_sel_income" in st.session_state and st.session_state["loan_sel_income"] not in income_bands:
                st.session_state["loan_sel_income"] = "All"
            sel_income = st.selectbox("Income Range", income_bands, key="loan_sel_income")

        with col_f5:
            credit_bands = ["All", "< 250K", "250K-500K", "500K-750K", "750K-1M", "1M+"]
            if "loan_sel_credit" in st.session_state and st.session_state["loan_sel_credit"] not in credit_bands:
                st.session_state["loan_sel_credit"] = "All"
            sel_credit = st.selectbox("Credit Amount Range", credit_bands, key="loan_sel_credit")

        with col_f6:
            st.write("")
            st.write("")
            st.button("Reset Filters", key="loan_reset_btn", on_click=reset_loan_filters, use_container_width=True)

    # Filtered data
    filtered_df = data

    if sel_contract != "All" and "NAME_CONTRACT_TYPE" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["NAME_CONTRACT_TYPE"] == sel_contract]

    if sel_gender != "All" and "CODE_GENDER" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["CODE_GENDER"] == sel_gender]

    if sel_target != "All" and "TARGET" in filtered_df.columns:
        if sel_target == "0 - Non-Default":
            filtered_df = filtered_df[filtered_df["TARGET"] == 0]
        elif sel_target == "1 - Default":
            filtered_df = filtered_df[filtered_df["TARGET"] == 1]

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

    if sel_credit != "All" and "AMT_CREDIT" in filtered_df.columns:
        cred = filtered_df["AMT_CREDIT"]
        if sel_credit == "< 250K":
            filtered_df = filtered_df[cred < 250000]
        elif sel_credit == "250K-500K":
            filtered_df = filtered_df[(cred >= 250000) & (cred < 500000)]
        elif sel_credit == "500K-750K":
            filtered_df = filtered_df[(cred >= 500000) & (cred < 750000)]
        elif sel_credit == "750K-1M":
            filtered_df = filtered_df[(cred >= 750000) & (cred < 1000000)]
        elif sel_credit == "1M+":
            filtered_df = filtered_df[cred >= 1000000]

    if filtered_df.empty:
        st.warning("No records match the selected loan application filter criteria.")
        return

    st.divider()

    # Metrics
    total_applications = len(filtered_df)

    if "NAME_CONTRACT_TYPE" in filtered_df.columns:
        cash_loans = int((filtered_df["NAME_CONTRACT_TYPE"] == "Cash loans").sum())
        revolving_loans = int((filtered_df["NAME_CONTRACT_TYPE"] == "Revolving loans").sum())
        cash_share = (cash_loans / total_applications * 100) if total_applications > 0 else 0.0
    else:
        cash_loans = 0
        revolving_loans = 0
        cash_share = 0.0

    if "AMT_CREDIT" in filtered_df.columns and not filtered_df["AMT_CREDIT"].dropna().empty:
        total_credit = float(filtered_df["AMT_CREDIT"].dropna().sum())
        avg_credit = float(filtered_df["AMT_CREDIT"].dropna().mean())
        median_credit = float(filtered_df["AMT_CREDIT"].dropna().median())
    else:
        total_credit = 0.0
        avg_credit = 0.0
        median_credit = 0.0

    if "AMT_GOODS_PRICE" in filtered_df.columns and not filtered_df["AMT_GOODS_PRICE"].dropna().empty:
        avg_goods_price = float(filtered_df["AMT_GOODS_PRICE"].dropna().mean())
    else:
        avg_goods_price = 0.0

    # Ratios
    if "AMT_CREDIT" in filtered_df.columns and "AMT_INCOME_TOTAL" in filtered_df.columns:
        valid_lti = (filtered_df["AMT_CREDIT"] / filtered_df["AMT_INCOME_TOTAL"]).dropna()
        avg_loan_to_income = float(valid_lti.mean()) if not valid_lti.empty else 0.0
    else:
        avg_loan_to_income = 0.0

    if "AMT_ANNUITY" in filtered_df.columns and "AMT_INCOME_TOTAL" in filtered_df.columns:
        valid_ati = ((filtered_df["AMT_ANNUITY"] / filtered_df["AMT_INCOME_TOTAL"]) * 100).dropna()
        avg_annuity_to_income = float(valid_ati.mean()) if not valid_ati.empty else 0.0
    else:
        avg_annuity_to_income = 0.0

    # Display KPI Metrics
    st.subheader("Key Performance Indicators (KPIs)", anchor=False)

    # Row 1: 5 KPIs
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        with st.container(border=True):
            st.caption("Total Applications")
            st.markdown(f"##### {total_applications:,}")

    with kpi2:
        with st.container(border=True):
            st.caption("Total Cash Loans")
            st.markdown(f"##### {cash_loans:,}")

    with kpi3:
        with st.container(border=True):
            st.caption("Total Revolving Loans")
            st.markdown(f"##### {revolving_loans:,}")

    with kpi4:
        with st.container(border=True):
            st.caption("Cash Loan Share")
            st.markdown(f"##### {cash_share:.1f}%")

    with kpi5:
        with st.container(border=True):
            st.caption("Total Loan Amount")
            st.markdown(f"##### ${total_credit:,.2f}")

    # Row 2: 5 KPIs
    kpi6, kpi7, kpi8, kpi9, kpi10 = st.columns(5)
    with kpi6:
        with st.container(border=True):
            st.caption("Average Loan Amount")
            st.markdown(f"##### ${avg_credit:,.2f}")

    with kpi7:
        with st.container(border=True):
            st.caption("Median Loan Amount")
            st.markdown(f"##### ${median_credit:,.2f}")

    with kpi8:
        with st.container(border=True):
            st.caption("Avg Loan-to-Income")
            st.markdown(f"##### {avg_loan_to_income:.2f}")

    with kpi9:
        with st.container(border=True):
            st.caption("Avg Annuity-to-Income")
            st.markdown(f"##### {avg_annuity_to_income:.2f}%")

    with kpi10:
        with st.container(border=True):
            st.caption("Average Goods Price")
            st.markdown(f"##### ${avg_goods_price:,.2f}")

    st.divider()

    # Charts
    st.subheader("Visual Analytics", anchor=False)

    # Row 1: Loan Amount Distribution & Credit Amount by Contract Type
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Loan Amount Distribution**")
            if "AMT_CREDIT" in filtered_df.columns and not filtered_df["AMT_CREDIT"].dropna().empty:
                credit_bins = pd.cut(
                    filtered_df["AMT_CREDIT"].dropna(),
                    bins=[0, 250000, 500000, 750000, 1000000, 1500000, float("inf")],
                    labels=["< 250K", "250K-500K", "500K-750K", "750K-1M", "1M-1.5M", "1.5M+"]
                )
                credit_distribution = pd.DataFrame({"Applications": credit_bins.value_counts().sort_index()})
                st.bar_chart(credit_distribution, y="Applications", color="#1B365D")
            else:
                st.info("Credit amount data not available.")

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Credit Amount by Contract Type**")
            if (
                "NAME_CONTRACT_TYPE" in filtered_df.columns and
                "AMT_CREDIT" in filtered_df.columns and
                not filtered_df.empty
            ):
                avg_credit_contract = filtered_df.groupby("NAME_CONTRACT_TYPE")["AMT_CREDIT"].mean()
                avg_credit_df = pd.DataFrame({"Average Credit Amount ($)": avg_credit_contract})
                st.bar_chart(avg_credit_df, y="Average Credit Amount ($)", color="#0D9488")
            else:
                st.info("Contract type or credit data not available.")

    # Row 2: Loan-to-Income Distribution & Annuity-to-Income Comparison
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        with st.container(border=True):
            st.markdown("**Loan-to-Income Distribution**")
            if "AMT_CREDIT" in filtered_df.columns and "AMT_INCOME_TOTAL" in filtered_df.columns:
                lti_series = (filtered_df["AMT_CREDIT"] / filtered_df["AMT_INCOME_TOTAL"]).dropna()
                if not lti_series.empty:
                    lti_bins = pd.cut(
                        lti_series,
                        bins=[0, 2, 4, 6, 8, float("inf")],
                        labels=["< 2x", "2x-4x", "4x-6x", "6x-8x", "8x+"]
                    )
                    lti_dist = pd.DataFrame({"Applications": lti_bins.value_counts().sort_index()})
                    st.bar_chart(lti_dist, y="Applications", color="#1B365D")
                else:
                    st.info("No valid loan-to-income data.")
            else:
                st.info("Loan or income columns not available.")

    with chart_col4:
        with st.container(border=True):
            st.markdown("**Annuity-to-Income Comparison by Contract Type**")
            if (
                "NAME_CONTRACT_TYPE" in filtered_df.columns and
                "AMT_ANNUITY" in filtered_df.columns and
                "AMT_INCOME_TOTAL" in filtered_df.columns and
                not filtered_df.empty
            ):
                temp_df = filtered_df.dropna(subset=["AMT_ANNUITY", "AMT_INCOME_TOTAL", "NAME_CONTRACT_TYPE"]).copy()
                if not temp_df.empty:
                    temp_df["ATI_RATIO"] = (temp_df["AMT_ANNUITY"] / temp_df["AMT_INCOME_TOTAL"]) * 100
                    ati_by_contract = temp_df.groupby("NAME_CONTRACT_TYPE")["ATI_RATIO"].mean()
                    ati_df = pd.DataFrame({"Avg Annuity-to-Income (%)": ati_by_contract})
                    st.bar_chart(ati_df, y="Avg Annuity-to-Income (%)", color="#0D9488")
                else:
                    st.info("No valid annuity-to-income records.")
            else:
                st.info("Annuity, income, or contract type data not available.")

    # Row 3: Contract Type Share & Default Rate by Contract Type
    chart_col5, chart_col6 = st.columns(2)

    with chart_col5:
        with st.container(border=True):
            st.markdown("**Contract Type Share**")
            if "NAME_CONTRACT_TYPE" in filtered_df.columns and not filtered_df["NAME_CONTRACT_TYPE"].dropna().empty:
                contract_counts = filtered_df["NAME_CONTRACT_TYPE"].value_counts()
                contract_df = pd.DataFrame({"Applications": contract_counts})
                st.bar_chart(contract_df, y="Applications", color="#1B365D")
            else:
                st.info("Contract type data not available.")

    with chart_col6:
        with st.container(border=True):
            st.markdown("**Default Rate by Contract Type (%)**")
            if (
                "NAME_CONTRACT_TYPE" in filtered_df.columns and
                "TARGET" in filtered_df.columns and
                not filtered_df.empty
            ):
                default_rate_contract = filtered_df.groupby("NAME_CONTRACT_TYPE")["TARGET"].mean() * 100
                default_contract_df = pd.DataFrame({"Default Rate (%)": default_rate_contract})
                st.bar_chart(default_contract_df, y="Default Rate (%)", color="#0D9488")
            else:
                st.info("Contract type or target data not available.")

    # Show data
    st.divider()
    st.subheader("Loan Application Details", anchor=False)
    preview_columns = [
        "SK_ID_CURR",
        "NAME_CONTRACT_TYPE",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "AMT_GOODS_PRICE",
        "NAME_TYPE_SUITE",
        "TARGET",
    ]
    available_preview_cols = [c for c in preview_columns if c in filtered_df.columns]
    with st.container(border=True):
        if available_preview_cols:
            st.dataframe(filtered_df[available_preview_cols].head(20), use_container_width=True)
        else:
            st.dataframe(filtered_df.head(20), use_container_width=True)

if __name__ == "__main__":
    try:
        sample_data = pd.read_csv("data/application_train.csv")
    except Exception:
        sample_data = None
    app(sample_data)
