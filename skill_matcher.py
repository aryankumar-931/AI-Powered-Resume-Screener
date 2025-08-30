def match_skills(jd_skills, resume_skills):
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)
    matched = list(jd_set & resume_set)
    missing = list(jd_set - resume_set)
    match_percentage = (len(matched) / len(jd_set)) * 100 if jd_set else 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": round(match_percentage, 2)
    }
