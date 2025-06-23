import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { Check, Crown, Zap, Star, ArrowRight } from 'lucide-react';
import { toast } from 'react-toastify';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || 'pk_live_51Q5ggyHoMaNLQxI6VWVy1iTRmkCjFuHVCRKD15UjidVmz4FSxXYiLdlyN4ZhlA8rD4Ev8rCre7rcgCaMCsz5cfcM0071bToTrH');

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PricingPage = () => {
  const { user, isAuthenticated } = useAuth();
  const [loading, setLoading] = useState({});

  const handleUpgrade = async (tier) => {
    if (!isAuthenticated) {
      toast.info('Please sign up or log in to upgrade');
      return;
    }

    setLoading({ ...loading, [tier]: true });

    try {
      const response = await fetch(`${API}/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tier: tier,
          user_email: user.email,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        window.location.href = data.checkout_url;
      } else {
        toast.error(data.detail || 'Failed to create checkout session');
      }
    } catch (error) {
      toast.error('Error processing upgrade');
    } finally {
      setLoading({ ...loading, [tier]: false });
    }
  };

  const plans = [
    {
      name: 'Free',
      tier: 'free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for trying out AutoFlow AI',
      features: [
        '1 automation per month',
        'Make.com & n8n templates',
        'JSON download',
        'Basic setup instructions',
        'Community support'
      ],
      buttonText: 'Current Plan',
      buttonDisabled: true,
      popular: false,
      gradient: 'from-gray-400 to-gray-500'
    },
    {
      name: 'Pro',
      tier: 'pro',
      price: '$19',
      period: 'per month',
      description: 'Great for small businesses and entrepreneurs',
      features: [
        '10 automations per month',
        'Make.com & n8n templates',
        'JSON download',
        'Detailed setup guides',
        'Bonus content & templates', 
        'Priority email support',
        'Automation history'
      ],
      buttonText: 'Upgrade to Pro',
      buttonDisabled: false,
      popular: true,
      gradient: 'from-blue-500 to-purple-600'
    },
    {
      name: 'Creator',
      tier: 'creator',
      price: '$49',
      period: 'per month',
      description: 'Best for agencies and power users',
      features: [
        'Unlimited automations',
        'Make.com & n8n templates',
        'JSON download',
        'Advanced setup guides',
        'Premium bonus content',
        'Priority chat support',
        'Custom automation requests',
        'White-label options'
      ],
      buttonText: 'Upgrade to Creator',
      buttonDisabled: false,
      popular: false,
      gradient: 'from-purple-600 to-pink-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Choose Your <span className="text-blue-600">Automation</span> Plan
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            From trying out AutoFlow AI to scaling your business automation – we have the perfect plan for you.
          </p>
        </div>

        {/* Current Plan Indicator */}
        {isAuthenticated && (
          <div className="text-center mb-8">
            <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              <Crown className="h-4 w-4 mr-2" />
              Current Plan: {user?.subscription_tier?.charAt(0).toUpperCase() + user?.subscription_tier?.slice(1)}
            </div>
          </div>
        )}

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {plans.map((plan) => (
            <div
              key={plan.tier}
              className={`relative bg-white rounded-2xl shadow-lg overflow-hidden ${
                plan.popular ? 'ring-2 ring-blue-600 transform scale-105' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute top-0 left-0 right-0">
                  <div className={`bg-gradient-to-r ${plan.gradient} text-white text-center py-2 text-sm font-medium`}>
                    <div className="flex items-center justify-center space-x-1">
                      <Star className="h-4 w-4" />
                      <span>Most Popular</span>
                    </div>
                  </div>
                </div>
              )}

              <div className={`p-8 ${plan.popular ? 'pt-12' : ''}`}>
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <div className="mb-4">
                    <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                    <span className="text-gray-600 ml-1">/{plan.period}</span>
                  </div>
                  <p className="text-gray-600">{plan.description}</p>
                </div>

                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <Check className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleUpgrade(plan.tier)}
                  disabled={plan.buttonDisabled || loading[plan.tier] || (isAuthenticated && user?.subscription_tier === plan.tier)}
                  className={`w-full py-3 px-6 rounded-lg font-bold text-lg transition-all duration-200 ${
                    plan.buttonDisabled || (isAuthenticated && user?.subscription_tier === plan.tier)
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : plan.popular
                      ? `bg-gradient-to-r ${plan.gradient} text-white hover:shadow-lg transform hover:-translate-y-1`
                      : 'bg-gray-900 text-white hover:bg-gray-800 hover:shadow-lg transform hover:-translate-y-1'
                  }`}
                >
                  {loading[plan.tier] ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Processing...
                    </div>
                  ) : isAuthenticated && user?.subscription_tier === plan.tier ? (
                    'Current Plan'
                  ) : (
                    <div className="flex items-center justify-center space-x-2">
                      <span>{plan.buttonText}</span>
                      {!plan.buttonDisabled && <ArrowRight className="h-5 w-5" />}
                    </div>
                  )}
                </button>

                {!isAuthenticated && !plan.buttonDisabled && (
                  <p className="text-center text-sm text-gray-500 mt-3">
                    <Link to="/register" className="text-blue-600 hover:underline">
                      Sign up
                    </Link> to upgrade
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Frequently Asked Questions
          </h2>
          
          <div className="space-y-8">
            <div className="bg-white rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                What platforms do you support?
              </h3>
              <p className="text-gray-600">
                We currently support Make.com and n8n, the two most popular no-code automation platforms. 
                Each automation template includes valid JSON that you can directly import into your platform of choice.
              </p>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                How does the automation generation work?
              </h3>
              <p className="text-gray-600">
                Our AI (powered by GPT-4) analyzes your task description and generates a complete automation workflow, 
                including step-by-step instructions, required apps, and a working JSON template that you can import and use immediately.
              </p>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Can I cancel my subscription anytime?
              </h3>
              <p className="text-gray-600">
                Yes! You can cancel your subscription at any time. You'll continue to have access to your paid features 
                until the end of your billing period, and you can always downgrade to the free plan.
              </p>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Do you offer refunds?
              </h3>
              <p className="text-gray-600">
                We offer a 30-day money-back guarantee. If you're not satisfied with AutoFlow AI within the first 30 days, 
                contact our support team for a full refund.
              </p>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                What kind of automations can I create?
              </h3>
              <p className="text-gray-600">
                You can create automations for virtually any business process: email marketing, CRM updates, 
                social media posting, data processing, file management, e-commerce workflows, and much more. 
                If it can be automated, we can help you build it!
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center mt-16">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Start Automating?
            </h2>
            <p className="text-xl text-blue-100 mb-6">
              Join thousands of entrepreneurs who are saving time with AI-powered automation templates.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {!isAuthenticated ? (
                <>
                  <Link
                    to="/register"
                    className="bg-white text-blue-600 font-bold py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors inline-flex items-center justify-center space-x-2"
                  >
                    <span>Start Free Trial</span>
                    <ArrowRight className="h-5 w-5" />
                  </Link>
                  <Link
                    to="/"
                    className="bg-transparent border-2 border-white text-white font-bold py-3 px-8 rounded-lg hover:bg-white hover:text-blue-600 transition-colors"
                  >
                    Try Generator
                  </Link>
                </>
              ) : (
                <Link
                  to="/dashboard"
                  className="bg-white text-blue-600 font-bold py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors inline-flex items-center justify-center space-x-2"
                >
                  <Zap className="h-5 w-5" />
                  <span>Go to Dashboard</span>
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;