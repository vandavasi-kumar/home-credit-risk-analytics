import streamlit as st
import pandas as pd
import altair as alt

def app(data):
    st.title("Home Credit | Executive Overview", anchor=False)
    st.write("Key performance indicators and overall loan portfolio summary from the Home Credit dataset")
    st.divider()

    if data is None:
        st.error("No dataset available to display. Please verify that data/application_train.csv is loaded.")
        return

    # Filters
    bounds = st.session_state.get("global_bounds", {})
    min_income = bounds.get("min_income", float(data["AMT_INCOME_TOTAL"].min()) if "AMT_INCOME_TOTAL" in data.columns and not data["AMT_INCOME_TOTAL"].dropna().empty else 25650.0)
    max_income = bounds.get("max_income", float(data["AMT_INCOME_TOTAL"].max()) if "AMT_INCOME_TOTAL" in data.columns and not data["AMT_INCOME_TOTAL"].dropna().empty else 117000000.0)
    min_credit = bounds.get("min_credit", float(data["AMT_CREDIT"].min()) if "AMT_CREDIT" in data.columns and not data["AMT_CREDIT"].dropna().empty else 45000.0)
    max_credit = bounds.get("max_credit", float(data["AMT_CREDIT"].max()) if "AMT_CREDIT" in data.columns and not data["AMT_CREDIT"].dropna().empty else 4050000.0)

    default_filters = {
        "gender": "All",
        "contract": "All",
        "target": "All",
        "income": (min_income, max_income),
        "credit": (min_credit, max_credit),
    }

    if "global_applied_filters" not in st.session_state:
        st.session_state["global_applied_filters"] = default_filters

    if "exec_form_id" not in st.session_state:
        st.session_state["exec_form_id"] = 0

    applied = st.session_state["global_applied_filters"]

    with st.form(key=f"exec_filters_form_{st.session_state['exec_form_id']}", border=True):
        st.subheader("Filter Options", anchor=False)
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            gender_options = ["All", "F", "M", "XNA"]
            cur_gender = applied.get("gender", "All")
            gender_idx = gender_options.index(cur_gender) if cur_gender in gender_options else 0
            sel_gender = st.selectbox("Gender", gender_options, index=gender_idx)

        with col_f2:
            contract_options = ["All", "Cash loans", "Revolving loans"]
            cur_contract = applied.get("contract", "All")
            contract_idx = contract_options.index(cur_contract) if cur_contract in contract_options else 0
            sel_contract = st.selectbox("Contract Type", contract_options, index=contract_idx)

        with col_f3:
            target_options = ["All", "0 - No Payment Difficulties", "1 - Payment Difficulties"]
            cur_target = applied.get("target", "All")
            target_idx = target_options.index(cur_target) if cur_target in target_options else 0
            sel_target = st.selectbox("Target Status", target_options, index=target_idx)

        col_f4, col_f5 = st.columns(2)

        with col_f4:
            cur_income = applied.get("income", (min_income, max_income))
            income_step = 1000.0 if (max_income - min_income) >= 10000.0 else 1.0
            sel_income = st.slider(
                "Income Range",
                min_value=min_income,
                max_value=max_income,
                value=cur_income,
                step=income_step,
            )

        with col_f5:
            cur_credit = applied.get("credit", (min_credit, max_credit))
            credit_step = 1000.0 if (max_credit - min_credit) >= 10000.0 else 1.0
            sel_credit = st.slider(
                "Credit Amount Range",
                min_value=min_credit,
                max_value=max_credit,
                value=cur_credit,
                step=credit_step,
            )

        col_b1, col_b2, _ = st.columns([1, 1, 4])
        with col_b1:
            btn_apply = st.form_submit_button("Apply Filters", use_container_width=True)
        with col_b2:
            btn_reset = st.form_submit_button("Reset Filters", use_container_width=True)

    if btn_apply:
        st.session_state["global_applied_filters"] = {
            "gender": sel_gender,
            "contract": sel_contract,
            "target": sel_target,
            "income": sel_income,
            "credit": sel_credit,
        }
        st.rerun()
    elif btn_reset:
        st.session_state["global_applied_filters"] = default_filters
        st.session_state["exec_form_id"] += 1
        st.rerun()

    if data.empty:
        st.warning("No records match the selected filter criteria. Please adjust your filters or click Reset Filters.")
        return

    st.divider()

    # Metrics
    total_apps = len(data)
    default_apps = int((data["TARGET"] == 1).sum()) if "TARGET" in data.columns else 0
    non_default_apps = int((data["TARGET"] == 0).sum()) if "TARGET" in data.columns else 0
    default_rate = (default_apps / total_apps * 100) if total_apps > 0 else 0.0

    avg_credit = float(data["AMT_CREDIT"].mean()) if "AMT_CREDIT" in data.columns and not data["AMT_CREDIT"].dropna().empty else 0.0
    avg_income = float(data["AMT_INCOME_TOTAL"].mean()) if "AMT_INCOME_TOTAL" in data.columns and not data["AMT_INCOME_TOTAL"].dropna().empty else 0.0

    st.subheader("Key Performance Indicators (KPIs)", anchor=False)

    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        with st.container(border=True):
            st.caption("Total Applications")
            st.markdown(f"##### {total_apps:,}")

    with kpi2:
        with st.container(border=True):
            st.caption("Defaults")
            st.markdown(f"##### {default_apps:,}")

    with kpi3:
        with st.container(border=True):
            st.caption("Default Rate")
            st.markdown(f"##### {default_rate:.2f}%")

    with kpi4:
        with st.container(border=True):
            st.caption("Non-defaults")
            st.markdown(f"##### {non_default_apps:,}")

    with kpi5:
        with st.container(border=True):
            st.caption("Average Credit")
            st.markdown(f"##### ${avg_credit:,.2f}")

    with kpi6:
        with st.container(border=True):
            st.caption("Average Income")
            st.markdown(f"##### ${avg_income:,.2f}")

    st.divider()

    # Charts
    st.subheader("Visual Analytics", anchor=False)

    # Row 1: Two-column layout
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        with st.container(border=True):
            st.markdown("**Default vs Non-default**")
            if total_apps > 0:
                non_def_pct = (non_default_apps / total_apps * 100)
                def_pct = (default_apps / total_apps * 100)
                donut_df = pd.DataFrame({
                    "Status": ["Non-default", "Default"],
                    "Applications": [non_default_apps, default_apps],
                    "Percentage": [f"{non_def_pct:.1f}%", f"{def_pct:.1f}%"]
                })
                donut_df["Legend"] = donut_df["Status"] + ": " + donut_df["Applications"].map("{:,}".format) + " (" + donut_df["Percentage"] + ")"

                donut_chart = alt.Chart(donut_df).mark_arc(innerRadius=60, outerRadius=110).encode(
                    theta=alt.Theta(field="Applications", type="quantitative"),
                    color=alt.Color(
                        field="Legend",
                        type="nominal",
                        scale=alt.Scale(range=["#1B365D", "#0D9488"]),
                        legend=alt.Legend(title="Application Status", orient="bottom")
                    ),
                    tooltip=["Status:N", "Applications:Q", "Percentage:N"]
                ).properties(height=320)
                st.altair_chart(donut_chart, use_container_width=True)
            else:
                st.info("No applications available.")

    with row1_col2:
        with st.container(border=True):
            st.markdown("**Application Outcome**")
            outcome_df = pd.DataFrame({
                "Status": ["Non-default", "Default"],
                "Applications": [non_default_apps, default_apps]
            })
            outcome_chart = alt.Chart(outcome_df).mark_bar(size=50).encode(
                x=alt.X("Status:N", title="Application Outcome", sort=["Non-default", "Default"], axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Applications:Q", title="Applications", axis=alt.Axis(format="~s")),
                color=alt.Color("Status:N", scale=alt.Scale(domain=["Non-default", "Default"], range=["#1B365D", "#0D9488"]), legend=None),
                tooltip=[
                    alt.Tooltip("Status:N", title="Outcome"),
                    alt.Tooltip("Applications:Q", title="Applications", format=",")
                ]
            ).properties(height=320)
            st.altair_chart(outcome_chart, use_container_width=True)

    # Row 2: Two-column layout
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        with st.container(border=True):
            st.markdown("**Loan Amount Distribution (AMT_CREDIT)**")
            if "AMT_CREDIT" in data.columns and not data["AMT_CREDIT"].dropna().empty:
                credit_bins = pd.cut(
                    data["AMT_CREDIT"].dropna(),
                    bins=[0, 250000, 500000, 750000, 1000000, 1500000, float("inf")],
                    labels=["< 250K", "250K-500K", "500K-750K", "750K-1M", "1M-1.5M", "1.5M+"]
                )
                credit_counts = credit_bins.value_counts().sort_index()
                credit_dist_df = pd.DataFrame({
                    "Credit Bracket": credit_counts.index.astype(str),
                    "Applications": credit_counts.values
                })
                hist_chart = alt.Chart(credit_dist_df).mark_bar(size=36).encode(
                    x=alt.X("Credit Bracket:N", title="Credit Amount (AMT_CREDIT)", sort=["< 250K", "250K-500K", "500K-750K", "750K-1M", "1M-1.5M", "1.5M+"], axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Applications:Q", title="Applications", axis=alt.Axis(format="~s")),
                    color=alt.value("#1B365D"),
                    tooltip=[
                        alt.Tooltip("Credit Bracket:N", title="Bracket"),
                        alt.Tooltip("Applications:Q", title="Applications", format=",")
                    ]
                ).properties(height=320)
                st.altair_chart(hist_chart, use_container_width=True)
            else:
                st.info("Credit amount data not available.")

    with row2_col2:
        with st.container(border=True):
            st.markdown("**Default Rate by Contract Type**")
            if "NAME_CONTRACT_TYPE" in data.columns and "TARGET" in data.columns and not data.empty:
                contract_stats = data.groupby("NAME_CONTRACT_TYPE")["TARGET"].agg(["mean", "count"]).reset_index()
                contract_stats["Default Rate (%)"] = (contract_stats["mean"] * 100).round(2)
                contract_stats["Rate Label"] = contract_stats["Default Rate (%)"].astype(str) + "%"

                contract_chart = alt.Chart(contract_stats).mark_bar(size=50).encode(
                    x=alt.X("NAME_CONTRACT_TYPE:N", title="Contract Type", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Default Rate (%):Q", title="Default Rate (%)", scale=alt.Scale(zero=True)),
                    color=alt.Color("NAME_CONTRACT_TYPE:N", scale=alt.Scale(domain=["Cash loans", "Revolving loans"], range=["#1B365D", "#0D9488"]), legend=None),
                    tooltip=[
                        alt.Tooltip("NAME_CONTRACT_TYPE:N", title="Contract Type"),
                        alt.Tooltip("Default Rate (%):Q", title="Default Rate", format=".2f"),
                        alt.Tooltip("count:Q", title="Applications", format=",")
                    ]
                ).properties(height=320)
                st.altair_chart(contract_chart, use_container_width=True)
            else:
                st.info("Contract type or target data not available.")

    # Row 3: Income vs Credit Amount (Scatter plot)
    with st.container(border=True):
        st.markdown("**Income vs Credit Amount**")
        if "AMT_INCOME_TOTAL" in data.columns and "AMT_CREDIT" in data.columns:
            scatter_data = data[["AMT_INCOME_TOTAL", "AMT_CREDIT"]].dropna()
            if len(scatter_data) > 1000:
                scatter_data = scatter_data.sample(n=1000, random_state=42)
            if not scatter_data.empty:
                scatter_chart = alt.Chart(scatter_data).mark_circle(size=35, opacity=0.55).encode(
                    x=alt.X("AMT_INCOME_TOTAL:Q", title="Annual Income (AMT_INCOME_TOTAL)", axis=alt.Axis(format="$,.0f")),
                    y=alt.Y("AMT_CREDIT:Q", title="Credit Amount (AMT_CREDIT)", axis=alt.Axis(format="$,.0f")),
                    color=alt.value("#0D9488"),
                    tooltip=[
                        alt.Tooltip("AMT_INCOME_TOTAL:Q", title="Annual Income", format="$,.2f"),
                        alt.Tooltip("AMT_CREDIT:Q", title="Credit Amount", format="$,.2f")
                    ]
                ).properties(height=340)
                st.altair_chart(scatter_chart, use_container_width=True)
            else:
                st.info("No records available to display scatter chart.")
        else:
            st.info("Income or credit amount data not available.")

    # Show data
    st.divider()
    st.subheader("Data Preview", anchor=False)
    preview_columns = [
        "SK_ID_CURR",
        "TARGET",
        "NAME_CONTRACT_TYPE",
        "CODE_GENDER",
        "AMT_CREDIT",
        "AMT_INCOME_TOTAL",
        "AMT_ANNUITY",
    ]
    display_columns = [col for col in preview_columns if col in data.columns]
    with st.container(border=True):
        if display_columns:
            st.dataframe(data[display_columns].head(20), use_container_width=True)
        else:
            st.dataframe(data.head(20), use_container_width=True)

if __name__ == "__main__":
    try:
        sample_data = pd.read_csv("data/application_train.csv")
    except Exception:
        sample_data = None
    app(sample_data)
