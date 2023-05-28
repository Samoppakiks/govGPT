from .config import openaiapi, openaiorg, pinecone_api_key, pinecone_environment
import os
import openai
import pinecone
import pickle
import re
import re
import json
import time
from spacy.lang.en import English


"""openaiapi = os.environ.get("OPENAI_API_KEY")
openaiorg = os.environ.get("OPENAI_ORG_ID")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
pinecone_environment = os.environ.get("PINECONE_ENV")"""

openai.api_key = openaiapi
openai.organization = openaiorg


def create_embeddings(chunk, model_engine="text-embedding-ada-002"):
    response = openai.Embedding.create(input=[chunk], model=model_engine)
    embedding = response["data"][0]["embedding"]
    return embedding


def upsert_embeddings(index, embeddings, namespace):
    for i, (chunk_id, embedding, metadata) in enumerate(embeddings):
        index.upsert(vectors=[(chunk_id, embedding, metadata)], namespace=namespace)
        print(f"Upserted {i+1} embeddings")


def query_vector_database(query, namespace=None):
    pinecone.init(
        api_key=pinecone_api_key,
        environment=pinecone_environment,
    )
    index_name = "rajgov"
    index = pinecone.Index(index_name)
    # Create an embedding for the query
    model_engine = "text-embedding-ada-002"
    query_response = openai.Embedding.create(input=[query], model=model_engine)
    query_embedding = query_response["data"][0]["embedding"]

    # Query the index
    if namespace is not None:
        results = index.query(
            queries=[query_embedding],
            top_k=5,
            include_metadata=True,
            namespace=namespace,
        )
    else:
        results = index.query(
            queries=[query_embedding],
            top_k=5,
            include_metadata=True,
        )

    return results


def process_extracted_text(
    query,
    df,
    search_scope="current_file",
):
    pinecone.init(
        api_key=pinecone_api_key,
        environment=pinecone_environment,
    )
    index_name = "rajgov"
    index = pinecone.Index(index_name)
    # Your existing code...
    embeddings = []
    total_chunks = len(df)
    for i, row in df.iterrows():
        embedding = create_embeddings(row["Text Content"])
        print(f"Created embedding for chunk {i}/{total_chunks}")
        metadata = {
            "text": row["Text Content"],
            "department": row["Department"],
            "type_of_document": row["Type of Document"],
            "year": row["Year"],
            "Title": row["Title"],
            "Page Number": row["Page No"],
        }
        embeddings.append((f"chunk_{i}", embedding, metadata))
    namespace = df["Title"][0]
    df.to_csv(f"./extracted_texts/{namespace}_df.csv", index=False)

    # Upserting embeddings to namespace
    upsert_embeddings(index, embeddings, namespace)
    results = query_vector_database(query, namespace)
    answer, search_results = chatgpt_summarize_results(query, results)
    print(f"ANSWER: {answer}")
    return answer, search_results


def chatgpt_summarize_results(query, results):  # focus_phrases)
    search_results = []

    for match in results["results"][0]["matches"]:
        # Extract all the metadata information
        score = match["score"]
        # title = match["metadata"]["Title"]
        # page_number = match["metadata"]["Page Number"]
        department = match["metadata"]["department"]
        type_of_document = match["metadata"]["type_of_document"]
        year = match["metadata"]["year"]
        text = match["metadata"]["text"]

        # Append the result as a dictionary to the list
        search_results.append(
            {
                "Score": score,
                # "Page Number": page_number,
                # "Title": title,
                "Department": department,
                "Type of Document": type_of_document,
                "Year": year,
                "Text": text,
            }
        )

    print(search_results)
    search_results_str = "\n".join([str(result) for result in search_results])

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant working at a government help center facilities. People ask you questions related to permissable activities,and  for information on government services.",
            },
            {
                "role": "user",
                "content": f"The query is: '{query}'. Based on the following search results, provide an answer to the query, after considering each result with respect to the query and checking if anything related to the query can be inferred from each result. Finally, comment on reason for your final interpreation, as well as any additional information that may not be contained in the text that may help answer the query. considering not only exact matches but also possible inferences about the expected action that can be made based on the results. :\n\n{search_results_str}",  # You may also use the focus phrases : {focus_phrases} for better inference.
            },
        ],
    )

    gpt_response = response.choices[0].message["content"].strip()

    return gpt_response, search_results


def chatgpt_get_response(context, query):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant working at a government help center facilities. People ask you questions related to permissable activities, and for information on government services.",
            },
            {"role": "user", "content": context},
            {"role": "user", "content": query},
        ],
    )

    return response.choices[0].message["content"].strip()
