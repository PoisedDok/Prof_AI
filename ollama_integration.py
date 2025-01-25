import requests
import json
import logging

OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434

def ask_ollama(prompt):
    """
    Sends the user's prompt to the Ollama AI and aggregates the streaming response.
    """
    url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"
    payload = {
        "model": "falcon3:1b",  # Use your preferred model
        "prompt": prompt
    }

    try:
        logging.debug(f"Sending request to Ollama: {url} with payload: {payload}")
        response = requests.post(url, json=payload, timeout=60, stream=True)
        response.raise_for_status()

        full_response = []
        for chunk in response.iter_lines():
            if chunk:
                try:
                    # Parse the chunk as JSON
                    chunk_data = json.loads(chunk.decode("utf-8"))
                    response_text = chunk_data.get("response", "")
                    done = chunk_data.get("done", False)
                    
                    # Append to the full response
                    full_response.append(response_text)
                    
                    # Stop if 'done' is True
                    if done:
                        break
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decoding error: {e}")
        
        # Join the full response
        final_response = ''.join(full_response)
        logging.debug(f"Full response from AI: {final_response}")
        return final_response.strip()

    except requests.exceptions.RequestException as e:
        logging.error(f"Error communicating with Ollama: {e}")
        return "Error: Unable to process your request."
