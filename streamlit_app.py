import streamlit as st
import requests

st.title("📜 AI Legal Petition Drafter")

with st.form("petition_form"):
    case_type = st.text_input("Case Type", "writ_petition")
    court_name = st.text_input("Court Name")
    draft_type = st.text_input("draft_type", "petition")
    jurisdiction = st.text_input("Jurisdiction")
    petitioner = st.text_input("Petitioner")
    respondent = st.text_input("Respondent")
    key_dates = st.text_area("Important Dates (comma separated)")
    relief = st.text_area("Relief Sought")
    legal_articles = st.text_area("Legal Articles (comma separated)")
    rules = st.text_area("Rules to Follow (comma separated)")
    case_summary = st.text_area("Case Summary")
    precedents = st.text_area("Precedents")

    submitted = st.form_submit_button("Generate Petition")

if submitted:
    payload = {
        "case_type": case_type,
        "court_name": court_name,
        "draft_type": draft_type,
        "jurisdiction": jurisdiction,
        "petitioner": petitioner,
        "respondent": respondent,
        "case_summary": case_summary,
        "key_dates": [d.strip() for d in key_dates.split(",")],
        "relief_sought": relief,
        "legal_articles": [a.strip() for a in legal_articles.split(",")],
        "rules_to_follow": [r.strip() for r in rules.split(",")],
        "precedents": [p.strip() for p in precedents.split(",")],
    }

    with st.spinner("Generating..."):
        res = requests.post("http://localhost:8000/generate", json=payload)

    if res.status_code == 200:
        with open("petition.docx", "wb") as f:
            f.write(res.content)
        st.success("Petition generated!")
        st.download_button(
            "Download Petition", data=res.content, file_name="petition.docx"
        )
    else:
        st.error("Failed to generate petition.")
