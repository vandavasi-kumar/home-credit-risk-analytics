import streamlit as st
import pandas as pd

@st.cache_data
def convert_to_csv(df_input, include_index=False):
    return df_input.to_csv(index=include_index).encode("utf-8")

def app(data):
    # 1. Page Heading and Description
    st.title("Reports & Data Download", anchor=False)
    st.caption("Generate executive portfolio summaries and export filtered application datasets as CSV.")
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
    total_applications = len(filtered_df)
    default_applications = int((filtered_df["TARGET"] == 1).sum()) if "TARGET" in filtered_df.columns else 0
    non_default_applications = int((filtered_df["TARGET"] == 0).sum()) if "TARGET" in filtered_df.columns else 0
    default_rate = (default_applications / total_applications * 100) if total_applications > 0 else 0.0

    st.subheader("Key Performance Indicators", anchor=False)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container(border=True):
            st.caption("Total Applications")
            st.markdown(f"##### {total_applications:,}")
    with col2:
        with st.container(border=True):
            st.caption("Default Applications")
            st.markdown(f"##### {default_applications:,}")
    with col3:
        with st.container(border=True):
            st.caption("Non-Default Applications")
            st.markdown(f"##### {non_default_applications:,}")
    with col4:
        with st.container(border=True):
            st.caption("Default Rate")
            st.markdown(f"##### {default_rate:.2f}%")

    st.divider()

    # 3. Section 1: Dataset Summary & Data Export
    st.subheader("Dataset Summary & Full Export", anchor=False)
    with st.container(border=True):
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        with summary_col1:
            with st.container(border=True):
                st.caption("Total Rows in Selection")
                st.markdown(f"##### {len(filtered_df):,}")
        with summary_col2:
            with st.container(border=True):
                st.caption("Total Attributes (Columns)")
                st.markdown(f"##### {filtered_df.shape[1]:,}")
        with summary_col3:
            with st.container(border=True):
                mem_mb = filtered_df.memory_usage(deep=False).sum() / (1024 * 1024)
                st.caption("Estimated Memory Footprint")
                st.markdown(f"##### {mem_mb:.1f} MB")

        st.markdown("**Export Filtered Application Dataset**")
        st.caption("Download the active filtered records for offline reporting and data analysis:")
        dl_col1, dl_col2 = st.columns(2)

        with dl_col1:
            top_records = filtered_df.head(10000)
            csv_sample = convert_to_csv(top_records, include_index=False)
            st.download_button(
                label=f"Download Sample CSV (First {len(top_records):,} rows)",
                data=csv_sample,
                file_name="filtered_applications_sample.csv",
                mime="text/csv",
                use_container_width=True
            )

        with dl_col2:
            export_df = filtered_df if len(filtered_df) <= 50000 else filtered_df.head(50000)
            csv_full = convert_to_csv(export_df, include_index=False)
            st.download_button(
                label=f"Download Dataset CSV ({len(filtered_df):,} rows)",
                data=csv_full,
                file_name="filtered_applications_full.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.divider()

    # 4. Section 2: Target Distribution Summary
    st.subheader("Target Distribution Summary", anchor=False)
    with st.container(border=True):
        if "TARGET" in filtered_df.columns and not filtered_df["TARGET"].dropna().empty:
            target_counts = filtered_df["TARGET"].value_counts()
            target_summary_df = pd.DataFrame({
                "Target Code": [0, 1],
                "Classification Description": ["Non-Default (No Payment Difficulties)", "Default (Payment Difficulties)"],
                "Application Count": [int(target_counts.get(0, 0)), int(target_counts.get(1, 0))],
                "Proportion (%)": [
                    round(int(target_counts.get(0, 0)) / total_applications * 100, 2) if total_applications > 0 else 0.0,
                    round(int(target_counts.get(1, 0)) / total_applications * 100, 2) if total_applications > 0 else 0.0
                ]
            })
            st.dataframe(target_summary_df, use_container_width=True)

            target_csv = convert_to_csv(target_summary_df, include_index=False)
            st.download_button(
                label="Download Target Distribution Summary (CSV)",
                data=target_csv,
                file_name="target_distribution_summary.csv",
                mime="text/csv"
            )
        else:
            st.info("Target data not available in filtered dataset.")

    st.divider()

    # 5. Section 3: Contract Type Summary
    st.subheader("Contract Type Summary", anchor=False)
    with st.container(border=True):
        if "NAME_CONTRACT_TYPE" in filtered_df.columns and not filtered_df["NAME_CONTRACT_TYPE"].dropna().empty:
            contract_grouped = filtered_df.groupby("NAME_CONTRACT_TYPE").agg(
                Total_Applications=("TARGET", "count") if "TARGET" in filtered_df.columns else ("NAME_CONTRACT_TYPE", "count"),
                Default_Count=("TARGET", "sum") if "TARGET" in filtered_df.columns else ("NAME_CONTRACT_TYPE", lambda x: 0),
                Default_Rate_Pct=("TARGET", lambda x: round(x.mean() * 100, 2)) if "TARGET" in filtered_df.columns else ("NAME_CONTRACT_TYPE", lambda x: 0.0),
                Avg_Credit_Amount=("AMT_CREDIT", lambda x: round(x.mean(), 2)) if "AMT_CREDIT" in filtered_df.columns else ("NAME_CONTRACT_TYPE", lambda x: 0.0)
            ).reset_index()

            contract_grouped.columns = [
                "Contract Type", "Total Applications", "Default Count", "Default Rate (%)", "Avg Credit Amount ($)"
            ]
            st.dataframe(contract_grouped, use_container_width=True)

            contract_csv = convert_to_csv(contract_grouped, include_index=False)
            st.download_button(
                label="Download Contract Type Summary (CSV)",
                data=contract_csv,
                file_name="contract_type_summary.csv",
                mime="text/csv"
            )
        else:
            st.info("Contract type data not available.")

    st.divider()

    # 6. Section 4: Gender Summary
    st.subheader("Gender Summary", anchor=False)
    with st.container(border=True):
        if "CODE_GENDER" in filtered_df.columns and not filtered_df["CODE_GENDER"].dropna().empty:
            gender_grouped = filtered_df.groupby("CODE_GENDER").agg(
                Total_Applications=("TARGET", "count") if "TARGET" in filtered_df.columns else ("CODE_GENDER", "count"),
                Default_Count=("TARGET", "sum") if "TARGET" in filtered_df.columns else ("CODE_GENDER", lambda x: 0),
                Default_Rate_Pct=("TARGET", lambda x: round(x.mean() * 100, 2)) if "TARGET" in filtered_df.columns else ("CODE_GENDER", lambda x: 0.0),
                Avg_Annual_Income=("AMT_INCOME_TOTAL", lambda x: round(x.mean(), 2)) if "AMT_INCOME_TOTAL" in filtered_df.columns else ("CODE_GENDER", lambda x: 0.0),
                Avg_Credit_Amount=("AMT_CREDIT", lambda x: round(x.mean(), 2)) if "AMT_CREDIT" in filtered_df.columns else ("CODE_GENDER", lambda x: 0.0)
            ).reset_index()

            gender_grouped.columns = [
                "Gender", "Total Applications", "Default Count", "Default Rate (%)", "Avg Annual Income ($)", "Avg Credit ($)"
            ]
            st.dataframe(gender_grouped, use_container_width=True)

            gender_csv = convert_to_csv(gender_grouped, include_index=False)
            st.download_button(
                label="Download Gender Summary (CSV)",
                data=gender_csv,
                file_name="gender_summary.csv",
                mime="text/csv"
            )
        else:
            st.info("Gender data not available.")

    st.divider()

    # 7. Section 5 & 6: Financial Distribution Summaries
    st.subheader("Financial Distribution Summaries", anchor=False)
    sum_col1, sum_col2 = st.columns(2)
    with sum_col1:
        with st.container(border=True):
            st.markdown("**Income Summary**")
            if "AMT_INCOME_TOTAL" in filtered_df.columns and not filtered_df["AMT_INCOME_TOTAL"].dropna().empty:
                income_desc = filtered_df["AMT_INCOME_TOTAL"].describe().round(2).to_frame(name="Annual Income ($)")
                income_desc.index.name = "Statistic"
                st.dataframe(income_desc, use_container_width=True)

                income_csv = convert_to_csv(income_desc, include_index=True)
                st.download_button(
                    label="Download Income Summary (CSV)",
                    data=income_csv,
                    file_name="income_summary.csv",
                    mime="text/csv"
                )
            else:
                st.info("Income data not available.")

    with sum_col2:
        with st.container(border=True):
            st.markdown("**Credit Amount Summary**")
            if "AMT_CREDIT" in filtered_df.columns and not filtered_df["AMT_CREDIT"].dropna().empty:
                credit_desc = filtered_df["AMT_CREDIT"].describe().round(2).to_frame(name="Credit Amount ($)")
                credit_desc.index.name = "Statistic"
                st.dataframe(credit_desc, use_container_width=True)

                credit_csv = convert_to_csv(credit_desc, include_index=True)
                st.download_button(
                    label="Download Credit Amount Summary (CSV)",
                    data=credit_csv,
                    file_name="credit_amount_summary.csv",
                    mime="text/csv"
                )
            else:
                st.info("Credit amount data not available.")

if __name__ == "__main__":
    try:
        sample_data = pd.read_csv("data/application_train.csv")
    except Exception:
        sample_data = None
    app(sample_data)
