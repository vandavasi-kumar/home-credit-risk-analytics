import streamlit as st
import pandas as pd

def app(data):
    st.title("Customer Demographics", anchor=False)
    st.write("Customer profile, family structure, education and age analysis with default risk.")
    st.divider()

    if data is None:
        st.error("No dataset available to display. Please verify that data/application_train.csv is loaded.")
        return

    if data.empty:
        return

    # Filters
    def reset_demo_filters():
        st.session_state["demo_sel_gender"] = "All"
        st.session_state["demo_sel_age"] = "All"
        st.session_state["demo_sel_family"] = "All"
        st.session_state["demo_sel_edu"] = "All"
        st.session_state["demo_sel_target"] = "All"

    with st.container(border=True):
        st.subheader("Filter Options", anchor=False)
        col_f1, col_f2, col_f3, col_f4, col_f5, col_f6 = st.columns([2, 2, 2, 2, 2, 1.2])

        with col_f1:
            gender_options = ["All"] + sorted(data["CODE_GENDER"].dropna().unique().tolist()) if "CODE_GENDER" in data.columns else ["All"]
            if "demo_sel_gender" in st.session_state and st.session_state["demo_sel_gender"] not in gender_options:
                st.session_state["demo_sel_gender"] = "All"
            sel_gender = st.selectbox("Gender", gender_options, key="demo_sel_gender")

        with col_f2:
            age_options = ["All", "< 30", "30-40", "40-50", "50-60", "60+"]
            if "demo_sel_age" in st.session_state and st.session_state["demo_sel_age"] not in age_options:
                st.session_state["demo_sel_age"] = "All"
            sel_age = st.selectbox("Age Group", age_options, key="demo_sel_age")

        with col_f3:
            family_options = ["All"] + sorted(data["NAME_FAMILY_STATUS"].dropna().unique().tolist()) if "NAME_FAMILY_STATUS" in data.columns else ["All"]
            if "demo_sel_family" in st.session_state and st.session_state["demo_sel_family"] not in family_options:
                st.session_state["demo_sel_family"] = "All"
            sel_family = st.selectbox("Family Status", family_options, key="demo_sel_family")

        with col_f4:
            edu_options = ["All"] + sorted(data["NAME_EDUCATION_TYPE"].dropna().unique().tolist()) if "NAME_EDUCATION_TYPE" in data.columns else ["All"]
            if "demo_sel_edu" in st.session_state and st.session_state["demo_sel_edu"] not in edu_options:
                st.session_state["demo_sel_edu"] = "All"
            sel_edu = st.selectbox("Education", edu_options, key="demo_sel_edu")

        with col_f5:
            target_options = ["All", "0 - Non-Default", "1 - Default"]
            if "demo_sel_target" in st.session_state and st.session_state["demo_sel_target"] not in target_options:
                st.session_state["demo_sel_target"] = "All"
            sel_target = st.selectbox("Target (Default)", target_options, key="demo_sel_target")

        with col_f6:
            st.write("")
            st.write("")
            st.button("Reset Filters", key="demo_reset_btn", on_click=reset_demo_filters, use_container_width=True)

    # Filtered data
    filtered_df = data

    if sel_gender != "All" and "CODE_GENDER" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["CODE_GENDER"] == sel_gender]

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

    if sel_family != "All" and "NAME_FAMILY_STATUS" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["NAME_FAMILY_STATUS"] == sel_family]

    if sel_edu != "All" and "NAME_EDUCATION_TYPE" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["NAME_EDUCATION_TYPE"] == sel_edu]

    if sel_target != "All" and "TARGET" in filtered_df.columns:
        if sel_target == "0 - Non-Default":
            filtered_df = filtered_df[filtered_df["TARGET"] == 0]
        elif sel_target == "1 - Default":
            filtered_df = filtered_df[filtered_df["TARGET"] == 1]

    if filtered_df.empty:
        st.warning("No records match the selected demographic filter criteria.")
        return

    st.divider()

    # Metrics
    total_customers = len(filtered_df)

    if "DAYS_BIRTH" in filtered_df.columns and not filtered_df["DAYS_BIRTH"].dropna().empty:
        avg_age = float((filtered_df["DAYS_BIRTH"].abs() / 365).mean())
    else:
        avg_age = 0.0

    if "CODE_GENDER" in filtered_df.columns:
        female_customers = int((filtered_df["CODE_GENDER"] == "F").sum())
        male_customers = int((filtered_df["CODE_GENDER"] == "M").sum())
    else:
        female_customers = 0
        male_customers = 0

    if "NAME_FAMILY_STATUS" in filtered_df.columns:
        married_customers = int((filtered_df["NAME_FAMILY_STATUS"] == "Married").sum())
    else:
        married_customers = 0

    if "CNT_FAM_MEMBERS" in filtered_df.columns and not filtered_df["CNT_FAM_MEMBERS"].dropna().empty:
        avg_family_size = float(filtered_df["CNT_FAM_MEMBERS"].dropna().mean())
    else:
        avg_family_size = 0.0

    if "CNT_CHILDREN" in filtered_df.columns:
        customers_with_children = int((filtered_df["CNT_CHILDREN"] > 0).sum())
    else:
        customers_with_children = 0

    st.subheader("Key Performance Indicators (KPIs)", anchor=False)

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        with st.container(border=True):
            st.caption("Total Customers")
            st.markdown(f"##### {total_customers:,}")

    with col2:
        with st.container(border=True):
            st.caption("Male Customers")
            st.markdown(f"##### {male_customers:,}")

    with col3:
        with st.container(border=True):
            st.caption("Female Customers")
            st.markdown(f"##### {female_customers:,}")

    with col4:
        with st.container(border=True):
            st.caption("Average Customer Age")
            st.markdown(f"##### {avg_age:.1f} years")

    with col5:
        with st.container(border=True):
            st.caption("Married Customers")
            st.markdown(f"##### {married_customers:,}")

    with col6:
        with st.container(border=True):
            st.caption("Average Family Size")
            st.markdown(f"##### {avg_family_size:.1f}")

    with col7:
        with st.container(border=True):
            st.caption("Customers with Children")
            st.markdown(f"##### {customers_with_children:,}")


    st.divider()

    # Charts
    st.subheader("Visual Analytics", anchor=False)

    # Row 1: Age Distribution & Gender Distribution
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Age Distribution**")
            if "DAYS_BIRTH" in filtered_df.columns and not filtered_df["DAYS_BIRTH"].dropna().empty:
                age_years = filtered_df["DAYS_BIRTH"].abs() / 365
                age_bins = pd.cut(
                    age_years,
                    bins=[0, 25, 35, 45, 55, 65, 100],
                    labels=["< 25", "25-35", "35-45", "45-55", "55-65", "65+"]
                )
                age_distribution = pd.DataFrame({"Customers": age_bins.value_counts().sort_index()})
                st.bar_chart(age_distribution, y="Customers", color="#1B365D")
            else:
                st.info("Age data not available.")

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Customer Distribution by Gender**")
            if "CODE_GENDER" in filtered_df.columns and not filtered_df["CODE_GENDER"].dropna().empty:
                gender_counts = filtered_df["CODE_GENDER"].value_counts()
                gender_df = pd.DataFrame({"Customers": gender_counts})
                st.bar_chart(gender_df, y="Customers", color="#0D9488")
            else:
                st.info("Gender data not available.")

    # Row 2: Family Status Distribution & Default Rate by Education
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        with st.container(border=True):
            st.markdown("**Customer Distribution by Family Status**")
            if "NAME_FAMILY_STATUS" in filtered_df.columns and not filtered_df["NAME_FAMILY_STATUS"].dropna().empty:
                family_counts = filtered_df["NAME_FAMILY_STATUS"].value_counts()
                family_df = pd.DataFrame({"Customers": family_counts})
                st.bar_chart(family_df, y="Customers", color="#1B365D")
            else:
                st.info("Family status data not available.")

    with chart_col4:
        with st.container(border=True):
            st.markdown("**Default Rate by Education**")
            if "NAME_EDUCATION_TYPE" in filtered_df.columns and "TARGET" in filtered_df.columns and not filtered_df.empty:
                edu_default = filtered_df.groupby("NAME_EDUCATION_TYPE")["TARGET"].mean() * 100
                edu_default_df = pd.DataFrame({"Default Rate (%)": edu_default})
                st.bar_chart(edu_default_df, y="Default Rate (%)", color="#0D9488")
            else:
                st.info("Education or target data not available.")

    # Row 3: Default Rate by Age Group & Customer Distribution by Housing Type
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
            st.markdown("**Customer Distribution by Housing Type**")
            if "NAME_HOUSING_TYPE" in filtered_df.columns and not filtered_df["NAME_HOUSING_TYPE"].dropna().empty:
                housing_counts = filtered_df["NAME_HOUSING_TYPE"].value_counts()
                housing_df = pd.DataFrame({"Customers": housing_counts})
                st.bar_chart(housing_df, y="Customers", color="#1B365D")
            else:
                st.info("Housing type data not available.")

    # Show data
    st.divider()
    st.subheader("Data Preview", anchor=False)
    preview_columns = [
        "SK_ID_CURR",
        "TARGET",
        "CODE_GENDER",
        "DAYS_BIRTH",
        "NAME_EDUCATION_TYPE",
        "NAME_FAMILY_STATUS",
        "NAME_HOUSING_TYPE",
        "CNT_FAM_MEMBERS",
        "CNT_CHILDREN",
    ]
    display_columns = [col for col in preview_columns if col in filtered_df.columns]
    with st.container(border=True):
        if display_columns:
            st.dataframe(filtered_df[display_columns].head(20), use_container_width=True)
        else:
            st.dataframe(filtered_df.head(20), use_container_width=True)

if __name__ == "__main__":
    try:
        sample_data = pd.read_csv("data/application_train.csv")
    except Exception:
        sample_data = None
    app(sample_data)
