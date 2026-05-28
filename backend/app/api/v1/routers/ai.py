from fastapi import APIRouter
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("KEY:", GEMINI_API_KEY)

client = genai.Client(api_key=GEMINI_API_KEY)

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def ai_chat(data: ChatRequest):

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=data.message
    )

    return {
        "response": response.text
    }