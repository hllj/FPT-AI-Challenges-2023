# QNAI-Challenges-2023
Quy Nhon AI Challenges 2023 - Challenge 2

# API

## Thêm OPEN_API_KEY và Cohere API KEY vào file .env
OPEN_API_KEY=
COHERE_API_KEY=

## Install libraries

```bash
pip install -r requirements.txt
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