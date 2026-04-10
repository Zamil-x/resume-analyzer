from flask import Flask, render_template, request
from PyPDF2 import PdfReader

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['resume']
    
    if file:
        reader = PdfReader(file)
        text = ""

        for page in reader.pages:
            text += page.extract_text()

        # 🔍 skill check
        skills = ["python", "java", "html", "css", "sql"]
        found_skills = []

        for skill in skills:
            if skill.lower() in text.lower():
                found_skills.append(skill)

        # ⭐ score calculation
        score = len(found_skills) * 20

        if score >= 80:
            message = "Excellent Resume 👍"
        elif score >= 50:
                message = "Good, but can improve 🙂"
        else:
                message = "Needs improvement ⚠️"

        return render_template("result.html", skills=', '.join(found_skills), score=score)
    
    return "No file uploaded"

if __name__ == "__main__":
    app.run(debug=True)