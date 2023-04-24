import os
from .pdftext import extract_text_from_pdf
from .embedchat import process_extracted_text
import pickle
from .embedchat import chatgpt_get_response


def chat_with_model(context, query):
    response = chatgpt_get_response(context, query)
    return response


def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_extracted_text_path(pdf_path):
    return f"./extracted_texts/{os.path.splitext(os.path.basename(pdf_path))[0]}.txt"


def read_extracted_text(txt_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        return file.read()


def process_pdf_and_query(pdf_path, query, search_scope='current_file', department=None, type_of_document=None, year=None):
    create_directory_if_not_exists("./embeddings")

    txt_file_path = get_extracted_text_path(pdf_path)
    if os.path.exists(txt_file_path):
        extracted_text = read_extracted_text(txt_file_path)
    else:
        extracted_text = extract_text_from_pdf(pdf_path)

    answer, search_results = process_extracted_text(
        query, extracted_text, pdf_path, search_scope, department=department, type_of_document=type_of_document, year=year)
    return answer, search_results


if __name__ == "__main__":
    pdf_path = '../PDF/File_Udaan_pads.pdf'
    query = 'What is Rajivika producing for Udaan scheme?'
    final = process_pdf_and_query(pdf_path, query)
    print(final)
