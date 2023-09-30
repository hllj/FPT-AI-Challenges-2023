# Library
import json
import uuid
import openai
import streamlit as st
import pika
import uuid
import os
import json
from utils import open_file,get_summary

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

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY')

system_text = open_file('prompt/system_patient.txt')
# Initialize RabbitMQ

def callback_doctor_app(ch, method, properties, body):
    prescription = body.decode("utf-8")
    st.markdown("Đơn thuốc của bác sĩ \n" + prescription)   
    # st.status.update(label="Complete!", state="complete", expanded=False)   
    state = {
        'sessionId': st.session_state.sessionId,
        'prescription': prescription,
    }   
    with open(f'doctors/{st.session_state.sessionId}.json', 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=4)


url = os.environ.get('CLOUDAMQP_URL', 'amqp://bbcaqtmc:tX2Nex9rE8bJsrFNjvr9c7q-Mw-AqZ5w@armadillo.rmq.cloudamqp.com/bbcaqtmc')
params = pika.URLParameters(url)
params.socket_timeout = 10

connection = pika.BlockingConnection(params) # Connect to CloudAMQP
channel = connection.channel() # start a channel

reply_queue = channel.queue_declare(queue='', exclusive=True)

channel.basic_consume(queue=reply_queue.method.queue, auto_ack=True,
    on_message_callback=callback_doctor_app)

channel.queue_declare(queue='request-queue')

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

# Initialize Chat Messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Optional
    st.session_state.messages.append({"role": "system", "content": system_text})
    st.session_state.summary = ""

# Initialize full_response outside the user input check
full_response = ""

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
                temperature=0.1,  # Set temperature
                max_tokens=1024,  # Set max tokens
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

        # RabbitMQ Integration
        print(f'summary: {st.session_state.summary}')
        st.info('Bác sĩ đã tham gia vào đoạn chat', icon="ℹ️")
        channel.basic_publish('', routing_key='request-queue', properties=pika.BasicProperties(
            reply_to=reply_queue.method.queue,
            correlation_id=st.session_state.sessionId
        ), body=st.session_state.summary)

        channel.start_consuming()
      
    state = {
        'sessionId': st.session_state.sessionId,
        'messages': st.session_state.messages,
        'summary': st.session_state.summary
    }
    
    with open(f'users/{st.session_state.sessionId}.json', 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=4)
        
        
