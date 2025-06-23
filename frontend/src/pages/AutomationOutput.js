import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Download, Copy, ExternalLink, ArrowLeft, CheckCircle } from 'lucide-react';
import { toast } from 'react-toastify';

const AutomationOutput = () => {
  const { id } = useParams();
  const [automation, setAutomation] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Get automation data from localStorage (for guest users)
    const storedAutomation = localStorage.getItem('current_automation');
    if (storedAutomation) {
      const automationData = JSON.parse(storedAutomation);
      if (automationData.id === id) {
        setAutomation(automationData);
      }
    }
  }, [id]);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('JSON copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadJSON = () => {
    if (!automation) return;
    
    const element = document.createElement('a');
    const file = new Blob([automation.automation_json], { type: 'application/json' });
    element.href = URL.createObjectURL(file);
    element.download = `${automation.platform.toLowerCase()}-automation-${Date.now()}.json`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    toast.success('JSON file downloaded!');
  };

  if (!automation) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading automation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Link
            to="/"
            className="flex items-center space-x-2 text-blue-600 hover:text-blue-700"
          >
            <ArrowLeft className="h-5 w-5" />
            <span>Back to Generator</span>
          </Link>
          
          <div className="flex items-center space-x-2 text-green-600">
            <CheckCircle className="h-6 w-6" />
            <span className="font-semibold">Automation Generated!</span>
          </div>
        </div>

        {/* Summary Card */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                🚀 Your Automation is Ready!
              </h1>
              <p className="text-lg text-gray-600 mb-4">
                {automation.automation_summary}
              </p>
              <div className="flex items-center space-x-4">
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  Platform: {automation.platform}
                </span>
                <span className="text-sm text-gray-500">
                  Generated on {new Date(automation.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          {/* Task Description */}
          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <h3 className="font-semibold text-gray-900 mb-2">Original Request:</h3>
            <p className="text-gray-700 italic">"{automation.task_description}"</p>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column */}
          <div className="space-y-8">
            {/* Required Tools */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                🧰 Required Apps & Tools
              </h2>
              <ul className="space-y-3">
                {automation.required_tools.map((tool, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-700">{tool}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Workflow Steps */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                📊 Automation Workflow Steps
              </h2>
              <ol className="space-y-4">
                {automation.workflow_steps.map((step, index) => (
                  <li key={index} className="flex items-start space-x-4">
                    <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </span>
                    <span className="text-gray-700 pt-1">{step.replace(/^\d+\.\s*/, '')}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* JSON Template */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                  🧠 JSON Automation Template
                </h2>
                <div className="flex space-x-2">
                  <button
                    onClick={() => copyToClipboard(automation.automation_json)}
                    className="flex items-center space-x-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg text-sm transition-colors"
                  >
                    <Copy className="h-4 w-4" />
                    <span>{copied ? 'Copied!' : 'Copy'}</span>
                  </button>
                  <button
                    onClick={downloadJSON}
                    className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-sm transition-colors"
                  >
                    <Download className="h-4 w-4" />
                    <span>Download</span>
                  </button>
                </div>
              </div>
              <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                <pre className="text-green-400 text-sm whitespace-pre-wrap font-mono">
                  {automation.automation_json}
                </pre>
              </div>
            </div>

            {/* Setup Instructions */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                📋 Setup Instructions
              </h2>
              <div className="prose prose-sm max-w-none">
                <div className="whitespace-pre-wrap text-gray-700">
                  {automation.setup_instructions}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bonus Content */}
        {automation.bonus_content && (
          <div className="bg-white rounded-lg shadow-md p-6 mt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
              🎁 Bonus Assets
            </h2>
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-gray-700">
                {automation.bonus_content}
              </div>
            </div>
          </div>
        )}

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-8 mt-8 text-center text-white">
          <h2 className="text-2xl font-bold mb-4">Need More Automations?</h2>
          <p className="text-blue-100 mb-6">
            Upgrade to Pro for 10 automations per month or Creator for unlimited access.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="bg-white text-blue-600 font-bold py-3 px-6 rounded-lg hover:bg-gray-100 transition-colors"
            >
              Sign Up for More
            </Link>
            <Link
              to="/pricing"
              className="bg-transparent border-2 border-white text-white font-bold py-3 px-6 rounded-lg hover:bg-white hover:text-blue-600 transition-colors"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomationOutput;