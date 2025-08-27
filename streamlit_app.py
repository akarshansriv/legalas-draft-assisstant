import streamlit as st
import requests

st.title("📜 AI Legal Petition Drafter (RAG)")

# Form fields
draft_type = st.selectbox("Draft Type", ["writ_petition", "review_petition", "curative_petition", "civil_suit"])
petitioner = st.text_input("Petitioner")
respondent = st.text_input("Respondent")
court_name = st.text_input("Court Name")
jurisdiction = st.text_input("Jurisdiction")
case_type = st.text_input("Case Type", "WRIT PETITION")
key_dates = st.text_input("Key Dates (comma separated)")
relief = st.text_area("Relief Sought")
legal_articles = st.text_input("Legal Articles (comma separated)")
rules = st.text_input("Rules to follow (comma separated)")
case_summary = st.text_area("Case Summary")

# File upload for ingestion
uploaded_files = st.file_uploader(
    "Upload reference documents (PDF/DOCX/TXT) for permanent ingestion",
    accept_multiple_files=True,
)

# Ingest files permanently into the knowledge base
if st.button("Ingest Files"):
    if not uploaded_files:
        st.warning("Please upload at least one file to ingest.")
    else:
        files = []
        for f in uploaded_files:
            files.append(("files", (f.name, f.getvalue(), f.type)))
        with st.spinner("Ingesting into knowledge base..."):
            res = requests.post("http://localhost:8000/ingest", files=files)
            if res.status_code == 200:
                st.success("Files ingested successfully into the knowledge base!")
            else:
                st.error(f"Ingestion failed: {res.status_code} {res.text}")

# Generate draft using already ingested files
if st.button("Generate Draft"):
    with st.spinner("Generating..."):
        data = {
            "draft_type": draft_type,
            "petitioner": petitioner,
            "respondent": respondent,
            "court_name": court_name,
            "jurisdiction": jurisdiction,
            "case_type": case_type,
            "key_dates": key_dates,
            "relief_sought": relief,
            "legal_articles": legal_articles,
            "rules_to_follow": rules,
            "case_summary": case_summary,
        }

        res = requests.post("http://localhost:8000/generate", data=data)
        if res.status_code == 200:
            with open("petition.docx", "wb") as f:
                f.write(res.content)
            st.success("Draft generated successfully!")
            st.download_button(
                "Download Petition",
                data=open("petition.docx", "rb"),
                file_name="petition.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        else:
            st.error(f"Generation failed: {res.status_code} {res.text}")
