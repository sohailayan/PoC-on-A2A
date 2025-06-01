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

app = FastAPI(title="Blog Generator A2A Agent")

# --- Serve the Agent Card ---
@app.get("/.well-known/agent.json")
async def agent_card():
    try:
        with open("../agent_cards/blog_card.json", encoding="utf-8") as f:
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

# --- /run endpoint for A2A tasks ---
@app.post("/run")
async def run_handler(a2a_req: A2ARequest):
    if a2a_req.method != "tasks/send":
        return {
            "jsonrpc": "2.0",
            "id": a2a_req.id,
            "error": {"code": -32601, "message": "Method not found"}
        }

    # Extract blog prompt from message parts
    message = a2a_req.params.get("message", {})
    blog_prompt = ""
    for part in message.get("parts", []):
        if part.get("type") == "text":
            blog_prompt = part.get("text", "")
            break

    if not blog_prompt:
        return {
            "jsonrpc": "2.0",
            "id": a2a_req.id,
            "error": {"code": -32602, "message": "No valid text part found in message"}
        }

    # Optionally, extract extra parameters from task (e.g., length, style)
    task_params = a2a_req.params.get("task", {})
    length = task_params.get("length", "medium")
    style = task_params.get("style", "formal")

    # Azure AI client setup
    endpoint = os.getenv("AZURE_API_ENDPOINT")  # e.g., "https://your-resource-name.openai.azure.com/"
    model = os.getenv("AZURE_DEPLOYMENT_NAME")  # e.g., "gpt-4" or your deployment name
    token = os.getenv("AZURE_API_KEY")

    if not endpoint or not model or not token:
        return {
            "jsonrpc": "2.0",
            "id": a2a_req.id,
            "error": {"code": -32001, "message": "Missing environment configuration"}
        }

    try:
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(token),
        )
        response = client.complete(
            messages=[
                SystemMessage(f"You are a {style} blog writer. Create a {length} post about: {blog_prompt}"),
                UserMessage("Generate a well-structured blog post with headings and sections."),
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=1500,
            model=model
        )
        blog_content = response.choices[0].message.content
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": a2a_req.id,
            "error": {"code": -32000, "message": f"LLM call failed: {str(e)}"}
        }

    # Return A2A-compliant result
    return {
        "jsonrpc": "2.0",
        "id": a2a_req.id,
        "result": {
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "mimeType": "text/markdown",
                    "data": {"text": blog_content}
                }
            ]
        }
    }
