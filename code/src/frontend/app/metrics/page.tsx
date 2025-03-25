'use client';

import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';
import { Navbar } from '../../components/Navigation/Navbar';
import { IncidentService } from '../../lib/services/incidentService';
import { Incident } from '../../lib/types/incident';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

const incidentService = new IncidentService();

export default function Metrics() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const data = await incidentService.getIncidents();
        setIncidents(data);
      } catch (error) {
        console.error('Failed to fetch incidents:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchIncidents();
  }, []);

  // Prepare data for Severity Distribution (Pie Chart)
  const severityData = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [{
      data: [
        incidents.filter(i => i.severity === 'critical').length,
        incidents.filter(i => i.severity === 'high').length,
        incidents.filter(i => i.severity === 'medium').length,
        incidents.filter(i => i.severity === 'low').length,
      ],
      backgroundColor: [
        'rgba(255, 99, 132, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(255, 205, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
      ],
    }],
  };

  // Prepare data for Component Distribution (Bar Chart)
  const componentData = {
    labels: ['API Gateway', 'Database', 'Message Queue'],
    datasets: [{
      label: 'Active Incidents',
      data: [
        incidents.filter(i => i.component === 'api-gateway' && i.status !== 'resolved').length,
        incidents.filter(i => i.component === 'database' && i.status !== 'resolved').length,
        incidents.filter(i => i.component === 'message-queue' && i.status !== 'resolved').length,
      ],
      backgroundColor: 'rgba(54, 162, 235, 0.8)',
    }],
  };

  // Mock data for Resolution Time Trend (Line Chart)
  const resolutionTimeData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Average Resolution Time (hours)',
      data: [24, 20, 18, 22, 16, 15],
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1,
    }],
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="text-center">
              Loading metrics...
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Incident Metrics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Severity Distribution */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Incident Severity Distribution</h3>
              <div className="h-64">
                <Pie 
                  data={severityData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                  }}
                />
              </div>
            </div>

            {/* Component Distribution */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Active Incidents by Component</h3>
              <div className="h-64">
                <Bar
                  data={componentData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: {
                          stepSize: 1
                        }
                      }
                    }
                  }}
                />
              </div>
            </div>

            {/* Resolution Time Trend */}
            <div className="bg-white p-6 rounded-lg shadow md:col-span-2">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Resolution Time Trend</h3>
              <div className="h-64">
                <Line
                  data={resolutionTimeData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        title: {
                          display: true,
                          text: 'Hours'
                        }
                      }
                    }
                  }}
                />
              </div>
            </div>

            {/* Summary Statistics */}
            <div className="bg-white p-6 rounded-lg shadow md:col-span-2">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Summary Statistics</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-600 font-medium">Total Incidents</p>
                  <p className="text-2xl font-semibold text-blue-900">{incidents.length}</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-600 font-medium">Resolution Rate</p>
                  <p className="text-2xl font-semibold text-green-900">
                    {Math.round((incidents.filter(i => i.status === 'resolved').length / incidents.length) * 100)}%
                  </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-purple-600 font-medium">Avg Response Time</p>
                  <p className="text-2xl font-semibold text-purple-900">15m</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 