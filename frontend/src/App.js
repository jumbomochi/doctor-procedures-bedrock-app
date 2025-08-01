import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Activity, Brain, Zap } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import QuickActions from './components/QuickActions';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-white to-maroon-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-maroon-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-maroon-600 rounded-lg flex items-center justify-center maroon-shadow">
                  <Activity className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-maroon-800">Doctor Procedures App</h1>
                  <p className="text-sm text-maroon-600">AI-Powered Medical Procedure Management</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="hidden sm:flex items-center space-x-2 text-sm text-maroon-600">
                  <Brain className="w-4 h-4" />
                  <span>Powered by Amazon Bedrock</span>
                </div>
                <div className="flex items-center space-x-2 px-3 py-1 bg-maroon-100 text-maroon-800 rounded-full text-sm font-medium">
                  <Zap className="w-4 h-4" />
                  <span>Online</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-maroon-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col sm:flex-row justify-between items-center">
              <div className="text-sm text-maroon-600">
                © 2025 Doctor Procedures App. Built with React & AWS Bedrock.
              </div>
              <div className="flex items-center space-x-4 mt-2 sm:mt-0">
                <div className="text-xs text-maroon-500">
                  API: https://jj6skt98b3.execute-api.us-east-1.amazonaws.com
                </div>
                <div className="text-xs text-maroon-500">
                  Agent ID: EBGEJR3FWL
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

const Dashboard = () => {
  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg card-shadow p-6 border border-maroon-100">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-maroon-800 mb-2">
            Welcome to Doctor Procedures Management
          </h2>
          <p className="text-maroon-600 max-w-2xl mx-auto">
            Manage medical procedures with the power of AI. Chat with our intelligent assistant or use quick actions 
            to add procedures, get cost quotes, and view procedure history. All powered by Amazon Bedrock and Nova Pro.
          </p>
        </div>
        
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="text-center p-4 bg-maroon-50 rounded-lg border border-maroon-100">
            <div className="w-12 h-12 bg-maroon-600 rounded-lg flex items-center justify-center mx-auto mb-3 maroon-shadow">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-semibold text-maroon-800">AI Assistant</h3>
            <p className="text-sm text-maroon-600 mt-1">Natural language processing for complex queries</p>
          </div>
          
          <div className="text-center p-4 bg-maroon-50 rounded-lg border border-maroon-100">
            <div className="w-12 h-12 bg-maroon-700 rounded-lg flex items-center justify-center mx-auto mb-3 maroon-shadow">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-semibold text-maroon-800">Real-time Data</h3>
            <p className="text-sm text-maroon-600 mt-1">Live updates from DynamoDB database</p>
          </div>
          
          <div className="text-center p-4 bg-maroon-50 rounded-lg border border-maroon-100">
            <div className="w-12 h-12 bg-maroon-800 rounded-lg flex items-center justify-center mx-auto mb-3 maroon-shadow">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-semibold text-maroon-800">Fast Actions</h3>
            <p className="text-sm text-maroon-600 mt-1">Quick forms for common operations</p>
          </div>
        </div>
      </div>

      {/* Main Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chat Interface */}
        <div className="lg:col-span-1">
          <div className="h-[600px]">
            <ChatInterface />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="lg:col-span-1">
          <QuickActions />
        </div>
      </div>

      {/* Tips Section */}
      <div className="bg-maroon-50 rounded-lg p-6 border border-maroon-100">
        <h3 className="text-lg font-semibold text-maroon-800 mb-4">💡 Tips for using the app</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-maroon-700 mb-2">Chat Examples:</h4>
            <ul className="space-y-1 text-maroon-600">
              <li>• "Show me the history for Dr. Smith"</li>
              <li>• "What is the cost for procedure TEST001?"</li>
              <li>• "Add a procedure for Dr. Johnson"</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-maroon-700 mb-2">Quick Actions:</h4>
            <ul className="space-y-1 text-maroon-600">
              <li>• Use forms for structured data entry</li>
              <li>• Results appear instantly below forms</li>
              <li>• Click the ✕ to return to main menu</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
