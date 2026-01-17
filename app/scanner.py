from pydantic import BaseModel
from typing import List, Literal
from app.engine import get_chat_engine

# --- Data Models ---
class ModelCard(BaseModel):
    name: str
    description: str
    use_case: str
    risk_category: Literal["Minimal", "Limited", "High", "Unacceptable", "Unknown"]
    is_biometric: bool

class ComplianceCheck(BaseModel):
    check_name: str
    status: Literal["PASS", "FAIL", "WARNING"]
    reason: str

class AuditReport(BaseModel):
    model_name: str
    compliance_score: int
    checks: List[ComplianceCheck]

# --- The Logic ---
async def scan_model(card: ModelCard) -> AuditReport:
    """
    1. Constructs a specific prompt based on the user's Model Card.
    2. Uses the RAG engine to find relevant laws.
    3. Returns a structured audit report.
    """
    engine = get_chat_engine()
    
    # We craft a prompt that forces the AI to look for specific violations
    audit_prompt = f"""
    REVIEW THIS AI SYSTEM AGAINST THE EU AI ACT.

    [SYSTEM DETAILS]
    Name: {card.name}
    Description: {card.description}
    Use Case: {card.use_case}
    Self-Assessed Risk: {card.risk_category}
    Biometric Features: {card.is_biometric}

    [TASK]
    Based on the retrieved context (EU AI Act), generate a compliance report.
    1. Check for Prohibited Practices (Article 5).
    2. Check for High-Risk Classification (Annex III).
    3. Check for Transparency Obligations (Article 50).

    [OUTPUT FORMAT]
    Return ONLY a JSON string (no markdown) with this structure:
    {{
        "model_name": "{card.name}",
        "compliance_score": <0-100 integer>,
        "checks": [
            {{ "check_name": "Prohibited Practices", "status": "PASS/FAIL", "reason": "..." }},
            {{ "check_name": "High Risk Classification", "status": "WARNING", "reason": "..." }}
        ]
    }}
    """
    
    # Query the RAG engine
    response = engine.chat(audit_prompt)
    
    # Parse the raw text response into our Pydantic model
    # (In a real app, we'd add error handling for bad JSON here)
    import json
    
    # Strip markdown code blocks if Gemini adds them
    clean_json = response.response.replace("```json", "").replace("```", "").strip()
    
    data = json.loads(clean_json)
    return AuditReport(**data)