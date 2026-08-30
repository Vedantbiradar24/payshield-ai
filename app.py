import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(page_title="PayShield AI", page_icon="🛡️", layout="wide")

st.title("🛡️ PayShield AI")
st.subheader("AI-Driven Transaction Risk Analyzer")
st.write("Upload transaction data to detect potentially risky or fraudulent payments in real time.")

def calculate_risk(row):
    score = 0
    reasons = []

    if row['amount'] > 50000:
        score += 40
        reasons.append("Unusually high transaction amount")
    elif row['amount'] > 20000:
        score += 20
        reasons.append("Above-average transaction amount")

    hour = int(row['time'].split(":")[0])
    if hour < 5 or hour > 23:
        score += 25
        reasons.append("Transaction occurred at an unusual hour")

    if row['location'] == 'Unknown' or row['is_new_location'] == 'Yes':
        score += 25
        reasons.append("Transaction from a new or unrecognized location")

    if row['card_type'] == 'Prepaid':
        score += 10
        reasons.append("Prepaid cards carry higher fraud risk")

    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    reason_text = "; ".join(reasons) if reasons else "No risk indicators detected"
    return pd.Series([level, score, reason_text])


def get_ai_explanation(row):
    prompt = f"""You are a fraud risk analyst. In 1-2 short sentences, explain in simple language why this transaction got a {row['risk_level']} risk rating.
Transaction: amount={row['amount']}, time={row['time']}, location={row['location']}, new_location={row['is_new_location']}, card_type={row['card_type']}, risk_score={row['risk_score']}, flagged_reasons={row['reason']}"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI explanation unavailable: {e}"


uploaded_file = st.file_uploader("Upload transaction CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df[['risk_level', 'risk_score', 'reason']] = df.apply(calculate_risk, axis=1)

    st.success(f"Analyzed {len(df)} transactions")

    col1, col2, col3 = st.columns(3)
    col1.metric("High Risk", len(df[df['risk_level'] == 'High']))
    col2.metric("Medium Risk", len(df[df['risk_level'] == 'Medium']))
    col3.metric("Low Risk", len(df[df['risk_level'] == 'Low']))

    st.dataframe(df, use_container_width=True)

    st.subheader("🤖 AI Explanation for a Transaction")
    row_index = st.selectbox("Select a transaction row to explain", df.index)
    if st.button("Get AI Explanation"):
        with st.spinner("Asking Gemini AI..."):
            explanation = get_ai_explanation(df.loc[row_index])
            st.info(explanation)
else:
    st.info("Upload a CSV with columns: amount, time, location, is_new_location, card_type")