import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ------------------------------
# Extract skills from JD
# ------------------------------
def extract_required_skills(job_description):

    prompt = f"""
Extract the key technical skills required from this job description.

Return ONLY a comma-separated list.

Job Description:
{job_description}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()


# ------------------------------
# Extract resume skills
# ------------------------------
def extract_resume_skills(resume_text):

    prompt = f"""
Extract the key technical skills from this resume.

Return ONLY a comma-separated list.

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()


# ------------------------------
# Resume summary
# ------------------------------
def summarize_resume(resume_text):

    prompt = f"""
Summarize this resume in 2 short sentences.

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=150
    )

    return response.choices[0].message.content.strip()


# ------------------------------
# Skill match + gap analysis
# ------------------------------
def calculate_skill_match(jd_skills, resume_skills):

    jd_list = [s.strip().lower() for s in jd_skills.split(",")]
    resume_list = [s.strip().lower() for s in resume_skills.split(",")]

    matches = [s for s in jd_list if s in resume_list]
    missing = [s for s in jd_list if s not in resume_list]

    if len(jd_list) == 0:
        return 0, [], []

    percentage = int((len(matches) / len(jd_list)) * 100)

    return percentage, matches, missing


# ------------------------------
# Candidate evaluation
# ------------------------------
def evaluate_candidate(job_description, resume_text):

    prompt = f"""
You are an AI HR recruitment assistant.

Analyze the Job Description and Resume.

Score the candidate out of 100 based on:
- Skill match (40%)
- Experience (40%)
- Education (20%)

Return STRICTLY in this format:

Score: <number>

Reasoning:
<short explanation>

Job Description:
{job_description}

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a professional HR assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )

    content = response.choices[0].message.content

    match = re.search(r"Score:\s*(\d+)", content)
    score = int(match.group(1)) if match else 0

    return {"score": score, "details": content}


# ------------------------------
# Interview questions
# ------------------------------
def generate_interview_questions(job_description, resume_text):

    prompt = f"""
Generate exactly 3 technical interview questions.

Format:

1. Question
2. Question
3. Question

Job Description:
{job_description}

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()


# ------------------------------
# Hiring decision agent
# ------------------------------
def hiring_decision_agent(job_description, results):

    summary = "\n".join(
        [f"{r['name']} | Score {r['score']} | SkillMatch {r['skill_match']}%" for r in results]
    )

    prompt = f"""
You are an AI hiring assistant.

Return:

Top Candidate:
Decision:
Reason:
Next Step:

Job Description:
{job_description}

Candidates:
{summary}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=250
    )

    return response.choices[0].message.content.strip()


# ------------------------------
# Hiring insight
# ------------------------------
def hiring_insight(job_description, results):

    summary = "\n".join([f"{r['name']} Score {r['score']}" for r in results])

    prompt = f"""
Provide a short hiring insight.

Job Description:
{job_description}

Candidates:
{summary}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()