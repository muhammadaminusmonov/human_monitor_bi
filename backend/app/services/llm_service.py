import streamlit as st
from anthropic import Anthropic

def generate_ai_response(prompt: str) -> str:
    """
    Sends a prompt to Claude and returns the text response.
    """
    try:
        # Initialize the client using your streamlit secrets
        client = Anthropic(
            api_key=st.secrets["ANTHROPIC_API_KEY"],
        )

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
        
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"