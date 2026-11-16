# Home Credit Risk Analytics Dashboard

## Project Overview

The **Home Credit Risk Analytics Dashboard** is an interactive, multi-page web application built with **Streamlit** for exploring, visualizing, and analyzing loan application data and credit default risk. Using the Home Credit Default Risk application training dataset, this dashboard provides credit risk analysts, underwriters, and portfolio managers with comprehensive insights into borrower demographics, financial characteristics, repayment affordability, credit history indicators, and predictive machine learning models.

---

## Project Objectives

- **Analyze Loan Application Data:** Examine application outcomes, loan credit distributions, contract types, and portfolio-level trends.
- **Understand Customer Demographics:** Profile applicants by age, gender, education level, and family status to identify key borrower segments.
- **Explore Default and Non-Default Patterns:** Compare defaulting and non-defaulting borrowers across various risk factors and credit metrics.
- **Analyze Income, Employment, and Credit Features:** Evaluate the impact of income levels, employment duration, occupation types, and credit inquiries on loan performance.
- **Provide Machine Learning-Based Default Prediction:** Deliver an interactive default risk prediction tool powered by a machine learning model with real-time scoring and scenario evaluation.

---

## Technologies Used

- **Python:** Core programming language.
- **Streamlit:** Interactive web application framework and user interface.
- **Pandas:** High-performance data manipulation, aggregation, and filtering.
- **NumPy:** Numerical computations and vectorized operations.
- **Scikit-learn:** Machine learning model training, preprocessing pipeline, and classification performance evaluation.

---

## Project Structure

The project follows a modular, multi-page structure with clean separation between the entrypoint application and individual page analytical modules:

```
Home_Credit_Risk_Analytics/
├── .streamlit/
│   └── config.toml                  # Streamlit theme and UI configuration
├── dashboard_pages/
│   ├── 01_Executive_Overview.py     # Portfolio KPIs and executive summary
│   ├── 02_Customer_Demographics.py  # Borrower demographic and family analysis
│   ├── 03_Loan_Application_Analysis.py # Loan amounts, contracts, and ratio bands
│   ├── 04_Default_Risk_Analysis.py  # Risk concentration and default patterns
│   ├── 05_Income_Employment.py      # Income types, occupation, and employment duration
│   ├── 06_Credit_Bureau_Analysis.py # External credit bureau inquiries analysis
│   ├── 07_Previous_Loan_Applications.py # Historical loan application characteristics
│   ├── 08_Repayment_Installments.py # Repayment affordability and debt burden
│   ├── 09_ML_Default_Prediction.py  # Machine learning default classification model
│   └── 10_Reports_Data_Download.py  # Executive reporting and dynamic CSV export
├── data/
│   └── application_train.csv        # Primary dataset (user-provided; not in Git)
├── .gitignore                       # Git ignore rules for data, cache, and secrets
├── app.py                           # Main application entrypoint and global state
├── README.md                        # Project documentation
└── requirements.txt                 # Python library dependencies
```

---

## Dataset

This project relies exclusively on the **`application_train.csv`** dataset from the **Kaggle Home Credit Default Risk** competition:

- **Row Count:** 307,511 loan applications
- **Column Count:** 122 applicant and loan attributes
- **Target Variable:** `TARGET` (where `0` indicates no payment difficulties and `1` indicates payment difficulties / default)

### Obtaining the Dataset

Due to size considerations, the dataset is **not included in this Git repository**. To run the dashboard:

1. Download `application_train.csv` from the [Kaggle Home Credit Default Risk competition page](https://www.kaggle.com/c/home-credit-default-risk/data).
2. Create a folder named `data/` in the project root directory (if it does not already exist).
3. Place `application_train.csv` directly into the `data/` folder:
   ```
   Home_Credit_Risk_Analytics/data/application_train.csv
   ```

---

## Installation and Setup

Follow these steps to set up and run the project locally:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Home_Credit_Risk_Analytics
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify dataset placement:**
   Ensure `data/application_train.csv` is present in the `data/` directory before starting the application.

---

## Run the Application

Launch the Streamlit dashboard by running:

```bash
streamlit run app.py
```

The application will start locally and open in your default web browser (typically at `http://localhost:8501`).

---

## Dashboard Pages

The dashboard consists of 10 dedicated analytical pages accessible via the sidebar navigation:

1. **Executive Overview (`01_Executive_Overview.py`):**
   Presents high-level portfolio metrics including Total Applications, Defaults, Default Rate, Non-defaults, Average Credit, and Average Income. Features global filters (Gender, Contract Type, Target Status, Income Range, Credit Range), dynamic distribution charts, and a data preview.

2. **Customer Demographics (`02_Customer_Demographics.py`):**
   Analyzes applicant age groups, gender distribution, education attainment, and family status alongside default risk correlations.

3. **Loan Application Analysis (`03_Loan_Application_Analysis.py`):**
   Examines loan amount structures, contract type proportions, goods price coverage, and discretized credit and income affordability bands.

4. **Default Risk Analysis (`04_Default_Risk_Analysis.py`):**
   Investigates default concentration across borrower profiles, external risk scores (`EXT_SOURCE_2`, `EXT_SOURCE_3`), and flags high-risk application segments.

5. **Income & Employment (`05_Income_Employment.py`):**
   Explores income distributions, income sources, occupational types, and employment longevity in relation to loan repayment performance.

6. **Credit Bureau Analysis (`06_Credit_Bureau_Analysis.py`):**
   Evaluates external credit bureau inquiries across multiple time horizons (hour, day, week, month, year) and their predictive correlation with default likelihood.

7. **Previous Loan Applications (`07_Previous_Loan_Applications.py`):**
   Reviews credit characteristics, average loan annuities, goods price ratios, and credit request structures based on historical application attributes available in the training dataset.

8. **Repayment & Installments (`08_Repayment_Installments.py`):**
   Evaluates debt burden indicators, including Debt-to-Income (DTI / Annuity-to-Income ratio), leverage (Credit-to-Income ratio), and implied loan maturity terms.

9. **ML Default Prediction (`09_ML_Default_Prediction.py`):**
   Demonstrates a supervised machine learning classification pipeline (Logistic Regression with StandardScaler) evaluated on holdout data. Displays Accuracy, Precision, Recall, F1-score, Confusion Matrix, and an interactive loan evaluation simulator for real-time risk assessment.

10. **Reports & Data Download (`10_Reports_Data_Download.py`):**
    Provides executive portfolio summary tables, risk segment breakdowns, and a one-click CSV export feature for filtered application data.

---

## Project Limitations

- **Single Dataset Scope:** All analyses, visualizations, and machine learning models in this dashboard are derived strictly from `application_train.csv`.
- **No Supplementary Relational Tables:** This project does not utilize or incorporate external supplementary files from the Kaggle competition (such as `bureau.csv`, `bureau_balance.csv`, `previous_application.csv`, `POS_CASH_balance.csv`, `installments_payments.csv`, or `credit_card_balance.csv`). All historical bureau inquiry counts and prior loan variables reflect the aggregated summary fields recorded directly within `application_train.csv`.

---

## Author

**Kumar Vandavasi**
