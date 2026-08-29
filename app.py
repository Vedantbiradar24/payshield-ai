import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="PayShield AI", page_icon="🛡️", layout="wide")

st.title("🛡️ PayShield AI")
st.subheader("AI-Driven Transaction Risk Analyzer")
st.write("Upload transaction data to detect potentially risky or fraudulent payments in real time.")

def calculate_risk(row):
    score = 0
    reasons = []

    # Rule 1: Unusually high amount
    if row['amount'] > 50000:
        score += 40
        reasons.append("Unusually high transaction amount")
    elif row['amount'] > 20000:
        score += 20
        reasons.append("Above-average transaction amount")

    # Rule 2: Odd hour transaction (late night)
    hour = int(row['time'].split(":")[0])
    if hour < 5 or hour > 23:
        score += 25
        reasons.append("Transaction occurred at an unusual hour")

    # Rule 3: New / unrecognized location
    if row['location'] == 'Unknown' or row['is_new_location'] == 'Yes':
        score += 25
        reasons.append("Transaction from a new or unrecognized location")

    # Rule 4: Card type risk
    if row['card_type'] == 'Prepaid':
        score += 10
        reasons.append("Prepaid cards carry higher fraud risk")

    # Final classification
    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    reason_text = "; ".join(reasons) if reasons else "No risk indicators detected"
    return pd.Series([level, score, reason_text])


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
else:
    st.info("Upload a CSV with columns: amount, time, location, is_new_location, card_type")