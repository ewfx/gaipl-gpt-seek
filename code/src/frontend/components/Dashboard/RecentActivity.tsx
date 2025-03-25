'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { IncidentService } from '../../lib/services/incidentService';
import { Incident } from '../../lib/types/incident';
import { useIncidentContext } from '../../lib/contexts/IncidentContext';

const incidentService = new IncidentService();

export const RecentActivity = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [isClosing, setIsClosing] = useState<Record<string, boolean>>({});
  const { refreshIncidents } = useIncidentContext();

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const data = await incidentService.getIncidents();
        // Sort by created_at date and take the 5 most recent
        const sortedIncidents = data
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 5);
        setIncidents(sortedIncidents);
      } catch (error) {
        console.error('Failed to fetch incidents:', error);
      }
    };

    fetchIncidents();
    const interval = setInterval(fetchIncidents, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const handleCloseIncident = async (e: React.MouseEvent, incidentId: string) => {
    e.preventDefault(); // Prevent navigation to incident details
    setIsClosing(prev => ({ ...prev, [incidentId]: true }));
    
    try {
      await incidentService.closeIncident(incidentId);
      // Update the incident status locally
      setIncidents(prevIncidents =>
        prevIncidents.map(incident =>
          incident.id === incidentId
            ? { ...incident, status: 'resolved' }
            : incident
        )
      );
      // Trigger refresh of other components
      refreshIncidents();
    } catch (error) {
      console.error('Failed to close incident:', error);
      alert('Failed to close incident. Please try again.');
    } finally {
      setIsClosing(prev => ({ ...prev, [incidentId]: false }));
    }
  };

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours === 1 ? '' : 's'} ago`;
    const days = Math.floor(hours / 24);
    return `${days} day${days === 1 ? '' : 's'} ago`;
  };

  const getStatusColor = (status: string, severity: string) => {
    if (status === 'resolved') return 'bg-green-100 text-green-800';
    if (severity === 'critical') return 'bg-red-100 text-red-800';
    if (severity === 'high') return 'bg-orange-100 text-orange-800';
    if (severity === 'medium') return 'bg-yellow-100 text-yellow-800';
    return 'bg-blue-100 text-blue-800';
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
      </div>
      <div className="divide-y divide-gray-200">
        {incidents.map((incident) => (
          <div key={incident.id} className="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
            <div className="flex items-center justify-between">
              <Link href={`/incidents/${incident.id}`} className="flex-1">
                <div className="flex items-center">
                  <span className={`inline-flex items-center justify-center h-8 w-8 rounded-full ${
                    incident.status === 'resolved' ? 'bg-green-100 text-green-600' :
                    incident.severity === 'critical' ? 'bg-red-100 text-red-600' :
                    incident.severity === 'high' ? 'bg-orange-100 text-orange-600' :
                    'bg-yellow-100 text-yellow-600'
                  }`}>
                    {incident.status === 'resolved' ? '✓' :
                     incident.severity === 'critical' ? '!' :
                     incident.severity === 'high' ? '⚠' :
                     '•'}
                  </span>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900">{incident.title}</p>
                    <p className="text-sm text-gray-500">{incident.description}</p>
                  </div>
                </div>
              </Link>
              <div className="ml-4 flex items-center space-x-4">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  getStatusColor(incident.status, incident.severity)
                }`}>
                  {incident.status.replace('_', ' ')}
                </span>
                <p className="text-xs text-gray-500">{getTimeAgo(incident.created_at)}</p>
                {incident.status !== 'resolved' && (
                  <button
                    onClick={(e) => handleCloseIncident(e, incident.id)}
                    disabled={isClosing[incident.id]}
                    className={`px-3 py-1 rounded-md text-sm font-medium text-white ${
                      isClosing[incident.id]
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-green-600 hover:bg-green-700'
                    }`}
                  >
                    {isClosing[incident.id] ? 'Closing...' : 'Close'}
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
        {incidents.length === 0 && (
          <div className="px-6 py-4 text-center text-gray-500">
            No recent incidents
          </div>
        )}
      </div>
    </div>
  );
}; 