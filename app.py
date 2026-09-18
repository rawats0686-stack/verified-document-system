from flask import Flask, render_template, request
import os
import hashlib
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def init_db():
    conn = sqlite3.connect("documents.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT UNIQUE,
            filename TEXT,
            file_hash TEXT,
            uploaded_at TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


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

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(file_path)

    document_hash = calculate_hash(file_path)

    document_id = "DOC-" + uuid.uuid4().hex[:8].upper()

    uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("documents.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO documents
        (document_id, filename, file_hash, uploaded_at, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        document_id,
        file.filename,
        document_hash,
        uploaded_at,
        "Pending"
    ))

    conn.commit()
    conn.close()

    return f"""
    <h2>Document uploaded successfully!</h2>

    <p><b>Document ID:</b> {document_id}</p>

    <p><b>SHA-256 Hash:</b></p>
    <p>{document_hash}</p>

    <p><b>Status:</b> Pending</p>

    <p><b>Uploaded At:</b> {uploaded_at}</p>
    """


if __name__ == "__main__":
    init_db()
    app.run(debug=True)