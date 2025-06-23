import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, Link } from 'react-router-dom';
import { Plus, Download, Eye, Calendar, Zap, Crown, TrendingUp, Lightbulb, Sparkles, RefreshCw } from 'lucide-react';
import { toast } from 'react-toastify';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const { user, isAuthenticated, token } = useAuth();
  const [automations, setAutomations] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [taskDescription, setTaskDescription] = useState('');
  const [platform, setPlatform] = useState('Make.com');
  const [aiModel, setAiModel] = useState('gpt-4');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      fetchAutomations();
      fetchTemplates();
    }
  }, [isAuthenticated, token]);

  const fetchAutomations = async () => {
    try {
      const response = await fetch(`${API}/my-automations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAutomations(data);
      } else {
        toast.error('Failed to fetch automations');
      }
    } catch (error) {
      toast.error('Error loading automations');
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API}/templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const createAutomation = async (e) => {
    e.preventDefault();
    if (!taskDescription.trim()) {
      toast.error('Please describe what you want to automate');
      return;
    }

    setCreating(true);

    try {
      const response = await fetch(`${API}/generate-automation`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_description: taskDescription,
          platform: platform,
          ai_model: aiModel,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success('Automation created successfully!');
        setAutomations([data, ...automations]);
        setShowCreateForm(false);
        setTaskDescription('');
        // Also update localStorage for the output page
        localStorage.setItem('current_automation', JSON.stringify(data));
        window.open(`/automation/${data.id}`, '_blank');
      } else {
        toast.error(data.detail || 'Failed to create automation');
      }
    } catch (error) {
      toast.error('Error creating automation');
    } finally {
      setCreating(false);
    }
  };

  const useTemplate = async (templateName) => {
    setCreating(true);
    try {
      const response = await fetch(`${API}/generate-automation`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_description: `Use template: ${templateName}`,
          platform: platform,
          ai_model: aiModel,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success(`Template "${templateName}" added to your automations!`);
        setAutomations([data, ...automations]);
        setShowTemplates(false);
        localStorage.setItem('current_automation', JSON.stringify(data));
        window.open(`/automation/${data.id}`, '_blank');
      } else {
        toast.error(data.detail || 'Failed to use template');
      }
    } catch (error) {
      toast.error('Error using template');
    } finally {
      setCreating(false);
    }
  };

  const downloadJSON = (automation) => {
    if (!automation || !automation.automation_json) {
      toast.error('No automation data to download');
      return;
    }
    
    try {
      // Create a more explicit download process
      const jsonString = automation.automation_json;
      const blob = new Blob([jsonString], { 
        type: 'application/json;charset=utf-8' 
      });
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${automation.platform.toLowerCase().replace('.', '-')}-automation-${Date.now()}.json`;
      
      // Force download by appending to DOM and clicking
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Automation JSON downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      
      // Fallback: Open JSON in new window for manual save
      try {
        const jsonString = automation.automation_json;
        const newWindow = window.open();
        newWindow.document.write('<pre>' + jsonString + '</pre>');
        newWindow.document.close();
        toast.info('JSON opened in new window - save manually');
      } catch (fallbackError) {
        toast.error('Download failed. Please copy the JSON manually.');
      }
    }
  };

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  const usagePercentage = (user?.automations_used / user?.automations_limit) * 100;
  const canCreateMore = user?.automations_used < user?.automations_limit;

  const groupedTemplates = templates.reduce((acc, template) => {
    if (!acc[template.category]) {
      acc[template.category] = [];
    }
    acc[template.category].push(template);
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Welcome back, {user?.email}
            </p>
          </div>
          
          <div className="flex space-x-3 mt-4 md:mt-0">
            <Link
              to="/converter"
              className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-lg flex items-center space-x-2"
            >
              <RefreshCw className="h-5 w-5" />
              <span>Converter</span>
            </Link>
            
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg flex items-center space-x-2"
            >
              <Sparkles className="h-5 w-5" />
              <span>Templates</span>
            </button>
            
            {canCreateMore ? (
              <button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg flex items-center space-x-2"
              >
                <Plus className="h-5 w-5" />
                <span>Create Custom</span>
              </button>
            ) : (
              <Link
                to="/pricing"
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-2 px-4 rounded-lg flex items-center space-x-2"
              >
                <Crown className="h-5 w-5" />
                <span>Upgrade Plan</span>
              </Link>
            )}
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Zap className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Automations Created</p>
                <p className="text-2xl font-bold text-gray-900">{user?.automations_used || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Usage This Month</p>
                <p className="text-2xl font-bold text-gray-900">
                  {user?.automations_used}/{user?.automations_limit}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Crown className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Current Plan</p>
                <p className="text-2xl font-bold text-gray-900 capitalize">
                  {user?.subscription_tier || 'Free'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Usage Progress */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Monthly Usage</span>
            <span className="text-sm text-gray-500">
              {user?.automations_used}/{user?.automations_limit} automations
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                usagePercentage >= 80 ? 'bg-red-600' : usagePercentage >= 60 ? 'bg-yellow-600' : 'bg-blue-600'
              }`}
              style={{ width: `${Math.min(usagePercentage, 100)}%` }}
            ></div>
          </div>
          {usagePercentage >= 80 && (
            <p className="text-sm text-red-600 mt-2">
              You're running low on automations. <Link to="/pricing" className="underline">Consider upgrading</Link>.
            </p>
          )}
        </div>

        {/* Templates Library */}
        {showTemplates && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center">
                <Sparkles className="h-6 w-6 mr-2 text-purple-600" />
                Automation Templates
              </h2>
              <button
                onClick={() => setShowTemplates(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
              {Object.entries(groupedTemplates).map(([category, categoryTemplates]) => (
                <div key={category}>
                  <h3 className="font-semibold text-gray-900 mb-2">{category}</h3>
                  {categoryTemplates.map((template) => (
                    <div
                      key={template.id}
                      className="border border-gray-200 rounded-lg p-4 mb-3 hover:border-blue-500 transition-colors cursor-pointer"
                      onClick={() => useTemplate(template.name)}
                    >
                      <h4 className="font-medium text-blue-600 mb-1">{template.name}</h4>
                      <p className="text-sm text-gray-600">{template.description}</p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {template.tags.slice(0, 3).map((tag) => (
                          <span key={tag} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Create Automation Form */}
        {showCreateForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Create Custom Automation</h2>
            <form onSubmit={createAutomation} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What do you want to automate?
                </label>
                <textarea
                  value={taskDescription}
                  onChange={(e) => setTaskDescription(e.target.value)}
                  placeholder="Describe your automation task..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  rows={3}
                  required
                />
              </div>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Platform
                  </label>
                  <select
                    value={platform}
                    onChange={(e) => setPlatform(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="Make.com">Make.com</option>
                    <option value="n8n">n8n</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    AI Model
                  </label>
                  <select
                    value={aiModel}
                    onChange={(e) => setAiModel(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="gpt-4">GPT-4 (Best Overall)</option>
                    <option value="claude-3-5-sonnet-20241022">Claude 3.5 (Better Logic)</option>
                  </select>
                </div>
              </div>

              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={creating}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-2 px-4 rounded-lg flex items-center space-x-2"
                >
                  {creating ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <Zap className="h-4 w-4" />
                  )}
                  <span>{creating ? 'Creating...' : 'Generate Automation'}</span>
                </button>
                
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-700 font-bold py-2 px-4 rounded-lg"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Automations List */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Your Automations</h2>
          </div>

          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">Loading automations...</p>
            </div>
          ) : automations.length === 0 ? (
            <div className="p-8 text-center">
              <Zap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No automations yet</h3>
              <p className="text-gray-600 mb-4">Create your first automation to get started!</p>
              {canCreateMore && (
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg"
                >
                  Create First Automation
                </button>
              )}
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {automations.map((automation) => (
                <div key={automation.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-lg font-medium text-gray-900">
                          {automation.automation_summary}
                        </h3>
                        {automation.is_template && (
                          <span className="bg-purple-100 text-purple-800 text-xs font-medium px-2 py-1 rounded-full">
                            Template
                          </span>
                        )}
                      </div>
                      <p className="text-gray-600 text-sm mb-3">
                        "{automation.task_description}"
                      </p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center space-x-1">
                          <Calendar className="h-4 w-4" />
                          <span>{new Date(automation.created_at).toLocaleDateString()}</span>
                        </span>
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                          {automation.platform}
                        </span>
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                          {automation.ai_model === 'gpt-4' ? 'GPT-4' : 'Claude 3.5'}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => {
                          localStorage.setItem('current_automation', JSON.stringify(automation));
                          window.open(`/automation/${automation.id}`, '_blank');
                        }}
                        className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 px-3 py-1 rounded text-sm"
                      >
                        <Eye className="h-4 w-4" />
                        <span>View</span>
                      </button>
                      
                      <button
                        onClick={() => downloadJSON(automation)}
                        className="flex items-center space-x-1 text-green-600 hover:text-green-700 px-3 py-1 rounded text-sm"
                      >
                        <Download className="h-4 w-4" />
                        <span>JSON</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;