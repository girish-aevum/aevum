import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Navbar from '../components/Navbar';
import BackButton from '../components/BackButton';
import apiClient from '../apiClient';
import { 
  CheckIcon, 
  CreditCardIcon, 
  StarIcon,
  DocumentTextIcon,
  CalendarIcon
} from '../utils/icons';

const SubscriptionPlan = ({ plan, currentPlan, onSelect }) => {
  const isCurrentPlan = currentPlan && currentPlan.plan.id === plan.id;
  
  // Helper function to parse features
  const parseFeatures = (features) => {
    // Log the raw features for debugging
    console.log('Raw Features:', features);
    console.log('Features Type:', typeof features);

    // If features is already an array, return it
    if (Array.isArray(features)) return features;
    
    // If features is a string, try to split
    if (typeof features === 'string') {
      return features.split(',').map(feature => feature.trim()).filter(Boolean);
    }
    
    // If features is an object or unexpected type, convert to array or return empty array
    return features ? [features.toString()] : [];
  };

  // Parse features
  const planFeatures = parseFeatures(plan.features);
  
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className={`
        bg-white dark:bg-gray-800 
        rounded-2xl 
        shadow-xl 
        p-6 
        h-full
        flex 
        flex-col
        border 
        ${isCurrentPlan 
          ? 'border-brand-primary' 
          : 'border-gray-200 dark:border-gray-700'}
      `}
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          {plan.name}
        </h3>
        {isCurrentPlan && (
          <span className="bg-brand-primary text-white px-3 py-1 rounded-full text-xs">
            Current Plan
          </span>
        )}
      </div>
      
      <div className="mb-4">
        <p className="text-4xl font-bold text-brand-primary">
          ₹{plan.price}
          <span className="text-sm text-gray-500 dark:text-gray-400 ml-1">
            / {plan.billing_cycle || 'Monthly'}
          </span>
        </p>
        <p className="text-gray-600 dark:text-gray-400 mt-2 flex-grow">
          {plan.description}
        </p>
      </div>
      
      <ul className="space-y-3 mb-6 flex-grow">
        {planFeatures.map((feature, index) => (
          <li 
            key={index} 
            className="flex items-center text-gray-700 dark:text-gray-300"
          >
            <CheckIcon className="h-5 w-5 text-green-500 mr-2" />
            {feature}
          </li>
        ))}
      </ul>
      
      {!isCurrentPlan && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onSelect(plan)}
          className="w-full bg-brand-primary text-white py-3 rounded-xl hover:bg-brand-secondary transition-colors mt-auto"
        >
          {currentPlan ? 'Upgrade' : 'Select Plan'}
        </motion.button>
      )}
    </motion.div>
  );
};

function Subscription() {
  const [plans, setPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [subscriptionHistory, setSubscriptionHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSubscriptionData = async () => {
      try {
        // Fetch subscription plans from public endpoint
        const plansResponse = await apiClient.get('/authentication/subscription/plans/');
        console.log('Subscription Plans:', plansResponse.data);
        
        // Ensure plans is an array
        const fetchedPlans = Array.isArray(plansResponse.data) 
          ? plansResponse.data 
          : (plansResponse.data.results || []);
        
        setPlans(fetchedPlans);

        // Fetch current user's subscription
        const currentSubscriptionResponse = await apiClient.get('/authentication/subscription/my-subscription/');
        setCurrentPlan(currentSubscriptionResponse.data);

        // Fetch subscription history
        const historyResponse = await apiClient.get('/authentication/subscription/history/');
        setSubscriptionHistory(historyResponse.data.results || []);

        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch subscription data', err);
        setError(err.response?.data?.error || 'Failed to load subscription information');
        setPlans([]);
        setLoading(false);
      }
    };

    fetchSubscriptionData();
  }, []);

  const handlePlanSelect = async (selectedPlan) => {
    try {
      // Confirm plan upgrade/selection
      const confirmUpgrade = window.confirm(
        `Are you sure you want to ${currentPlan ? 'upgrade to' : 'select'} the ${selectedPlan.name} plan?`
      );

      if (confirmUpgrade) {
        const response = await apiClient.post('/authentication/subscription/upgrade/', {
          plan_id: selectedPlan.id,
          payment_method: 'ONLINE' // Default payment method
        });

        // Update current plan
        setCurrentPlan(response.data.subscription);
        
        // Show success message
        alert(`Successfully ${currentPlan ? 'upgraded to' : 'selected'} ${selectedPlan.name} plan`);
      }
    } catch (err) {
      console.error('Failed to select/upgrade plan', err);
      alert(err.response?.data?.error || 'Failed to process subscription');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1 }}
          className="w-16 h-16 border-4 border-brand-primary border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-brand-primary/10 dark:from-gray-900 dark:via-gray-900 dark:to-brand-primary/20 flex flex-col">
      <Navbar />
      
      <main className="flex-grow container mx-auto px-4 py-12">
        {/* Back Button */}
        <div className="mb-8">
          <BackButton 
            destination="/dashboard" 
            label="Back to Dashboard" 
          />
        </div>

        {/* Subscription Plans Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-primary to-brand-secondary bg-clip-text text-transparent">
            Subscription Plans
          </h1>
          <p className="mt-4 text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Choose the plan that best fits your wellness journey. Upgrade, downgrade, or cancel anytime.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 text-red-800 dark:text-red-200 px-4 py-3 rounded-xl mb-6 text-center">
            {error}
          </div>
        )}

        <div className="w-full overflow-hidden px-4 md:px-8 lg:px-12">
          <motion.div 
            drag="x"
            dragConstraints={{ left: -((plans.length - 1) * 320), right: 0 }}
            dragElastic={0.3}
            className="flex space-x-6 cursor-grab active:cursor-grabbing"
          >
            {plans.map((plan, index) => (
              <motion.div 
                key={plan.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ 
                  opacity: 1, 
                  scale: 1,
                  transition: { 
                    delay: index * 0.1,
                    type: "spring",
                    stiffness: 300,
                    damping: 20
                  }
                }}
                whileHover={{ 
                  scale: 1.05,
                  transition: { type: "spring", stiffness: 300 }
                }}
                whileDrag={{ scale: 0.95 }}
                className="flex-shrink-0 w-72 md:w-80 lg:w-96"
              >
                <SubscriptionPlan 
                  plan={plan} 
                  currentPlan={currentPlan} 
                  onSelect={handlePlanSelect} 
                />
              </motion.div>
            ))}
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: plans.length > 3 ? 1 : 0 }}
            className="mt-4 flex justify-center items-center space-x-2"
          >
            {plans.map((_, index) => (
              <motion.div
                key={index}
                className="w-2 h-2 rounded-full bg-gray-300 dark:bg-gray-600"
                animate={{
                  scale: index === 0 ? 1.5 : 1,
                  backgroundColor: index === 0 
                    ? 'rgb(59, 130, 246)' 
                    : 'rgb(209, 213, 219)' 
                }}
              />
            ))}
          </motion.div>
        </div>

        {plans.length === 0 && !loading && (
          <div className="text-center mt-12">
            <p className="text-gray-600 dark:text-gray-400 text-xl">
              No subscription plans are currently available.
            </p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-brand-primary text-white rounded-lg"
            >
              Retry
            </button>
          </div>
        )}

        {/* Current Subscription Section */}
        {currentPlan && (
          <div className="mt-12 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Your Current Subscription
            </h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xl font-semibold text-brand-primary">
                  {currentPlan.plan.name}
                </p>
                <p className="text-gray-600 dark:text-gray-400">
                  Renews on {new Date(currentPlan.end_date).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <CreditCardIcon className="h-8 w-8 text-brand-primary" />
                <StarIcon className="h-8 w-8 text-yellow-500" />
              </div>
            </div>
          </div>
        )}

        {/* Subscription History Section */}
        <div className="mt-12 max-w-4xl mx-auto">
          <div className="flex items-center space-x-3 mb-6">
            <DocumentTextIcon className="h-8 w-8 text-brand-primary" />
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              Subscription History
            </h2>
          </div>

          {subscriptionHistory.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 text-center">
              <p className="text-gray-600 dark:text-gray-400">
                No subscription history available.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {subscriptionHistory.map((historyItem, index) => (
                <motion.div
                  key={historyItem.id || index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ 
                    opacity: 1, 
                    y: 0,
                    transition: { 
                      delay: index * 0.1,
                      type: "spring",
                      stiffness: 300,
                      damping: 20
                    }
                  }}
                  className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 flex items-center justify-between"
                >
                  <div>
                    <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      {historyItem.action_type} - {historyItem.new_plan?.name || 'Plan Change'}
                    </p>
                    <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 mt-2">
                      <CalendarIcon className="h-5 w-5" />
                      <p className="text-sm">
                        {new Date(historyItem.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-brand-primary font-bold">
                      {historyItem.amount ? `₹${historyItem.amount}` : 'N/A'}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {historyItem.notes || 'No additional details'}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default Subscription; 