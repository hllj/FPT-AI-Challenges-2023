# Library
import glob
import json
import re
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
load_dotenv('.env.default')

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
    
    col1, _ = st.columns([4, 8])
    col1.info(st.session_state.summary_info, icon="ℹ️")
    col1.button(label='Đưa ra đơn thuốc tham khảo', key="summary_button", on_click=click_button_suggestion, args=(st.session_state.summary_info, st.session_state.properties,))

def click_button_suggestion(summary_info,properties):
    url = "http://localhost:3000/doctor"
    payload = json.dumps({
        "summary": summary_info
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    prescription = response.json()['data']['prescription']
    actives = response.json()['data']['drugs']

    st.session_state.actives = actives
    st.session_state.prescription = prescription
                    
def form_submit(drug_choose, regex_choose, prescription,properties):
    text = "Bạn đã chọn\n\n"
    final_prescription = prescription
    for active in drug_choose:
        text += f"- Hoạt chất {active}: " + drug_choose[active] + "\n\n"
        pattern = regex_choose[active].replace('(', '\(').replace(')', '\)')
        # final_prescription = final_prescription.replace(active, drug_choose[active])
        final_prescription = re.sub(pattern, drug_choose[active], final_prescription)
    st.session_state.final_prescription = final_prescription

def back_on_click():
    del st.session_state['final_prescription']
    time.sleep(0.5)

@st.cache_data(experimental_allow_widgets=True, show_spinner=False)
def consumer(st):
    # Integrate RabbitMQ

    url = os.environ.get('CLOUDAMQP_URL', 'amqp://ezclrtka:zNMh77RlTx9Vz-S1bal3EILSwNcOpDiO@fuji.lmq.cloudamqp.com/ezclrtka')
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
        page_title="Hệ thống hỗ trợ dược sĩ",
        page_icon=":robot_face:",
        layout='wide'
    )

    st.title("🤖 Hệ thống hỗ trợ dược sĩ")

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
    st.sidebar.write("Đây là một trợ lý y tế ảo dành cho dược sĩ dễ dàng kê các đơn thuốc phù hợp cho bệnh nhân")
        
    if 'prescription' in st.session_state and ('final_prescription' not in st.session_state) and ('actives' in st.session_state and len(st.session_state.actives) > 0):
        st.empty()
        with st.container():
            col1, col2 = st.columns([4, 8])
            with col1:
                col1.info(st.session_state.summary_info, icon="ℹ️")
                col1.divider()
                col1.info(st.session_state.prescription, icon="🤖")
            with col2:
                with st.expander('Hãy lựa chọn các biệt dược', expanded=True):
                    drug_choose = {}
                    regex_choose = {}
                    for idx, active in enumerate(st.session_state.actives):
                        options = ()
                        for drug in active['drugs']:
                            options = options + (drug['Biệt dược'], )
                        label = '**' + 'Hoạt chất: ' + active['active'].replace('*', '').replace('.', ' ') + '**'
                        st.markdown(f'{idx + 1}. ' + label)
                        col1, col2 = st.columns([8, 4])
                        with col1:
                            option = st.selectbox(
                                key=active['active'],
                                label=label,
                                label_visibility="collapsed",
                                options=options,
                                index=0,
                            )
                        drug_choose[active['active']] = option
                        for drug in active['drugs']:
                            if drug['Biệt dược'] == option:
                                regex_choose[active['active']] = drug[drug['query_field']]
                                break
                        quantity = [drug['Số lượng'] for drug in active['drugs'] if drug['Biệt dược'] == option][0]
                        col2.text('Số lượng: ' + str(quantity))
                    css='''
                        <style>
                            [data-testid="stExpander"] div:has(>.streamlit-expanderContent) {
                                overflow: scroll;
                                height: 400px;
                            }
                        </style>
                        '''
                    st.markdown(css, unsafe_allow_html=True)
                st.text_area(label="Lưu ý của dược sĩ", placeholder="Ghi chú của bạn", key='doctor_reminder')
                form_button = st.button(label='Xác nhận', on_click=form_submit, args=(drug_choose, regex_choose, st.session_state.prescription, st.session_state.properties))
        st.empty()
    
    if 'final_prescription' in st.session_state:
        with st.spinner('Đang chờ xử lý'):
            time.sleep(0.5)
        st.empty()
        with st.container():
            col1, col2 = st.columns([4, 8])
            with col1:
                col1.info(st.session_state.summary_info, icon="ℹ️")
                col1.divider()
                col1.info(st.session_state.prescription, icon="🤖")
            with col2:
                final = st.session_state.final_prescription
                if 'doctor_reminder' in st.session_state and len(st.session_state.doctor_reminder) > 0:
                    final += '\n\n' + 'Lưu ý của dược sĩ:' + '\n' + st.session_state.doctor_reminder
                text = st.text_area(label="Chỉnh sửa đơn thuốc trước khi gửi cho bệnh nhân", value=final, height=400)
                col1, col2 = st.columns(2)
                col1.button('Gửi đơn thuốc cho bệnh nhân', on_click=click_send_prescription, args=(text, st.session_state.properties,))
                col2.button(label='Trở lại', on_click=back_on_click)
        st.empty()
    
    asyncio.run(consumer(st))