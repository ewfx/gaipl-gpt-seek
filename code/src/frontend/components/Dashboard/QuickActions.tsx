'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { IncidentService } from '../../lib/services/incidentService';

const incidentService = new IncidentService();

export const QuickActions = () => {
  const [isCreatingIncident, setIsCreatingIncident] = useState(false);

  const handleCreateIncident = async () => {
    setIsCreatingIncident(true);
    try {
      const incident = await incidentService.createIncident({
        title: "API Gateway High CPU Usage",
        description: "API Gateway is experiencing high CPU usage causing increased response times.",
        component: "api-gateway",
        severity: "high",
        affected_service: "customer-portal",
        status: "open",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });
      
      // Analyze the incident immediately
      await incidentService.analyzeIncident(incident.id);
      
      // Reload the page to show the new incident
      window.location.reload();
    } catch (error) {
      console.error('Failed to create incident:', error);
      alert('Failed to create incident. Please try again.');
    } finally {
      setIsCreatingIncident(false);
    }
  };

  const actions = [
    {
      title: 'Create Incident',
      description: 'Report a new incident for analysis',
      icon: (
        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      onClick: handleCreateIncident,
      loading: isCreatingIncident
    },
    {
      title: 'System Health',
      description: 'View current system metrics and status',
      icon: (
        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      href: '/health'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {actions.map((action, index) => (
        action.href ? (
          <Link key={index} href={action.href} className="block">
            <div className="bg-white rounded-lg shadow p-6 hover:bg-gray-50 transition duration-150">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                    {action.icon}
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">{action.title}</h3>
                  <p className="mt-1 text-sm text-gray-500">{action.description}</p>
                </div>
              </div>
            </div>
          </Link>
        ) : (
          <button
            key={index}
            onClick={action.onClick}
            disabled={action.loading}
            className="block w-full"
          >
            <div className={`bg-white rounded-lg shadow p-6 hover:bg-gray-50 transition duration-150 ${
              action.loading ? 'opacity-75 cursor-not-allowed' : ''
            }`}>
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                    {action.loading ? (
                      <svg className="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    ) : action.icon}
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900">{action.title}</h3>
                  <p className="mt-1 text-sm text-gray-500">{action.description}</p>
                </div>
              </div>
            </div>
          </button>
        )
      ))}
    </div>
  );
}; 