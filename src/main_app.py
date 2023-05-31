# from .config import pinecone_api_key, pinecone_environment
import os

# from .pdftext import extract_text_from_pdf
from .embedchat import (
    process_extracted_text,
    chatgpt_get_response,
    query_vector_database,
    chatgpt_summarize_results,
)
import requests
import os
import pandas as pd
from .extract import analyze_read, clean_and_split_text, chunks

pinecone_api_key = os.environ.get("PINECONE_API_KEY")
pinecone_environment = os.environ.get("PINECONE_ENV")


def get_pinecone_namespaces():
    url = "https://rajgov-f44d42f.svc.northamerica-northeast1-gcp.pinecone.io/describe_index_stats"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Api-Key": pinecone_api_key,
    }
    response = requests.get(url, headers=headers)  # Update the method to GET
    print("Server response:", response.text)
    json_response = response.json()
    namespaces = json_response.get("namespaces", [])
    return namespaces


def chat_with_model(context, query):
    response = chatgpt_get_response(context, query)
    return response


def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def add_metadata(df, filename, department=None, type_of_document=None, year=None):
    df["Year"] = year
    df["Department"] = department
    df["Type of Document"] = type_of_document
    df["Title"] = filename
    return df


def process_pdf_and_query(query, df=None, search_scope="current_file", namespace=None):
    # ...
    if df is not None:
        answer, search_results = process_extracted_text(query, df, search_scope)
    elif namespace is not None:
        # Query the index using the provided namespace
        results = query_vector_database(query, namespace)
        answer, search_results = chatgpt_summarize_results(query, results)
    return answer, search_results


if __name__ == "__main__":
    pdf_path = "../PDF/File_Udaan_pads.pdf"
    query = "What is Rajivika producing for Udaan scheme?"
    final = process_pdf_and_query(pdf_path, query)
    print(final)
