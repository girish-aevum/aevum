import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FaUserCircle, 
  FaChartLine, 
  FaHeartbeat, 
  FaBell, 
  FaCog, 
  FaSignOutAlt,
  FaRunning,
  FaWeight,
  FaCalendarCheck,
  FaFlask, // DNA Profiling icon
  FaShieldAlt, // Subscription icon
  FaBrain,
  FaAppleAlt,
  FaMagic
} from 'react-icons/fa';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

import { authService } from '../apiClient';
import apiClient from '../apiClient';
import Navbar from '../components/Navbar';

// Skeleton Loading Component
const SkeletonLoader = ({ width, height }) => (
  <div 
    className="bg-gray-200 dark:bg-gray-700 animate-pulse" 
    style={{ width, height }}
  />
);

// Dashboard Card Component
const DashboardCard = ({ title, icon, children, className = '' }) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3 }}
    className={`
      bg-white/70 dark:bg-gray-800/70 
      backdrop-blur-lg 
      border border-gray-200 dark:border-gray-700 
      rounded-2xl 
      shadow-xl 
      p-6 
      ${className}
    `}
  >
    <div className="flex items-center mb-4">
      {icon}
      <h2 className="text-xl font-semibold ml-3 text-gray-800 dark:text-gray-200">
        {title}
      </h2>
    </div>
    {children}
  </motion.div>
);

