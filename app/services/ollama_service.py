import ollama

def get_chat_response(messages: list, context: str = "") -> str:
    """
    Sends the conversation history to Ollama and returns the AI's response.
    Includes RAG context if provided.
    """
    system_prompt = "You are a helpful AI assistant."
    if context:
        system_prompt += f"\n\nContext information is below.\n---------------------\n{context}\n---------------------\nGiven the context information, answer the user's question."
        
    api_messages = [{"role": "system", "content": system_prompt}]
    
    for msg in messages:
        # msg can be a dict from frontend or SQLAlchemy model
        role = msg.role if hasattr(msg, 'role') else msg['role']
        content = msg.content if hasattr(msg, 'content') else msg['content']
        
        # Convert enum or whatever it is to string
        if hasattr(role, 'value'):
            role = role.value
            
        api_messages.append({"role": role, "content": content})
        
    response = ollama.chat(
        model="llama3",
        messages=api_messages
    )
    return response['message']['content']

def get_embedding(text: str) -> list[float]:
    """
    Generates an embedding vector for the given text using Ollama.
    """
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )
    return response['embedding']
