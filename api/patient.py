from dotenv import load_dotenv

load_dotenv()

from typing import Union, List

from fastapi import FastAPI

from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str
    
class ChatMessage(BaseModel):
    messages: List[Message]

@app.post("/patient")
def process_patient(chat: ChatMessage):
    messages = chat.messages
    summary = "Summary for Patient:"
    summary += "\n" + "\n".join([message.content for message in messages if message.role == 'user']) + "\n"
    return {
        "msg": "SUCCESS",
        "code": 0,
        "data": {
            "response": summary
        }
    }
