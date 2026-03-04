import streamlit as st
import os
import pandas as pd

from app.resume_parser import extract_text_from_pdf
from app.agent import (
    evaluate_candidate,
    extract_required_skills,
    extract_resume_skills,
    calculate_skill_match,
    generate_interview_questions,
    hiring_decision_agent,
    summarize_resume,
    hiring_insight
)

st.title("AI HR Recruitment Agent")

job_description = st.text_area("Enter Job Description")

uploaded_files = st.file_uploader(
    "Upload Candidate Resumes",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Analyze Candidates"):

    if not job_description:
        st.warning("Please enter a job description")

    elif not uploaded_files:
        st.warning("Please upload resumes")

    else:

        with st.spinner("Analyzing candidates..."):

            skills = extract_required_skills(job_description)

            st.subheader("Required Skills")
            st.write(skills)

            results = []

            for file in uploaded_files:

                temp = f"temp_{file.name}"

                with open(temp, "wb") as f:
                    f.write(file.getbuffer())

                try:

                    resume_text = extract_text_from_pdf(temp)

                    summary = summarize_resume(resume_text)

                    resume_skills = extract_resume_skills(resume_text)

                    match, matched, missing = calculate_skill_match(
                        skills,
                        resume_skills
                    )

                    evaluation = evaluate_candidate(
                        job_description,
                        resume_text
                    )

                    results.append({
                        "name": file.name,
                        "score": evaluation["score"],
                        "details": evaluation["details"],
                        "skill_match": match,
                        "matched_skills": matched,
                        "missing_skills": missing,
                        "summary": summary,
                        "resume_text": resume_text
                    })

                finally:
                    if os.path.exists(temp):
                        os.remove(temp)

            results.sort(key=lambda x: x["score"], reverse=True)

            # Comparison table
            df = pd.DataFrame([
                {
                    "Candidate": r["name"],
                    "Score": r["score"],
                    "Skill Match": f"{r['skill_match']}%"
                }
                for r in results
            ])

            st.subheader("Candidate Comparison")
            st.table(df)

            # Chart
            st.subheader("Score Visualization")
            st.bar_chart(df.set_index("Candidate")["Score"])

            # Hiring decision
            decision = hiring_decision_agent(job_description, results)

            st.subheader("AI Hiring Decision")
            st.success(decision)

            # Hiring insight
            insight = hiring_insight(job_description, results)

            st.subheader("AI Hiring Insight")
            st.info(insight)

            # Download report
            csv = pd.DataFrame(results).to_csv(index=False)

            st.download_button(
                "Download Hiring Report",
                csv,
                "hiring_report.csv",
                "text/csv"
            )

            st.subheader("Candidate Details")

            for i, candidate in enumerate(results, 1):

                st.write(f"### {i}. {candidate['name']}")

                st.write("Resume Summary")
                st.write(candidate["summary"])

                st.write(f"Score: {candidate['score']}/100")
                st.progress(candidate["score"] / 100)

                st.write(f"Skill Match: {candidate['skill_match']}%")
                st.progress(candidate["skill_match"] / 100)

                st.write(
                    "Matching Skills:",
                    ", ".join(candidate["matched_skills"]) or "None"
                )

                st.write(
                    "Missing Skills:",
                    ", ".join(candidate["missing_skills"]) or "None"
                )

                with st.expander("AI Evaluation"):
                    st.write(candidate["details"])

                with st.expander("Interview Questions"):

                    questions = generate_interview_questions(
                        job_description,
                        candidate["resume_text"]
                    )

                    st.write(questions)