import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, Link } from 'react-router-dom';
import { RefreshCw, Upload, Download, Copy, ArrowRight, Crown, Zap, AlertCircle } from 'lucide-react';
import { toast } from 'react-toastify';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BlueprintConverter = () => {
  const { user, isAuthenticated, token } = useAuth();
  const [sourcePlatform, setSourcePlatform] = useState('Make.com');
  const [targetPlatform, setTargetPlatform] = useState('n8n');
  const [aiModel, setAiModel] = useState('gpt-4');
  const [blueprintJson, setBlueprintJson] = useState('');
  const [converting, setConverting] = useState(false);
  const [conversionResult, setConversionResult] = useState(null);
  const [conversions, setConversions] = useState([]);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      fetchConversions();
    }
  }, [isAuthenticated, token]);

  const fetchConversions = async () => {
    try {
      const response = await fetch(`${API}/my-conversions`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setConversions(data);
      }
    } catch (error) {
      console.error('Error fetching conversions:', error);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const jsonContent = e.target.result;
          JSON.parse(jsonContent); // Validate JSON
          setBlueprintJson(jsonContent);
          toast.success('Blueprint uploaded successfully!');
        } catch (error) {
          toast.error('Invalid JSON file. Please upload a valid blueprint.');
        }
      };
      reader.readAsText(file);
    }
  };

  const handleConvert = async () => {
    if (!blueprintJson.trim()) {
      toast.error('Please upload or paste a blueprint first');
      return;
    }

    if (sourcePlatform === targetPlatform) {
      toast.error('Source and target platforms must be different');
      return;
    }

    setConverting(true);

    try {
      const response = await fetch(`${API}/convert-blueprint`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          blueprint_json: blueprintJson,
          source_platform: sourcePlatform,
          target_platform: targetPlatform,
          ai_model: aiModel,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setConversionResult(data);
        toast.success('Blueprint converted successfully!');
        fetchConversions(); // Refresh conversion history
      } else {
        toast.error(data.detail || 'Failed to convert blueprint');
      }
    } catch (error) {
      toast.error('Error converting blueprint');
    } finally {
      setConverting(false);
    }
  };

  const copyToClipboard = (text) => {
    // Fallback for when Clipboard API is blocked
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
      const result = document.execCommand('copy');
      if (result) {
        setCopied(true);
        toast.success('JSON copied to clipboard!');
        setTimeout(() => setCopied(false), 2000);
      } else {
        throw new Error('Copy command failed');
      }
    } catch (err) {
      console.error('Fallback copy failed:', err);
      toast.error('Please manually select and copy the JSON below');
    } finally {
      document.body.removeChild(textArea);
    }
  };

  const downloadJSON = (jsonContent, filename) => {
    if (!jsonContent) {
      toast.error('No JSON content to download');
      return;
    }
    
    try {
      // Create a more explicit download process
      const blob = new Blob([jsonContent], { 
        type: 'application/json;charset=utf-8' 
      });
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || `blueprint-${Date.now()}.json`;
      
      // Force download by appending to DOM and clicking
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Blueprint JSON downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      
      // Fallback: Open JSON in new window for manual save
      try {
        const newWindow = window.open();
        newWindow.document.write('<pre>' + jsonContent + '</pre>');
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

  // Check if user has Pro or Creator access
  const hasProAccess = user?.subscription_tier === 'pro' || user?.subscription_tier === 'creator';

  if (!hasProAccess) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <Crown className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Blueprint Converter
            </h1>
            <p className="text-xl text-gray-600 mb-6">
              Convert blueprints between Make.com and n8n formats
            </p>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
              <div className="flex items-center justify-center mb-4">
                <AlertCircle className="h-8 w-8 text-yellow-600 mr-2" />
                <h3 className="text-lg font-semibold text-yellow-800">Pro Feature</h3>
              </div>
              <p className="text-yellow-700 mb-4">
                Blueprint conversion is available for Pro and Creator subscribers only.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/pricing"
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors inline-flex items-center justify-center space-x-2"
              >
                <Crown className="h-5 w-5" />
                <span>Upgrade to Pro</span>
              </Link>
              <Link
                to="/dashboard"
                className="bg-gray-300 hover:bg-gray-400 text-gray-700 font-bold py-3 px-6 rounded-lg transition-colors"
              >
                Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            <RefreshCw className="inline h-8 w-8 mr-2 text-blue-600" />
            Blueprint Converter
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Convert automation blueprints between Make.com and n8n formats using AI.
            Upload your blueprint and get a perfectly converted version for your target platform.
          </p>
        </div>

        {/* Converter Form */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Convert Blueprint</h2>
          
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source Platform
              </label>
              <select
                value={sourcePlatform}
                onChange={(e) => setSourcePlatform(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Make.com">Make.com</option>
                <option value="n8n">n8n</option>
              </select>
            </div>

            <div className="flex items-center justify-center">
              <ArrowRight className="h-6 w-6 text-gray-400" />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Platform
              </label>
              <select
                value={targetPlatform}
                onChange={(e) => setTargetPlatform(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Make.com">Make.com</option>
                <option value="n8n">n8n</option>
              </select>
            </div>
          </div>

          <div className="mb-6">
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

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Blueprint File
            </label>
            <input
              type="file"
              accept=".json"
              onChange={handleFileUpload}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Or Paste Blueprint JSON
            </label>
            <textarea
              value={blueprintJson}
              onChange={(e) => setBlueprintJson(e.target.value)}
              placeholder="Paste your Make.com or n8n blueprint JSON here..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 min-h-[200px] font-mono text-sm"
            />
          </div>

          <button
            onClick={handleConvert}
            disabled={converting || !blueprintJson.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-3 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            {converting ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <RefreshCw className="h-5 w-5" />
            )}
            <span>{converting ? 'Converting...' : 'Convert Blueprint'}</span>
          </button>
        </div>

        {/* Conversion Result */}
        {conversionResult && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Conversion Result</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              {/* Converted JSON */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Converted {conversionResult.target_platform} Blueprint
                  </h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => copyToClipboard(conversionResult.converted_json)}
                      className="flex items-center space-x-1 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded text-sm"
                    >
                      <Copy className="h-4 w-4" />
                      <span>{copied ? 'Copied!' : 'Copy'}</span>
                    </button>
                    <button
                      onClick={() => downloadJSON(
                        conversionResult.converted_json,
                        `converted-${conversionResult.target_platform.toLowerCase().replace('.', '-')}-${Date.now()}.json`
                      )}
                      className="flex items-center space-x-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
                    >
                      <Download className="h-4 w-4" />
                      <span>Download</span>
                    </button>
                  </div>
                </div>
                <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto max-h-96">
                  <pre className="text-green-400 text-sm whitespace-pre-wrap font-mono">
                    {conversionResult.converted_json}
                  </pre>
                </div>
              </div>

              {/* Conversion Notes */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Notes</h3>
                <div className="bg-blue-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <div className="text-sm text-gray-700 whitespace-pre-wrap">
                    {conversionResult.conversion_notes}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Conversion History */}
        {conversions.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Conversion History</h2>
            <div className="space-y-4">
              {conversions.slice(0, 5).map((conversion) => (
                <div key={conversion.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-gray-900">
                        {conversion.source_platform} → {conversion.target_platform}
                      </span>
                      <span className="ml-2 text-xs text-gray-500">
                        {new Date(conversion.created_at).toLocaleDateString()}
                      </span>
                      <span className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                        {conversion.ai_model === 'gpt-4' ? 'GPT-4' : 'Claude 3.5'}
                      </span>
                    </div>
                    <button
                      onClick={() => downloadJSON(
                        conversion.converted_json,
                        `conversion-${conversion.target_platform.toLowerCase().replace('.', '-')}-${conversion.id}.json`
                      )}
                      className="text-blue-600 hover:text-blue-700 text-sm"
                    >
                      Download
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BlueprintConverter;