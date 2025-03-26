'use client';

import React, { useEffect, useState } from 'react';
import { IncidentService } from '../../lib/services/incidentService';
import { Incident } from '../../lib/types/incident';
import { useIncidentContext } from '../../lib/contexts/IncidentContext';

const incidentService = new IncidentService();

export const IncidentOverview = () => {
  const { refreshKey } = useIncidentContext();
  const [metrics, setMetrics] = useState({
    activeIncidents: 0,
    systemHealth: 0,
    avgResponseTime: 0,
    resolutionRate: 0,
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const incidents = await incidentService.getIncidents();
        const activeIncidents = incidents.filter(i => i.status !== 'resolved').length;
        const totalIncidents = incidents.length;
        
        // Calculate resolution rate
        const resolvedIncidents = incidents.filter(i => i.status === 'resolved').length;
        const resolutionRate = totalIncidents > 0 
          ? Math.round((resolvedIncidents / totalIncidents) * 100) 
          : 100;

        // For demo purposes, we'll calculate system health as inverse of critical/high severity incidents
        const criticalIncidents = incidents.filter(i => 
          i.status !== 'resolved' && (i.severity === 'critical' || i.severity === 'high')
        ).length;
        const systemHealth = Math.max(0, 100 - (criticalIncidents * 10));

        // For demo purposes, use a fixed response time
        const avgResponseTime = 15;

        setMetrics({
          activeIncidents,
          systemHealth,
          avgResponseTime,
          resolutionRate,
        });
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [refreshKey]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Active Incidents */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-red-100 text-red-600">
            <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="ml-4">
            <h2 className="text-gray-600 text-sm font-medium">Active Incidents</h2>
            <p className="text-2xl font-semibold text-gray-900">{metrics.activeIncidents}</p>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-green-100 text-green-600">
            <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="ml-4">
            <h2 className="text-gray-600 text-sm font-medium">System Health</h2>
            <p className="text-2xl font-semibold text-gray-900">{metrics.systemHealth}%</p>
          </div>
        </div>
      </div>

      {/* Response Time */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-blue-100 text-blue-600">
            <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="ml-4">
            <h2 className="text-gray-600 text-sm font-medium">Avg Response Time</h2>
            <p className="text-2xl font-semibold text-gray-900">{metrics.avgResponseTime}m</p>
          </div>
        </div>
      </div>

      {/* Resolution Rate */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center">
          <div className="p-3 rounded-full bg-purple-100 text-purple-600">
            <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="ml-4">
            <h2 className="text-gray-600 text-sm font-medium">Resolution Rate</h2>
            <p className="text-2xl font-semibold text-gray-900">{metrics.resolutionRate}%</p>
          </div>
        </div>
      </div>
    </div>
  );
}; 