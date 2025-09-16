from prompt import classification_prompt
import google.generativeai as genai
import time
import json
from decimal import Decimal
def sanitize_input(text):
    text=text.replace("`","")
    text=text.replace("#", "")
    return text 

def get_moderation_prompt(text,word_limit=500):
    sanitize_text=sanitize_input(text)
    words=sanitize_text.split()
    if len(words)>word_limit:
        sanitize_text=" ".join(words[:word_limit])  
    return classification_prompt(text=sanitize_text)

def analyze_comment(text,model,max_retries=10,initial_delay=5):
    prompt=get_moderation_prompt(text)
    retry_count=0
    delay=initial_delay
    while retry_count<max_retries:
        try:
            response=model.generate_content(prompt)
            json_text = response.text.strip().replace('```json', '').replace('```', '').strip()
            return json.loads(json_text, parse_float=Decimal)
        except genai.types.generation_types.BlockedPromptException as e:
            # Return a custom JSON indicating the block
            return {"decision": "block", "categories": [{"label": "blocked-by-api", "code": "API_BLOCK"}]}
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON from API response. Response text: {response.text}")
            return None
        except Exception as e:
            if '429' in str(e): 
                logging.warning(f"Rate limit hit. Retrying in {delay} seconds...")
                time.sleep(delay)
                retry_count += 1
                delay *= 2  
            else:
                logging.error(f"An unexpected error occurred with Google AI API: {e}")
                return None
    return None