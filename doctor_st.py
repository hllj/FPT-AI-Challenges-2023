# Library
import glob
import json
import uuid
import openai
import requests
import streamlit as st
import pika
import uuid
import os
import json
import time 
from dotenv import load_dotenv
load_dotenv()

import asyncio

def click_send_prescription(prescription, properties):
    print(prescription)
    st.session_state.channel.basic_publish('', routing_key=properties.reply_to, body= prescription)

openai.api_key = os.environ.get('OPENAI_API_KEY')

def on_request_message_received(channel, method, properties, body):
    summary_info = body.decode("utf-8")
    sessionId = properties.correlation_id
    if 'summary_info' not in st.session_state:
        st.session_state.summary_info = ""
        
    st.session_state.summary_info = summary_info
    st.session_state.properties = properties
    
    st.info(st.session_state.summary_info, icon="ℹ️")
    st.button(label='Đưa ra đơn thuốc tham khảo', key="summary_button", on_click=click_button_suggestion, args=(st.session_state.summary_info, st.session_state.properties,))
    

def click_button_suggestion(summary_info,properties):
    url = "http://localhost:3000/doctor"
    payload = json.dumps({
        "summary": summary_info
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    prescription = response.json()['data']['response']['response']
    if prescription:
        url = "http://localhost:3000/storage"

        payload = json.dumps({
            "text": prescription
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        actives = response.json()['data']['response']

        st.session_state.actives = actives
        st.session_state.prescription = prescription   
                    
def form_submit(drug_choose,prescription,properties):
    text = "Bạn đã chọn\n\n"
    final_prescription = prescription
    for active in drug_choose:
        text += f"- Hoạt chất {active}: " + drug_choose[active] + "\n\n"
        final_prescription = final_prescription.replace(active, drug_choose[active])
    st.session_state.final_prescription = final_prescription

@st.cache_data(experimental_allow_widgets=True)
def consumer(st):
    # Integrate RabbitMQ

    url = os.environ.get('CLOUDAMQP_URL', 'amqps://ndtfovdr:pRLAJm2d7gIyFOaxlq74Q0PEg3fDsLnw@gerbil.rmq.cloudamqp.com/ndtfovdr')
    params = pika.URLParameters(url)
    params.socket_timeout = 10
    connection = pika.BlockingConnection(params) # Connect to CloudAMQP
    st.session_state.channel = connection.channel() # start a channel
    st.session_state.channel.queue_declare(queue='request-queue')
    st.session_state.channel.basic_consume(queue='request-queue', auto_ack=True,
        on_message_callback=on_request_message_received)
    st.session_state.channel.start_consuming()

if __name__ == "__main__":
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
        
    if 'prescription' in st.session_state and 'actives' in st.session_state and len(st.session_state.actives) > 0:
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
            st.form_submit_button(label='Lựa chọn', on_click=form_submit, args=(drug_choose, st.session_state.prescription, st.session_state.properties,)) 
    
    if 'final_prescription' in st.session_state:
        st.markdown(st.session_state.final_prescription)
        st.button('Gửi đơn thuốc cho bệnh nhân', on_click=click_send_prescription, args=(st.session_state.final_prescription, st.session_state.properties,))
    
    asyncio.run(consumer(st))