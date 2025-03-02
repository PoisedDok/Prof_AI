
# Prof AI

Prof AI is a Python application that integrates with AI models via the Ollama and Gemini APIs. It provides a simple interface to send a user's prompt to either model and process the streamed or full responses accordingly.

## Features

- **Ollama Integration:** Sends prompts to an Ollama-based model with streaming responses ([`ask_ai`](ollama_integration.py#L4)).
- **Gemini Integration:** Sends prompts to the Gemini API and parses the completed response.
- Configurable logging for debugging and error tracking.

## Getting Started

### Prerequisites

- Python 3.12 or newer
- An active API key for the Gemini service (replace the placeholder in [`ollama_integration.py`](ollama_integration.py))
- Access to an Ollama server running at the configured host and port

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/your_username/prof-ai.git
   cd prof-ai
   ```

2. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

## Configuration

Configure your API keys and server settings in the ollama_integration.py file:

- **Ollama:** Adjust the `OLLAMA_HOST` and `OLLAMA_PORT` if needed.
- **Gemini:** Replace the `GEMINI_API_KEY` placeholder with your actual API key.

## Usage

You can call the main AI function `ask_ai` from your application. For example:

```python
from ollama_integration import ask_ai

response = ask_ai("What is the capital of France?", model="ollama")
print(response)
```

You may also have additional scripts like main.py for running the application interactively or integrating with other modules (e.g., course_data.py, simulation.py, stt.py, tts.py).

## Project Structure

```plaintext
.
├── __pycache__/
├── assets/
├── course_data.py
├── course_mode.py
├── db.py
├── expert_mode.py
├── ffmpeg-7.0.2-full_build/
├── hi.txt
├── livestream_app.log
├── main.py
├── ollama_integration.py
├── README.md
├── requirements.txt
├── simulation.py
├── simulations/
├── stt.py
├── tts.py
└── workers.py
```

## Contributing

Feel free to open issues or submit pull requests to improve the project.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
```

You can adjust the contents as needed before pushing to GitHub.
You can adjust the contents as needed before pushing to GitHub.

