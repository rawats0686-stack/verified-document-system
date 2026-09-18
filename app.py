from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["document"]

    if file.filename == "":
        return "No file selected"

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

    return "Document uploaded successfully!"

if __name__ == "__main__":
    app.run(debug=True)