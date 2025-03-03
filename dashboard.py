import streamlit as st
import requests

st.set_page_config(page_title="Ollama & MindsDB Chat", page_icon="💬", layout="wide")  

FASTAPI_URL = "http://127.0.0.1:8000/chat/"

# Sidebar settings
model = st.sidebar.selectbox("Select Model", ["deepseek-coder:1.3b"])
component = st.sidebar.selectbox("Select Component", ["Chat with ollama", "Defect Management", "automated test case", "All"])
use_mindsdb = st.sidebar.checkbox("Use MindsDB instead of Ollama")
st.sidebar.write("---")

# Redirect based on component selection
if component == "Defect Management":
    st.query_params = {"page": "defect_management"}
elif component == "automated test case":
    st.query_params = {"page": "automated_test_case"}
elif component == "All":
    st.query_params = {"page": "all"}
else:
    st.query_params = {"page": "chat"}

# Get the current page from query params
query_params = st.query_params
page = query_params.get("page", "chat")

# Display content based on the current page
if page == "defect_management":
    st.title("Defect Management")
    st.write("This is the Defect Management page.")
elif page == "automated_test_case":
    st.title("Automated Test Case")
    st.write("This is the Automated Test Case page.")
elif page == "all":
    st.title("All Components")
    st.write("This is the page for all components.")
else:
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