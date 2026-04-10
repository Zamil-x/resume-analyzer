from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['resume']
    
    if file:
        filename = file.filename
        return f"File uploaded: {filename}"
    
    return "No file uploaded"

if __name__ == "__main__":
    app.run(debug=True)