import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Literal
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# --- Load environment variables ---
load_dotenv()

app = FastAPI(title="Translator A2A Agent")

# --- Serve the Agent Card ---
@app.get("/.well-known/agent.json")
async def agent_card():
    try:
        with open("../agent_cards/translate_card.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(404, detail="Agent card not found")
    except Exception as e:
        raise HTTPException(500, detail=f"Agent card load failed: {str(e)}")

# --- A2A-compliant request model ---
class A2ARequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: str
    params: Dict[str, Any]

# --- /run endpoint for translation ---
@app.post("/run")
async def run_handler(a2a_req: A2ARequest):
    if a2a_req.method != "tasks/send":
        return {
            "jsonrpc": "2.0",
            "id": a2a_req.id,
            "error": {"code": -32601, "message": "Method not found"}
        }

    # Extract translation parameters
    task_params = a2a_req.params.get("task", {})
    source_lang = task_params.get("source_lang", "en")
    target_lang = task_params.get("target_lang", "fr")

    # Extract the text to translate
    message = a2a_req.params.get("message", {})
    text_to_translate = ""
    for part in message.get("parts", []):
        if part.get("type") == "text":
            text_to_translate = part.get("text", "")
            break

    if not text_to_translate.strip():
        return {
            "jsonrpc": "2.0",
            "id": a2a_req.id,
            "error": {"code": -32602, "message": "No text provided for translation."}
        }

    # Azure AI configuration
    endpoint = os.getenv("AZURE_API_ENDPOINT")
    model = os.getenv("AZURE_DEPLOYMENT_NAME")
    token = os.getenv("AZURE_API_KEY")

    if not all([endpoint, model, token]):
        return {
            "jsonrpc": "2.0",
            "id": a2a_req.id,
            "error": {"code": -32001, "message": "Invalid service configuration"}
        }

    try:
        # Call the LLM to translate
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(token),
        )
        prompt = (
            f"Translate the following text from {source_lang} to {target_lang}:\n{text_to_translate}"
        )
        response = client.complete(
            messages=[
                SystemMessage("You are a translation assistant."),
                UserMessage(prompt),
            ],
            temperature=0.3,
            top_p=1.0,
            max_tokens=1500,
            model=model
        )
        translated_text = response.choices[0].message.content
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": a2a_req.id,
            "error": {"code": -32000, "message": f"Translation failed: {str(e)}"}
        }

    # Return A2A-compliant response
    return {
        "jsonrpc": "2.0",
        "id": a2a_req.id,
        "result": {
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "mimeType": "text/markdown",
                    "data": {"text": translated_text}
                }
            ]
        }
    }
