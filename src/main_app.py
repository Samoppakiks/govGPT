import os
from .pdftext import extract_text_from_pdf
from .embedchat import process_extracted_text
import pickle
from .embedchat import chatgpt_get_response
import requests

from .config import pinecone_api_key, pinecone_environment
from .extract import analyze_read, clean_and_split_text, chunks

"""pinecone_api_key = os.environ.get("PINECONE_API_KEY")
pinecone_environment = os.environ.get("PINECONE_ENV")"""


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


"""def get_extracted_text_path(pdf_path):
    return f"./extracted_texts/{os.path.splitext(os.path.basename(pdf_path))[0]}.txt"


def read_extracted_text(txt_file_path):
    with open(txt_file_path, "r", encoding="utf-8") as file:
        return file.read()"""


def process_pdf_and_query(
    query,
    search_scope="current_file",
    pdf_path=None,
    namespace=None,
    department=None,
    type_of_document=None,
    year=None,
):
    create_directory_if_not_exists("./embeddings")

    if pdf_path:
        txt_file_path = get_extracted_text_path(pdf_path)
        if os.path.exists(txt_file_path):
            extracted_text = read_extracted_text(txt_file_path)
        else:
            extracted_text = extract_text_from_pdf(pdf_path)
    elif namespace:
        txt_file_path = f"./extracted_texts/{namespace}.txt"
        if os.path.exists(txt_file_path):
            extracted_text = read_extracted_text(txt_file_path)
        else:
            print(f"Error: No text file found for the namespace '{namespace}'")
            return None, None
    else:
        extracted_text = ""

    answer, search_results = process_extracted_text(
        query,
        extracted_text,
        pdf_path,
        search_scope,
        department=department,
        type_of_document=type_of_document,
        year=year,
        namespace=namespace,
    )
    return answer, search_results


if __name__ == "__main__":
    pdf_path = "../PDF/File_Udaan_pads.pdf"
    query = "What is Rajivika producing for Udaan scheme?"
    final = process_pdf_and_query(pdf_path, query)
    print(final)


"""okay. i will now share the script of the existing process_extracted_text function that creates the embeddings and upserts them (that is what it is called, not process_pdf_and_query). please refactor it so that it has a seperate create_embeddings function. please also remove the parts that deal with creation of chunks, as that has already been handled. finally, check if there is any need to read the csv we have created for querying inside the semantic database. if not, why are we reading the csv saved inside extracted_text? please also comment if you see any other obsolete or contradictory pieces of code . here is the function : "def process_extracted_text(
    query,
    text,
    pdf_path,
    search_scope="current_file",
    namespace=None,
    department=None,
    type_of_document=None,
    year=None,
):
    # selecting the huggingface tokeniser and selecting the chunk sizes

    texts = []
    # max_length = 4000
    # overlap = 100

    # splitting the text into chunks using our custom function
    texts = clean_and_split_text(text)
    write_chunks_to_file(texts, pdf_path, namespace)

    # initialising the openai api key
    model_engine = "text-embedding-ada-002"

    # initialising pinecone
    pinecone.init(
        api_key=pinecone_api_key,
        environment=pinecone_environment,
    )

    # fetching the name of the created index and initialising it
    index_name = "rajgov"
    index = pinecone.Index(index_name)

    # creating embeddings of chunks and uploading them into the index
    # Get embeddings for the PDF file
    if pdf_path:
        file_name = os.path.splitext(os.path.basename(pdf_path))[0]
    else:
        file_name = namespace
    embeddings_file_path = f"./embeddings/{file_name}_embeddings.pkl"

    if namespace is None:
        namespace = file_name

    embeddings = []
    if not os.path.exists(embeddings_file_path):
        # creating embeddings of chunks and save them to a file
        length = len(texts)
        print(f"Creating embeddings of {length} chunks")
        for i, chunk in enumerate(texts):
            response = openai.Embedding.create(input=[chunk], model=model_engine)
            embedding = response["data"][0]["embedding"]
            metadata = {"text": chunk}
            if department is not None:
                metadata["department"] = department
            if type_of_document is not None:
                metadata["type_of_document"] = type_of_document
            if year is not None:
                metadata["year"] = year
            embeddings.append((f"chunk_{i}", embedding, metadata))

            with open(embeddings_file_path, "ab") as f:
                print(
                    f"Saving embeddings of chunk_{i}/{length} to {embeddings_file_path}"
                )
                pickle.dump([(f"chunk_{i}", embedding, metadata)], f)

            # Upserting embeddings to namespace
            index.upsert(
                vectors=[(f"chunk_{i}", embedding, metadata)], namespace=namespace
            )
    else:
        # load embeddings from the file
        with open(embeddings_file_path, "rb") as f:
            print(f"Loading embeddings from {embeddings_file_path}")
            while True:
                try:
                    embeddings.append(pickle.load(f))
                except EOFError:
                    break

        completed_chunks = len(embeddings)
        print(f"Completed chunks: {completed_chunks}")

        # Continue creating embeddings from where it left off
        for i, chunk in enumerate(texts[completed_chunks:], start=completed_chunks):
            response = openai.Embedding.create(input=[chunk], model=model_engine)
            embedding = response["data"][0]["embedding"]
            metadata = {"text": chunk}
            if department is not None:
                metadata["department"] = department
            if type_of_document is not None:
                metadata["type_of_document"] = type_of_document
            if year is not None:
                metadata["year"] = year
            embeddings.append((f"chunk_{i}", embedding, metadata))

            with open(embeddings_file_path, "ab") as f:
                print(f"Saving embeddings of chunk_{i} to {embeddings_file_path}")
                pickle.dump([(f"chunk_{i}", embedding, metadata)], f)

            # Upserting embeddings to namespace
            index.upsert(
                vectors=[(f"chunk_{i}", embedding, metadata)], namespace=namespace
            )

    # preparing the query
    """query = translate_to_english_chatgpt(query)
    focus_phrases = extract_focus_phrases(query)
    print(f"QUERY: {query}")"""

    # querying the index
    query_response = openai.Embedding.create(input=[query], model=model_engine)
    query_embedding = query_response["data"][0]["embedding"]

    # the response will be in json with id, metadata with text, and score
    if search_scope == "current_file":
        results = index.query(
            queries=[query_embedding],
            top_k=5,
            include_metadata=True,
            namespace=namespace,
        )
    else:  # search_scope == 'entire_database'
        results = index.query(queries=[query_embedding], top_k=5, include_metadata=True)
    print(results)

    answer, search_results = chatgpt_summarize_results(
        query, results
    )  # focus_phrases,)

    print(f"ANSWER: {answer}")

    return answer, search_results""""