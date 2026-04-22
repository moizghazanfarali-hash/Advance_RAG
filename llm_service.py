import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query, context_chunks):
    if not context_chunks: return "Information not found in context."
    
    formatted_context = "\n\n".join([f"Source: {c['metadata']['source']}\n{c['content']}" for c in context_chunks])
    
    system_prompt = """You are a professional AI Assistant. Your task is to answer the user's question based strictly on the provided context.
    
    Guidelines:
    1. Only use the information from the context provided.
    2. If the answer is not present in the context, state clearly that the information is not available in the documents.
    3. Be technical, precise, and preserve any specific numbers, versions (like v14, v15, etc.), or dates mentioned in the text.
    4. Do not mention "Tesla" or "v14" unless they are actually part of the context or the user's question.
    5. Maintain a professional and helpful tone.
    """

    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Context:\n{formatted_context}\n\nQuestion: {query}"}],
        temperature=0.1
    )
    return response.choices[0].message.content