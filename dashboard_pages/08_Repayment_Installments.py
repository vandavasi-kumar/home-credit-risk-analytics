import streamlit as st
import pandas as pd

def app(data):
    # 1. Page Heading and Description
    st.title("Repayment & Installments", anchor=False)
    st.caption("Evaluate applicant repayment affordability, debt burden ratios, and default risk indicators.")
    st.divider()

    if data is None:
        st.error("No dataset available to display. Please verify that data/application_train.csv is loaded.")
        return

    # Handle cases where no records match the filters
    if data.empty:
        st.warning("No records found matching the criteria.")
        return

    filtered_df = data.copy()

    

    # 2. Compute Affordability Features
    if "AMT_ANNUITY" in filtered_df.columns and "AMT_INCOME_TOTAL" in filtered_df.columns:
        filtered_df["ANNUITY_INCOME_RATIO"] = (filtered_df["AMT_ANNUITY"] / filtered_df["AMT_INCOME_TOTAL"]) * 100
    else:
        filtered_df["ANNUITY_INCOME_RATIO"] = pd.Series(dtype=float)

    if "AMT_CREDIT" in filtered_df.columns and "AMT_INCOME_TOTAL" in filtered_df.columns:
        filtered_df["CREDIT_INCOME_RATIO"] = filtered_df["AMT_CREDIT"] / filtered_df["AMT_INCOME_TOTAL"]
    else:
        filtered_df["CREDIT_INCOME_RATIO"] = pd.Series(dtype=float)

    if "AMT_CREDIT" in filtered_df.columns and "AMT_ANNUITY" in filtered_df.columns:
        filtered_df["IMPLIED_TERM_YEARS"] = filtered_df["AMT_CREDIT"] / filtered_df["AMT_ANNUITY"]
    else:
        filtered_df["IMPLIED_TERM_YEARS"] = pd.Series(dtype=float)

    # 3. KPI Metrics Calculations
    total_records = len(filtered_df)
    avg_annuity = float(filtered_df["AMT_ANNUITY"].dropna().mean()) if "AMT_ANNUITY" in filtered_df.columns and not filtered_df["AMT_ANNUITY"].dropna().empty else 0.0

    valid_dti = filtered_df["ANNUITY_INCOME_RATIO"].dropna()
    avg_dti = float(valid_dti.mean()) if not valid_dti.empty else 0.0

    valid_leverage = filtered_df["CREDIT_INCOME_RATIO"].dropna()
    avg_leverage = float(valid_leverage.mean()) if not valid_leverage.empty else 0.0

    valid_term = filtered_df["IMPLIED_TERM_YEARS"].dropna()
    avg_term = float(valid_term.mean()) if not valid_term.empty else 0.0

    high_burden_count = int((valid_dti > 30.0).sum()) if not valid_dti.empty else 0
    default_rate = float((filtered_df["TARGET"] == 1).mean() * 100) if "TARGET" in filtered_df.columns and total_records > 0 else 0.0

    st.subheader("Key Performance Indicators", anchor=False)
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        with st.container(border=True):
            st.caption("Average Loan Annuity")
            st.markdown(f"##### ${avg_annuity:,.2f}")
    with kpi2:
        with st.container(border=True):
            st.caption("Annuity / Income Ratio")
            st.markdown(f"##### {avg_dti:.1f}%")
    with kpi3:
        with st.container(border=True):
            st.caption("Credit / Income Leverage")
            st.markdown(f"##### {avg_leverage:.2f}x")
    with kpi4:
        with st.container(border=True):
            st.caption("High Debt Burden (>30%)")
            st.markdown(f"##### {high_burden_count:,}")
    with kpi5:
        with st.container(border=True):
            st.caption("Implied Repayment Term")
            st.markdown(f"##### {avg_term:.1f} yrs")
    with kpi6:
        with st.container(border=True):
            st.caption("Overall Default Rate")
            st.markdown(f"##### {default_rate:.2f}%")

    st.divider()

    # 4. Visual Analytics Section
    st.subheader("Visual Analytics", anchor=False)

    # Row 1: Annuity-to-Income Burden Distribution & Credit-to-Income Leverage Distribution
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Annuity-to-Income Ratio Distribution (DTI)**")
            st.caption("Distribution of applicants by debt-to-income percentage")
            if not valid_dti.empty:
                dti_bins = pd.cut(
                    valid_dti,
                    bins=[0, 10, 20, 30, 40, float("inf")],
                    labels=["< 10%", "10-20%", "20-30%", "30-40%", "40%+"]
                )
                st.bar_chart(pd.DataFrame({"Applications": dti_bins.value_counts().sort_index()}), y="Applications", color="#1B365D")
            else:
                st.info("Annuity or income data not available.")

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Credit-to-Income Leverage Distribution**")
            st.caption("Distribution of credit amount relative to annual income")
            if not valid_leverage.empty:
                lev_bins = pd.cut(
                    valid_leverage,
                    bins=[0, 2, 4, 6, 8, float("inf")],
                    labels=["< 2x", "2-4x", "4-6x", "6-8x", "8x+"]
                )
                st.bar_chart(pd.DataFrame({"Applications": lev_bins.value_counts().sort_index()}), y="Applications", color="#1B365D")
            else:
                st.info("Credit or income data not available.")

    # Row 2: Default Rate by DTI & Default Rate by Leverage
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        with st.container(border=True):
            st.markdown("**Default Rate by Annuity-to-Income Ratio**")
            st.caption("Default incidence across debt-to-income tiers")
            if not valid_dti.empty and "TARGET" in filtered_df.columns and not filtered_df.empty:
                dti_bins_grp = pd.cut(
                    filtered_df["ANNUITY_INCOME_RATIO"],
                    bins=[0, 10, 20, 30, 40, float("inf")],
                    labels=["< 10%", "10-20%", "20-30%", "30-40%", "40%+"]
                )
                dti_default = filtered_df.groupby(dti_bins_grp, observed=False)["TARGET"].mean() * 100
                st.bar_chart(pd.DataFrame({"Default Rate (%)": dti_default}), y="Default Rate (%)", color="#0D9488")
            else:
                st.info("DTI or target data not available.")

    with chart_col4:
        with st.container(border=True):
            st.markdown("**Default Rate by Credit-to-Income Leverage**")
            st.caption("Default incidence across leverage multiples")
            if not valid_leverage.empty and "TARGET" in filtered_df.columns and not filtered_df.empty:
                lev_bins_grp = pd.cut(
                    filtered_df["CREDIT_INCOME_RATIO"],
                    bins=[0, 2, 4, 6, 8, float("inf")],
                    labels=["< 2x", "2-4x", "4-6x", "6-8x", "8x+"]
                )
                lev_default = filtered_df.groupby(lev_bins_grp, observed=False)["TARGET"].mean() * 100
                st.bar_chart(pd.DataFrame({"Default Rate (%)": lev_default}), y="Default Rate (%)", color="#0D9488")
            else:
                st.info("Leverage or target data not available.")

    # Row 3: Annuity vs Income Scatter & Annuity-to-Income Burden by Age Group
    chart_col5, chart_col6 = st.columns(2)

    with chart_col5:
        with st.container(border=True):
            st.markdown("**Annuity vs Annual Income (Sampled)**")
            st.caption("Scatter relationship between applicant income and loan annuity")
            if "AMT_INCOME_TOTAL" in filtered_df.columns and "AMT_ANNUITY" in filtered_df.columns:
                scatter_sample = filtered_df[["AMT_INCOME_TOTAL", "AMT_ANNUITY"]].dropna()
                # Trim extreme income outliers for clearer visualization
                scatter_sample = scatter_sample[scatter_sample["AMT_INCOME_TOTAL"] <= 1000000]
                if len(scatter_sample) > 1000:
                    scatter_sample = scatter_sample.sample(n=1000, random_state=42)
                if not scatter_sample.empty:
                    st.scatter_chart(scatter_sample, x="AMT_INCOME_TOTAL", y="AMT_ANNUITY", color="#1B365D")
                else:
                    st.info("No records available to display scatter chart.")
            else:
                st.info("Income or annuity data not available.")

    with chart_col6:
        with st.container(border=True):
            st.markdown("**Average Annuity / Income Ratio by Age Group**")
            st.caption("Mean debt service burden across borrower age brackets")
            if "DAYS_BIRTH" in filtered_df.columns and not valid_dti.empty:
                age_years = filtered_df["DAYS_BIRTH"].abs() / 365
                age_bins = pd.cut(
                    age_years,
                    bins=[0, 30, 40, 50, 60, 100],
                    labels=["< 30", "30-40", "40-50", "50-60", "60+"]
                )
                age_dti = filtered_df.groupby(age_bins, observed=False)["ANNUITY_INCOME_RATIO"].mean()
                st.bar_chart(pd.DataFrame({"Avg DTI (%)": age_dti}), y="Avg DTI (%)", color="#1B365D")
            else:
                st.info("Age or DTI data not available.")

    st.divider()

    # 5. Data Preview
    st.subheader("Sample Repayment & Affordability Indicators", anchor=False)
    with st.container(border=True):
        preview_df = filtered_df.copy()
        if "DAYS_BIRTH" in preview_df.columns:
            preview_df["AGE_YEARS"] = (preview_df["DAYS_BIRTH"].abs() / 365).round(1)

        preview_df["ANNUITY_INCOME_RATIO"] = preview_df["ANNUITY_INCOME_RATIO"].round(2)
        preview_df["CREDIT_INCOME_RATIO"] = preview_df["CREDIT_INCOME_RATIO"].round(2)

        preview_cols = [
            "SK_ID_CURR", "TARGET", "AMT_INCOME_TOTAL",
            "AMT_CREDIT", "AMT_ANNUITY", "ANNUITY_INCOME_RATIO",
            "CREDIT_INCOME_RATIO", "AGE_YEARS"
        ]
        disp_cols = [c for c in preview_cols if c in preview_df.columns]
        if disp_cols:
            st.dataframe(preview_df[disp_cols].head(20), use_container_width=True)
        else:
            st.dataframe(filtered_df.head(20), use_container_width=True)

if __name__ == "__main__":
    try:
        sample_data = pd.read_csv("data/application_train.csv")
    except Exception:
        sample_data = None
    app(sample_data)
