from urllib import response

from flask import Flask, render_template, request
import os
import re
import pdfplumber
from PyPDF2 import PdfReader
from docx import Document
from openai import OpenAI



app = Flask(__name__)

# 🔑 SET YOUR GEMINI API KEY HERE
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)
# ---------- FILE TEXT EXTRACTION ----------

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


# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['resume']

    if not file:
        return render_template("result.html", error="No file uploaded.")

    filename = file.filename.lower()

    if filename.endswith('.pdf'):
        text = extract_text_from_pdf(file)
    elif filename.endswith('.docx'):
        text = extract_text_from_docx(file)
    else:
        return render_template("result.html", error="Upload PDF or DOCX only.")

    text = text.lower()

    # fallback skills
    skills_list = ["python", "java", "c", "html", "css", "javascript", "sql"]
    found_skills = [s for s in skills_list if s in text]

    # default values
    summary = ""
    ai_skills = ""
    suggestions = ""
    score = 0
    message = "Analysis complete"

    try:
        # 🔥 STRONG PROMPT
        prompt = f"""
You are a professional resume analyzer.

Analyze the resume and return output EXACTLY in this format:

SUMMARY:
Write 2-3 sentence professional overview of the candidate's profile only.

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
    model="deepseek-ai/deepseek-v3.2",
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=1,
    top_p=0.95,
    max_tokens=8192
)

        ai_analysis = response.choices[0].message.content

       
        print("AI RESPONSE:\n", ai_analysis)

        if not ai_analysis:
            raise Exception("Empty AI response")

        # ---------- PARSING ----------

        try:
            summary = ai_analysis.split("SUMMARY:")[1].split("SCORE:")[0].strip()
        except:
            summary = "No summary found"

        try:
            score_match = re.search(r'SCORE:\s*(\d+)', ai_analysis)
            if score_match:
                score = int(score_match.group(1))
        except:
            score = 0

        try:
            ai_skills = ai_analysis.split("SKILLS:")[1].split("SUGGESTIONS:")[0].strip()
            ai_skills = ai_skills.replace("\n", ", ").strip().strip(',')
        except:
            ai_skills = ', '.join(found_skills)

        try:
            suggestions = ai_analysis.split("SUGGESTIONS:")[1].strip()
        except:
            suggestions = "No suggestions found"

        message = "AI Analysis complete 🚀"

    except Exception as e:
        print("FULL ERROR:", e)

        error_text = str(e)

        if "RESOURCE_EXHAUSTED" in error_text:
            summary = "AI quota exceeded. Please try again later."
            ai_skills = ', '.join(found_skills)
            suggestions = "Gemini API free tier limit reached."
            score = min(len(found_skills) * 20, 100)
            message = "Quota limit reached"

        else:
            summary = "AI failed to analyze resume."
            ai_skills = ', '.join(found_skills)
            suggestions = "Try again later."
            score = min(len(found_skills) * 20, 100)
            message = "AI failed"

    return render_template("result.html",
                           summary=summary,
                           skills=ai_skills,
                           suggestions=suggestions,
                           score=score,
                           message=message)


# ---------- RUN ----------

if __name__ == "__main__":
    app.run(debug=True)