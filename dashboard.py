import streamlit as st
import requests
import pandas as pd
import re  # To detect SQL queries

# Set page config (MUST BE FIRST)
st.set_page_config(page_title="Ollama & MindsDB Chat", page_icon="💬", layout="wide")  

FASTAPI_URL = "http://127.0.0.1:8000/chat/"
MINDSDB_URL = "http://127.0.0.1:47334/api/sql/query"  # MindsDB SQL API Endpoint

# Sidebar settings
model = st.sidebar.selectbox("Select Model", ["deepseek-coder:1.3b"])
component = st.sidebar.selectbox("Select Component", ["Chat with ollama", "Defect Management", "Automated Test Case", "All"])
use_mindsdb = st.sidebar.checkbox("Use MindsDB instead of Ollama")
st.sidebar.write("---")

# Detect if input is an SQL query
def is_sql_query(text):
    sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]
    return any(text.strip().upper().startswith(keyword) for keyword in sql_keywords)

# Redirect based on component selection
if component == "Defect Management":
    st.query_params = {"page": "defect_management"}
elif component == "Automated Test Case":
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
    if use_mindsdb:
        st.title("🐖 MindsDB Database Manager")
        st.write("Execute SQL queries directly on MindsDB.")

        query = st.text_area("Enter SQL Query:", "")

        if st.button("Run Query"):
            if not query.strip():
                st.warning("Please enter a valid SQL query.")
            else:
                payload = {"query": query}
                try:
                    response = requests.post(MINDSDB_URL, json=payload)
                    response_data = response.json()

                    if "error" in response_data:
                        st.error(f"❌ Error from MindsDB: {response_data['error']}")
                    elif "success" in response_data and not response_data["success"]:
                        st.error(f"❌ MindsDB Query Failed: {response_data.get('message', 'Unknown error')}")
                    elif "data" in response_data and isinstance(response_data["data"], list) and response_data["data"]:
                        df = pd.DataFrame(response_data["data"])
                        st.write("### Query Results:")
                        st.dataframe(df)
                    else:
                        st.warning("⚠️ No data returned from MindsDB.")

                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.title("💬 Chat with Ollama & MindsDB")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Type your message or SQL query...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            if is_sql_query(user_input):
                payload = {"query": user_input}
                try:
                    response = requests.post(MINDSDB_URL, json=payload)
                    response_data = response.json()

                    if "error" in response_data:
                        st.session_state.messages.append({"role": "assistant", "content": f"❌ Error: {response_data['error']}"})
                        with st.chat_message("assistant"):
                            st.error(response_data["error"])
                    elif "data" in response_data and isinstance(response_data["data"], list) and response_data["data"]:
                        df = pd.DataFrame(response_data["data"])
                        st.session_state.messages.append({"role": "assistant", "content": "### Query Results:\n"})
                        with st.chat_message("assistant"):
                            st.dataframe(df)
                    else:
                        st.warning("⚠️ No data returned from MindsDB.")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error executing query: {str(e)}")
            else:
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
