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


st.subheader("✍️ Check a Single Transaction Manually")
with st.form("manual_check_form"):
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        manual_amount = st.number_input("Amount (₹)", min_value=0, value=1000)
        manual_time = st.text_input("Time (HH:MM, 24-hour)", value="14:30")
        manual_location = st.text_input("Location", value="Mumbai")
    with m_col2:
        manual_new_location = st.selectbox("Is this a new location?", ["No", "Yes"])
        manual_card_type = st.selectbox("Card Type", ["Credit", "Debit", "Prepaid"])

    manual_submit = st.form_submit_button("Check Risk")

if manual_submit:
    manual_row = pd.Series({
        "amount": manual_amount,
        "time": manual_time,
        "location": manual_location,
        "is_new_location": manual_new_location,
        "card_type": manual_card_type
    })
    manual_level, manual_score, manual_reason = calculate_risk(manual_row)
    manual_row["risk_level"] = manual_level
    manual_row["risk_score"] = manual_score
    manual_row["reason"] = manual_reason

    st.write(f"**Risk Level:** {manual_level} ({manual_score}/100)")
    st.write(f"**Reason:** {manual_reason}")

    with st.spinner("Getting AI explanation..."):
        ai_text = get_ai_explanation(manual_row)
        st.info(ai_text)

st.divider()

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

    st.subheader("📊 Risk Distribution")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        risk_counts = df['risk_level'].value_counts()
        st.bar_chart(risk_counts)

    with chart_col2:
        st.write("Risk Score Distribution")
        st.line_chart(df['risk_score'])

    st.subheader("🔍 Filter Transactions")
    selected_risk = st.multiselect(
        "Show only these risk levels",
        options=["High", "Medium", "Low"],
        default=["High", "Medium", "Low"]
    )
    filtered_df = df[df['risk_level'].isin(selected_risk)]
    st.dataframe(filtered_df, use_container_width=True)

    csv_download = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Filtered Results as CSV",
        data=csv_download,
        file_name="payshield_risk_results.csv",
        mime="text/csv"
    )

    st.subheader("🤖 AI Explanation for a Transaction")
    row_index = st.selectbox("Select a transaction row to explain", df.index)
    if st.button("Get AI Explanation"):
        with st.spinner("Asking Gemini AI..."):
            explanation = get_ai_explanation(df.loc[row_index])
            st.info(explanation)

    st.subheader("📋 Batch Risk Summary (High Risk Transactions)")
    if st.button("Generate Summary for All High-Risk Transactions"):
        high_risk_df = df[df['risk_level'] == 'High']
        if len(high_risk_df) == 0:
            st.write("No high-risk transactions found.")
        else:
            summary_prompt = f"""You are a fraud risk analyst. Below are {len(high_risk_df)} high-risk transactions flagged by a rule-based system. 
Write a short 3-4 sentence summary highlighting common patterns across these transactions, to help a risk team prioritize their review.

{high_risk_df[['amount','time','location','card_type','reason']].to_string(index=False)}"""
            with st.spinner("Generating summary with Gemini AI..."):
                try:
                    summary_response = model.generate_content(summary_prompt)
                    st.success(summary_response.text.strip())
                except Exception as e:
                    st.error(f"Summary unavailable: {e}")

    st.subheader("📄 Download Full Analysis Report")
    report_lines = [
        "PayShield AI - Transaction Risk Analysis Report",
        f"Total Transactions Analyzed: {len(df)}",
        f"High Risk: {len(df[df['risk_level'] == 'High'])}",
        f"Medium Risk: {len(df[df['risk_level'] == 'Medium'])}",
        f"Low Risk: {len(df[df['risk_level'] == 'Low'])}",
        "",
        "--- High Risk Transactions ---"
    ]
    for _, r in df[df['risk_level'] == 'High'].iterrows():
        report_lines.append(f"Amount: {r['amount']}, Time: {r['time']}, Location: {r['location']}, Card: {r['card_type']} -> Reason: {r['reason']}")

    report_text = "\n".join(report_lines)
    st.download_button(
        label="📄 Download Text Report",
        data=report_text,
        file_name="payshield_report.txt",
        mime="text/plain"
    )
else:
    st.info("Upload a CSV with columns: amount, time, location, is_new_location, card_type")