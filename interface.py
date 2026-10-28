import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Delhi NGO Trust & Risk Auditor", layout="wide")

st.title("🛡️ Delhi NGO Verification & Risk Detection Engine")
st.markdown("Auditing public reviews, operational signals, and NLP sentiment to evaluate donor risk.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "delhi_ngos_assessed.csv")

@st.cache_data
def load_data():
    if not os.path.exists(CSV_FILE):
        return None, f"File not found at: {CSV_FILE}. Please run train_model.py first to generate delhi_ngos_assessed.csv!"
    try:
        data = pd.read_csv(CSV_FILE)
        return data, None
    except Exception as e:
        return None, f"Failed to load CSV: {str(e)}"

df, error_msg = load_data()

if error_msg:
    st.error(error_msg)
    st.stop()

st.sidebar.header("Filter & Search")
search_term = st.sidebar.text_input("Search NGO by Name:", "")

all_tiers = df["risk_tier"].dropna().unique().tolist() if "risk_tier" in df.columns else []
selected_tier = st.sidebar.multiselect(
    "Filter by Risk Tier:",
    options=all_tiers,
    default=all_tiers
)

filtered_df = df[df["risk_tier"].isin(selected_tier)] if all_tiers else df
if search_term and "ngo_name" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["ngo_name"].astype(str).str.contains(search_term, case=False)]

col1, col2, col3 = st.columns(3)
col1.metric("Safe / High Credibility", len(df[df["risk_tier"] == "Safe / High Credibility"]) if "risk_tier" in df.columns else 0)
col2.metric("Needs Verification", len(df[df["risk_tier"] == "Moderate / Needs Independent Verification"]) if "risk_tier" in df.columns else 0)
col3.metric("Elevated Risk Flagged", len(df[df["risk_tier"] == "Elevated Risk / Requires Caution"]) if "risk_tier" in df.columns else 0)

st.divider()

if filtered_df.empty:
    st.warning("No NGOs match your selected criteria.")
else:
    for _, row in filtered_df.head(10).iterrows():
        name = row.get("ngo_name", "Unknown NGO")
        score = round(row.get("credibility_score", 0), 1)
        
        with st.expander(f"📌 {name} — Score: {score}/100"):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Risk Tier:** {row.get('risk_tier', 'N/A')}")
            c2.write(f"**Average Rating:** {row.get('avg_review_rating', 'N/A')} ⭐")
            c3.write(f"**Reviews Counted:** {row.get('authentic_review_count', 'N/A')}")

            st.info(f"**Audit Findings:** {row.get('risk_factors_explanation', 'No red flags identified.')}")
            if pd.notna(row.get("aggregated_reviews")):
                st.caption(f"Review Snippets: {row['aggregated_reviews']}")