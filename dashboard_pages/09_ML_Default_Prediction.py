import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

@st.cache_resource
def train_model(data_len, _data):
    # Select available prediction features
    df = _data.copy()

    # Limit training size for snappy UI responsiveness
    if len(df) > 30000:
        df = df.sample(n=30000, random_state=42)

    # Convert DAYS_BIRTH to Age in years
    age_series = df["DAYS_BIRTH"].abs() / 365 if "DAYS_BIRTH" in df.columns else pd.Series(40.0, index=df.index)

    # Convert DAYS_EMPLOYED to Employed years (handling 365243 anomaly)
    if "DAYS_EMPLOYED" in df.columns:
        emp_series = df["DAYS_EMPLOYED"].apply(
            lambda d: abs(d) / 365 if pd.notna(d) and d != 365243 else 0.0
        )
    else:
        emp_series = pd.Series(5.0, index=df.index)

    # Impute missing values with median
    income_series = df["AMT_INCOME_TOTAL"] if "AMT_INCOME_TOTAL" in df.columns else pd.Series(150000.0, index=df.index)
    credit_series = df["AMT_CREDIT"] if "AMT_CREDIT" in df.columns else pd.Series(500000.0, index=df.index)

    if "AMT_ANNUITY" in df.columns:
        annuity_median = df["AMT_ANNUITY"].median()
        annuity_series = df["AMT_ANNUITY"].fillna(annuity_median)
    else:
        annuity_series = pd.Series(25000.0, index=df.index)

    if "EXT_SOURCE_2" in df.columns:
        ext2_median = df["EXT_SOURCE_2"].median() if not df["EXT_SOURCE_2"].dropna().empty else 0.5
        ext2_series = df["EXT_SOURCE_2"].fillna(ext2_median)
    else:
        ext2_series = pd.Series(0.5, index=df.index)

    features_df = pd.DataFrame({
        "AMT_INCOME_TOTAL": income_series,
        "AMT_CREDIT": credit_series,
        "AMT_ANNUITY": annuity_series,
        "AGE_YEARS": age_series,
        "EMPLOYED_YEARS": emp_series,
        "EXT_SOURCE_2": ext2_series
    })

    y = df["TARGET"]

    X_train, X_test, y_train, y_test = train_test_split(
        features_df, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
    ])

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    return pipe, acc, prec, rec, f1, cm, len(X_train), len(X_test)

