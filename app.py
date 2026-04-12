from flask import Flask, render_template, request
import pdfplumber
from PyPDF2 import PdfReader
from docx import Document
from openai import OpenAI
import re

app = Flask(__name__)

# -------------------------------
# OPENROUTER CLIENT
# -------------------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

# -------------------------------
# FILE TEXT EXTRACTION
# -------------------------------
def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text


def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


# -------------------------------
# ROUTES
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("resume")

    if not file:
        return render_template("result.html", error="No file uploaded.")

    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file)
    else:
        return render_template("result.html", error="Upload PDF or DOCX only.")

    skills_list = [
        "python", "java", "c", "c++", "html", "css",
        "javascript", "sql", "mysql", "flask", "django"
    ]
    found_skills = [skill for skill in skills_list if skill.lower() in text.lower()]

    try:
        prompt = f"""
You are a professional ATS resume analyzer.

Analyze the resume and return EXACTLY in this format:

SUMMARY:
Write 2-3 sentence professional overview of the candidate.

SCORE:
Give a score out of 100.

SKILLS:
List technical and soft skills comma separated.

SUGGESTIONS:
Give 4 bullet point improvement suggestions only.

Resume:
{text[:2000]}
"""

        response = client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b:free",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        ai_analysis = response.choices[0].message.content.strip()

        print("AI RESPONSE:\n", ai_analysis)

        # -------------------------------
        # PARSING
        # -------------------------------
        try:
            summary = ai_analysis.split("SUMMARY:")[1].split("SCORE:")[0].strip()
        except:
            summary = "No summary found."

        try:
            score_match = re.search(r"SCORE:\s*(\d+)", ai_analysis)
            score = int(score_match.group(1)) if score_match else 50
        except:
            score = 50

        try:
            ai_skills = ai_analysis.split("SKILLS:")[1].split("SUGGESTIONS:")[0].strip()
            ai_skills = ai_skills.replace("\n", ", ").strip().strip(",")
        except:
            ai_skills = ", ".join(found_skills)

        try:
            suggestions = ai_analysis.split("SUGGESTIONS:")[1].strip()
        except:
            suggestions = "No suggestions found."

        message = "AI Analysis Complete 🚀"

    except Exception as e:
        print("FULL ERROR:", e)

        summary = "AI failed to analyze resume."
        ai_skills = ", ".join(found_skills)
        suggestions = "Try improving skills and formatting."
        score = min(len(found_skills) * 15 + 20, 100)
        message = "Basic Analysis (AI Failed)"

    return render_template(
        "result.html",
        summary=summary,
        skills=ai_skills,
        suggestions=suggestions,
        score=score,
        message=message
    )


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)