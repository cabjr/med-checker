import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Medication Interaction Checker", layout="wide")

st.title("Medication Interaction Checker")
st.write("Screening tool using uploaded interaction dataset (CSV-based).")

# -----------------------------
# Clean medication names
# -----------------------------
def clean_med_name(med):
    med = med.lower()

    # remove brand names in parentheses
    med = re.sub(r"\(.*?\)", "", med)

    # remove dosing (everything after numbers)
    med = re.sub(r"\b\d+.*", "", med)

    # remove common extra words
    remove_words = [
        "tablet", "capsule", "injection", "pen", "solution",
        "mg", "mcg", "ml", "unit", "units", "cr", "er"
    ]

    for word in remove_words:
        med = med.replace(word, "")

    return med.strip()

# -----------------------------
# Load dataset safely
# -----------------------------
@st.cache_data
def load_interactions():
    try:
        df = pd.read_csv("interactions.csv")

        # Clean column names
        df.columns = [c.strip().lower() for c in df.columns]

        # Ensure required columns exist
        required = {"drug", "severity", "reason"}
        if not required.issubset(set(df.columns)):
            st.error("CSV must contain: drug, severity, reason")
            return pd.DataFrame()

        # Normalize drug names
        df["drug"] = df["drug"].astype(str).str.lower().str.strip()

        return df

    except FileNotFoundError:
        st.error("interactions.csv not found in repository.")
        return pd.DataFrame()

df_interactions = load_interactions()

# -----------------------------
# Stop if no data
# -----------------------------
if df_interactions.empty:
    st.warning("No interaction data loaded. Check your CSV file in GitHub.")
    st.stop()

st.success(f"Loaded {len(df_interactions)} interaction records")

# -----------------------------
# Check function
# -----------------------------
def check_meds(meds, df):
    results = []

    for med in meds:
        cleaned = clean_med_name(med)

        match = df[df["drug"] == cleaned]

        if match.empty:
            results.append({
                "Original Input": med,
                "Matched Name": cleaned,
                "Severity": "🟢 None",
                "Reason": "No interaction found"
            })
        else:
            row = match.iloc[0]
            results.append({
                "Original Input": med,
                "Matched Name": cleaned,
                "Severity": row.get("severity", "Unknown"),
                "Reason": row.get("reason", "")
            })

    return pd.DataFrame(results)

# -----------------------------
# Input
# -----------------------------
med_input = st.text_area(
    "Enter medications (one per line):",
    placeholder="""ondansetron (ZOFRAN) 4 mg tablet
rizatriptan (MAXALT) 10 mg tablet
sertraline 100 mg tablet"""
)

# -----------------------------
# Run check
# -----------------------------
if st.button("Check Interactions"):

    meds = [m.strip() for m in med_input.split("\n") if m.strip()]

    if not meds:
        st.warning("Please enter at least one medication.")
    else:
        results_df = check_meds(meds, df_interactions)

        st.subheader("Results")
        st.dataframe(results_df, use_container_width=True)

        st.subheader("Summary")
        st.write(results_df["Severity"].value_counts())

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("For screening purposes only. Not a substitute for clinical judgment.")
