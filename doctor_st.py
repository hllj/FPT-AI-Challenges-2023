# Library
import glob
import json
import uuid
import openai
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

if 'sessionId' not in st.session_state:
    st.session_state.sessionId =  str(uuid.uuid4())

# Get content
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
def click_button_user_session(sessionId):
    f = open(f"users/{sessionId}.json", 'r')
    state = json.load(f)
    f.close()
    st.session_state.sessionId = state['sessionId']
    st.session_state.summary = state['summary']
    st.session_state.messages = state['messages']
    st.session_state.messages.append({'role': 'summary', 'content': st.session_state.summary})
    
    doctor_state = {
        'seen': True,
        'prescription': None
    }
    with open(f'doctors/{sessionId}.json', 'w', encoding='utf-8') as f:
        json.dump(doctor_state, f, ensure_ascii=False, indent=4)

def click_button_suggestion(summary):
    url = "http://0.0.0.0:8001/doctor"
    payload = json.dumps({
        "summary": summary
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    doctor_response = response.json()['data']['response']['response']
    st.session_state.messages.append({'role': 'suggestion', 'content': doctor_response})
    
def click_send_prescription(sessionId, prescription):
    doctor_state = {
        'seen': True,
        'prescription': prescription
    }
    with open(f'doctors/{sessionId}.json', 'w', encoding='utf-8') as f:
        json.dump(doctor_state, f, ensure_ascii=False, indent=4)

# Custom Streamlit app title and icon
st.set_page_config(
    page_title="Hệ thống hỗ trợ bác sĩ",
    page_icon=":robot_face:",
)

st.title("🤖 Hệ thống hỗ trợ bác sĩ")

# Sidebar Configuration
st.sidebar.title("FPT AI CHALLENGE 2023")

html_code = """
<div style="display: flex; justify-content: space-between;">
    <img src="https://inkythuatso.com/uploads/thumbnails/800/2021/11/logo-fpt-inkythuatso-1-01-01-14-33-35.jpg" width="35%">
    <img src="https://hackathon.quynhon.ai/QAI-QuyNhon.c9fe9a3855f9b592.png" width="65%">
</div>
"""

st.sidebar.markdown(html_code, unsafe_allow_html=True)

# Enhance the sidebar styling
st.sidebar.subheader("Mô tả")
st.sidebar.write("Đây là một trợ lý y tế ảo dành cho dược sĩ dễ dàng chọn các đơn thuốc cho bệnh nhân")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# CHAT MODEL

st.sidebar.subheader("Các đoạn chat")

path_sessions = glob.glob("users/*.json")

for path_session in path_sessions:
    sessionId = path_session.split('/')[1].split('.')[0]
    st.sidebar.button(f"{sessionId}", on_click=click_button_user_session, args=(sessionId,))

# Initialize Chat Messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Optional
    st.session_state.summary = ""

# Initialize full_response outside the user input check
full_response = ""

# Display Chat History
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if message['content'] != '':
                st.markdown(message["content"])
        if message['role'] == 'summary' and message['content'] != '':
            st.button('Đưa ra đơn thuốc tham khảo', on_click=click_button_suggestion, args=(st.session_state.summary,))
            
        if message['role'] == 'suggestion':
            st.button('Gửi đơn thuốc cho bệnh nhân', on_click=click_send_prescription, args=(st.session_state.sessionId, message['content']))