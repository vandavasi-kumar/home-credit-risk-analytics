import streamlit as st
import pandas as pd

def app(data):
    st.title("Credit Bureau Analysis", anchor=False)
    st.write("Analysis of customers' external credit history from the bureau dataset")
    st.divider()

    if data is None:
        st.error("No dataset available to display. Please verify that data/application_train.csv is loaded.")
        return

    if data.empty:
        return

    # Explanatory card

    # Filters
    def reset_bureau_filters():
        st.session_state["bureau_sel_contract"] = "All"
        st.session_state["bureau_sel_gender"] = "All"
        st.session_state["bureau_sel_inq"] = "All"

    with st.container(border=True):
        st.subheader("Filter Options", anchor=False)
        col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1.2])

        with col_f1:
            contract_options = ["All"] + sorted(data["NAME_CONTRACT_TYPE"].dropna().unique().tolist()) if "NAME_CONTRACT_TYPE" in data.columns else ["All"]
            if "bureau_sel_contract" in st.session_state and st.session_state["bureau_sel_contract"] not in contract_options:
                st.session_state["bureau_sel_contract"] = "All"
            sel_contract = st.selectbox("Contract Type", contract_options, key="bureau_sel_contract")

        with col_f2:
            gender_options = ["All"] + sorted(data["CODE_GENDER"].dropna().unique().tolist()) if "CODE_GENDER" in data.columns else ["All"]
            if "bureau_sel_gender" in st.session_state and st.session_state["bureau_sel_gender"] not in gender_options:
                st.session_state["bureau_sel_gender"] = "All"
            sel_gender = st.selectbox("Gender", gender_options, key="bureau_sel_gender")

        with col_f3:
            inquiry_options = ["All", "0 Inquiries", "1 Inquiry", "2 Inquiries", "3 Inquiries", "4+ Inquiries"]
            if "bureau_sel_inq" in st.session_state and st.session_state["bureau_sel_inq"] not in inquiry_options:
                st.session_state["bureau_sel_inq"] = "All"
            sel_inquiry = st.selectbox("Yearly Bureau Inquiries", inquiry_options, key="bureau_sel_inq")

        with col_f4:
            st.write("")
            st.write("")
            st.button("Reset Filters", key="bureau_reset_btn", on_click=reset_bureau_filters, use_container_width=True)

    # Filtered data
    filtered_df = data

    if sel_contract != "All" and "NAME_CONTRACT_TYPE" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["NAME_CONTRACT_TYPE"] == sel_contract]

    if sel_gender != "All" and "CODE_GENDER" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["CODE_GENDER"] == sel_gender]

    if sel_inquiry != "All" and "AMT_REQ_CREDIT_BUREAU_YEAR" in filtered_df.columns:
        inq = filtered_df["AMT_REQ_CREDIT_BUREAU_YEAR"]
        if sel_inquiry == "0 Inquiries":
            filtered_df = filtered_df[inq == 0]
        elif sel_inquiry == "1 Inquiry":
            filtered_df = filtered_df[inq == 1]
        elif sel_inquiry == "2 Inquiries":
            filtered_df = filtered_df[inq == 2]
        elif sel_inquiry == "3 Inquiries":
            filtered_df = filtered_df[inq == 3]
        elif sel_inquiry == "4+ Inquiries":
            filtered_df = filtered_df[inq >= 4]

    if filtered_df.empty:
        st.warning("No records match the selected credit bureau filter criteria.")
        return

    st.divider()

    # Metrics
    bureau_year_avg = float(filtered_df["AMT_REQ_CREDIT_BUREAU_YEAR"].dropna().mean()) if "AMT_REQ_CREDIT_BUREAU_YEAR" in filtered_df.columns and not filtered_df["AMT_REQ_CREDIT_BUREAU_YEAR"].dropna().empty else 0.0
    bureau_history_count = int(filtered_df["AMT_REQ_CREDIT_BUREAU_YEAR"].notna().sum()) if "AMT_REQ_CREDIT_BUREAU_YEAR" in filtered_df.columns else 0

    if "TARGET" in filtered_df.columns and "AMT_REQ_CREDIT_BUREAU_YEAR" in filtered_df.columns:
        with_bureau = filtered_df[filtered_df["AMT_REQ_CREDIT_BUREAU_YEAR"].notna()]
        bureau_default_rate = float((with_bureau["TARGET"] == 1).mean() * 100) if not with_bureau.empty else 0.0
    else:
        bureau_default_rate = 0.0

    if "DEF_30_CNT_SOCIAL_CIRCLE" in filtered_df.columns:
        social_defaulters_count = int((filtered_df["DEF_30_CNT_SOCIAL_CIRCLE"].dropna() > 0).sum())
    else:
        social_defaulters_count = 0

    ext_2_avg = float(filtered_df["EXT_SOURCE_2"].dropna().mean()) if "EXT_SOURCE_2" in filtered_df.columns and not filtered_df["EXT_SOURCE_2"].dropna().empty else 0.0
    ext_3_avg = float(filtered_df["EXT_SOURCE_3"].dropna().mean()) if "EXT_SOURCE_3" in filtered_df.columns and not filtered_df["EXT_SOURCE_3"].dropna().empty else 0.0

    st.subheader("Key Performance Indicators (KPIs)", anchor=False)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        with st.container(border=True):
            st.caption("Avg Inquiries (Year)")
            st.markdown(f"##### {bureau_year_avg:.2f}")

    with col2:
        with st.container(border=True):
            st.caption("With Bureau History")
            st.markdown(f"##### {bureau_history_count:,}")

    with col3:
        with st.container(border=True):
            st.caption("Bureau Default Rate")
            st.markdown(f"##### {bureau_default_rate:.2f}%")

    with col4:
        with st.container(border=True):
            st.caption("Avg External Score 2")
            st.markdown(f"##### {ext_2_avg:.3f}" if ext_2_avg > 0 else "##### N/A")

    with col5:
        with st.container(border=True):
            st.caption("Avg External Score 3")
            st.markdown(f"##### {ext_3_avg:.3f}" if ext_3_avg > 0 else "##### N/A")

    with col6:
        with st.container(border=True):
            st.caption("Social Overdue (30D)")
            st.markdown(f"##### {social_defaulters_count:,}")

    st.divider()

    # Charts
    st.subheader("Visual Analytics", anchor=False)

    # Row 1: Average Inquiries by Time Horizon & Default Rate by Yearly Inquiries
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Average Bureau Inquiries by Time Horizon**")
            inquiry_cols = {
                "Hour": "AMT_REQ_CREDIT_BUREAU_HOUR",
                "Day": "AMT_REQ_CREDIT_BUREAU_DAY",
                "Week": "AMT_REQ_CREDIT_BUREAU_WEEK",
                "Month": "AMT_REQ_CREDIT_BUREAU_MON",
                "Quarter": "AMT_REQ_CREDIT_BUREAU_QRT",
                "Year": "AMT_REQ_CREDIT_BUREAU_YEAR",
            }
            avg_inquiries = {}
            for label, col in inquiry_cols.items():
                if col in filtered_df.columns and not filtered_df[col].dropna().empty:
                    avg_inquiries[label] = round(float(filtered_df[col].dropna().mean()), 3)
            if avg_inquiries:
                inquiry_df = pd.DataFrame(list(avg_inquiries.items()), columns=["Horizon", "Avg Inquiries"]).set_index("Horizon")
                st.bar_chart(inquiry_df, color="#1B365D")
            else:
                st.info("Bureau inquiry timeframe data not available.")

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Default Rate by Yearly Bureau Inquiries**")
            if "AMT_REQ_CREDIT_BUREAU_YEAR" in filtered_df.columns and "TARGET" in filtered_df.columns and not filtered_df.empty:
                year_bins_grp = pd.cut(
                    filtered_df["AMT_REQ_CREDIT_BUREAU_YEAR"].dropna(),
                    bins=[-1, 0, 1, 2, 3, 5, float("inf")],
                    labels=["0 Inquiries", "1 Inquiry", "2 Inquiries", "3 Inquiries", "4-5 Inquiries", "6+ Inquiries"]
                )
                inquiry_default = filtered_df.groupby(year_bins_grp, observed=False)["TARGET"].mean() * 100
                st.bar_chart(pd.DataFrame({"Default Rate (%)": inquiry_default}), y="Default Rate (%)", color="#0D9488")
            else:
                st.info("Inquiry or target data not available.")

    # Row 2: External Risk Scores & Social Circle Default Observations
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        with st.container(border=True):
            st.markdown("**Average External Risk Scores: Default vs Non-Default**")
            score_cols = ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
            available_scores = [c for c in score_cols if c in filtered_df.columns]
            if available_scores and "TARGET" in filtered_df.columns and not filtered_df.empty:
                scores_by_target = filtered_df.groupby("TARGET")[available_scores].mean()
                target_labels = {0: "Non-Default (0)", 1: "Default (1)"}
                scores_by_target.index = [target_labels.get(i, str(i)) for i in scores_by_target.index]
                st.bar_chart(scores_by_target.T, color=["#1B365D", "#0D9488"])
            else:
                st.info("External scores or target data not available.")

    with chart_col4:
        with st.container(border=True):
            st.markdown("**Applicant Social Circle Defaults (30 vs 60 Days)**")
            if "DEF_30_CNT_SOCIAL_CIRCLE" in filtered_df.columns and "DEF_60_CNT_SOCIAL_CIRCLE" in filtered_df.columns:
                def30_clean = filtered_df["DEF_30_CNT_SOCIAL_CIRCLE"].dropna()
                def60_clean = filtered_df["DEF_60_CNT_SOCIAL_CIRCLE"].dropna()

                b30 = pd.cut(def30_clean, bins=[-1, 0, 1, 2, float("inf")], labels=["0 Defaults", "1 Default", "2 Defaults", "3+ Defaults"]).value_counts().sort_index()
                b60 = pd.cut(def60_clean, bins=[-1, 0, 1, 2, float("inf")], labels=["0 Defaults", "1 Default", "2 Defaults", "3+ Defaults"]).value_counts().sort_index()

                social_df = pd.DataFrame({
                    "30 Days Past Due": b30,
                    "60 Days Past Due": b60
                })
                st.bar_chart(social_df, color=["#1B365D", "#0D9488"])
            else:
                st.info("Social circle delinquency data not available.")

    # Show data
    st.divider()
    st.subheader("Bureau Credit Records Sample", anchor=False)
    bureau_preview_cols = [
        "SK_ID_CURR",
        "TARGET",
        "AMT_REQ_CREDIT_BUREAU_YEAR",
        "AMT_REQ_CREDIT_BUREAU_QRT",
        "AMT_REQ_CREDIT_BUREAU_MON",
        "EXT_SOURCE_1",
        "EXT_SOURCE_2",
        "EXT_SOURCE_3",
        "DEF_30_CNT_SOCIAL_CIRCLE"
    ]
    display_cols = [c for c in bureau_preview_cols if c in filtered_df.columns]
    with st.container(border=True):
        if display_cols:
            st.dataframe(filtered_df[display_cols].head(20), use_container_width=True)
        else:
            st.dataframe(filtered_df.head(20), use_container_width=True)

if __name__ == "__main__":
    try:
        sample_data = pd.read_csv("data/application_train.csv")
    except Exception:
        sample_data = None
    app(sample_data)
