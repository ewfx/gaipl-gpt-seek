'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { IncidentService } from '../../../lib/services/incidentService';
import { Incident, IncidentAction } from '../../../lib/types/incident';
import { Navbar } from '../../../components/Navigation/Navbar';

const incidentService = new IncidentService();

// Toast notification component
const Toast = ({ message, type, onClose }: { message: string; type: 'success' | 'error'; onClose: () => void }) => (
  <div className="fixed top-4 right-4 z-50 animate-fade-in">
    <div className={`rounded-lg p-4 flex items-center space-x-2 ${
      type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
    }`}>
      <span className="text-sm font-medium">{message}</span>
      <button
        onClick={onClose}
        className="ml-4 text-sm font-medium hover:text-opacity-75"
      >
        ✕
      </button>
    </div>
  </div>
);

export default function IncidentDetails() {
  const params = useParams();
  const incidentId = params.id as string;
  
  const [incident, setIncident] = useState<Incident | null>(null);
  const [analysis, setAnalysis] = useState<string>('');
  const [actions, setActions] = useState<IncidentAction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [healthStatus, setHealthStatus] = useState<string>('');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    const fetchIncidentDetails = async () => {
      try {
        const incidents = await incidentService.getIncidents();
        const currentIncident = incidents.find(i => i.id === incidentId);
        if (currentIncident) {
          setIncident(currentIncident);
          
          // Get analysis and recommended actions
          const analysisResult = await incidentService.analyzeIncident(incidentId);
          setAnalysis(analysisResult.analysis);
          setActions(analysisResult.recommended_actions);
          
          // Get health status
          const healthCheck = await incidentService.getHealthCheck(incidentId);
          setHealthStatus(healthCheck.status);
        }
      } catch (error) {
        console.error('Failed to fetch incident details:', error);
      }
    };

    fetchIncidentDetails();
  }, [incidentId]);

  const executeAction = async (actionId: string) => {
    setIsLoading(true);
    try {
      const result = await incidentService.executeAction(incidentId, actionId);
      if (result.success) {
        // Refresh incident details
        const incidents = await incidentService.getIncidents();
        const updatedIncident = incidents.find(i => i.id === incidentId);
        if (updatedIncident) {
          setIncident(updatedIncident);
        }
        
        // Get new health status
        const healthCheck = await incidentService.getHealthCheck(incidentId);
        setHealthStatus(healthCheck.status);

        // Show success toast
        setToast({
          message: result.message || 'Action executed successfully',
          type: 'success'
        });
      }
    } catch (error) {
      console.error('Failed to execute action:', error);
      setToast({
        message: 'Failed to execute action. Please try again.',
        type: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved':
        return 'bg-green-100 text-green-800';
      case 'analyzing':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-red-100 text-red-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600';
      case 'high':
        return 'text-orange-600';
      case 'medium':
        return 'text-yellow-600';
      default:
        return 'text-blue-600';
    }
  };

  if (!incident) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 sm:px-0">
            <h2 className="text-2xl font-semibold text-gray-900">Loading incident details...</h2>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          <div className="bg-white shadow rounded-lg overflow-hidden">
            {/* Header */}
            <div className="px-6 py-5 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-semibold text-gray-900">{incident.title}</h1>
                  <p className="mt-1 text-sm text-gray-500">{incident.description}</p>
                </div>
                <div className="flex items-center space-x-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(incident.status)}`}>
                    {incident.status.replace('_', ' ')}
                  </span>
                  <span className={`text-sm font-medium ${getSeverityColor(incident.severity)}`}>
                    {incident.severity.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>

            {/* Details */}
            <div className="px-6 py-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <h3 className="text-sm font-medium text-gray-500">Component</h3>
                <p className="mt-1 text-sm text-gray-900">{incident.component}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500">Affected Service</h3>
                <p className="mt-1 text-sm text-gray-900">{incident.affected_service}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-500">Created</h3>
                <p className="mt-1 text-sm text-gray-900">
                  {new Date(incident.created_at).toLocaleString()}
                </p>
              </div>
            </div>

            {/* Analysis */}
            <div className="px-6 py-4 border-t border-gray-200">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Analysis</h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{analysis}</p>
              </div>
            </div>

            {/* Health Status */}
            <div className="px-6 py-4 border-t border-gray-200">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Current Health Status</h2>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                healthStatus === 'healthy' ? 'bg-green-100 text-green-800' :
                healthStatus === 'degraded' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {healthStatus}
              </span>
            </div>

            {/* Actions */}
            <div className="px-6 py-4 border-t border-gray-200">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Recommended Actions</h2>
              <div className="space-y-4">
                {actions.map((action) => (
                  <div key={action.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">{action.title}</h3>
                        <p className="mt-1 text-sm text-gray-500">{action.description}</p>
                      </div>
                      <button
                        onClick={() => executeAction(action.id)}
                        disabled={isLoading || incident.status === 'resolved'}
                        className={`px-4 py-2 rounded-md text-sm font-medium text-white ${
                          isLoading || incident.status === 'resolved'
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700'
                        }`}
                      >
                        {isLoading ? 'Executing...' : 'Execute'}
                      </button>
                    </div>
                  </div>
                ))}
                {actions.length === 0 && (
                  <p className="text-sm text-gray-500">No actions available</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 