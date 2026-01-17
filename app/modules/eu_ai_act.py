from typing import Dict, List
from app.modules.base import RegulationModule, ComplianceReport, CheckResult

class EUAIActModule(RegulationModule):
    @property
    def metadata(self):
        return {
            "name": "EU AI Act",
            "jurisdiction": "European Union",
            "version": "Final Text (2024)",
            "effective_date": "2026-08-02"
        }

    def get_questionnaire(self) -> List[Dict]:
        return [
            {
                "id": "use_case",
                "text": "What is the primary function of the AI system?",
                "type": "select",
                "options": ["Biometric Identification", "Critical Infrastructure", "Education/Vocational Training", "Employment Management", "Credit Scoring", "Public Services", "General Purpose (Chatbot)", "Other"]
            },
            {
                "id": "human_oversight",
                "text": "Is there a human in the loop reviewing decisions?",
                "type": "boolean"
            },
            {
                "id": "sensitive_data",
                "text": "Does the system process special categories of personal data (race, health, politics)?",
                "type": "boolean"
            }
        ]

    async def evaluate(self, inputs: Dict, rag_engine=None) -> ComplianceReport:
        """
        Here we combine Rule-Based Logic (Fast) with GenAI Logic (Deep).
        """
        use_case = inputs.get("use_case")
        human_loop = inputs.get("human_oversight")
        
        # --- 1. Rule-Based High Risk Classification (Annex III) ---
        high_risk_cases = [
            "Biometric Identification", "Critical Infrastructure", 
            "Education/Vocational Training", "Employment Management", 
            "Credit Scoring", "Public Services"
        ]
        
        is_high_risk = use_case in high_risk_cases
        risk_level = "High" if is_high_risk else "Limited"
        
        checks = []
        
        # --- 2. GenAI Check: Prohibited Practices (Article 5) ---
        # We ask Gemini to double-check if this specific use case sounds prohibited
        if rag_engine:
            prompt = f"""
            Analyze this use case against EU AI Act Article 5 (Prohibited Practices).
            Use Case: {use_case}
            Description: {inputs.get('description', 'No description provided')}
            
            Is this likely a PROHIBITED practice? (Yes/No).
            Explain why briefly.
            """
            response = str(rag_engine.chat(prompt))
            
            status = "FAIL" if "yes" in response.lower() else "PASS"
            checks.append(CheckResult(
                check_id="ART_5",
                name="Prohibited Practices Check",
                status=status,
                reason=response[:200] + "...",
                reference_articles=["Article 5"]
            ))

        # --- 3. Obligations Logic ---
        obligations = []
        if is_high_risk:
            obligations = [
                "Establish a Risk Management System (Art 9)",
                "Data Governance & Training Data Requirements (Art 10)",
                "Technical Documentation (Art 11)",
                "Record Keeping (Art 12)",
                "Transparency & Instructions for Use (Art 13)",
                "Human Oversight Measures (Art 14)",
                "Accuracy, Robustness & Cybersecurity (Art 15)"
            ]
            checks.append(CheckResult(
                check_id="ANNEX_III",
                name="High Risk Classification",
                status="WARNING",
                reason=f"System falls under Annex III category: {use_case}",
                reference_articles=["Annex III", "Article 6"]
            ))
        else:
            obligations = ["Transparency (Art 50) - Disclose that content is AI generated"]
            checks.append(CheckResult(
                check_id="LOW_RISK",
                name="Risk Classification",
                status="PASS",
                reason="Does not explicitly fall under Annex III high-risk categories.",
                reference_articles=["Article 50"]
            ))

        return ComplianceReport(
            risk_level=risk_level,
            compliance_score=30 if is_high_risk else 85,
            key_obligations=obligations,
            checks=checks
        )