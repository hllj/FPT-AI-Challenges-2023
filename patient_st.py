# Library
import openai
import streamlit as st
import pandas as pd
from datetime import datetime

# Get content
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
# Custom Streamlit app title and icon
st.set_page_config(
    page_title="Trợ lý ảo HDH",
    page_icon=":robot_face:",
)

st.title("Trợ lý ảo")

# Sidebar Configuration
st.sidebar.title("Hỗ trợ")

openai.api_key = st.secrets["OPENAI_API_KEY"]
    
# CHAT MODEL
# Initialize DataFrame to store chat history
chat_history_df = pd.DataFrame(columns=["Timestamp", "Chat"])

# Reset Button
if st.sidebar.button(":arrows_counterclockwise: Làm mới cuộc trò chuyện"):
    # Save the chat history to the DataFrame before clearing it
    if st.session_state.messages:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        new_entry = pd.DataFrame({"Timestamp": [timestamp], "Chat": [chat_history]})
        chat_history_df = pd.concat([chat_history_df, new_entry], ignore_index=True)

        # Save the DataFrame to a CSV file
        chat_history_df.to_csv("chat_history.csv", index=False)

    # Clear the chat messages and reset the full response
    st.session_state.messages = []
    full_response = ""
    
# Initialize Chat Messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    system_text= open_file('prompt/system_patient.txt')
    # Optional
    st.session_state.messages.append({"role": "system", "content": system_text})

# Initialize full_response outside the user input check
full_response = ""

# Display Chat History
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"]) 



# User Input and AI Response
if prompt := st.chat_input("What is up?"):
    
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        print('Chat', st.session_state.messages)
        for response in openai.ChatCompletion.create(
            model='gpt-3.5-turbo',  # Use the selected model name
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
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})