import os
from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from src.main_app import process_pdf_and_query as main
from src.main_app import chat_with_model
from src.main_app import get_pinecone_namespaces
from src.main_app import generate_answer
import logging
import time
from datetime import datetime

# Configure logger
logger = logging.getLogger("govGPT_usage")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("govGPT_usage.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

UPLOAD_FOLDER = "files"
ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
socketio = SocketIO(app)


def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form["query"]
        search_scope = request.form["search_scope"]
        namespace = (
            request.form["namespace"]
            if not request.form.get("namespace-disabled", "false") == "true"
            else None
        )

        print(f"Query: {query}")
        print(f"Search scope: {search_scope}")
        print(f"Selected namespace: {namespace}")

        if "pdf" in request.files and request.files["pdf"].filename != "":
            file = request.files["pdf"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            else:
                pdf_path = None
        else:
            pdf_path = None

        department = request.form.get("department")
        type_of_document = request.form.get("type_of_document")
        year = request.form.get("year")

        search_results = main(
            query, search_scope, pdf_path, namespace, department, type_of_document, year
        )

        """timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"Timestamp: {timestamp}, Query: {query}, Search scope: {search_scope}, Namespace: {namespace}, PDF Path: {pdf_path}, Department: {department}, Type of Document: {type_of_document}, Year: {year}, Answer: {answer}, Search Results: {search_results}"
        logger.info(log_message)"""

        if pdf_path:
            os.remove(pdf_path)  # Delete the PDF file after processing

        session["query"] = query
        # session["answer"] = answer
        session["search_results"] = search_results
        session["department"] = department
        session["type_of_document"] = type_of_document
        session["year"] = year
        session["namespace"] = namespace
        session["search_scope"] = search_scope
        session["pdf_path"] = pdf_path

        # Redirect to the result route
        return redirect(url_for("result"))

    # Fetch the namespaces outside the POST check
    namespaces = get_pinecone_namespaces()
    return render_template("index.html", namespaces=namespaces)


@app.route("/result")
def result():
    query = session.get("query", "")
    search_results = session.get("search_results", "")
    return render_template("results.html", query=query, search_results=search_results)


@socketio.on("get_answer", namespace="/results")
def get_answer():
    query = session.get("query", "")
    search_results = session.get("search_results", "")
    answer = generate_answer(query, search_results)
    search_scope = session.get("search_scope", "")
    namespace = session.get("namespace", "")
    pdf_path = session.get("pdf_path", "")
    department = session.get("department", "")
    type_of_document = session.get("type_of_document", "")
    year = session.get("year", "")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"Timestamp: {timestamp}, Query: {query}, Search scope: {search_scope}, Namespace: {namespace}, PDF Path: {pdf_path}, Department: {department}, Type of Document: {type_of_document}, Year: {year}, Answer: {answer}, Search Results: {search_results}"
    logger.info(log_message)
    emit("answer_ready", {"answer": answer})


@app.route("/chat", methods=["POST"])
def chat():
    if request.method == "POST":
        query = request.form["query"]
        context = request.form["context"]
        answer = chat_with_model(context, query)
        return jsonify(answer=answer)


if __name__ == "__main__":
    socketio.run(app, debug=True)
