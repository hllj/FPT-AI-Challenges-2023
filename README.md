# QNAI-Challenges-2023
FPT AI Challenges 2023 - Challenge 2

# API

## Thêm OPEN_API_KEY và Cohere API KEY vào file .env

- Thêm OPEN_API_KEY và Cohere API KEY vào file .env
- Setup Pinecone database với PINECONE_API_KEY, INDEX_NAME, INDEX_ENV
- Setup MongoDB cho storage
- Setup RabbitMQ từ https://www.cloudamqp.com/

```bash
OPENAI_API_KEY=
COHERE_API_KEY=
PINECONE_API_KEY=
INDEX_NAME=
INDEX_ENV=

MONGODB_SERVER="localhost"
MONGODB_PORT=27017
MONGODB_DB="storage"

CLOUDAMQP_URL=
```

## Install libraries

```bash
pip install -r requirements.txt
```

# Databases

## Import data hoạt chất và tpcn vào mongoDB cho Storage Database

```bash
python store_mongodb.py
```

## Import data vào Pinecone

```bash
python store_db_index.py
```

## Start API

### Start API cho Patient

```bash
uvicorn api.patient:app --reload --host=0.0.0.0 --port=8000
```

### Start API cho Doctor

```bash
uvicorn api.doctor:app --reload --host=0.0.0.0 --port=8001
```

# Streamlit UI

## UI cho người bệnh

```bash
streamlit run patient_st.py
```

## UI cho bác sĩ

```bash
streamlit run doctor_st.py
```