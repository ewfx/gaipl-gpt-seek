export interface Incident {
  id: string;
  title: string;
  description: string;
  component: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  affected_service: string;
  status: 'open' | 'analyzing' | 'in_progress' | 'resolved';
  created_at: string;
  updated_at: string;
}

export interface IncidentAction {
  id: string;
  type: 'diagnostic' | 'remediation';
  title: string;
  description: string;
  params?: Record<string, any>;
}

export interface HealthCheckResult {
  status: 'healthy' | 'degraded' | 'unhealthy';
  metrics: {
    name: string;
    value: number;
    unit: string;
    threshold?: number;
  }[];
  message: string;
} 