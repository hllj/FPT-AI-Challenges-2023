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
    st.session_state.prescription = doctor_response
    st.session_state.messages.append({'role': 'suggestion', 'content': doctor_response})
    
def click_send_prescription(sessionId, prescription):
    doctor_state = {
        'seen': True,
        'prescription': prescription
    }
    with open(f'doctors/{sessionId}.json', 'w', encoding='utf-8') as f:
        json.dump(doctor_state, f, ensure_ascii=False, indent=4)

def click_send_prescription_to_storage(sessionId, prescription):
    print('check', 'click_send_prescription_to_storage')
    url = "http://0.0.0.0:8001/storage"

    payload = json.dumps({
        "text": prescription
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    actives = response.json()['data']['response']
    st.session_state.actives = actives
    st.session_state.messages.append({'role': 'assistant', 'content': 'Đây là một số thuốc hiện có trong kho mà tôi tìm được!'})

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
    st.session_state.prescription = ""
    st.session_state.actives = []
    st.session_state.drug_choose = {}
    st.session_state.final = ""

# Initialize full_response outside the user input check
full_response = ""

# Display Chat History
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if message['content'] != '':
                st.markdown(message["content"])
        
        if message['content'] == st.session_state.summary and st.session_state.summary != '':
            st.button(label='Đưa ra đơn thuốc tham khảo', key="summary_button", on_click=click_button_suggestion, args=(st.session_state.summary,))
            
        if message['role'] == 'suggestion' and message['content'] == st.session_state.prescription:
            st.button('Tìm thuốc', on_click=click_send_prescription_to_storage, args=(st.session_state.sessionId, st.session_state.prescription))
        
        if message['content'] == "Đây là một số thuốc hiện có trong kho mà tôi tìm được!" and len(st.session_state.actives) > 0:
            with st.form("Hãy chọn thuốc từ các hoạt chất"):
                drug_choose = {}
                for active in st.session_state.actives:
                    with st.container():
                        st.title('Hoạt chất: ' + active['active'])
                        for drug in active['drugs']:
                            col1, col2, col3 = st.columns([4, 4, 4])
                            with col1:
                                st.markdown(drug['Biệt dược'])
                            with col2:
                                st.markdown("Số lượng hiện còn: " + str(drug['Số lượng']))
                            with col3:
                                checkbox_value = st.checkbox(label=drug['_id'], key=drug['_id'], label_visibility="hidden")
                                if checkbox_value == True:
                                    drug_choose[active['active']] = drug['Biệt dược']
                            st.divider()
                submitted = st.form_submit_button("Lựa chọn")
                if submitted:
                    st.session_state.drug_choose = drug_choose
                    text = "Bạn đã chọn\n\n"
                    final_prescription = st.session_state.prescription
                    for active in drug_choose:
                        text += f"- Hoạt chất {active}: " + drug_choose[active] + "\n\n"
                        final_prescription = final_prescription.replace(active, drug_choose[active])
                    st.session_state.final = final_prescription
                    st.session_state.messages.append({"role": "assistant", "content": text})
                    
                    st.session_state.messages.append({'role': 'final', 'content': "Đơn thuốc cuối cùng bạn lựa chọn\n\n" + st.session_state.final})
                    
        if message['role'] == 'final':
            st.markdown('Bạn có muốn gửi đơn thuốc cho bệnh nhân không ?')
            st.button('Gửi đơn thuốc cho bệnh nhân', on_click=click_send_prescription, args=(st.session_state.sessionId, st.session_state.final))
                        