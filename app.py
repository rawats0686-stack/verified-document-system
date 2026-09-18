from flask import Flask, render_template, request
import os
import hashlib

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["document"]

    if file.filename == "":
        return "No file selected"

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    document_hash = calculate_hash(file_path)

    return f"""
    <h2>Document uploaded successfully!</h2>
    <p><b>SHA-256 Hash:</b></p>
    <p>{document_hash}</p>
    """


if __name__ == "__main__":
    app.run(debug=True)