import glob
from dotenv import load_dotenv
load_dotenv()
import os
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from llama_index import (QuestionAnswerPrompt, RefinePrompt)
from store_db_index import build_index
from langchain.chat_models import ChatOpenAI

temperature = 0 # It can be range from (0-1) as openai
max_tokens = 512 # token limit

index = build_index()

#Inserting Prompt Template
PROMPT_TEMPLATE = (
        "Đây là thông tin về bối cảnh bệnh:"
        "\n-----------------------------\n"
        "{context_str}"
        "\n-----------------------------\n"
        "Hãy trả lời câu hỏi sau đây bằng cách đưa ra 1 đơn thuốc tham khảo dựa trên thông tin về bối cảnh bệnh:{query_str} \n"
    )

QA_PROMPT = QuestionAnswerPrompt(PROMPT_TEMPLATE)

# Build index and query engine
query_engine = index.as_query_engine(text_qa_template=QA_PROMPT,llm=ChatOpenAI(temperature=temperature,model="gpt-3.5-turbo",max_tokens=max_tokens))
app = FastAPI()

class PatientDescription(BaseModel):
    summary: str

@app.post("/doctor")
def send_to_doctor(description: PatientDescription):
    summary = description.summary
    response = query_engine.query(summary)
    return {
        "msg": "SUCCESS",
        "code": 0,
        "data": {
            "response": response
        }
    }