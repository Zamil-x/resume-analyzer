from flask import Flask, render_template, request
import os
import re
from PyPDF2 import PdfReader
import pdfplumber
from docx import Document
from openai import OpenAI


app = Flask(__name__)

# Initialize OpenAI client (optional - only if API key is available)
openai_api_key = os.getenv('OPENAI_API_KEY')
print("API KEY:", openai_api_key)
client = None
if openai_api_key:
    try:
        client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        print(f"Warning: OpenAI client initialization failed: {e}")
        client = None

def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except:
        # Fallback to PyPDF2
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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['resume']
    
    if file:
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        else:
            return render_template("result.html", error="Unsupported file type. Please upload PDF or DOCX.")
        
        text = text.lower()
        
        # Basic skill check (keep for now, but AI will do better)
        skills = [
            "python", "java", "c", "c++",
            "html", "css", "javascript",
            "sql", "mysql",
            "react", "node", "flask",
            "machine learning", "data analysis"
        ]
        found_skills = [skill for skill in skills if skill in text]
        
        # AI Analysis
        summary = ""
        ai_skills = ""
        suggestions = ""
        score = 0
        message = "Analysis complete"
        
        if client:  # Only use AI if client is initialized
            try:
                prompt = f"""
                        You are a resume analyzer.

                        Return output in this EXACT format:

                        SUMMARY:
                        <short summary>

                        SCORE:
                        <number out of 100>

                        SKILLS:
                        <comma separated skills>

                        SUGGESTIONS:
                        <bullet points>

                        Resume:
                        {text[:3000]}
                        """
                
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                
                ai_analysis = response.choices[0].message.content.strip()
                print("AI RESPONSE:\n", ai_analysis)
                

                score_match = re.search(r'SCORE:\s*(\d+)', ai_analysis)
                if score_match:
                    score = int(score_match.group(1))
                
                # Parse AI response (simple split, could be improved)
                lines = ai_analysis.split('\n')
                
                current_section = ""
                for line in lines:
                    if line.strip().startswith("SUMMARY"):
                        current_section = "summary"
                    elif "skills" in line.lower():
                        current_section = "skills"
                    elif "suggestions" in line.lower():
                        current_section = "suggestions"
                    else:
                        if current_section == "summary":
                            summary += line + " "
                        elif current_section == "skills":
                            ai_skills += line + " , "
                        elif current_section == "suggestions":
                            suggestions += line + " "
                
                # Fallback score if AI fails
                if score == 0:
                    score = min(len(found_skills) * 20, 100)
                
                message = "Analysis complete (AI-powered)"
                
            except Exception as e:
                # Fallback if AI fails
                print(f"AI analysis failed: {e}")
                summary = "Unable to generate AI summary."
                ai_skills = ', '.join(found_skills)
                suggestions = "Consider adding more details about your experience and skills."
                score = min(len(found_skills) * 20, 100)
                message = "Basic analysis (AI failed)"
        else:
            # No API key - use basic analysis
            summary = "Basic resume analysis (AI features not available)"
            ai_skills = ', '.join(found_skills)
            suggestions = "To get AI-powered suggestions, set your OPENAI_API_KEY environment variable."
            score = min(len(found_skills) * 20, 100)
            message = "Basic analysis (AI features disabled)"
        
        return render_template("result.html", 
                               skills=ai_skills or ', '.join(found_skills), 
                               score=score,
                               message=message,
                               summary=summary,
                               suggestions=suggestions)
    else:
        return render_template("result.html", error="No file uploaded.")
    
    return "No file uploaded"

if __name__ == "__main__":
    app.run(debug=True)