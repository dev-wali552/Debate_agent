from dotenv import load_dotenv
load_dotenv()
from graph import graph
from langchain_core.messages import HumanMessage
from fastapi import FastAPI ,UploadFile,File,Form
from fastapi.responses import Response
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from gtts import gTTS
import io
import os
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sunny-shortbread-273f53.netlify.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    topic : str
    session_id : str
@app.get("/")
def root():
    return {"message": "Debate_agent is running"}
@app.post("/debate")
async def chat(request: ChatRequest):
    config = {"configurable": {"thread_id": request.session_id}}
    result = await graph.ainvoke(
            {"topic": request.topic, "messages": [HumanMessage(content=request.topic)]
    }, config=config)

    return {
    "pros": result["pros"],
    "cons": result["con"],
    "winner": result["winner"],
    "reasoning": result["reasoning"]
}
    
@app.post("/voice-debate")
async def voice_chat(audio: UploadFile = File(...), session_id: str = Form(...)):

    # STEP 1: Whisper STT — audio bytes → text
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    audio_bytes = await audio.read()
    transcription = groq_client.audio.transcriptions.create(
        file=(audio.filename or "audio.webm", audio_bytes),
        model="whisper-large-v3",
    )
    user_text = transcription.text

    # STEP 2: graph.ainvoke — same as /chat
    config = {"configurable": {"thread_id": session_id}}
    result = await graph.ainvoke(
        {"topic": user_text, "messages": [HumanMessage(content=user_text)]},
        config=config
    ) 
    response_text = result["winner"]

    # STEP 3: gTTS TTS — text → audio bytes
    tts = gTTS(text=response_text, lang='en')
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    audio_data = audio_buffer.read()

    audio_base64 = base64.b64encode(audio_data).decode("utf-8")


    # STEP 4: Return audio back to frontend
    return {
    "pros": result["pros"],
    "cons": result["cons"],
    "winner":result["winner"],
    "reasoning": result["reasoning"],
    "audio": audio_base64  # frontend decodes this and plays it
}
