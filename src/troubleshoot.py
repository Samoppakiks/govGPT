# uncomment to check the path of your python interpreter
"""import sys
print(sys.executable)"""


# Uncomment this to delete namespaces
"""pinecone_api_key = os.environ.get("PINECONE_API_KEY")
pinecone_environment = os.environ.get("PINECONE_ENV")"""

"""from config import pinecone_api_key, pinecone_environment

import pinecone
import requests

pinecone.init(
    api_key=pinecone_api_key,
    environment=pinecone_environment,
)


def get_pinecone_namespaces():
    url = "https://rajgov-f44d42f.svc.northamerica-northeast1-gcp.pinecone.io/describe_index_stats"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Api-Key": pinecone_api_key,
    }
    response = requests.get(url, headers=headers)
    print("Server response:", response.text)
    json_response = response.json()
    namespaces = json_response.get("namespaces", {})
    return namespaces


namespaces = get_pinecone_namespaces()
namespaces_list = list(namespaces.keys())

print("Namespaces:")
for idx, namespace in enumerate(namespaces_list):
    print(f"{idx}: {namespace}")


index_name = "rajgov"
index = pinecone.Index(index_name)

delete_response_namespace_1 = index.delete(
    delete_all=True,
    namespace="FAQ_LTC.pdf",
)
print("Deletion response for namespace 1:", delete_response_namespace_1)


namespaces_new = get_pinecone_namespaces()

print("New Namespaces:")
for idx, namespace in enumerate(namespaces_new):
    print(f"{idx}: {namespace}")"""
