import streamlit as st
import requests
import json

st.set_page_config(page_title="🏦 Smart Lender Portal", page_icon="💰", layout="centered")

st.title("🏦 Smart Lender Info & Q&A Portal")
st.caption("Find lenders that match your eligibility — and ask AI any questions about them.")

# ------------------------------
# 1️⃣ Lender Data
# ------------------------------
lenders = [
    {
        "name": "Bank A",
        "min_income": 30000,
        "min_credit": 650,
        "states": ["California", "Texas", "Florida"],
        "property_types": ["House", "Condo"],
        "min_down_payment": 10000,
        "interest": "8%"
    },
    {
        "name": "Finance Co.",
        "min_income": 50000,
        "min_credit": 700,
        "states": ["New York", "California"],
        "property_types": ["Apartment", "House"],
        "min_down_payment": 15000,
        "interest": "7%"
    },
    {
        "name": "Loan Corp",
        "min_income": 40000,
        "min_credit": 620,
        "states": ["Florida", "Nevada", "Texas"],
        "property_types": ["House", "Land"],
        "min_down_payment": 8000,
        "interest": "9%"
    }
]

# ------------------------------
# 2️⃣ Session State (to persist data)
# ------------------------------
if "eligible" not in st.session_state:
    st.session_state.eligible = []

# ------------------------------
# 3️⃣ Eligibility Inputs
# ------------------------------
with st.form("criteria_form"):
    st.subheader("🔍 Check Your Eligibility")

    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("Monthly Income ($)", min_value=0, step=500)
        credit_score = st.number_input("Credit Score", min_value=0, max_value=900, step=10)
    with col2:
        state = st.selectbox("Select Your State", [
            "California", "Texas", "Florida", "New York", "Nevada", "Illinois", "Ohio"
        ])
        property_type = st.selectbox("Type of Property", ["House", "Condo", "Apartment", "Land"])

    down_payment = st.number_input("Down Payment ($)", min_value=0, step=1000)
    check_btn = st.form_submit_button("Check Eligibility")

if check_btn:
    eligible = [
        l for l in lenders
        if income >= l["min_income"]
        and credit_score >= l["min_credit"]
        and state in l["states"]
        and property_type in l["property_types"]
        and down_payment >= l["min_down_payment"]
    ]
    st.session_state.eligible = eligible

# ------------------------------
# 4️⃣ Display Eligible Lenders
# ------------------------------
if st.session_state.eligible:
    st.success(f"🎉 You qualify for {len(st.session_state.eligible)} lender(s)! Scroll below 👇")
    for lender in st.session_state.eligible:
        with st.expander(f"{lender['name']} (Interest: {lender['interest']})"):
            st.write(f"**Minimum Income:** ${lender['min_income']}")
            st.write(f"**Minimum Credit Score:** {lender['min_credit']}")
            st.write(f"**Eligible States:** {', '.join(lender['states'])}")
            st.write(f"**Property Types:** {', '.join(lender['property_types'])}")
            st.write(f"**Minimum Down Payment:** ${lender['min_down_payment']}")
            st.write("💬 Ask a question about this lender:")

            question = st.text_input(f"Question about {lender['name']}", key=f"q_{lender['name']}")
            ask_btn = st.button(f"Ask {lender['name']}", key=f"btn_{lender['name']}")

            if ask_btn and question.strip():
                with st.spinner("Thinking..."):
                    prompt = (
                        f"You are a financial advisor. Here is lender information:\n"
                        f"{json.dumps(lender, indent=2)}\n\n"
                        f"User question: {question}\n\n"
                        f"Provide a clear, factual, and helpful answer."
                    )

                    try:
                        API_KEY = st.secrets["GROQ_API_KEY"]
                    except KeyError:
                        st.error("❌ GROQ_API_KEY not found in secrets.")
                        st.stop()

                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": "llama3-8b-8192",
                        "messages": [
                            {"role": "system", "content": "You are a helpful lender advisor."},
                            {"role": "user", "content": prompt}
                        ]
                    }

                    response = requests.post(url, headers=headers, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        answer = data["choices"][0]["message"]["content"]
                        st.info(answer)
                    else:
                        st.error(f"⚠️ API Error {response.status_code}: {response.text}")

elif check_btn:
    st.error("❌ No lenders match your criteria.")
