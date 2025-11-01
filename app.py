import streamlit as st
import requests
import json

# ============================
#  STREAMLIT PAGE SETTINGS
# ============================
st.set_page_config(page_title="Lender Info Portal", page_icon="🏦", layout="centered")

st.title("🏦 Lender Info & Q&A Portal")
st.write("Check your eligibility and ask AI-powered questions about lenders.")

# ============================
#  LENDER DATA
# ============================
lenders = [
    {"name": "Bank A", "min_income": 30000, "min_credit": 650, "interest": "8%"},
    {"name": "Finance Co.", "min_income": 50000, "min_credit": 700, "interest": "7%"},
    {"name": "Loan Corp", "min_income": 40000, "min_credit": 620, "interest": "9%"}
]

# ============================
#  USER INPUTS
# ============================
st.subheader("💰 Check Your Eligibility")
income = st.number_input("Enter your monthly income", min_value=0)
credit_score = st.number_input("Enter your credit score", min_value=0, max_value=900)
check_btn = st.button("Check Eligibility")

eligible = []

if check_btn:
    eligible = [l for l in lenders if income >= l["min_income"] and credit_score >= l["min_credit"]]
    if eligible:
        st.success(f"🎉 You are eligible for {len(eligible)} lender(s). Scroll below to explore.")
    else:
        st.error("❌ No lenders match your criteria yet. Try increasing your income or credit score.")

st.divider()

# ============================
#  SHOW LENDERS + QUESTION BOX
# ============================
if eligible:
    for lender in eligible:
        with st.expander(f"{lender['name']} (Interest: {lender['interest']})"):
            st.write(f"**Minimum Income:** {lender['min_income']}")
            st.write(f"**Minimum Credit Score:** {lender['min_credit']}")
            st.write("💬 Ask a question about this lender:")

            question = st.text_input(f"Question about {lender['name']}", key=lender['name'])
            ask_btn = st.button(f"Ask {lender['name']}", key=f"btn_{lender['name']}")

            if ask_btn and question.strip():
                with st.spinner("Thinking..."):
                    # Build prompt
                    prompt = (
                        f"You are a loan advisor. Based on this lender info:\n"
                        f"{json.dumps(lender)}\n\n"
                        f"Answer the following user question:\n'{question}'"
                    )

                    # ============================
                    #  CALL GROQ LLM API
                    # ============================
                    API_KEY = st.secrets["GROQ_API_KEY"]  # stored securely in Streamlit Cloud
                    url = "https://api.groq.com/openai/v1/chat/completions"

                    payload = {
                        "model": "llama3-8b-8192",
                        "messages": [
                            {"role": "system", "content": "You are a helpful lender assistant."},
                            {"role": "user", "content": prompt}
                        ]
                    }

                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    }

                    response = requests.post(url, headers=headers, json=payload)
                    if response.status_code == 200:
                        answer = response.json()["choices"][0]["message"]["content"]
                        st.info(answer)
                    else:
                        st.error("⚠️ Error fetching response from LLM.")