function Dashboard() {
  const [user, setUser] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [subscriptionData, setSubscriptionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const [dnaKitOrders, setDNAKitOrders] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const currentUser = authService.getCurrentUser();
        console.log('Current User from localStorage:', currentUser);

        if (!currentUser) {
          navigate('/login');
          return;
        }

        // Fetch user profile
        const profileResponse = await apiClient.get('/authentication/profile/');
        console.log('Profile Response:', profileResponse.data);
        
        // Log specific user details
        console.log('User ID:', profileResponse.data.user.id);
        console.log('Username:', profileResponse.data.user.username);
        console.log('Email:', profileResponse.data.user.email);
        console.log('First Name:', profileResponse.data.user.first_name);
        console.log('Last Name:', profileResponse.data.user.last_name);

        setUser(profileResponse.data.user);

        // Fetch current subscription
        const subscriptionResponse = await apiClient.get('/authentication/subscription/my-subscription/');
        console.log('Subscription Response:', subscriptionResponse.data);
        setSubscriptionData(subscriptionResponse.data);

        // Fetch health data (mock data for now)
        const mockHealthData = {
          weightHistory: [
            { date: 'Jan', weight: 70 },
            { date: 'Feb', weight: 69.5 },
            { date: 'Mar', weight: 68.8 },
            { date: 'Apr', weight: 68.2 },
            { date: 'May', weight: 67.5 },
          ],
          activitySummary: {
            totalSteps: 45678,
            caloriesBurned: 2345,
            activeMinutes: 87
          },
          healthGoals: [
            { 
              title: 'Weight Loss', 
              progress: 65, 
              target: '70 kg', 
              current: '68.2 kg' 
            },
            { 
              title: 'Daily Steps', 
              progress: 80, 
              target: '10,000', 
              current: '8,000' 
            }
          ]
        };
        setHealthData(mockHealthData);

        // Fetch DNA Kit Orders
        const dnaOrdersResponse = await apiClient.get('/dna-profile/orders/');
        console.log('DNA Kit Orders:', dnaOrdersResponse.data);
        setDNAKitOrders(dnaOrdersResponse.data?.results || []);

        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch data', error.response || error);
        // If profile fetch fails, try to get user from current user
        const currentUser = authService.getCurrentUser();
        if (currentUser) {
          console.log('Falling back to localStorage user:', currentUser);
          setUser(currentUser);
        }
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  const handleLogout = () => {
    authService.logout();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <SkeletonLoader width="200px" height="50px" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-brand-primary/10 dark:from-gray-900 dark:via-gray-900 dark:to-brand-primary/20 flex flex-col">
      <Navbar />
      
      <main className="flex-grow container mx-auto px-4 py-12">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {/* Profile Overview */}
          <DashboardCard 
            title="Profile" 
            icon={<FaUserCircle className="text-brand-primary text-2xl" />}
          >
            <div className="space-y-3">
              <p className="text-gray-600 dark:text-gray-400">
                <strong>Name:</strong> {user.first_name} {user.last_name}
              </p>
              <p className="text-gray-600 dark:text-gray-400">
                <strong>Email:</strong> {user.email}
              </p>
              <button 
                onClick={() => navigate('/profile')}
                className="w-full mt-4 px-4 py-2 bg-brand-primary text-white rounded-lg hover:bg-brand-secondary transition-colors"
              >
                View Full Profile
              </button>
            </div>
          </DashboardCard>

          {/* Health Metrics */}
          <DashboardCard 
            title="Health Metrics" 
            icon={<FaHeartbeat className="text-brand-primary text-2xl" />}
          >
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={healthData.weightHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="weight" 
                  stroke="#8884d8" 
                  strokeWidth={2} 
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-3 gap-2 text-center">
              <div>
                <FaWeight className="mx-auto text-brand-primary" />
                <p className="text-sm">Weight</p>
                <p className="font-bold">{healthData.weightHistory[healthData.weightHistory.length - 1].weight} kg</p>
              </div>
              <div>
                <FaRunning className="mx-auto text-brand-primary" />
                <p className="text-sm">Steps</p>
                <p className="font-bold">{healthData.activitySummary.totalSteps}</p>
              </div>
              <div>
                <FaCalendarCheck className="mx-auto text-brand-primary" />
                <p className="text-sm">Active Min</p>
                <p className="font-bold">{healthData.activitySummary.activeMinutes}</p>
              </div>
            </div>
          </DashboardCard>

          {/* Subscription Details */}
          <DashboardCard 
            title="Subscription" 
            icon={<FaShieldAlt className="text-brand-primary text-2xl" />}
          >
            {subscriptionData ? (
              <div className="space-y-3">
                <div>
                  <p className="text-gray-600 dark:text-gray-400">
                    <strong>Current Plan:</strong> {subscriptionData.plan.name}
                  </p>
                  <p className="text-gray-600 dark:text-gray-400 flex items-center">
                    {/* <FaCalendarAlt className="mr-2 text-brand-primary" /> */}
                    <strong>Expiry Date:</strong> {new Date(subscriptionData.end_date).toLocaleDateString()}
                  </p>
                </div>
                <div className="mt-2">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {subscriptionData.status === 'ACTIVE' 
                      ? 'Your subscription is currently active' 
                      : 'Your subscription has expired'}
                  </p>
                </div>
                <button 
                  onClick={() => navigate('/subscription')}
                  className="w-full mt-4 px-4 py-2 bg-brand-primary text-white rounded-lg hover:bg-brand-secondary transition-colors"
                >
                  Manage Subscription
                </button>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-gray-600 dark:text-gray-400">
                  No active subscription found
                </p>
                <button 
                  onClick={() => navigate('/subscription')}
                  className="w-full mt-4 px-4 py-2 bg-brand-primary text-white rounded-lg hover:bg-brand-secondary transition-colors"
                >
                  View Plans
                </button>
              </div>
            )}
          </DashboardCard>

          {/* DNA Profiling Card */}
          <DashboardCard 
            title="DNA Profiling" 
            icon={<FaFlask className="text-brand-primary text-2xl" />}
          >
            <div className="space-y-3">
              <p className="text-gray-600 dark:text-gray-400">
                Unlock personalized health insights through genetic testing.
              </p>
              
              {dnaKitOrders.length > 0 ? (
                <div>
                  <h3 className="text-md font-semibold mb-2 text-gray-700 dark:text-gray-300">
                    Recent Orders
                  </h3>
                  {dnaKitOrders.slice(0, 2).map((order) => (
                    <div 
                      key={order.order_id} 
                      className="bg-gray-100 dark:bg-gray-700 rounded-lg p-3 mb-2"
                    >
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">
                          {order.kit_type_name || 'DNA Kit'}
                        </span>
                        <span 
                          className={`
                            px-2 py-1 rounded-full text-xs font-semibold 
                            ${order.status === 'COMPLETED' 
                              ? 'bg-green-100 text-green-800' 
                              : order.status === 'PROCESSING' 
                              ? 'bg-yellow-100 text-yellow-800' 
                              : 'bg-blue-100 text-blue-800'}
                          `}
                        >
                          {order.status}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Order ID: {order.order_id}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Ordered on: {new Date(order.order_date).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              ) : null}
              
              <button 
                onClick={() => navigate('/dna-profiling')}
                className="w-full mt-4 px-4 py-2 bg-brand-primary text-white rounded-lg hover:bg-brand-secondary transition-colors"
              >
                {dnaKitOrders.length > 0 ? 'View All Orders' : 'Order DNA Kit'}
              </button>
            </div>
          </DashboardCard>

          {/* Smart Journal Card */}
          <DashboardCard 
            title="Smart Journal" 
            icon={<FaChartLine className="text-brand-primary text-2xl" />}
          >
            <div className="space-y-3">
              <p className="text-gray-600 dark:text-gray-400">
                Track your health, habits, and progress with the Smart Journal.
              </p>
              <button 
                onClick={() => navigate('/smart-journal')}
                className="w-full mt-4 px-4 py-2 bg-brand-primary text-white rounded-lg hover:bg-brand-secondary transition-colors"
              >
                Go to Smart Journal
              </button>
            </div>
          </DashboardCard>
          {/* Mental Wellness Card */}
          <DashboardCard 
            title="Mental Wellness" 
            icon={<FaBrain className="text-pink-500 text-2xl" />}
          >
            <div className="space-y-3">
              <p className="text-gray-600 dark:text-gray-400">
                Tools and insights for your mental wellbeing.
              </p>
              <button 
                onClick={() => navigate('/mental-wellness')}
                className="w-full mt-4 px-4 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition-colors"
              >
                Go to Mental Wellness
              </button>
            </div>
          </DashboardCard>
          {/* Nutrition Card */}
          <DashboardCard 
            title="Nutrition" 
            icon={<FaAppleAlt className="text-green-500 text-2xl" />}
          >
            <div className="space-y-3">
              <p className="text-gray-600 dark:text-gray-400">
                Personalized nutrition tracking and advice.
              </p>
              <button 
                onClick={() => navigate('/nutrition')}
                className="w-full mt-4 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              >
                Go to Nutrition
              </button>
            </div>
          </DashboardCard>
          {/* AI Companion Card */}
          <DashboardCard 
            title="AI Companion" 
            icon={<FaMagic className="text-blue-500 text-2xl" />}
          >
            <div className="space-y-3">
              <p className="text-gray-600 dark:text-gray-400">
                Your personal AI assistant for health, wellness, and more.
              </p>
              <button 
                onClick={() => navigate('/ai-companion')}
                className="w-full mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Go to AI Companion
              </button>
            </div>
          </DashboardCard>
        </motion.div>

        {/* Quick Actions */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          {[
            { icon: <FaCog />, title: 'Settings', action: () => navigate('/settings') },
            { icon: <FaBell />, title: 'Notifications', action: () => navigate('/notifications') },
            { icon: <FaChartLine />, title: 'Reports', action: () => navigate('/reports') },
            { 
              icon: <FaSignOutAlt />, 
              title: 'Logout', 
              action: handleLogout,
              className: 'bg-red-500 text-white hover:bg-red-600' 
            }
          ].map((action) => (
            <motion.button
              key={action.title}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={action.action}
              className={`
                flex flex-col items-center justify-center 
                bg-white/70 dark:bg-gray-800/70 
                backdrop-blur-lg 
                border border-gray-200 dark:border-gray-700 
                rounded-2xl 
                shadow-xl 
                p-4 
                text-gray-700 dark:text-gray-300 
                hover:bg-gray-100 dark:hover:bg-gray-700 
                transition-all
                ${action.className || ''}
              `}
            >
              <span className="text-2xl mb-2 text-brand-primary">{action.icon}</span>
              <span className="text-sm font-medium">{action.title}</span>
            </motion.button>
          ))}
        </motion.div>
      </main>

      <footer className="bg-white/50 dark:bg-gray-900/50 py-6 text-center text-gray-600 dark:text-gray-400">
        <div className="max-w-7xl mx-auto px-6">
          <p>© {new Date().getFullYear()} Aevum Health. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default Dashboard; 