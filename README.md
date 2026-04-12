# Resume Analyzer

A Flask-based web application that analyzes resumes using AI (OpenAI GPT) to provide summaries, scores, and improvement suggestions.

## Features

- Upload PDF or DOCX resumes
- AI-powered analysis using OpenAI GPT-3.5-turbo
- Skill detection
- Resume scoring (0-100)
- Personalized improvement suggestions

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up OpenAI API key:
   - Get an API key from [OpenAI](https://platform.openai.com/)
   - Set environment variable: `OPENAI_API_KEY=your_api_key_here`

3. Run the application:
   ```
   python app.py
   ```

4. Open http://127.0.0.1:5000/ in your browser

## Usage

1. Upload your resume (PDF or DOCX)
2. View the AI-generated analysis including skills, score, and suggestions

## Improvements Made

- Better text extraction using pdfplumber (fallback to PyPDF2)
- Support for DOCX files
- AI integration for comprehensive analysis
- Enhanced UI with more detailed results
- Error handling for unsupported files and AI failures