import React, { useState } from 'react';
import { Plus, DollarSign, Search, Calendar, User, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { apiClient } from '../api';

const QuickActions = () => {
  const [activeForm, setActiveForm] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Form states
  const [addProcedureForm, setAddProcedureForm] = useState({
    doctorName: '',
    procedureCode: '',
    procedureName: '',
    cost: ''
  });

  const [quoteForm, setQuoteForm] = useState({
    procedureCode: ''
  });

  const [historyForm, setHistoryForm] = useState({
    doctorName: '',
    limit: 5
  });

  const resetForms = () => {
    setActiveForm(null);
    setResult(null);
    setError(null);
    setAddProcedureForm({ doctorName: '', procedureCode: '', procedureName: '', cost: '' });
    setQuoteForm({ procedureCode: '' });
    setHistoryForm({ doctorName: '', limit: 5 });
  };

  const handleAddProcedure = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.addProcedure({
        doctorName: addProcedureForm.doctorName,
        procedureCode: addProcedureForm.procedureCode,
        procedureName: addProcedureForm.procedureName,
        cost: parseFloat(addProcedureForm.cost)
      });

      setResult({
        type: 'success',
        title: 'Procedure Added Successfully',
        message: response.message || 'Procedure has been added to the database.'
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGetQuote = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.getQuote(quoteForm.procedureCode);
      setResult({
        type: 'info',
        title: 'Cost Quote',
        message: response.message || `Quote for ${quoteForm.procedureCode}`,
        data: response
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGetHistory = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.getHistory(historyForm.doctorName, historyForm.limit);
      setResult({
        type: 'info',
        title: `History for ${historyForm.doctorName}`,
        message: response.message || `Found ${response.history?.length || 0} procedures`,
        data: response
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const ActionCard = ({ icon: Icon, title, description, onClick, color = 'maroon' }) => (
    <div
      onClick={onClick}
      className={`p-4 rounded-lg border-2 border-dashed border-maroon-200 hover:border-maroon-400 cursor-pointer transition-all duration-200 hover:card-shadow group`}
    >
      <div className={`w-10 h-10 bg-maroon-100 rounded-lg flex items-center justify-center mb-3 group-hover:bg-maroon-200 transition-colors`}>
        <Icon className={`w-5 h-5 text-maroon-600`} />
      </div>
      <h3 className="font-semibold text-maroon-800 mb-1">{title}</h3>
      <p className="text-sm text-maroon-600">{description}</p>
    </div>
  );

  return (
    <div className="bg-white rounded-lg card-shadow p-6 border border-maroon-100">
      <h2 className="text-xl font-semibold text-maroon-800 mb-6 flex items-center">
        <FileText className="w-5 h-5 mr-2 text-maroon-600" />
        Quick Actions
      </h2>

      {!activeForm && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ActionCard
            icon={Plus}
            title="Add Procedure"
            description="Add a new medical procedure to the database"
            onClick={() => setActiveForm('add')}
          />
          <ActionCard
            icon={DollarSign}
            title="Get Quote"
            description="Get cost estimate for a specific procedure"
            onClick={() => setActiveForm('quote')}
          />
          <ActionCard
            icon={Search}
            title="View History"
            description="View procedure history for a doctor"
            onClick={() => setActiveForm('history')}
          />
        </div>
      )}

      {/* Add Procedure Form */}
      {activeForm === 'add' && (
        <div className="animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-maroon-800">Add New Procedure</h3>
            <button
              onClick={resetForms}
              className="text-maroon-500 hover:text-maroon-700"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleAddProcedure} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-maroon-700 mb-1">
                  <User className="w-4 h-4 inline mr-1" />
                  Doctor Name
                </label>
                <input
                  type="text"
                  value={addProcedureForm.doctorName}
                  onChange={(e) => setAddProcedureForm({...addProcedureForm, doctorName: e.target.value})}
                  className="w-full px-3 py-2 border border-maroon-300 rounded-md focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:border-transparent"
                  placeholder="Dr. Smith"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-maroon-700 mb-1">
                  <FileText className="w-4 h-4 inline mr-1" />
                  Procedure Code
                </label>
                <input
                  type="text"
                  value={addProcedureForm.procedureCode}
                  onChange={(e) => setAddProcedureForm({...addProcedureForm, procedureCode: e.target.value})}
                  className="w-full px-3 py-2 border border-maroon-300 rounded-md focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:border-transparent"
                  placeholder="PROC001"
                  required
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-maroon-700 mb-1">
                Procedure Name
              </label>
              <input
                type="text"
                value={addProcedureForm.procedureName}
                onChange={(e) => setAddProcedureForm({...addProcedureForm, procedureName: e.target.value})}
                className="w-full px-3 py-2 border border-maroon-300 rounded-md focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:border-transparent"
                placeholder="Initial Consultation"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-maroon-700 mb-1">
                <DollarSign className="w-4 h-4 inline mr-1" />
                Cost
              </label>
              <input
                type="number"
                step="0.01"
                value={addProcedureForm.cost}
                onChange={(e) => setAddProcedureForm({...addProcedureForm, cost: e.target.value})}
                className="w-full px-3 py-2 border border-maroon-300 rounded-md focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:border-transparent"
                placeholder="150.00"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-success-500 text-white py-2 px-4 rounded-md hover:bg-success-600 focus:outline-none focus:ring-2 focus:ring-success-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? <Loader className="w-4 h-4 animate-spin mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
              {loading ? 'Adding...' : 'Add Procedure'}
            </button>
          </form>
        </div>
      )}

      {/* Get Quote Form */}
      {activeForm === 'quote' && (
        <div className="animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Get Cost Quote</h3>
            <button
              onClick={resetForms}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleGetQuote} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-maroon-700 mb-1">
                <FileText className="w-4 h-4 inline mr-1" />
                Procedure Code
              </label>
              <input
                type="text"
                value={quoteForm.procedureCode}
                onChange={(e) => setQuoteForm({...quoteForm, procedureCode: e.target.value})}
                className="w-full px-3 py-2 border border-maroon-300 rounded-md focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:border-transparent"
                placeholder="TEST001"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-warning-500 text-white py-2 px-4 rounded-md hover:bg-warning-600 focus:outline-none focus:ring-2 focus:ring-warning-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? <Loader className="w-4 h-4 animate-spin mr-2" /> : <DollarSign className="w-4 h-4 mr-2" />}
              {loading ? 'Getting Quote...' : 'Get Quote'}
            </button>
          </form>
        </div>
      )}

      {/* Get History Form */}
      {activeForm === 'history' && (
        <div className="animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">View Procedure History</h3>
            <button
              onClick={resetForms}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleGetHistory} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-maroon-700 mb-1">
                  <User className="w-4 h-4 inline mr-1" />
                  Doctor Name
                </label>
                <input
                  type="text"
                  value={historyForm.doctorName}
                  onChange={(e) => setHistoryForm({...historyForm, doctorName: e.target.value})}
                  className="w-full px-3 py-2 border border-maroon-300 rounded-md focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:border-transparent"
                  placeholder="Dr. Smith"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-maroon-700 mb-1">
                  Limit Results
                </label>
                <select
                  value={historyForm.limit}
                  onChange={(e) => setHistoryForm({...historyForm, limit: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-maroon-300 rounded-md focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:border-transparent"
                >
                  <option value={5}>5 procedures</option>
                  <option value={10}>10 procedures</option>
                  <option value={20}>20 procedures</option>
                </select>
              </div>
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-maroon-600 text-white py-2 px-4 rounded-md hover:bg-maroon-700 focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:ring-offset-2 maroon-shadow disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? <Loader className="w-4 h-4 animate-spin mr-2" /> : <Search className="w-4 h-4 mr-2" />}
              {loading ? 'Loading...' : 'View History'}
            </button>
          </form>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className={`mt-6 p-4 rounded-lg ${
          result.type === 'success' ? 'bg-success-50 border border-success-200' :
          result.type === 'error' ? 'bg-error-50 border border-error-200' :
          'bg-primary-50 border border-primary-200'
        } animate-fade-in`}>
          <div className="flex items-start">
            {result.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-success-600 mt-0.5 mr-3 flex-shrink-0" />
            ) : result.type === 'error' ? (
              <AlertCircle className="w-5 h-5 text-error-600 mt-0.5 mr-3 flex-shrink-0" />
            ) : (
              <FileText className="w-5 h-5 text-primary-600 mt-0.5 mr-3 flex-shrink-0" />
            )}
            <div className="flex-1">
              <h4 className={`font-semibold ${
                result.type === 'success' ? 'text-success-800' :
                result.type === 'error' ? 'text-error-800' :
                'text-primary-800'
              }`}>
                {result.title}
              </h4>
              <p className={`mt-1 text-sm ${
                result.type === 'success' ? 'text-success-700' :
                result.type === 'error' ? 'text-error-700' :
                'text-primary-700'
              }`}>
                {result.message}
              </p>
              
              {/* Show procedure history if available */}
              {result.data?.history && result.data.history.length > 0 && (
                <div className="mt-3">
                  <div className="text-sm font-medium text-primary-800 mb-2">
                    Procedures (Total Cost: ${result.data.totalCost || 'N/A'}):
                  </div>
                  <div className="space-y-2">
                    {result.data.history.map((procedure, index) => (
                      <div key={index} className="flex justify-between items-center text-sm bg-white p-2 rounded border">
                        <div>
                          <div className="font-medium">{procedure.procedure}</div>
                          <div className="text-gray-500 text-xs">
                            <Calendar className="w-3 h-3 inline mr-1" />
                            {new Date(procedure.time).toLocaleDateString()} at {new Date(procedure.time).toLocaleTimeString()}
                          </div>
                        </div>
                        <div className="font-semibold text-success-600">
                          ${procedure.cost}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-6 p-4 rounded-lg bg-error-50 border border-error-200 animate-fade-in">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-error-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-error-800">Error</h4>
              <p className="mt-1 text-sm text-error-700">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuickActions;
