import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["RAG_DB"]
collection = db["vector_store"]

def get_embeddings(text_list):
    headers = {"Authorization": f"Bearer {os.getenv('JINA_API_KEY')}", "Content-Type": "application/json"}
    data = {
        "model": "jina-embeddings-v5-text-small",
        "task": "retrieval.passage",
        "dimensions": 512,
        "input": text_list
    }
    response = requests.post("https://api.jina.ai/v1/embeddings", headers=headers, json=data)
    return [item["embedding"] for item in response.json()["data"]]

def add_to_mongodb(chunks, filename):
    if not chunks: return False
    embeddings = get_embeddings(chunks)
    data_to_insert = [{
        "content": text,
        "embedding": embeddings[i],
        "metadata": {"source": filename}
    } for i, text in enumerate(chunks)]
    collection.insert_many(data_to_insert)
    return True
