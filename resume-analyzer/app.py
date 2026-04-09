from flask import Flask, render_template, request
import os
from PyPDF2 import PdfReader

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# extract text from PDF
def extract_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.lower()

# simple keyword matching
def analyze(resume_text, job_desc):
    resume_words = set(resume_text.split())
    job_words = set(job_desc.lower().split())

    matched = resume_words.intersection(job_words)
    score = (len(matched) / len(job_words)) * 100

    missing = job_words - resume_words
    return round(score, 2), list(missing)[:10]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['resume']
        job_desc = request.form['job_desc']

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        resume_text = extract_text(file_path)
        score, missing = analyze(resume_text, job_desc)

        return render_template('index.html', score=score, missing=missing)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    