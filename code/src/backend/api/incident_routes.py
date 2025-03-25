"""
API routes for incident management and agent interaction.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query

from ..agents.incident_agent import IncidentAgent
from ..agents.mocks.service_mocks import MockIncidentManager
from ..utils.pydantic_classes import IncidentCreate, IncidentResponse,ActionRequest, ActionResponse, AnalysisResponse


# Create router
router = APIRouter(prefix="/incidents")

# In-memory store of IncidentAgent instances
# In a real app, you might want to use a more persistent solution
incident_agents: Dict[str, IncidentAgent] = {}

# Initialize mock incident manager
incident_manager = MockIncidentManager()


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(incident: IncidentCreate):
    """Create a new incident and initialize an agent for it."""
    # Use the mock incident manager to create an incident
    new_incident = incident_manager.create_incident(
        title=incident.title,
        description=incident.description,
        component=incident.component,
        severity=incident.severity,
        affected_service=incident.affected_service
    )
    
    # Initialize an agent for this incident
    incident_agents[new_incident["id"]] = IncidentAgent(new_incident)
    
    return new_incident


@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(
    component: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """List all incidents, with optional filtering."""
    filters = {}
    if component:
        filters["component"] = component
    if status:
        filters["status"] = status
    
    return incident_manager.list_incidents(**filters)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str):
    """Get details of a specific incident."""
    incident = incident_manager.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident


@router.post("/{incident_id}/analyze", response_model=AnalysisResponse)
async def analyze_incident(incident_id: str):
    """Analyze an incident and recommend actions."""
    # Check if the incident exists
    incident = incident_manager.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    
    # Check if we have an agent for this incident
    if incident_id not in incident_agents:
        incident_agents[incident_id] = IncidentAgent(incident)
    
    # Get analysis from the agent
    analysis = incident_agents[incident_id].analyze_incident()
    return analysis


@router.post("/{incident_id}/health-check", response_model=Dict[str, Any])
async def run_health_check(incident_id: str):
    """Run a health check for the affected component."""
    # Check if the incident exists
    incident = incident_manager.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    
    # Check if we have an agent for this incident
    if incident_id not in incident_agents:
        incident_agents[incident_id] = IncidentAgent(incident)
    
    # Run health check
    health_data = incident_agents[incident_id].run_health_check()
    return health_data


@router.post("/{incident_id}/execute-action", response_model=ActionResponse)
async def execute_action(action: ActionRequest, incident_id: str):
    """Execute a specific action for incident resolution."""
    # Check if the incident exists
    incident = incident_manager.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    
    # Check if we have an agent for this incident
    if incident_id not in incident_agents:
        incident_agents[incident_id] = IncidentAgent(incident)
    
    # Add incident_id to params
    params = action.params or {}
    params["incident_id"] = incident_id
    
    # Execute the action
    result = incident_agents[incident_id].execute_action(action.action_id, params)
    
    # Convert ActionResult to response
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error
    }


@router.post("/{incident_id}/close", response_model=Dict[str, Any])
async def close_incident(incident_id: str):
    """Close an incident and mark it as resolved."""
    # Check if the incident exists
    incident = incident_manager.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    
    # Resolve the incident
    resolved_incident = incident_manager.resolve_incident(
        incident_id,
        resolution="Incident closed by user after completing recommended actions."
    )
    
    if not resolved_incident:
        raise HTTPException(status_code=500, detail="Failed to close incident")
    
    return resolved_incident 