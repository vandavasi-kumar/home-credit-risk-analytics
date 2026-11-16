import streamlit as st
import pandas as pd

def app(data):
    # 1. Page Heading and Description
    st.title("Previous Loan Applications", anchor=False)
    st.caption("Analyze loan application structures, contract types, and credit characteristics for Home Credit applicants.")
    st.divider()

    if data is None:
        st.error("No dataset available to display. Please verify that data/application_train.csv is loaded.")
        return

    # Handle cases where no records match the filters
    if data.empty:
        st.warning("No records found matching the criteria.")
        return

    filtered_df = data


    # 2. KPI Metrics Calculations
    total_records = len(filtered_df)
    avg_credit = float(filtered_df["AMT_CREDIT"].dropna().mean()) if "AMT_CREDIT" in filtered_df.columns and not filtered_df["AMT_CREDIT"].dropna().empty else 0.0
    avg_goods = float(filtered_df["AMT_GOODS_PRICE"].dropna().mean()) if "AMT_GOODS_PRICE" in filtered_df.columns and not filtered_df["AMT_GOODS_PRICE"].dropna().empty else 0.0
    avg_annuity = float(filtered_df["AMT_ANNUITY"].dropna().mean()) if "AMT_ANNUITY" in filtered_df.columns and not filtered_df["AMT_ANNUITY"].dropna().empty else 0.0

    if "AMT_CREDIT" in filtered_df.columns and "AMT_GOODS_PRICE" in filtered_df.columns:
        valid_ratios = (filtered_df["AMT_CREDIT"] / filtered_df["AMT_GOODS_PRICE"]).dropna()
        avg_credit_to_goods = float(valid_ratios.mean() * 100) if not valid_ratios.empty else 0.0
    else:
        avg_credit_to_goods = 0.0

    default_rate = float((filtered_df["TARGET"] == 1).mean() * 100) if "TARGET" in filtered_df.columns and total_records > 0 else 0.0

    st.subheader("Key Performance Indicators", anchor=False)
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        with st.container(border=True):
            st.caption("Total Applications")
            st.markdown(f"##### {total_records:,}")
    with kpi2:
        with st.container(border=True):
            st.caption("Average Credit")
            st.markdown(f"##### ${avg_credit:,.2f}")
    with kpi3:
        with st.container(border=True):
            st.caption("Average Goods Price")
            st.markdown(f"##### ${avg_goods:,.2f}")
    with kpi4:
        with st.container(border=True):
            st.caption("Average Annuity")
            st.markdown(f"##### ${avg_annuity:,.2f}")
    with kpi5:
        with st.container(border=True):
            st.caption("Credit / Goods Ratio")
            st.markdown(f"##### {avg_credit_to_goods:.1f}%")
    with kpi6:
        with st.container(border=True):
            st.caption("Overall Default Rate")
            st.markdown(f"##### {default_rate:.2f}%")

    st.divider()

    # 3. Visual Analytics Section
    st.subheader("Visual Analytics", anchor=False)

    # Row 1: Applications by Contract Type & Average Credit by Income Type
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Applications by Contract Type**")
            st.caption("Distribution of applications across contract types")
            if "NAME_CONTRACT_TYPE" in filtered_df.columns and not filtered_df["NAME_CONTRACT_TYPE"].dropna().empty:
                contract_counts = filtered_df["NAME_CONTRACT_TYPE"].value_counts()
                st.bar_chart(pd.DataFrame({"Applications": contract_counts}), y="Applications", color="#1B365D")
            else:
                st.info("Contract type data not available.")

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Average Loan Credit by Income Type**")
            st.caption("Mean credit amount requested across income categories")
            if "NAME_INCOME_TYPE" in filtered_df.columns and "AMT_CREDIT" in filtered_df.columns:
                income_credit = filtered_df.groupby("NAME_INCOME_TYPE")["AMT_CREDIT"].mean().sort_values(ascending=False)
                st.bar_chart(pd.DataFrame({"Avg Credit ($)": income_credit}), y="Avg Credit ($)", color="#1B365D")
            else:
                st.info("Income type or credit data not available.")

    # Row 2: Average Goods Price by Education & Loan Credit vs Goods Price
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        with st.container(border=True):
            st.markdown("**Average Goods Price by Education Type**")
            st.caption("Mean goods price financed by applicant education level")
            if "NAME_EDUCATION_TYPE" in filtered_df.columns and "AMT_GOODS_PRICE" in filtered_df.columns:
                edu_goods = filtered_df.groupby("NAME_EDUCATION_TYPE")["AMT_GOODS_PRICE"].mean().sort_values(ascending=False)
                st.bar_chart(pd.DataFrame({"Avg Goods Price ($)": edu_goods}), y="Avg Goods Price ($)", color="#1B365D")
            else:
                st.info("Education or goods price data not available.")

    with chart_col4:
        with st.container(border=True):
            st.markdown("**Loan Credit vs Goods Price (Sampled)**")
            st.caption("Relationship between financed credit and underlying goods price")
            if "AMT_GOODS_PRICE" in filtered_df.columns and "AMT_CREDIT" in filtered_df.columns:
                scatter_sample = filtered_df[["AMT_GOODS_PRICE", "AMT_CREDIT"]].dropna()
                if len(scatter_sample) > 1000:
                    scatter_sample = scatter_sample.sample(n=1000, random_state=42)
                if not scatter_sample.empty:
                    st.scatter_chart(scatter_sample, x="AMT_GOODS_PRICE", y="AMT_CREDIT", color="#1B365D")
                else:
                    st.info("No records with both goods price and credit amount.")
            else:
                st.info("Goods price or credit data not available.")

    # Row 3: Loan Credit Amount Distribution & Default Rate by Income Type
    chart_col5, chart_col6 = st.columns(2)

    with chart_col5:
        with st.container(border=True):
            st.markdown("**Loan Credit Amount Distribution**")
            st.caption("Application count across credit brackets")
            if "AMT_CREDIT" in filtered_df.columns and not filtered_df["AMT_CREDIT"].dropna().empty:
                credit_bins = pd.cut(
                    filtered_df["AMT_CREDIT"].dropna(),
                    bins=[0, 250000, 500000, 750000, 1000000, 1500000, float("inf")],
                    labels=["< 250K", "250K-500K", "500K-750K", "750K-1M", "1M-1.5M", "1.5M+"]
                )
                st.bar_chart(pd.DataFrame({"Applications": credit_bins.value_counts().sort_index()}), y="Applications", color="#1B365D")
            else:
                st.info("Credit amount data not available.")

    with chart_col6:
        with st.container(border=True):
            st.markdown("**Default Rate by Income Type**")
            st.caption("Percentage of applicants who defaulted across income types")
            if "NAME_INCOME_TYPE" in filtered_df.columns and "TARGET" in filtered_df.columns and not filtered_df.empty:
                income_default = filtered_df.groupby("NAME_INCOME_TYPE")["TARGET"].mean() * 100
                st.bar_chart(pd.DataFrame({"Default Rate (%)": income_default.sort_values(ascending=False)}), y="Default Rate (%)", color="#0D9488")
            else:
                st.info("Income type or target data not available.")

    st.divider()

    # 4. Data Preview
    st.subheader("Sample Loan Application Characteristics", anchor=False)
    with st.container(border=True):
        preview_cols = [
            "SK_ID_CURR", "TARGET", "NAME_CONTRACT_TYPE",
            "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE",
            "AMT_INCOME_TOTAL", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE"
        ]
        disp_cols = [c for c in preview_cols if c in filtered_df.columns]
        if disp_cols:
            st.dataframe(filtered_df[disp_cols].head(20), use_container_width=True)
        else:
            st.dataframe(filtered_df.head(20), use_container_width=True)

if __name__ == "__main__":
    try:
        sample_data = pd.read_csv("data/application_train.csv")
    except Exception:
        sample_data = None
    app(sample_data)
