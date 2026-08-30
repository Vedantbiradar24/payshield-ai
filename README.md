# 🛡️ PayShield AI

**AI-Driven Transaction Risk Analyzer** — built for Razorpay AI Builder Internship 2026 (Track 2: AI Risk Manager)

## Problem
Manual transaction review is slow and inconsistent, while rigid rule-based fraud systems generate false positives without explaining why a transaction was flagged.

## Solution
PayShield AI analyzes transaction data (amount, time, location, card type) and:
- Assigns a Risk Score (Low / Medium / High) to every transaction using a rule-based scoring engine
- Uses Google's Gemini AI to generate a natural-language explanation for each risk classification
- Displays results on a simple, interactive dashboard for quick review

## Tech Stack
- Python
- Streamlit (dashboard/UI)
- Pandas (data processing)
- Gemini AI (natural language risk explanations)
- Rule-based explainable risk-scoring engine

## How to Run
1. Install dependencies: pip install -r requirements.txt
2. Add your Gemini API key to a .env file: GEMINI_API_KEY=your_key_here
3. Run: streamlit run app.py
4. Upload a CSV with columns: amount, time, location, is_new_location, card_type

## Sample Output
Given 10 sample transactions, the app correctly flagged high-risk patterns such as late-night transactions, unrecognized locations, and prepaid card usage — with Gemini AI generating clear, human-readable explanations for each risk score.