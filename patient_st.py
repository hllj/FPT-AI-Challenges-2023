# Library
import openai
import streamlit as st
import pandas as pd
from datetime import datetime

# Custom Streamlit app title and icon
st.set_page_config(
    page_title="VietAI Bot",
    page_icon=":robot_face:",
)

# Set the title
st.title("[VietAI-NTI] ChatGPT")

# Sidebar Configuration
st.sidebar.title("Model Configuration")

# Model Name Selector
model_name = st.sidebar.selectbox(
    "Select a Model",
    ["gpt-3.5-turbo", "gpt-4"],  # Add more model names as needed
    key="model_name",
)

# Temperature Slider
temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.2,
    max_value=2.0,
    value=1.0,
    step=0.1,
    key="temperature",
)

# Max tokens Slider
max_tokens = st.sidebar.slider(
    "Max Tokens",
    min_value=1,
    max_value=4095,
    value=256,
    step=1,
    key="max_tokens",
)

# Top p Slider
top_p = st.sidebar.slider(
    "Top P",
    min_value=0.00,
    max_value=1.00,
    value=1.00,
    step=0.01,
    key="top_p",
)

# Presence penalty Slider
presence_penalty = st.sidebar.slider(
    "Presence penalty",
    min_value=0.00,
    max_value=2.00,
    value=0.00,
    step=0.01,
    key="presence_penalty",
)

# Frequency penalty Slider
frequency_penalty = st.sidebar.slider(
    "Frequency penalty",
    min_value=0.00,
    max_value=2.00,
    value=0.00,
    step=0.01,
    key="frequency_penalty",
)

# Set OPENAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Initialize DataFrame to store chat history
chat_history_df = pd.DataFrame(columns=["Timestamp", "Chat"])

# Initialize Chat Messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize full_response outside the user input check
full_response = ""

# Reset Button
if st.sidebar.button("Reset Chat"):
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

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input and AI Response
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        for response in openai.ChatCompletion.create(
            model=model_name,  # Use the selected model name
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            temperature=temperature,  # Set temperature
            max_tokens=max_tokens,  # Set max tokens
            top_p=top_p, # Set top p
            frequency_penalty=frequency_penalty, # Set frequency penalty
            presence_penalty=presence_penalty, # Set presence penalty
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
