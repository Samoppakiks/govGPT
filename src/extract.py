import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from urllib.parse import urlparse, quote
from .config import azure_form_key, azure_form_endpoint
from spacy.lang.en import English
import re
import pandas as pd


key = azure_form_key
endpoint = azure_form_endpoint


def is_url(input):
    try:
        result = urlparse(input)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def analyze_read(local_file_path):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    if is_url(local_file_path):
        poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-read", local_file_path
        )
    else:
        with open(local_file_path, "rb") as f:
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-read", f.read()
            )
    result = poller.result()
    pages = []
    for page in result.pages:
        lines = [line.content for line in page.lines]
        page_text = " ".join(lines)
        pages.append((page.page_number, page_text))

    return pages


nlp = English()  # Just the language with no model
nlp.add_pipe("sentencizer")  # Adding a sentencizer pipeline component


def split_sentences(text):
    doc = nlp(text)
    return [sent.text for sent in doc.sents]


def split_into_chunks(text, max_len=800):
    sentences = split_sentences(text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_len:
            current_chunk += sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    return chunks


def clean_and_split_text(text):
    # text = " ".join(text.strip().split("\n"))
    # text = re.sub(r"\d+\n", "", text)
    text = re.sub(r"(\d+(\.|\')\.?\s[^—]+[,—])", r"@@@\1", text)
    segments = text.split("@@@")
    cleaned_segments = []
    for segment in segments:
        # segment = re.sub(r"\s+", " ", segment).strip()
        if len(segment) > 800:
            split_chunks = split_into_chunks(segment)
            cleaned_segments.extend(split_chunks)
        else:
            cleaned_segments.append(segment)
    cleaned_segments = [segment for segment in cleaned_segments if segment.strip()]
    total_chunks = len(cleaned_segments)
    print(f"Total chunks: {total_chunks}")
    return cleaned_segments


def chunks(input):
    pages = analyze_read(input)
    # Process the text from each page and store the results in a DataFram
    data = []
    for page_number, page_text in pages:
        cleaned_segments = clean_and_split_text(page_text)
        for i, segment in enumerate(cleaned_segments):
            data.append((page_number, i + 1, segment))

    df = pd.DataFrame(data, columns=["Page No", "Chunk No", "Text Content"])

    # Print the DataFrame
    print(df)
    return df
