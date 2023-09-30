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

def click_send_prescription( prescription,properties):
    print(prescription)
    channel.basic_publish('', routing_key=properties.reply_to, body= prescription)

openai.api_key = os.environ.get('OPENAI_API_KEY')

def on_request_message_received(channel, method, properties, body):
    summary_info = body.decode("utf-8")
    sessionId = properties.correlation_id
    if summary_info:
        st.info(summary_info, icon="ℹ️")
        st.button(label='Đưa ra đơn thuốc tham khảo', key="summary_button", on_click=click_button_suggestion, args=(summary_info,properties,))

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

        if len(actives) > 0:
            with st.form("Hãy chọn thuốc từ các hoạt chất"):
                drug_choose = {}
                for active in actives:
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
                st.form_submit_button(label='Lựa chọn', on_click=form_submit, args=(drug_choose,prescription,properties,))              
                    
def form_submit(drug_choose,prescription,properties):
    print(drug_choose)
    text = "Bạn đã chọn\n\n"
    final_prescription = prescription
    for active in drug_choose:
        text += f"- Hoạt chất {active}: " + drug_choose[active] + "\n\n"
        final_prescription = final_prescription.replace(active, drug_choose[active])
    final_prescription = final_prescription
    if final_prescription:
        st.markdown('Bạn có muốn gửi đơn thuốc cho bệnh nhân không ?')
        st.button('Gửi đơn thuốc cho bệnh nhân', on_click=click_send_prescription, args=(final_prescription,properties,))

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

    # Integrate RabbitMQ

    url = os.environ.get('CLOUDAMQP_URL', 'amqp://bbcaqtmc:tX2Nex9rE8bJsrFNjvr9c7q-Mw-AqZ5w@armadillo.rmq.cloudamqp.com/bbcaqtmc')
    params = pika.URLParameters(url)
    params.socket_timeout = 10
    connection = pika.BlockingConnection(params) # Connect to CloudAMQP
    channel = connection.channel() # start a channel
    channel.queue_declare(queue='request-queue')
    channel.basic_consume(queue='request-queue', auto_ack=True,
        on_message_callback=on_request_message_received)
    channel.start_consuming()
