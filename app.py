import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import os

st.set_page_config(page_title="Medication Interaction Checker")

st.title("Medication Interaction Checker")
st.write("Checks medications against full amitriptyline interaction dataset.")

# -----------------------------
# Load and parse HTML files
# -----------------------------
@st.cache_data
def load_interactions():
    interactions = []

    data_folder = "data"

    for file in os.listdir(data_folder):
        if file.endswith(".html"):
            with open(os.path.join(data_folder, file), "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "lxml")

            rows = soup.find_all("tr")

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue

                drug = cols[0].get_text(strip=True).lower()
                severity = cols[1].get_text(strip=True)
                reason = cols[2].get_text(strip=True)

                if drug:
                    interactions.append({
                        "drug": drug,
                        "severity": severity,
                        "reason": reason
                    })

    df = pd.DataFrame(interactions)
    df = df.drop_duplicates(subset=["drug"])

    return df

df_interactions = load_interactions()

# -----------------------------
# Normalize function
# -----------------------------
def normalize_med(med):
    return med.strip().lower()

# -----------------------------
# Check medications
# -----------------------------
def check_medications(med_list):
    results = []

    for med in med_list:
        med_clean = normalize_med(med)

        match = df_interactions[df_interactions["drug"] == med_clean]

        if match.empty:
            results.append({
                "Medication": med,
                "Severity": "🟢 None",
                "Reason": "No interaction found"
            })
        else:
            row = match.iloc[0]
            results.append({
                "Medication": med,
                "Severity": row["severity"],
                "Reason": row["reason"]
            })

    return pd.DataFrame(results)

# -----------------------------
# UI
# -----------------------------
med_input = st.text_area("Paste medication list (one per line):")

if st.button("Check Interactions"):
    meds = [m for m in med_input.split("\n") if m.strip()]

    if not meds:
        st.warning("Please enter at least one medication.")
    else:
        results_df = check_medications(meds)
        st.subheader("Results")
        st.dataframe(results_df)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.warning("Do not enter PHI. Screening tool only.")