def app(data):
    # 1. Page Heading and Description
    st.title("ML Default Prediction", anchor=False)
    st.caption("Predict credit default risk and evaluate applicant repayment probability using machine learning.")
    st.divider()

    if data is None:
        st.error("No dataset available to display. Please verify that data/application_train.csv is loaded.")
        return

    # Handle cases where no records match the filters
    if data.empty:
        st.warning("No records found matching the criteria.")
        return

    if "TARGET" not in data.columns:
        st.error("TARGET column not found in dataset. Cannot perform default prediction modeling.")
        return

    # Verify both classes exist in filtered dataset
    target_counts = data["TARGET"].value_counts()
    if len(target_counts) < 2:
        st.warning(
            "The active global filter currently restricts the dataset to a single target status. "
            "A classification model requires both non-default (0) and default (1) examples to train. "
            "Please adjust the Target Status filter on the Executive Overview page to 'All' to enable ML training."
        )
        return

    if len(data) < 50:
        st.warning("Not enough sample records in the current filter selection to train a reliable model (minimum 50 required).")
        return

    # 2. Train Model
    with st.spinner("Training predictive default model..."):
        pipeline, acc, prec, rec, f1, cm, n_train, n_test = train_model(len(data), data)

    # 3. Model Performance Section
    st.subheader("Model Performance Evaluation", anchor=False)
    st.caption(
        f"Evaluated on a 80/20 train/test split ({n_train:,} training records, {n_test:,} test records). "
        "Class weighting is applied to handle credit portfolio default imbalance."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container(border=True):
            st.caption("Accuracy")
            st.markdown(f"##### {acc * 100:.1f}%")
    with col2:
        with st.container(border=True):
            st.caption("Precision (Default)")
            st.markdown(f"##### {prec * 100:.1f}%")
    with col3:
        with st.container(border=True):
            st.caption("Recall (Default)")
            st.markdown(f"##### {rec * 100:.1f}%")
    with col4:
        with st.container(border=True):
            st.caption("F1-Score")
            st.markdown(f"##### {f1:.3f}")

    # Display Confusion Matrix
    st.subheader("Confusion Matrix", anchor=False)
    with st.container(border=True):
        cm_df = pd.DataFrame(
            [
                [f"{cm[0, 0]:,} (True Negative)", f"{cm[0, 1]:,} (False Positive)"],
                [f"{cm[1, 0]:,} (False Negative)", f"{cm[1, 1]:,} (True Positive)"]
            ],
            index=["Actual: No Default (0)", "Actual: Default (1)"],
            columns=["Predicted: No Default (0)", "Predicted: Default (1)"]
        )
        st.dataframe(cm_df, use_container_width=True)


    st.divider()

    # 4. Interactive Prediction Interface
    st.subheader("Interactive Applicant Risk Scoring", anchor=False)
    st.caption("Enter prospective loan applicant characteristics below to evaluate predicted repayment probability:")

    with st.container(border=True):
        with st.form("applicant_scoring_form"):
            form_col1, form_col2 = st.columns(2)

            with form_col1:
                input_income = st.number_input("Annual Income ($)", min_value=1000.0, max_value=5000000.0, value=150000.0, step=5000.0)
                input_credit = st.number_input("Requested Credit Amount ($)", min_value=1000.0, max_value=5000000.0, value=450000.0, step=10000.0)
                input_annuity = st.number_input("Estimated Loan Annuity ($)", min_value=500.0, max_value=500000.0, value=25000.0, step=1000.0)

            with form_col2:
                input_age = st.number_input("Applicant Age (Years)", min_value=18.0, max_value=90.0, value=38.0, step=1.0)
                input_employed = st.number_input("Years in Employment (0 for Unemployed / Retired)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
                input_ext2 = st.slider("External Credit Bureau Score 2 (0.0 = Poor, 1.0 = Excellent)", min_value=0.0, max_value=1.0, value=0.50, step=0.01)

            predict_button = st.form_submit_button("Predict Default Risk", use_container_width=True)

    if predict_button:
        applicant_data = pd.DataFrame([{
            "AMT_INCOME_TOTAL": input_income,
            "AMT_CREDIT": input_credit,
            "AMT_ANNUITY": input_annuity,
            "AGE_YEARS": input_age,
            "EMPLOYED_YEARS": input_employed,
            "EXT_SOURCE_2": input_ext2
        }])

        pred_class = pipeline.predict(applicant_data)[0]
        pred_prob = pipeline.predict_proba(applicant_data)[0][1]

        st.subheader("Assessment Result", anchor=False)
        with st.container(border=True):
            result_col1, result_col2 = st.columns(2)
            with result_col1:
                with st.container(border=True):
                    st.caption("Predicted Outcome")
                    st.markdown(f"##### {'Payment Difficulties (High Risk)' if pred_class == 1 else 'Payment on Schedule (Low Risk)'}")
            with result_col2:
                with st.container(border=True):
                    st.caption("Default Probability")
                    st.markdown(f"##### {pred_prob * 100:.1f}%")

            if pred_class == 1:
                st.warning(
                    f"Caution: Applicant is flagged with elevated credit default risk (Estimated Default Probability: {pred_prob * 100:.1f}%). "
                    "Recommend secondary underwriter review, debt consolidation verification, or collateral requirement."
                )
            else:
                st.success(
                    f"Approved: Applicant exhibits low default probability (Estimated Default Probability: {pred_prob * 100:.1f}%). "
                    "Financial indicators align with standard automated approval parameters."
                )

    st.divider()

    # 5. Educational Disclaimer

if __name__ == "__main__":
    try:
        sample_data = pd.read_csv("data/application_train.csv")
    except Exception:
        sample_data = None
    app(sample_data)
