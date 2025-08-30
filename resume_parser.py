# resume_parser.py

import os
import fitz        #from PyMuPDF
import re
from skill_matcher import match_skills

from jd_parser import extract_skills_from_text

def parse_resume(file_path, jd_skills):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()

        resume_skills = extract_skills_from_text(text)  # ✅ Use NLP-based extraction here
        result = match_skills(jd_skills, resume_skills)

        return {
            "file_name": os.path.basename(file_path),
            "resume_text": text,
            "matched_skills": result["matched_skills"],
            "missing_skills": result["missing_skills"],
            "match_percentage": result["match_percentage"]
        }

    except Exception as e:
        print(f"[Error] Resume parsing failed: {file_path} - {e}")
        return None

