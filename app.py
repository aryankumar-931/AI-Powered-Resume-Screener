import streamlit as st
import os
import tempfile
import pandas as pd
import re

from resume_parser import parse_resume
from jd_parser import extract_skills_from_pdf, extract_skills_from_text

st.set_page_config(page_title="Resume Screener", layout="wide")
st.title("🔍 AI-Powered Resume Matcher")
# st.markdown(
#     """
#     <div style='text-align: right; font-size: 18px; color: #ccc; margin-top: -20px;'>
#         -- By Aryan K.S.
#     </div>
#     """,
#     unsafe_allow_html=True
# )

# ---------------- TABS ---------------- #
tab1, tab2, tab3 = st.tabs(["📄 Upload & JD Setup", "📊 Matching Results", "📘 Skill Highlighting"])

# -------------- TAB 1: UPLOAD & JD SETUP -------------- #
with tab1:
    st.header("📄 Upload Job Description and Resumes")

    # Upload Job Description
    st.subheader("📑Upload JD")
    jd_format = st.radio("Select JD Format:", ("Text", "PDF"))
    if jd_format == "Text":
        jd_text_input = st.text_area("Paste the Job Description here")
        jd_skills = extract_skills_from_text(jd_text_input) if jd_text_input else []
    else:
        jd_file = st.file_uploader("Upload JD PDF", type=["pdf"], key="jd_pdf")
        jd_skills = extract_skills_from_pdf(jd_file) if jd_file else []

    if jd_skills:
        st.success(f"✅ Extracted {len(jd_skills)} skills from JD.")
        st.write(jd_skills)

    # Upload Resumes
    st.subheader("📂Upload Resumes")
    resume_files = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

    # Match Filter
    min_match_percent = st.slider("🎯 Minimum Match % to Display", 0, 100, 0)

    # Run Matching Button
    match_clicked = st.button("🔎 Start Matching")
    if match_clicked:
        st.subheader("Now go to next tab ''Matching Results''")
        st.snow()

# ------------ SHARED PROCESSING (Only if triggered) ------------ #
results = []
if 'match_clicked' in locals() and match_clicked and jd_skills and resume_files:
    for uploaded_resume in resume_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_resume.read())
            parsed = parse_resume(tmp.name, jd_skills)
            if parsed:
                parsed["original_file_name"] = uploaded_resume.name
                results.append(parsed)

    results = [r for r in results if r["match_percentage"] >= min_match_percent]
    results.sort(key=lambda x: x["match_percentage"], reverse=True)

    for idx, res in enumerate(results):
        res["index"] = idx + 1
        res["file_name"] = res.get("original_file_name", res["file_name"])


# -------------- TAB 2: MATCHING RESULTS -------------- #
with tab2:
    st.header("📊 Matching Results")
    if results:
        df_results = pd.DataFrame([{
            "No.": r["index"],
            "Resume": r["file_name"],
            "Match %": r["match_percentage"],
            "Matched Skills": ", ".join(r["matched_skills"]),
            "Missing Skills": ", ".join(r["missing_skills"]),
        } for r in results])

        st.dataframe(df_results.set_index("No."), use_container_width=True)

        # Download CSV
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results as CSV", data=csv, file_name="resume_matching_results.csv", mime="text/csv")
    else:
        st.warning("⚠️ No results yet. Run matching from the first tab.")

# -------------- TAB 3: SKILL HIGHLIGHTING -------------- #
with tab3:
    st.header("📘 Skill Highlighting in Resumes")
    if results:
        for res in results:
            highlighted_text = res["resume_text"]

            # Green highlight for matched
            for skill in res["matched_skills"]:
                highlighted_text = re.sub(
                    rf"\b({re.escape(skill)})\b",
                    r"<span style='color:green; font-weight:bold'>\1</span>",
                    highlighted_text,
                    flags=re.IGNORECASE,
                )

            # Red highlight for missing
            for skill in res["missing_skills"]:
                highlighted_text = re.sub(
                    rf"\b({re.escape(skill)})\b",
                    r"<span style='color:red; font-weight:bold'>\1</span>",
                    highlighted_text,
                    flags=re.IGNORECASE,
                )

            st.markdown(f"**📄 {res['file_name']}**", unsafe_allow_html=True)
            # Custom progress bar
            filled_blocks = int(res["match_percentage"] / 4)  # 25 blocks total
            empty_blocks = 25 - filled_blocks
            bar = "█" * filled_blocks + " " * empty_blocks
            st.markdown(
                f"<div style='font-family:monospace;'>📄 <b>{res['file_name']}</b> &nbsp;&nbsp; <span style='color:#1E90FF;'>{bar}</span> &nbsp;&nbsp; <b>{res['match_percentage']}%</b></div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='background-color:#f9f9f9; color: #000080; padding:12px; border-radius:10px; white-space: pre-wrap; text-align: justify'>{highlighted_text}</div>",
                unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
    else:

        st.info("ℹ️ No resumes to highlight. First run the matcher from Tab 1.")
