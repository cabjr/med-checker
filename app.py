import streamlit as st
import pandas as pd
import re
from difflib import get_close_matches

st.set_page_config(page_title="Medication Interaction Checker", layout="wide")

st.title("Medication Interaction Checker")
st.write("Enhanced screening with fuzzy matching + brand normalization")

# -----------------------------
# Clean medication names
# -----------------------------
def clean_med_name(med):
    med = med.lower()

    # remove anything in parentheses (brand names)
    med = re.sub(r"\(.*?\)", "", med)

    # remove dosing (numbers + units)
    med = re.sub(r"\d+(\.\d+)?\s*(mg|mcg|ml|units?|g)", "", med)

    # remove time-release terms
    med = re.sub(r"\b(hr|hour|hours|extended|release|er|xr|sr)\b", "", med)

    # remove formulation words
    med = re.sub(r"\b(tablet|capsule|injection|pen|solution)\b", "", med)

    # remove hyphens and weird characters
    med = re.sub(r"[^a-z\s]", " ", med)

    # collapse spaces
    med = re.sub(r"\s+", " ", med).strip()

    return med

# -----------------------------
# Brand mapping
# -----------------------------
brand_map = {
    "zofran": "ondansetron",
    "maxalt": "rizatriptan",
    "zoloft": "sertraline",
    "prozac": "fluoxetine",
    "imodium": "loperamide",
    "pepcid": "famotidine",
    "entocort": "budesonide",
    "skyrizi": "risankizumab",
}

def normalize_brand(name):
    for brand, generic in brand_map.items():
        if brand in name:
            return generic
    return name

# -----------------------------
# Severity formatting
# -----------------------------
def format_severity(sev):
    sev = str(sev).lower()
    if "major" in sev:
        return "🔴 Major"
    elif "moderate" in sev:
        return "🟠 Moderate"
    elif "minor" in sev:
        return "🟡 Minor"
    else:
        return "🟢 None"

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_interactions():
    try:
        df = pd.read_csv("interactions.csv")
        df.columns = [c.strip().lower() for c in df.columns]

        if not {"drug", "severity", "reason"}.issubset(df.columns):
            st.error("CSV must contain: drug, severity, reason")
            return pd.DataFrame()

        df["drug"] = df["drug"].astype(str).str.lower().str.strip()
        return df
    except:
        st.error("Error loading interactions.csv")
        return pd.DataFrame()

df_interactions = load_interactions()

if df_interactions.empty:
    st.warning("No interaction data loaded.")
    st.stop()

st.success(f"Loaded {len(df_interactions)} interaction records")

# -----------------------------
# Fuzzy match
# -----------------------------
def find_best_match(name, df):
    matches = get_close_matches(name, df["drug"].tolist(), n=1, cutoff=0.8)
    return matches[0] if matches else name

# -----------------------------
# Check meds
# -----------------------------
def check_meds(meds, df):
    results = []
    for med in meds:
        cleaned = clean_med_name(med)
        normalized = normalize_brand(cleaned)
        best_match = find_best_match(normalized, df)

        match = df[df["drug"] == best_match]

        if match.empty:
            results.append({
                "Original Input": med,
                "Matched Name": best_match,
                "Severity": format_severity("none"),
                "Reason": "No interaction found"
            })
        else:
            row = match.iloc[0]
            results.append({
                "Original Input": med,
                "Matched Name": best_match,
                "Severity": format_severity(row.get("severity", "")),
                "Reason": row.get("reason", "")
            })

    return pd.DataFrame(results)

# -----------------------------
# Session state init
# -----------------------------
if "med_input" not in st.session_state:
    st.session_state.med_input = ""

if "results_df" not in st.session_state:
    st.session_state.results_df = None

# -----------------------------
# CLEAR FUNCTION (fix)
# -----------------------------
def clear_all():
    st.session_state.med_input = ""
    st.session_state.results_df = None

# -----------------------------
# Input
# -----------------------------
st.text_area(
    "Enter medications (one per line):",
    key="med_input",
    placeholder="""ondansetron (ZOFRAN) 4 mg tablet
rizatriptan (MAXALT) 10 mg tablet
sertralin 100 mg tablet"""
)

# -----------------------------
# Buttons
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("Check Interactions"):
        meds = [m.strip() for m in st.session_state.med_input.split("\n") if m.strip()]

        if not meds:
            st.warning("Please enter at least one medication.")
        else:
            st.session_state.results_df = check_meds(meds, df_interactions)

with col2:
    st.button("Clear", on_click=clear_all)

# -----------------------------
# Display results
# -----------------------------
if st.session_state.results_df is not None:
    st.subheader("Results")
    st.dataframe(st.session_state.results_df, use_container_width=True)

    st.subheader("Summary")
    st.write(st.session_state.results_df["Severity"].value_counts())

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Enhanced matching enabled (brand + fuzzy). Use clinical judgment.")
