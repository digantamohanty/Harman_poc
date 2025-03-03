from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
import requests
app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama API endpoint

# Define request body model
class ChatRequest(BaseModel):
    message: str
    model: str = "deepseek-coder:1.3b"
    use_mindsdb: bool = False  # Flag to choose MindsDB or Ollama

# Function to query MindsDB
def query_mindsdb(message, model):
    try:
        connection = pymysql.connect(
            host="127.0.0.1", 
            user="root",
            password="",
            database="mindsdb"
        )
        cursor = connection.cursor()

        # Run a query using the MindsDB model
        query = f"SELECT response FROM mindsdb.{model} WHERE prompt = '{message}'"
        cursor.execute(query)
        result = cursor.fetchone()
        connection.close()

        if result:
            return {"response": result[0]}
        else:
            return {"response": "No response from the AI model in MindsDB."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Function to query Ollama
def query_ollama(message, model):
    payload = {"model": model, "prompt": message, "stream": False}

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/")
async def chat(request: ChatRequest):
    if request.use_mindsdb:
        return query_mindsdb(request.message, request.model)
    else:
        return query_ollama(request.message, request.model)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


