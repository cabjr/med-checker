import streamlit as st
import pandas as pd

st.set_page_config(page_title="Medication Contraindication Checker")

st.title("Medication Contraindication Checker")
st.write("Check a patient's medication list against amitriptyline package insert.")

# -----------------------------
# Drug Classification Dictionary
# -----------------------------
drug_classes = {
    "fluoxetine": ["SSRI", "CYP2D6 inhibitor"],
    "sertraline": ["SSRI"],
    "citalopram": ["SSRI"],
    "venlafaxine": ["SNRI"],
    "duloxetine": ["SNRI"],
    "tramadol": ["Serotonergic"],
    "sumatriptan": ["Triptan"],
    "rizatriptan": ["Triptan"],
    "linezolid": ["MAOI"],
    "phenelzine": ["MAOI"],
    "tranylcypromine": ["MAOI"],
    "lithium": ["Serotonergic"],
    "diphenhydramine": ["Anticholinergic"],
    "benztropine": ["Anticholinergic"],
    "cimetidine": ["CYP inhibitor"],
    "alcohol": ["CNS depressant"]
}

# -----------------------------
# Contraindication Rules
# -----------------------------
rules = [
    {
        "category": "MAOI",
        "severity": "🔴 Contraindicated",
        "reason": "Risk of severe reaction / serotonin syndrome"
    },
    {
        "category": "SSRI",
        "severity": "🟠 Major",
        "reason": "Serotonin syndrome risk"
    },
    {
        "category": "SNRI",
        "severity": "🟠 Major",
        "reason": "Serotonin syndrome risk"
    },
    {
        "category": "Triptan",
        "severity": "🟠 Major",
        "reason": "Serotonin syndrome risk"
    },
    {
        "category": "Serotonergic",
        "severity": "🟠 Major",
        "reason": "Serotonin syndrome risk"
    },
    {
        "category": "Anticholinergic",
        "severity": "🟡 Moderate",
        "reason": "Additive anticholinergic effects"
    },
    {
        "category": "CNS depressant",
        "severity": "🟡 Moderate",
        "reason": "Increased sedation / overdose risk"
    },
    {
        "category": "CYP2D6 inhibitor",
        "severity": "🟠 Major",
        "reason": "Increased amitriptyline levels"
    }
]

# -----------------------------
# Input
# -----------------------------
med_input = st.text_area("Paste medication list (one per line):")

def normalize_med(med):
    return med.strip().lower()

def check_medications(med_list):
    results = []

    for med in med_list:
        med_clean = normalize_med(med)
        classes = drug_classes.get(med_clean, [])

        if not classes:
            results.append({
                "Medication": med,
                "Flag": "🟢 None",
                "Reason": "No known interaction in tool"
            })
            continue

        for cls in classes:
            for rule in rules:
                if cls == rule["category"]:
                    results.append({
                        "Medication": med,
                        "Flag": rule["severity"],
                        "Reason": rule["reason"]
                    })

    return pd.DataFrame(results)

# -----------------------------
# Run Button
# -----------------------------
if st.button("Check Interactions"):
    meds = [m for m in med_input.split("\n") if m.strip()]

    if not meds:
        st.warning("Please enter at least one medication.")
    else:
        df = check_medications(meds)

        if df.empty:
            st.success("No interactions found.")
        else:
            st.subheader("Results")
            st.dataframe(df)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("For research/clinical support use only. Always apply clinical judgment.")
st.warning("Do not enter PHI. This tool is for screening purposes only based on FDA labeling.")
