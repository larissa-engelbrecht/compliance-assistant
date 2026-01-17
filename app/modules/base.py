from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Literal, Dict

# --- Standardized Output Models ---
class CheckResult(BaseModel):
    check_id: str
    name: str
    status: Literal["PASS", "FAIL", "WARNING", "MANUAL_REVIEW"]
    reason: str
    reference_articles: List[str]

class ComplianceReport(BaseModel):
    risk_level: str
    compliance_score: int
    key_obligations: List[str]
    checks: List[CheckResult]

# --- The Interface ---
class RegulationModule(ABC):
    """
    Base class for all Regulation Modules.
    Enforces a standard way to assess risk and generate reports.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> Dict[str, str]:
        """Name, Version, Jurisdiction"""
        pass

    @abstractmethod
    def get_questionnaire(self) -> List[Dict]:
        """Returns the questions this regulation needs answered."""
        pass

    @abstractmethod
    async def evaluate(self, inputs: Dict, rag_engine=None) -> ComplianceReport:
        """
        Takes user answers + RAG engine.
        Returns a standardized ComplianceReport.
        """
        pass