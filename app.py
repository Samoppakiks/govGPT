import os
from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from src.main_app import process_pdf_and_query as main
from src.main_app import chat_with_model

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
        # Check if the post request has the file part
        if 'pdf' not in request.files:
            return redirect(request.url)
        file = request.files['pdf']
        # If the user does not select a file, the browser submits an empty file.
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            query = request.form['query']
            search_scope = request.form['search_scope']  # Add this line
            department = request.form.get('department')
            type_of_document = request.form.get('type_of_document')
            year = request.form.get('year')
            answer, search_results = main(
                pdf_path, query, search_scope, department, type_of_document, year)
            os.remove(pdf_path)  # Delete the PDF file after processing
            # Redirect to the result route
            return redirect(url_for('result', answer=answer, search_results=search_results))
    return render_template('index.html')


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
