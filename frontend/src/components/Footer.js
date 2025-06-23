import React from 'react';
import { Link } from 'react-router-dom';
import { Zap, Heart, ExternalLink } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <Zap className="h-8 w-8 text-blue-400" />
              <span className="text-2xl font-bold">AutoFlow AI</span>
            </div>
            <p className="text-gray-300 mb-4 max-w-md">
              Transform any workflow into powerful automation with AI-generated templates for Make.com and n8n. 
              From idea to implementation in seconds.
            </p>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-400">Powered by:</span>
              <span className="text-sm text-blue-400">OpenAI GPT-4</span>
              <span className="text-sm text-purple-400">Anthropic Claude</span>
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Product</h3>
            <ul className="space-y-2">
              <li><Link to="/pricing" className="text-gray-300 hover:text-white transition-colors">Pricing</Link></li>
              <li><Link to="/dashboard" className="text-gray-300 hover:text-white transition-colors">Dashboard</Link></li>
              <li><Link to="/templates" className="text-gray-300 hover:text-white transition-colors">Templates</Link></li>
              <li><a href="https://make.com" target="_blank" rel="noopener noreferrer" className="text-gray-300 hover:text-white transition-colors flex items-center">
                Make.com <ExternalLink className="h-3 w-3 ml-1" />
              </a></li>
              <li><a href="https://n8n.io" target="_blank" rel="noopener noreferrer" className="text-gray-300 hover:text-white transition-colors flex items-center">
                n8n <ExternalLink className="h-3 w-3 ml-1" />
              </a></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Resources</h3>
            <ul className="space-y-2">
              <li><Link to="/about" className="text-gray-300 hover:text-white transition-colors">About</Link></li>
              <li><a href="https://docs.emergent.sh" target="_blank" rel="noopener noreferrer" className="text-gray-300 hover:text-white transition-colors flex items-center">
                Documentation <ExternalLink className="h-3 w-3 ml-1" />
              </a></li>
              <li><a href="https://emergent.sh" target="_blank" rel="noopener noreferrer" className="text-gray-300 hover:text-white transition-colors flex items-center">
                Emergent Platform <ExternalLink className="h-3 w-3 ml-1" />
              </a></li>
              <li><a href="mailto:support@emergent.sh" className="text-gray-300 hover:text-white transition-colors">Support</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="border-t border-gray-700 pt-8 mt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <span className="text-sm text-gray-400">© 2025 AutoFlow AI.</span>
              <span className="text-sm text-gray-400">Built with</span>
              <Heart className="h-4 w-4 text-red-500" />
              <span className="text-sm text-gray-400">on</span>
              <a href="https://emergent.sh" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 text-sm">
                Emergent.sh
              </a>
            </div>
            
            <div className="flex items-center space-x-6 text-sm text-gray-400">
              <span>Made possible by:</span>
              <div className="flex items-center space-x-4">
                <span className="bg-gray-800 px-3 py-1 rounded-full text-xs">React</span>
                <span className="bg-gray-800 px-3 py-1 rounded-full text-xs">FastAPI</span>
                <span className="bg-gray-800 px-3 py-1 rounded-full text-xs">MongoDB</span>
                <span className="bg-gray-800 px-3 py-1 rounded-full text-xs">Tailwind CSS</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;