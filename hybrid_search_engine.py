import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["RAG_DB"]

def get_query_embedding(query_text):
    headers = {"Authorization": f"Bearer {os.getenv('JINA_API_KEY')}", "Content-Type": "application/json"}
    data = {
        "model": "jina-embeddings-v5-text-small",
        "task": "retrieval.query",
        "dimensions": 512,
        "input": [query_text]
    }
    response = requests.post("https://api.jina.ai/v1/embeddings", headers=headers, json=data)
    return response.json()["data"][0]["embedding"]

def perform_hybrid_search(query_text, collection_name, n_results=40):
    query_vector = get_query_embedding(query_text)
    collection = db[collection_name]
    
    # 1. Sirf Keyword Search (Lucene) - No Nesting here
    # Ye pipeline "v14" aur "500 years" ko pakre ga
    text_query = {
        "$search": {
            "index": "vector_index",
            "text": { "query": query_text, "path": "content" }
        }
    }
    
    # 2. Sirf Vector Search (kNN) - Alag call
    vector_query = {
        "$search": {
            "index": "vector_index",
            "knnBeta": {
                "vector": query_vector,
                "path": "embedding",
                "k": 20
            }
        }
    }

    try:
        # Dono queries ko alag alag chalaya taake nesting error aye hi na
        text_results = list(collection.aggregate([text_query, {"$limit": 15}]))
        vector_results = list(collection.aggregate([vector_query, {"$limit": 15}]))
        
        # Dono ko merge kiya aur duplicates hataye
        all_results = {str(r['_id']): r for r in (text_results + vector_results)}.values()
        results_list = list(all_results)

        if not results_list: return []

        # 3. Jina Reranker - Ye chunks ko query ke mutabiq re-rank karega
        # Agar "v14" text results mein hai, Reranker usay top par le aye ga
        docs = [res["content"] for res in results_list]
        headers = {"Authorization": f"Bearer {os.getenv('JINA_API_KEY')}"}
        rerank_data = {
            "model": "jina-reranker-v2-base-multilingual",
            "query": query_text,
            "documents": docs,
            "top_n": n_results
        }
        
        resp = requests.post("https://api.jina.ai/v1/rerank", headers=headers, json=rerank_data)
        if resp.status_code == 200:
            indices = [item["index"] for item in resp.json()["results"]]
            return [results_list[i] for i in indices]
            
        return results_list[:n_results]
    except Exception as e:
        print(f"Professional Fix Error: {e}")
        return []