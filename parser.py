import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()
JINA_API_KEY = os.getenv("JINA_API_KEY")

def extract_content(file_path: str):
    url = "https://r.jina.ai/"
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "X-Return-Format": "markdown" 
    }
    
    with open(file_path, "rb") as f:
        response = requests.post(url, headers=headers, files={"file": f})
    
    if response.status_code != 200:
        raise Exception(f"Jina Reader Error: {response.text}")

    full_text = response.text
    
    # Step 1: Headings par split karein
    raw_sections = re.split(r'(^#+\s.*$)', full_text, flags=re.MULTILINE)
    
    final_chunks = []
    current_header = ""
    
    for section in raw_sections:
        section = section.strip()
        if not section: continue
        
        if section.startswith('#'):
            current_header = section
        else:
            # Header ko content ke sath jorein
            full_section_text = f"{current_header}\n{section}" if current_header else section
            
            # Step 2: Table-Safe Splitting
            if len(full_section_text) > 2500:
                # Sirf Double Newline par split karein taake table rows na tootain
                sub_parts = re.split(r'(?<= \n\n)', full_section_text)
                
                temp_chunk = ""
                for part in sub_parts:
                    # Limit 2200 taake context safe rahe
                    if len(temp_chunk) + len(part) > 2200: 
                        if temp_chunk:
                            final_chunks.append(temp_chunk.strip())
                        # Har naye chunk mein Header dobara shamil karein
                        temp_chunk = (current_header + "\n" + part) if current_header else part
                    else:
                        temp_chunk += part
                
                if temp_chunk:
                    final_chunks.append(temp_chunk.strip())
            else:
                final_chunks.append(full_section_text)
                
    return final_chunks