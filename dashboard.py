


import streamlit as st
import requests

st.set_page_config(page_title="Ollama & MindsDB Chat", page_icon="💬", layout="wide")  

FASTAPI_URL = "http://127.0.0.1:8000/chat/"

# Sidebar settings
model= st.sidebar.selectbox("Select Model", ["deepseek-coder:1.3b"])
component = st.sidebar.selectbox("select component", ["Defect Management","automated test case","All"])
use_mindsdb = st.sidebar.checkbox("Use MindsDB instead of Ollama")
st.sidebar.write("---")

st.title("💬 Chat with Ollama & MindsDB")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    payload = {"message": user_input, "model": model, "use_mindsdb": use_mindsdb}

    try:
        response = requests.post(FASTAPI_URL, json=payload)
        response_data = response.json()

        if "response" in response_data:
            bot_reply = response_data["response"]
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            with st.chat_message("assistant"):
                st.markdown(bot_reply)
        else:
            st.error("Error: Unexpected response format")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to FastAPI: {str(e)}")

