import os
import fitz  # PyMuPDF
import json
import re



from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Load predefined skills database
with open("skills_db.json", "r") as f:
    SKILLS_DB = set(json.load(f))

def extract_text_from_jd(jd_file):
    """Extract text from JD PDF or plain text file"""
    ext = os.path.splitext(jd_file.name)[-1].lower()
    if ext == ".pdf":
        text = ""
        with fitz.open(stream=jd_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    elif ext in [".txt", ".text"]:
        return jd_file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported JD file type. Use .pdf or .txt")

def clean_and_tokenize(text):
    """Basic NLP cleanup and tokenization"""
    text = text.lower()
    text = re.sub(r'\n+', ' ', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    filtered = [w for w in tokens if w not in stop_words]
    return filtered

def extract_skills_from_jd(text):
    """Match tokens against known skills"""
    tokens = clean_and_tokenize(text)
    found_skills = set()
    for token in tokens:
        if token in SKILLS_DB:
            found_skills.add(token)
    return list(found_skills)

# For testing as a script
if __name__ == "__main__":
    with open("jd_sample.pdf", "rb") as jd_file:
        jd_text = extract_text_from_jd(jd_file)
        skills = extract_skills_from_jd(jd_text)
        print("Extracted Skills:", skills)

import fitz  # PyMuPDF
import re

def extract_skills_from_pdf(uploaded_file):
    if not uploaded_file:
        return []

    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()

    return extract_skills_from_text(text)

def extract_skills_from_text(text):
    # Simple example skill list — update as needed
    skill_keywords = [
        "python", "machine learning", "nlp", "deep learning", "tensorflow", "keras",
        "pandas", "numpy", "sql", "django", "flask", "git", "html", "css", "react",
        "excel", "communication", "teamwork", "leadership", "java", "c++", "linux"
    ]

    text = text.lower()
    skills_found = [skill for skill in skill_keywords if skill.lower() in text]
    return list(set(skills_found))
