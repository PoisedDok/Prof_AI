import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configuration for both APIs
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
GEMINI_API_KEY = "AIzaSyD-Z8Qzus6wMzxsVW2ceOMqCTGRfSsW2qQ"  # Replace with your actual API key

def ask_ai(prompt, model="ollama"):
    """
    Sends the user's prompt to the specified AI model (Ollama or Gemini) and aggregates the response.
    """
    if model.lower() == "ollama":
        url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"
        payload = {
            "model": "deepseek-r1:1.5b",
            "prompt": prompt,
            "stream": True  # Explicitly enable streaming
        }

        try:
            logging.debug(f"Sending request to Ollama: {url}")
            response = requests.post(url, json=payload, timeout=60, stream=True)
            response.raise_for_status()

            full_response = []
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        chunk_data = json.loads(chunk.decode("utf-8"))
                        if "response" in chunk_data:
                            full_response.append(chunk_data["response"])
                        if chunk_data.get("done", False):
                            break
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON decoding error: {e}")
            
            return ''.join(full_response).strip()

        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama error: {e}")
            return "Error: Unable to process your request."

    elif model.lower() == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            logging.debug(f"Sending request to Gemini: {url}")
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            response_data = response.json()
            
            # Parse Gemini response
            if "candidates" in response_data:
                return response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                logging.error(f"Unexpected Gemini response: {json.dumps(response_data, indent=2)}")
                return "Error: Unexpected response format from Gemini."

        except requests.exceptions.RequestException as e:
            logging.error(f"Gemini error: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logging.error(f"Response content: {e.response.text}")
            return "Error: Unable to process your request."

    else:
        return "Error: Unsupported model. Choose 'ollama' or 'gemini'."