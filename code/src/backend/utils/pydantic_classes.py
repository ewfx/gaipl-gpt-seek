from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pydantic import BaseModel



@dataclass
class ContextMetadata:
    """Metadata for context information."""
    source: str
    relevance_score: float
    chunk_info: Dict[str, Any]
    timestamp: Optional[str] = None

@dataclass
class ModelContext:
    """Structured context for the model."""
    original_query: str
    retrieved_documents: List[Dict]
    metadata: List[ContextMetadata]
    additional_context: Optional[Dict] = None


class QueryRequest(BaseModel):
    query: str
    additional_context: Optional[Dict] = None
    force_refresh: bool = False

class QueryResponse(BaseModel):
    response: str
    sources: List[Dict]

# validate the execute command request
class ExecuteCommandRequest(BaseModel):
    command: str


# Define Pydantic models for API requests and responses
class IncidentCreate(BaseModel):
    title: str
    description: str
    component: str
    severity: str
    affected_service: str


class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    component: str
    severity: str
    affected_service: str
    created_at: str
    status: str


class ActionRequest(BaseModel):
    action_id: str
    params: Optional[Dict[str, Any]] = None


class ActionResponse(BaseModel):
    success: bool
    output: str = ""
    error: Optional[str] = None


class AnalysisResponse(BaseModel):
    incident_summary: str
    component_health: Dict[str, Any]
    kb_articles: List[Dict[str, Any]]
    recommended_actions: List[Dict[str, Any]]
    automation_level: str
    historical_incidents: List[Dict[str, Any]]

