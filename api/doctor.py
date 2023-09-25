from dotenv import load_dotenv

load_dotenv()

from typing import Union

from fastapi import FastAPI

from pydantic import BaseModel

import re

from llama_index import VectorStoreIndex, SimpleDirectoryReader

# Create a SimpleDirectoryReader object

reader = SimpleDirectoryReader(input_files=["data/Bệnh lỵ amip.txt","data/Gout.txt", "data/Viêm amidan cấp tính.txt","data/Viêm họng cấp.txt","data/Viêm phế quản cấp.txt","data/Đau khớp.txt"])

# Load the data from the text file
documents = reader.load_data()

from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index import LangchainEmbedding, ServiceContext
from llama_index import (QuestionAnswerPrompt, RefinePrompt)
from langchain.llms import Cohere

# model = "rerank-english-v2.0" #this is the model name from cohere. Select it that matches with you
model = "command"
temperature = 0 # It can be range from (0-1) as openai
max_tokens = 512 # token limit

embed_model = Cohere(model="embed-multilingual-v2.0",cohere_api_key="2G8Q6erN971QQLtee4VnNnIrVXolRo4JKe0xHMQo")


service_context = ServiceContext.from_defaults(embed_model=embed_model)
index = VectorStoreIndex.from_documents(documents)


text_qa_template = QuestionAnswerPrompt(
 """ [INST] <<SYS>>
Bạn là dược sĩ tại nhà thuốc. Dưới đây là thông tin cụ thể về đơn thuốc tham khảo dựa trên các triệu chứng.

{context_str}

Dựa trên thông tin trên, đầu tiên bạn cần tìm ra chẩn đoán từ các triệu chứng. Bạn không cần kê đơn thuốc ở giai đoạn này.

Nếu có nhiều hơn một chẩn đoán, bạn có thể phản hồi như sau: "Các triệu chứng của bạn không rõ ràng, có thể có nhiều chẩn đoán dựa trên các triệu chứng."

Nếu chỉ có một chẩn đoán, bạn có thể dựa trên thông tin được cung cấp để đưa ra đơn thuốc tham khảo.
<</SYS>>

{query_str} [/INST]"""
    )

# Build index and query engine
query_engine = index.as_query_engine(
    retriever_mode="embedding",
    verbose=True,
    text_qa_template=text_qa_template,
    service_context = service_context,
    similarity_top_k=3
    # refine_template=refine_template,
    # streaming=True,
)

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