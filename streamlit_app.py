import streamlit as st
import requests

st.title("📜 AI Legal Petition Drafter (RAG)")

# Form fields
draft_type = st.selectbox("Draft Type", ["writ_petition", "review_petition", "curative_petition", "civil_suit", "bail_application"])

# Conditional bail application type selection
bail_type = None
if draft_type == "bail_application":
    bail_type = st.selectbox("Bail Application Type", ["regular", "anticipatory"], help="Select the type of bail application")
    draft_type = f"bail_application_{bail_type}"
# Multiple Petitioners and Respondents
st.subheader("👥 Parties to the Case")

# Petitioners section
st.write("**Petitioners:**")
petitioners = []
num_petitioners = st.number_input("Number of Petitioners", min_value=1, max_value=10, value=1, key="num_petitioners")
for i in range(num_petitioners):
    petitioner_name = st.text_input(f"Petitioner {i+1}", key=f"petitioner_{i}")
    if petitioner_name:
        petitioners.append(petitioner_name)

# Respondents section
st.write("**Respondents:**")
respondents = []
num_respondents = st.number_input("Number of Respondents", min_value=1, max_value=10, value=1, key="num_respondents")
for i in range(num_respondents):
    respondent_name = st.text_input(f"Respondent {i+1}", key=f"respondent_{i}")
    if respondent_name:
        respondents.append(respondent_name)
court_name = st.text_input("Court Name")
jurisdiction = st.text_input("Jurisdiction")
case_type = st.text_input("Case Type", "WRIT PETITION")
key_dates = st.text_input("Key Dates (comma separated)")
relief = st.text_area("Relief Sought")
legal_articles = st.text_input("Legal Articles (comma separated)")
rules = st.text_input("Rules to follow (comma separated)")
case_summary = st.text_area("Case Summary")
instructions = st.text_area("Additional Instructions (optional)", placeholder="e.g., Explain every bullet point in detail, emphasize on these dates, etc.")

# File upload for ingestion
uploaded_files = st.file_uploader(
    "Upload reference documents (PDF/DOCX/TXT) for permanent ingestion",
    accept_multiple_files=True,
)

# Annexure file upload section
st.subheader("📎 Annexures")
st.write("Upload annexure documents that will be referenced in the petition and automatically added to the INDEX table.")
annexure_files = st.file_uploader(
    "Upload annexure documents (PDF/DOCX/TXT)",
    accept_multiple_files=True,
    key="annexure_uploader",
    help="These files will be temporarily ingested and referenced in the petition"
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
        import json
        
        data = {
            "draft_type": draft_type,
            "petitioners": json.dumps(petitioners),  # Convert to JSON string
            "respondents": json.dumps(respondents),  # Convert to JSON string
            "court_name": court_name,
            "jurisdiction": jurisdiction,
            "case_type": case_type,
            "key_dates": key_dates,
            "relief_sought": relief,
            "legal_articles": legal_articles,
            "rules_to_follow": rules,
            "case_summary": case_summary,
            "instructions": instructions,
        }

        # Prepare files for upload
        files = []
        if annexure_files:
            for f in annexure_files:
                files.append(("annexure_files", (f.name, f.getvalue(), f.type)))

        res = requests.post("http://localhost:8000/generate", data=data, files=files)
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
