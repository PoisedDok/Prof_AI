from ollama_integration import ask_ollama

def expert_mode_query(question):
    """
    Compose a specialized prompt for the 'Science Expert Mode'.
    This can be improved with instructions, conversation context, etc.
    """
    system_prompt = (
        "You are a highly knowledgeable science tutor. "
        "Explain concepts step by step and provide relevant details, "
        "but keep it clear and concise. "
        "The user asks:\n"
    )
    full_prompt = system_prompt + question.strip()
    response = ask_ollama(full_prompt)
    return response
