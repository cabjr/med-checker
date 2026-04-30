import streamlit as st
import pandas as pd

st.set_page_config(page_title="Medication Interaction Checker", layout="wide")

st.title("Medication Interaction Checker")
st.write("Screening tool using uploaded interaction dataset (CSV-based).")

# -----------------------------
# Load dataset safely
# -----------------------------
@st.cache_data
def load_interactions():
    try:
        df = pd.read_csv("interactions.csv")

        # Clean column names just in case
        df.columns = [c.strip().lower() for c in df.columns]

        # Ensure required columns exist
        required = {"drug", "severity", "reason"}
        if not required.issubset(set(df.columns)):
            st.error(f"CSV must contain columns: {required}")
            return pd.DataFrame()

        # Normalize drug names
        df["drug"] = df["drug"].astype(str).str.lower().str.strip()

        return df

    except FileNotFoundError:
        st.error("interactions.csv not found in repository.")
        return pd.DataFrame()

df_interactions = load_interactions()

# -----------------------------
# Safety check
# -----------------------------
if df_interactions.empty:
    st.warning("No interaction data loaded. Check your CSV file in GitHub.")
    st.stop()

st.success(f"Loaded {len(df_interactions)} interaction records")

# -----------------------------
# Input
# -----------------------------
med_input = st.text_area(
    "Enter medications (one per line):",
    placeholder="fluoxetine\ntramadol\nlisinopril"
)

# -----------------------------
# Check logic
# -----------------------------
def check_meds(meds, df):
    results = []

    for med in meds:
        clean = clean_med_name(med)

        match = df[df["drug"] == clean]

        if match.empty:
            results.append({
                "Original Input": med,
                "Matched Name": clean,
                "Severity": "🟢 None",
                "Reason": "No interaction found"
            })
        else:
            row = match.iloc[0]
            results.append({
                "Original Input": med,
                "Matched Name": clean,
                "Severity": row.get("severity", "Unknown"),
                "Reason": row.get("reason", "")
            })

    return pd.DataFrame(results)

# -----------------------------
# Run button
# -----------------------------
if st.button("Check Interactions"):

    meds = [m.strip() for m in med_input.split("\n") if m.strip()]

    if not meds:
        st.warning("Please enter at least one medication.")
    else:
        results_df = check_meds(meds, df_interactions)

        st.subheader("Results")
        st.dataframe(results_df, use_container_width=True)

        # Summary counts
        st.subheader("Summary")
        st.write(results_df["Severity"].value_counts())

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("For screening purposes only. Not a substitute for clinical judgment or full drug interaction databases.")
