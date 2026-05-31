from openai import OpenAI
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel
import json
import os

load_dotenv()

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    context: dict = {}

@router.post("/chat")
async def ai_chat(request: ChatRequest):
    system_prompt = f"""You are ASSBI Data Analyst. You ONLY analyze the surveillance data provided below.
Do not invent numbers. If data is empty, say so clearly.
Answer in a clear, concise way. Use bullet points or tables when helpful.

=== LIVE DATA SNAPSHOT ===
CAMERAS: {json.dumps(request.context.get('cameras', []), default=str)[:3000]}
LOGS: {json.dumps(request.context.get('logs', []), default=str)[:3000]}
LOCATIONS: {json.dumps(request.context.get('locations', []), default=str)[:1000]}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1000,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ]
    )

    return {"reply": response.choices[0].message.content}