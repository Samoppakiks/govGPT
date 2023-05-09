# uncomment to check the path of your python interpreter
"""import sys
print(sys.executable)"""


# Uncomment this to delete namespaces
"""import pinecone
import requests

pinecone.init(
    api_key="6d0b2d52-99bc-4de5-bec0-0c157c66ecbd",
    environment="northamerica-northeast1-gcp",
)


def get_pinecone_namespaces():
    url = "https://rajgov-f44d42f.svc.northamerica-northeast1-gcp.pinecone.io/describe_index_stats"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Api-Key": "6d0b2d52-99bc-4de5-bec0-0c157c66ecbd",
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
    namespace="201901240328415358086002-2-1-dop-a-2-acr-91dated24-1-2019",
)
print("Deletion response for namespace 1:", delete_response_namespace_1)


namespaces_new = get_pinecone_namespaces()

print("New Namespaces:")
for idx, namespace in enumerate(namespaces_new):
    print(f"{idx}: {namespace}")"""
