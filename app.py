import os
from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from src.main_app import process_pdf_and_query as main
from src.main_app import chat_with_model
from src.main_app import get_pinecone_namespaces

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        search_scope = request.form['search_scope']
        namespace = request.form['namespace'] if not request.form.get(
            'namespace-disabled', 'false') == 'true' else None

        print(f"Query: {query}")
        print(f"Search scope: {search_scope}")
        print(f"Selected namespace: {namespace}")

        if 'pdf' in request.files and request.files['pdf'].filename != '':
            file = request.files['pdf']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            else:
                pdf_path = None
        else:
            pdf_path = None

        department = request.form.get('department')
        type_of_document = request.form.get('type_of_document')
        year = request.form.get('year')

        answer, search_results = main(
            query, search_scope, pdf_path, namespace, department, type_of_document, year)

        if pdf_path:
            os.remove(pdf_path)  # Delete the PDF file after processing

        # Redirect to the result route
        return redirect(url_for('result', answer=answer, search_results=search_results))

    # Fetch the namespaces outside the POST check
    namespaces = get_pinecone_namespaces()
    return render_template('index.html', namespaces=namespaces)


@app.route('/result')
def result():
    answer = request.args.get('answer', '')
    search_results = request.args.get('search_results', '')
    return render_template('results.html', answer=answer, search_results=search_results)


@app.route('/chat', methods=['POST'])
def chat():
    if request.method == 'POST':
        query = request.form['query']
        context = request.form['context']
        answer = chat_with_model(context, query)
        return jsonify(answer=answer)


if __name__ == '__main__':
    app.run(debug=True)
