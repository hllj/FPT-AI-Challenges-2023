import glob
import re
from dotenv import load_dotenv
load_dotenv()
import os
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from llama_index import (QuestionAnswerPrompt, RefinePrompt)
from store_db_index import build_index
from langchain.chat_models import ChatOpenAI
from store_mongodb import StorageMongoDB

temperature = 0 # It can be range from (0-1) as openai
max_tokens = 1024 # token limit

index = build_index()

#Inserting Prompt Template
PROMPT_TEMPLATE = (
        "Bạn là dược sĩ tại nhà thuốc. Dưới đây là thông tin cụ thể về những đơn thuốc tham khảo dựa trên các triệu chứng:"
        "\n-----------------------------\n"
        "{context_str}"
        "\n-----------------------------\n"
        "Hãy trả lời câu hỏi sau đây bằng cách đưa ra những đơn thuốc tham khảo dựa trên thông tin được cung cấp phía trên:{query_str} \n"
    )

QA_PROMPT = QuestionAnswerPrompt(PROMPT_TEMPLATE)

# Build index and query engine
query_engine = index.as_query_engine(text_qa_template=QA_PROMPT,llm=ChatOpenAI(temperature=temperature,model="gpt-3.5-turbo",max_tokens=max_tokens))

storage_db = StorageMongoDB(server="localhost", port=int(27017), db="storage")

app = FastAPI()

class PatientDescription(BaseModel):
    summary: str
    
class Prescription(BaseModel):
    text: str
    limit: int
    sort: int

def get_actives(prescription):
    found_actives = []
    
    for regex_drug in storage_db.regex_drugs:
        if regex_drug == None:
            continue
        pattern = regex_drug.replace('(', '\(').replace(')', '\)')
        x = re.search(pattern, prescription)
        if x:
            found_actives.append({
                'query_field': 'Query',
                'active': regex_drug, 
                'start': x.start()
            })
    
    for active in storage_db.actives:
        if active == None:
            continue
        pattern = active.replace('(', '\(').replace(')', '\)')
        x = re.search(pattern, prescription)
        if x:
            found_actives.append({
                'query_field': 'Hoạt chất',
                'active': active, 
                'start': x.start()
            })
    
    found_actives.sort(key=lambda x: (x['start'], -len(x['active'])))
    
    all_actives = []
    all_actives.append(found_actives[0])
    
    for idx in range(1, len(found_actives)):
        if found_actives[idx]['start'] == found_actives[idx - 1]['start']:
            continue
        all_actives.append(found_actives[idx])

    return all_actives

@app.post("/doctor")
def send_to_doctor(description: PatientDescription):
    summary = description.summary
    response = query_engine.query(summary)
    prescription = response.response
    all_actives = get_actives(prescription)
    all_drugs = []
    
    for active in all_actives:
        active_name = active['active']
        query_field = active['query_field']
        drugs = list(storage_db.find_drug(query_field, active_name, 3, 1))
        for idx, drug in enumerate(drugs):
            drugs[idx]['_id'] = str(drug['_id'])
            drugs[idx]['query_field'] = query_field
        all_drugs.append({
            'active': active_name,
            'drugs': drugs
        })
    return {
        "msg": "SUCCESS",
        "code": 0,
        "data": {
            "prescription": prescription,
            "drugs": all_drugs
        }
    }

    
@app.get("/storage")
def get_drugs(prescription: Prescription):
    print(prescription.text)
    all_actives = get_actives(prescription.text)
    limit = prescription.limit
    sort = prescription.sort
    
    all_drugs = []
    
    for active in all_actives:
        active_name = active['active']
        query_field = active['query_field']
        drugs = list(storage_db.find_drug(query_field, active_name, limit, sort))
        for idx, drug in enumerate(drugs):
            drugs[idx]['_id'] = str(drug['_id'])
            drugs[idx]['query_field'] = query_field
        all_drugs.append({
            'active': active_name,
            'drugs': drugs
        })
    
    print('check', all_drugs)
    
    return {
        "msg": "SUCCESS",
        "code": 0,
        "data": {
            "response": all_drugs
        }
    }