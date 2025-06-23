import React from 'react';
import { ArrowRight, Zap, Users, Target, Award, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

const About = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            About <span className="text-blue-600">AutoFlow AI</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Democratizing automation by making no-code workflow creation accessible to everyone, 
            powered by cutting-edge AI technology.
          </p>
        </div>
      </div>

      {/* Mission Section */}
      <div className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Mission</h2>
              <p className="text-lg text-gray-600 mb-6">
                We believe automation should be accessible to everyone, not just developers. 
                AutoFlow AI bridges the gap between complex automation platforms and everyday users 
                by generating ready-to-use workflows from simple English descriptions.
              </p>
              <p className="text-lg text-gray-600 mb-6">
                Whether you're a small business owner, entrepreneur, or automation enthusiast, 
                our AI-powered platform helps you save time and increase productivity without 
                requiring technical expertise.
              </p>
              <Link
                to="/"
                className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
              >
                <span>Try AutoFlow AI</span>
                <ArrowRight className="h-5 w-5" />
              </Link>
            </div>
            
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-blue-50 p-6 rounded-xl text-center">
                <Target className="h-12 w-12 text-blue-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Precision</h3>
                <p className="text-sm text-gray-600">AI-generated automations that work exactly as intended</p>
              </div>
              
              <div className="bg-green-50 p-6 rounded-xl text-center">
                <Zap className="h-12 w-12 text-green-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Speed</h3>
                <p className="text-sm text-gray-600">From idea to working automation in seconds</p>
              </div>
              
              <div className="bg-purple-50 p-6 rounded-xl text-center">
                <Users className="h-12 w-12 text-purple-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Accessibility</h3>
                <p className="text-sm text-gray-600">No coding required - plain English is enough</p>
              </div>
              
              <div className="bg-yellow-50 p-6 rounded-xl text-center">
                <Award className="h-12 w-12 text-yellow-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Quality</h3>
                <p className="text-sm text-gray-600">Production-ready templates with detailed guides</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Technology Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Powered by Advanced AI</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              AutoFlow AI leverages the latest in artificial intelligence to understand your automation needs 
              and generate perfect workflows for leading no-code platforms.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <span className="text-xl font-bold text-green-600">GPT</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">OpenAI GPT-4</h3>
              <p className="text-gray-600 mb-4">
                Best overall automation generation with comprehensive understanding 
                of business processes and workflow logic.
              </p>
              <a href="https://openai.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-700 inline-flex items-center">
                Learn more <ExternalLink className="h-4 w-4 ml-1" />
              </a>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="bg-orange-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <span className="text-xl font-bold text-orange-600">AI</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Anthropic Claude 3.5</h3>
              <p className="text-gray-600 mb-4">
                Superior logical reasoning for complex automation flows with 
                advanced conditional logic and decision trees.
              </p>
              <a href="https://anthropic.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-700 inline-flex items-center">
                Learn more <ExternalLink className="h-4 w-4 ml-1" />
              </a>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Smart Selection</h3>
              <p className="text-gray-600 mb-4">
                Our platform intelligently chooses the best AI model for your specific 
                automation type to ensure optimal results.
              </p>
              <Link to="/pricing" className="text-blue-600 hover:text-blue-700 inline-flex items-center">
                Get started <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Platform Support */}
      <div className="py-16 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Platform Support</h2>
            <p className="text-xl text-gray-600">
              Generate automations for the most popular no-code automation platforms
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-8 rounded-xl text-center">
              <div className="bg-white w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4 shadow-md">
                <span className="text-2xl font-bold text-purple-600">M</span>
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-3">Make.com</h3>
              <p className="text-gray-600 mb-4">
                Enterprise-grade automation platform with 1000+ integrations. 
                Perfect for complex workflows and business processes.
              </p>
              <a href="https://make.com" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:text-purple-700 inline-flex items-center font-medium">
                Visit Make.com <ExternalLink className="h-4 w-4 ml-1" />
              </a>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-teal-50 p-8 rounded-xl text-center">
              <div className="bg-white w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4 shadow-md">
                <span className="text-2xl font-bold text-green-600">n8n</span>
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-3">n8n</h3>
              <p className="text-gray-600 mb-4">
                Open-source workflow automation tool with full control and customization. 
                Ideal for developers and advanced users.
              </p>
              <a href="https://n8n.io" target="_blank" rel="noopener noreferrer" className="text-green-600 hover:text-green-700 inline-flex items-center font-medium">
                Visit n8n.io <ExternalLink className="h-4 w-4 ml-1" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Credits */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Built with Excellence</h2>
          
          <div className="bg-white rounded-xl p-8 shadow-lg">
            <p className="text-lg text-gray-600 mb-6">
              AutoFlow AI was crafted with cutting-edge technology and deployed on the 
              <a href="https://emergent.sh" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-700 font-medium mx-1">
                Emergent.sh platform
              </a>
              - the fastest way to build, deploy, and scale AI-powered applications.
            </p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900">Frontend</h4>
                <p className="text-sm text-blue-700">React 19 + Tailwind CSS</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-900">Backend</h4>
                <p className="text-sm text-green-700">FastAPI + Python</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-semibold text-purple-900">Database</h4>
                <p className="text-sm text-purple-700">MongoDB</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="font-semibold text-orange-900">Payments</h4>
                <p className="text-sm text-orange-700">Stripe</p>
              </div>
            </div>

            <div className="border-t pt-6">
              <p className="text-sm text-gray-500">
                Deployed and powered by{' '}
                <a href="https://emergent.sh" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-700 font-medium">
                  Emergent.sh
                </a>
                {' '}- The AI-First Development Platform
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="py-16 bg-blue-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Automate Your Workflows?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of users who are saving time with AI-powered automation templates.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/"
              className="bg-white text-blue-600 font-bold py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors inline-flex items-center justify-center space-x-2"
            >
              <span>Start Automating</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              to="/pricing"
              className="bg-transparent border-2 border-white text-white font-bold py-3 px-8 rounded-lg hover:bg-white hover:text-blue-600 transition-colors"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;