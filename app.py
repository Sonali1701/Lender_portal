import streamlit as st
import requests
import json

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Loan Prequalification (Groq-Powered)", page_icon="🏦", layout="centered")

st.title("🏦 Loan Prequalification Portal (Groq AI)")
st.caption("Enter borrower info → Groq LLM analyzes eligibility based on loan guidelines.")

st.markdown(
    """
    ### 📘 Reference:
    Guideline Source: [CakeTPO Products](https://caketpo.com/products)
    *(AI uses these programs — Alternative Doc, DSCR, Closed-End Seconds — to assess eligibility.)*
    """
)

st.divider()

# -----------------------------
# FORM INPUTS (Borrower Data)
# -----------------------------
with st.form("borrower_form"):
    st.header("Core Profile")
    col1, col2 = st.columns(2)
    with col1:
        credit_score = st.number_input("Credit Score", min_value=0, max_value=900, value=720)
        cob_credit = st.number_input("Co-borrower Credit Score (if applicable)", min_value=0, max_value=900, value=0)
        zip_code = st.text_input("ZIP Code")
        state = st.text_input("State (e.g., CA, TX, FL)")
    with col2:
        credit_hist = st.text_area("Credit History Summary (e.g., bankruptcies, late payments)")
        cob_credit_hist = st.text_area("Co-borrower Credit History Summary")

    st.header("Loan Details")
    col3, col4 = st.columns(2)
    with col3:
        loan_purpose = st.selectbox("Loan Purpose", ["Purchase", "Refinance"])
        loan_amount = st.number_input("Loan Amount Requested ($)", min_value=0, step=1000, value=350000)
        property_type = st.selectbox("Property Type", ["Single-Family", "Condo", "Multi-Unit", "Manufactured Home"])
        occupancy_type = st.selectbox("Occupancy Type", ["Primary Residence", "Second Home", "Investment"])
    with col4:
        loan_program = st.selectbox("Loan Program Type", ["Conventional", "FHA", "VA", "USDA", "Jumbo", "NON-QM"])
        loan_term = st.selectbox("Loan Term", ["30-Year Fixed", "15-Year Fixed", "ARM"])
        est_rate = st.number_input("Estimated Interest Rate (%)", min_value=0.0, step=0.125, value=7.25, format="%.3f")

    st.header("Property Information")
    col5, col6 = st.columns(2)
    with col5:
        property_value = st.number_input("Estimated Property Value ($)", min_value=0, step=1000, value=500000)
        county = st.text_input("County (optional)")
    with col6:
        down_payment = st.number_input("Down Payment ($)", min_value=0, step=1000, value=100000)
        dp_pct = (down_payment / property_value * 100) if property_value else 0
        st.write(f"💰 **Down Payment %:** {dp_pct:.2f}%")

    st.header("Income & Liabilities")
    col7, col8 = st.columns(2)
    with col7:
        gross_income = st.number_input("Gross Monthly Income ($)", min_value=0, step=100, value=10000)
        cob_income = st.number_input("Co-borrower Gross Monthly Income ($)", min_value=0, step=100, value=0)
    with col8:
        monthly_debt = st.number_input("Total Monthly Debt Obligations ($)", min_value=0, step=100, value=800)
        employment_type = st.selectbox("Employment Type", ["W-2", "Self-Employed", "Retired", "Other"])

    st.header("Timing & Financials")
    closing_time = st.selectbox("Target Closing Timeframe", ["ASAP", "30 days", "45 days", "60 days"])
    liquid_assets = st.number_input("Available Liquid Assets ($)", min_value=0, step=1000, value=50000)

    submitted = st.form_submit_button("Analyze with Groq")

# -----------------------------
# WHEN FORM IS SUBMITTED
# -----------------------------
if submitted:
    st.divider()
    st.subheader("Processing borrower data with Groq AI...")

    # Combine inputs into a single borrower profile
    borrower_data = {
        "credit_score": credit_score,
        "co_borrower_credit_score": cob_credit,
        "state": state,
        "zip_code": zip_code,
        "credit_history": credit_hist,
        "co_borrower_credit_history": cob_credit_hist,
        "loan_purpose": loan_purpose,
        "loan_amount_requested": loan_amount,
        "property_type": property_type,
        "occupancy_type": occupancy_type,
        "loan_program": loan_program,
        "loan_term": loan_term,
        "estimated_rate": est_rate,
        "property_value": property_value,
        "down_payment": down_payment,
        "down_payment_percent": dp_pct,
        "gross_monthly_income": gross_income,
        "co_borrower_income": cob_income,
        "monthly_debt": monthly_debt,
        "employment_type": employment_type,
        "liquid_assets": liquid_assets,
        "closing_timeframe": closing_time,
    }

    # -----------------------------
    # GROQ MODEL PROMPT
    # -----------------------------
    prompt = f"""
    You are an experienced mortgage underwriter.
    Using the following borrower data, determine:
    - Maximum eligible loan amount
    - Estimated interest rate range
    - Estimated monthly payment (PITI)
    - Combined DTI ratio
    - Likely program fit (Conventional / FHA / VA / NON-QM / DSCR)
    - Pre-approval status: Pre-approved / Needs review / Not eligible
    Reference loan guidelines from CakeTPO where applicable.

    Borrower Data:
    {json.dumps(borrower_data, indent=2)}
    """

    # -----------------------------
    # CALL GROQ API
    # -----------------------------
    try:
        headers = {
            "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a helpful mortgage advisor."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
            },
            timeout=60,
        )

        if response.status_code == 200:
            data = response.json()
            ai_answer = data["choices"][0]["message"]["content"]
            st.success("✅ Groq AI Response:")
            st.write(ai_answer)
        else:
            st.error(f"API Error {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"Error calling Groq API: {e}")
