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

    <br>
    <a href="/">Go Back</a>
    """


@app.route("/verify", methods=["POST"])
def verify():
    document_id = request.form["document_id"]
    file = request.files["document"]

    if file.filename == "":
        return "No document selected"

    conn = sqlite3.connect("documents.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT filename, file_hash, uploaded_at, status
        FROM documents
        WHERE document_id = ?
    """, (document_id,))

    document = cursor.fetchone()

    conn.close()

    if document is None:
        return "<h2>Document ID not found!</h2>"

    filename, stored_hash, uploaded_at, status = document

    temp_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "verify_temp"
    )

    file.save(temp_path)

    current_hash = calculate_hash(temp_path)

    os.remove(temp_path)

    if current_hash == stored_hash:
        result = "ORIGINAL DOCUMENT ✅"
    else:
        result = "DOCUMENT MODIFIED ⚠️"

    return f"""
    <h2>{result}</h2>

    <p><b>Document ID:</b> {document_id}</p>

    <p><b>Original Filename:</b> {filename}</p>

    <p><b>Authority Status:</b> {status}</p>

    <p><b>Stored Hash:</b></p>
    <p>{stored_hash}</p>

    <p><b>Current Hash:</b></p>
    <p>{current_hash}</p>

    <p><b>Uploaded At:</b> {uploaded_at}</p>

    <br>
    <a href="/">Go Back</a>
    """


@app.route("/approve", methods=["POST"])
def approve():
    document_id = request.form["document_id"]

    conn = sqlite3.connect("documents.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE documents
        SET status = ?
        WHERE document_id = ?
    """, ("Approved", document_id))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return "<h2>Document ID not found!</h2>"

    conn.close()

    return f"""
    <h2>Document Approved ✅</h2>

    <p><b>Document ID:</b> {document_id}</p>
    <p><b>Status:</b> Approved</p>

    <br>
    <a href="/">Go Back</a>
    """


@app.route("/reject", methods=["POST"])
def reject():
    document_id = request.form["document_id"]

    conn = sqlite3.connect("documents.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE documents
        SET status = ?
        WHERE document_id = ?
    """, ("Rejected", document_id))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return "<h2>Document ID not found!</h2>"

    conn.close()

    return f"""
    <h2>Document Rejected ❌</h2>

    <p><b>Document ID:</b> {document_id}</p>
    <p><b>Status:</b> Rejected</p>

    <br>
    <a href="/">Go Back</a>
    """


if __name__ == "__main__":
    init_db()
    app.run(debug=True)