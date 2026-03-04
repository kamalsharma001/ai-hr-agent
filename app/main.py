from resume_parser import extract_text_from_pdf
from agent import evaluate_candidate
import os


if __name__ == "__main__":

    job_description = """
Looking for a Python Developer with:
- Strong Python skills
- Experience in FastAPI or Django
- Knowledge of machine learning
- Understanding of REST APIs
- Good problem-solving skills
"""

    resumes_folder = "resumes"   # Create this folder
    results = []

    for file in os.listdir(resumes_folder):
        if file.endswith(".pdf"):
            path = os.path.join(resumes_folder, file)
            resume_text = extract_text_from_pdf(path)

            evaluation = evaluate_candidate(job_description, resume_text)

            results.append({
                "name": file,
                "score": evaluation["score"],
                "details": evaluation["details"]
            })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    print("\n=== RANKED CANDIDATES ===\n")

    for rank, candidate in enumerate(results, start=1):
        print(f"{rank}. {candidate['name']} - {candidate['score']}/100\n")