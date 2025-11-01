import streamlit as st
import pandas as pd
import requests
import json

# -----------------------------
# PAGE SETTINGS
# -----------------------------
st.set_page_config(page_title="🏦 Lender Directory & AI Q&A", page_icon="💬", layout="wide")
st.title("🏦 Lender Directory & AI Assistant")
st.caption("Browse lender details, filter by criteria, and ask AI questions about any lender.")

# -----------------------------
# LOAD CSV DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("lenders.csv")
    # Clean up column names (remove extra spaces)
    df.columns = [c.strip().replace("\n", " ") for c in df.columns]
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ lenders.csv not found. Please upload it or place it in the same folder.")
    st.stop()

# -----------------------------
# FILTER OPTIONS
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    loan_type = st.selectbox("Filter by Loan Type", ["All"] + sorted(df["TYPE OF LOAN"].dropna().unique().tolist()))
with col2:
    state_filter = st.text_input("Filter by State or Niche (keywords like 'TX', 'state', etc.)")
with col3:
    search_name = st.text_input("Search Lender Name")

filtered_df = df.copy()

if loan_type != "All":
    filtered_df = filtered_df[filtered_df["TYPE OF LOAN"].str.contains(loan_type, case=False, na=False)]

if state_filter:
    filtered_df = filtered_df[
        filtered_df["TOP NICHE"].astype(str).str.contains(state_filter, case=False, na=False)
    ]

if search_name:
    filtered_df = filtered_df[
        filtered_df["LENDER"].astype(str).str.contains(search_name, case=False, na=False)
    ]

st.success(f"Showing {len(filtered_df)} matching lenders.")

# -----------------------------
# DISPLAY RESULTS
# -----------------------------
for _, row in filtered_df.iterrows():
    with st.expander(f"🏦 {row['LENDER']}  —  {row.get('COMP', '')} COMP"):
        st.write(f"**AE:** {row.get('AE FIRST', '')} {row.get('AE LAST', '')}")
        st.write(f"**Email:** {row.get('EMAIL', '')}")
        st.write(f"**Phone:** {row.get('CELL PHO', '')}")
        st.write(f"**Loan Type:** {row.get('TYPE OF LOAN', '')}")
        st.write(f"**UW Fee:** {row.get('UW FEE', '')}")
        st.write(f"**Top Niche:** {row.get('TOP NICHI', '')}")
        st.write(f"**Notes:** {row.get('Notes', '')}")

        st.divider()
        st.write("💬 Ask a question about this lender:")

        question = st.text_input(f"Question about {row['LENDER']}", key=f"q_{row['LENDER']}")
        ask_btn = st.button(f"Ask {row['LENDER']}", key=f"btn_{row['LENDER']}")

        if ask_btn and question.strip():
            with st.spinner("Thinking..."):
                # Build prompt
                lender_info = row.to_dict()
                prompt = (
                    f"You are a mortgage advisor assistant. Based on the following lender information:\n"
                    f"{json.dumps(lender_info, indent=2)}\n\n"
                    f"User question: {question}\n"
                    f"Answer concisely and professionally."
                )

                # GROQ API CALL
                API_KEY = st.secrets["GROQ_API_KEY"]
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": "You are a helpful mortgage lending assistant."},
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
