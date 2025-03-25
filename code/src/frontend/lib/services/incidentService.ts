import { Incident, IncidentAction, HealthCheckResult } from '../types/incident';

const API_BASE_URL = 'http://localhost:8000';

export class IncidentService {
  async createIncident(incident: Omit<Incident, 'id'>): Promise<Incident> {
    const response = await fetch(`${API_BASE_URL}/incidents/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(incident),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create incident');
    }
    
    return response.json();
  }

  async getIncidents(): Promise<Incident[]> {
    const response = await fetch(`${API_BASE_URL}/incidents/`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch incidents');
    }
    
    return response.json();
  }

  async analyzeIncident(incidentId: string): Promise<{ analysis: string; recommended_actions: IncidentAction[] }> {
    const response = await fetch(`${API_BASE_URL}/incidents/${incidentId}/analyze`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to analyze incident');
    }
    
    return response.json();
  }

  async executeAction(incidentId: string, actionId: string, params: Record<string, any> = {}): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE_URL}/incidents/${incidentId}/execute-action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action_id: actionId, params }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to execute action');
    }
    
    return response.json();
  }

  async getHealthCheck(incidentId: string): Promise<HealthCheckResult> {
    const response = await fetch(`${API_BASE_URL}/incidents/${incidentId}/health-check`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to get health check');
    }
    
    return response.json();
  }

  async closeIncident(incidentId: string): Promise<Incident> {
    const response = await fetch(`${API_BASE_URL}/incidents/${incidentId}/close`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to close incident');
    }
    
    return response.json();
  }
} 