'use client';

import React, { useEffect, useState } from 'react';
import { IncidentService } from '../../lib/services/incidentService';
import { Navbar } from '../../components/Navigation/Navbar';

const incidentService = new IncidentService();

export default function SystemHealth() {
  const [metrics, setMetrics] = useState({
    componentHealth: {} as Record<string, {
      status: 'healthy' | 'degraded' | 'unhealthy',
      incidents: number,
      lastIncident: string
    }>,
    totalIncidents: 0,
    activeIncidents: 0,
    criticalIncidents: 0
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const incidents = await incidentService.getIncidents();
        
        // Calculate component health
        const componentHealth: Record<string, {
          status: 'healthy' | 'degraded' | 'unhealthy',
          incidents: number,
          lastIncident: string
        }> = {};

        incidents.forEach(incident => {
          if (!componentHealth[incident.component]) {
            componentHealth[incident.component] = {
              status: 'healthy',
              incidents: 0,
              lastIncident: ''
            };
          }

          componentHealth[incident.component].incidents++;
          
          // Update last incident time
          if (!componentHealth[incident.component].lastIncident || 
              new Date(incident.created_at) > new Date(componentHealth[incident.component].lastIncident)) {
            componentHealth[incident.component].lastIncident = incident.created_at;
          }

          // Update status based on active incidents and severity
          if (incident.status !== 'resolved') {
            if (incident.severity === 'critical') {
              componentHealth[incident.component].status = 'unhealthy';
            } else if (incident.severity === 'high') {
              componentHealth[incident.component].status = 'degraded';
            }
          }
        });

        setMetrics({
          componentHealth,
          totalIncidents: incidents.length,
          activeIncidents: incidents.filter(i => i.status !== 'resolved').length,
          criticalIncidents: incidents.filter(i => i.severity === 'critical' && i.status !== 'resolved').length
        });
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'unhealthy':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Overview Cards */}
        <div className="px-4 sm:px-0">
          <h1 className="text-2xl font-semibold text-gray-900 mb-6">System Health</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-2">Total Incidents</h2>
              <p className="text-3xl font-bold text-gray-900">{metrics.totalIncidents}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-2">Active Incidents</h2>
              <p className="text-3xl font-bold text-orange-600">{metrics.activeIncidents}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-2">Critical Incidents</h2>
              <p className="text-3xl font-bold text-red-600">{metrics.criticalIncidents}</p>
            </div>
          </div>

          {/* Component Health Table */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-5 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Component Health</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {Object.entries(metrics.componentHealth).map(([component, health]) => (
                <div key={component} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{component}</h3>
                      <p className="text-sm text-gray-500">
                        Last incident: {health.lastIncident ? formatDate(health.lastIncident) : 'No incidents'}
                      </p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-600">
                        {health.incidents} incident{health.incidents !== 1 ? 's' : ''}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(health.status)}`}>
                        {health.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
              {Object.keys(metrics.componentHealth).length === 0 && (
                <div className="px-6 py-4 text-center text-gray-500">
                  No component health data available
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 