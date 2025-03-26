import { Navbar } from '../components/Navigation/Navbar';
import { IncidentOverview } from '../components/Dashboard/IncidentOverview';
import { RecentActivity } from '../components/Dashboard/RecentActivity';
import { QuickActions } from '../components/Dashboard/QuickActions';
import { ChatInterface } from '../components/Chat/ChatInterface';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Overview Cards */}
        <div className="px-4 sm:px-0">
          <IncidentOverview />
        </div>

        {/* Quick Actions */}
        <div className="mt-8 px-4 sm:px-0">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <QuickActions />
        </div>

        {/* Two Column Layout */}
        <div className="mt-8 px-4 sm:px-0">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Chat Interface */}
            <div className="lg:col-span-2">
              <h2 className="text-lg font-medium text-gray-900 mb-4">AI Assistant</h2>
              <div className="bg-white rounded-lg shadow">
                <ChatInterface />
              </div>
            </div>

            {/* Recent Activity */}
            <div className="lg:col-span-1">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
              <RecentActivity />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 