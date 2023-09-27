# Library
import glob
import json
import uuid
import openai
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

# Get content
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
def get_summary(history_context):
    prompt = open_file('prompt/system_summary.txt').format(history_context=history_context)
    print("Summary", prompt)
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',  # Use the selected model name
        messages=[
            {"role": "system", "content": prompt}
        ],
        temperature=0.0,  # Set temperature
        max_tokens=2048,  # Set max tokens
        stream=False,
    )
    summary = response.choices[0].message.content
    return summary

def click_button_session(sessionId):
    f = open(f"users/{sessionId}.json", 'r')
    state = json.load(f)
    f.close()
    st.session_state.messages = state['messages']
    st.session_state.sessionId = state['sessionId']
    st.session_state.summary = state['summary']

if 'sessionId' not in st.session_state:
    st.session_state.sessionId = str(uuid.uuid4())

# Custom Streamlit app title and icon
st.set_page_config(
    page_title="Trợ lý ảo",
    page_icon=":robot_face:",
)

st.title("🤖 Trợ lý ảo")

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
st.sidebar.write("Đây là một trợ lý y tế ảo giúp kết nối người dùng và dược sĩ\
    giúp người dùng có thể được điều trị các bệnh thông thường từ xa")

openai.api_key = st.secrets["OPENAI_API_KEY"]

system_text = open_file('prompt/system_patient.txt')

# CHAT MODEL

st.sidebar.subheader("Làm mới cuộc trò chuyện")
# Reset Button
if st.sidebar.button(":arrows_counterclockwise: Làm mới"):
    # Save the chat history to the DataFrame before clearing it
    state = {
        'sessionId': st.session_state.sessionId,
        'messages': st.session_state.messages,
        'summary': st.session_state.summary
    }
    if st.session_state.messages:
        with open(f'users/{st.session_state.sessionId}.json', 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=4)

    # Clear the chat messages and reset the full response
    st.session_state.sessionId =  str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": system_text})
    st.session_state.summary = ""
    full_response = ""

st.sidebar.subheader("Các đoạn chat")

path_sessions = glob.glob("users/*.json")

for path_session in path_sessions:
    sessionId = path_session.split('/')[1].split('.')[0]
    st.sidebar.button(f"{sessionId}", on_click=click_button_session, args=(sessionId,))

# Initialize Chat Messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Optional
    st.session_state.messages.append({"role": "system", "content": system_text})
    st.session_state.summary = ""
    
if "doctor" not in st.session_state:
    st.session_state.doctor = {
        "seen": False,
        "prescription" : None
    }
    with open(f'doctors/{st.session_state.sessionId}.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.doctor, f, ensure_ascii=False, indent=4)


# Initialize full_response outside the user input check
full_response = ""

def get_doctor_notification(sessionId):
    f = open(f"doctors/{sessionId}.json", 'r')
    doctor_state = json.load(f)
    f.close()
    
    seen = doctor_state['seen']
    prescription = doctor_state['prescription']
    
    return seen, prescription

# Display Chat History
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"]) 

# User Input and AI Response
if prompt := st.chat_input("Bạn cần hỗ trợ điều gì?"):
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    print('chat', st.session_state.messages)
    
    seen, prescription = get_doctor_notification(st.session_state.sessionId)
    
    if seen != st.session_state.doctor['seen']:
        st.info('Bác sĩ đã tham gia vào đoạn chat', icon="ℹ️")
        st.session_state.doctor['seen'] = seen
        
    if prescription != st.session_state.doctor['prescription'] and prescription != '':
        st.session_state.messages.append({"role": "doctor", "content": prescription})
        st.session_state.doctor['prescription'] = prescription

    # Assistant Message
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Initialize st.status for the task
        with st.status("Processing...", expanded=True) as status:
            for response in openai.ChatCompletion.create(
                model='gpt-3.5-turbo-0613',  # Use the selected model name
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=0.2,  # Set temperature
                max_tokens=2048,  # Set max tokens
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            
            # Update st.status to show that the task is complete
            status.update(label="Complete!", state="complete", expanded=False)
        
        message_placeholder.markdown(full_response)
    
    # Append assistant's response to messages
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    if 'tôi đã thu thập đủ thông tin' in full_response.lower():
        st.markdown("Tôi đang xử lý và gửi thông tin tới cho bác sĩ.")
        history_context = "\n"
        for m in st.session_state.messages[:-1]:
            if m["role"] == "user":
                history_context += "Câu trả lời: " + m["content"] + "\n"
            if m["role"] == "assistant":
                history_context += "Câu hỏi: " + m["content"] + "\n"
        history_context += "\n"
        with st.status("Đang tổng hợp thông tin ...", expanded=True) as status:
            st.session_state.summary = get_summary(history_context)
            # Update st.status to show that the task is complete
            status.update(label="Complete!", state="complete", expanded=False)
            # st.status("Completed!").update("Response generated.")
        
        st.markdown("Đây là một số thông tin mà tôi đã tổng hợp\n" + st.session_state.summary)
        
    state = {
        'sessionId': st.session_state.sessionId,
        'messages': st.session_state.messages,
        'summary': st.session_state.summary
    }
    
    with open(f'users/{st.session_state.sessionId}.json', 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=4)
        
