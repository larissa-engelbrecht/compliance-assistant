from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.engine import get_chat_engine
from app.modules.eu_ai_act import EUAIActModule

app = FastAPI(title="Compliance Assistant API")

# Initialize the Module
active_module = EUAIActModule()

# --- Data Models ---
class SourceNode(BaseModel):
    text: str
    page: str
    score: float

class ChatResponse(BaseModel):
    response: str
    sources: List[SourceNode]

class ChatRequest(BaseModel):
    message: str

class AuditRequest(BaseModel):
    inputs: Dict[str, Any]  # Flexible input dictionary

# --- Endpoints ---

@app.get("/")
def health_check():
    return {"status": "active", "module": active_module.metadata}

@app.get("/questionnaire")
def get_questions():
    """Frontend calls this to build the form dynamically"""
    return active_module.get_questionnaire()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        engine = get_chat_engine()
        # The 'response' object from LlamaIndex contains both text and sources
        response = engine.chat(request.message)
        
        # Extract sources
        source_data = []
        if response.source_nodes:
            for node in response.source_nodes:
                # Get page number from metadata (defaulting to "1" if missing)
                page_num = node.metadata.get("page_label", "Unknown")
                
                source_data.append(SourceNode(
                    text=node.node.get_text(),
                    page=page_num,
                    score=node.score or 0.0
                ))
        
        return ChatResponse(
            response=str(response),
            sources=source_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))