import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { ArrowRight, Zap, Clock, Download, Star } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LandingPage = () => {
  const [taskDescription, setTaskDescription] = useState('');
  const [platform, setPlatform] = useState('Make.com');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!taskDescription.trim()) {
      toast.error('Please describe what you want to automate');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API}/generate-automation-guest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_description: taskDescription,
          platform: platform,
          user_email: email || null,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store the automation data in localStorage for the output page
        localStorage.setItem('current_automation', JSON.stringify(data));
        navigate(`/automation/${data.id}`);
      } else {
        toast.error(data.detail || 'Failed to generate automation');
      }
    } catch (error) {
      toast.error('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="pt-20 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Turn Any Workflow into
              <span className="text-blue-600"> Automation</span> — Instantly
            </h1>
            <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
              Describe your task in plain English. We'll generate a ready-to-use automation template
              for Make.com or n8n, complete with setup instructions and JSON files.
            </p>

            {/* Automation Form */}
            <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-xl p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-left text-lg font-medium text-gray-700 mb-3">
                    What do you want to automate?
                  </label>
                  <textarea
                    value={taskDescription}
                    onChange={(e) => setTaskDescription(e.target.value)}
                    placeholder="Example: When someone fills out my contact form, send them a welcome email and add them to my CRM..."
                    className="w-full p-4 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none min-h-[120px] text-gray-800"
                    required
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-left text-lg font-medium text-gray-700 mb-3">
                      Choose Platform
                    </label>
                    <select
                      value={platform}
                      onChange={(e) => setPlatform(e.target.value)}
                      className="w-full p-4 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none text-gray-800"
                    >
                      <option value="Make.com">Make.com</option>
                      <option value="n8n">n8n</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-left text-lg font-medium text-gray-700 mb-3">
                      Email (optional)
                    </label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your@email.com"
                      className="w-full p-4 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none text-gray-800"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-4 px-8 rounded-lg text-xl transition-colors flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <span>Generate My Automation</span>
                      <ArrowRight className="h-6 w-6" />
                    </>
                  )}
                </button>
              </form>

              <p className="text-sm text-gray-500 mt-4">
                Free tier: 1 automation • 
                <a href="/register" className="text-blue-600 hover:underline ml-1">Sign up</a> for more
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything You Need to Automate
            </h2>
            <p className="text-xl text-gray-600">
              From idea to working automation in seconds
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Instant Generation</h3>
              <p className="text-gray-600">
                Powered by GPT-4, get working automation templates in seconds, not hours.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Download className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Ready-to-Import JSON</h3>
              <p className="text-gray-600">
                Get valid JSON files that you can directly import into Make.com or n8n.
              </p>
            </div>

            <div className="text-center p-6">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Clock className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Step-by-Step Guides</h3>
              <p className="text-gray-600">
                Beginner-friendly instructions to set up your automation, even if you're new to no-code.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Social Proof */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">
            Trusted by Automation Enthusiasts
          </h2>
          <div className="flex justify-center items-center space-x-2 mb-8">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="h-6 w-6 text-yellow-400 fill-current" />
            ))}
            <span className="ml-2 text-gray-600 text-lg">4.9/5 from 500+ automations created</span>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <p className="text-gray-600 mb-4 italic">
                "AutoFlow AI saved me hours of setup time. The generated Make.com template worked perfectly for my e-commerce order processing!"
              </p>
              <p className="font-semibold">Sarah K., E-commerce Owner</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <p className="text-gray-600 mb-4 italic">
                "As a non-technical founder, this tool is a game-changer. I can now automate complex workflows without hiring a developer."
              </p>
              <p className="font-semibold">Mike R., SaaS Founder</p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-16 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Automate Your First Workflow?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of entrepreneurs saving time with AI-powered automation templates.
          </p>
          <a
            href="#form"
            className="bg-white text-blue-600 font-bold py-3 px-8 rounded-lg text-lg hover:bg-gray-100 transition-colors inline-flex items-center space-x-2"
          >
            <span>Get Started Free</span>
            <ArrowRight className="h-5 w-5" />
          </a>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;