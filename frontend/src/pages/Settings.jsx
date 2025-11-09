import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../apiClient';
import Navbar from '../components/Navbar';
import { motion } from 'framer-motion';
import { 
  LockClosedIcon, 
  BellIcon, 
  EyeIcon, 
  EyeSlashIcon,
  ShieldCheckIcon 
} from '@heroicons/react/24/solid';

function Settings() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  
  // New state for notification preferences
  const [notificationPreferences, setNotificationPreferences] = useState({
    emailNotifications: false,
    smsNotifications: false
  });

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      navigate('/login');
      return;
    }
    setUser(currentUser);

    // TODO: Fetch actual notification preferences from backend
    // For now, we'll use localStorage to persist preferences
    const savedPreferences = JSON.parse(localStorage.getItem('notificationPreferences') || '{}');
    setNotificationPreferences({
      emailNotifications: savedPreferences.emailNotifications || false,
      smsNotifications: savedPreferences.smsNotifications || false
    });
  }, [navigate]);

  const handleNotificationToggle = (type) => {
    const updatedPreferences = {
      ...notificationPreferences,
      [type]: !notificationPreferences[type]
    };
    
    setNotificationPreferences(updatedPreferences);
    
    // Save to localStorage
    localStorage.setItem('notificationPreferences', JSON.stringify(updatedPreferences));
    
    // TODO: In a real app, send these preferences to backend
    console.log('Updated notification preferences:', updatedPreferences);
  };

  const handlePasswordInputChange = (e) => {
    const { name, value } = e.target;
    setPasswordForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    try {
      // TODO: Implement actual password change API call
      console.log('Password change submitted');
      setSuccessMessage('Password changed successfully');
      setIsChangingPassword(false);
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (error) {
      console.error('Password change failed', error);
      setError(error.message || 'Failed to change password');
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-brand-primary/10 dark:from-gray-900 dark:via-gray-900 dark:to-brand-primary/20 flex flex-col">
      <Navbar />
      
      <main className="flex-grow container mx-auto px-4 py-12">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl mx-auto bg-white dark:bg-gray-800 shadow-2xl rounded-2xl border border-gray-200 dark:border-gray-700 p-10"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-primary to-brand-secondary bg-clip-text text-transparent mb-8">
            Account Settings
          </h1>

          <div className="space-y-6">
            {/* Security Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <ShieldCheckIcon className="h-6 w-6 text-brand-primary" />
                  <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                    Security
                  </h2>
                </div>
                <button 
                  onClick={() => setIsChangingPassword(!isChangingPassword)}
                  className="px-4 py-2 bg-brand-primary/10 text-brand-primary rounded-lg hover:bg-brand-primary/20 transition-colors"
                >
                  {isChangingPassword ? 'Cancel' : 'Change Password'}
                </button>
              </div>

              {isChangingPassword && (
                <motion.form 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  transition={{ duration: 0.3 }}
                  onSubmit={handleChangePassword} 
                  className="space-y-4"
                >
                  {error && (
                    <div className="bg-red-50 dark:bg-red-900 text-red-500 p-3 rounded-xl text-sm">
                      {error}
                    </div>
                  )}
                  {successMessage && (
                    <div className="bg-green-50 dark:bg-green-900 text-green-500 p-3 rounded-xl text-sm">
                      {successMessage}
                    </div>
                  )}

                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <LockClosedIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="current_password"
                      name="current_password"
                      type={showPasswords.current ? "text" : "password"}
                      value={passwordForm.current_password}
                      onChange={handlePasswordInputChange}
                      placeholder="Current Password"
                      required
                      className="block w-full pl-10 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    />
                    <button
                      type="button"
                      onClick={() => togglePasswordVisibility('current')}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                    >
                      {showPasswords.current ? (
                        <EyeSlashIcon className="h-5 w-5" />
                      ) : (
                        <EyeIcon className="h-5 w-5" />
                      )}
                    </button>
                  </div>

                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <LockClosedIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="new_password"
                      name="new_password"
                      type={showPasswords.new ? "text" : "password"}
                      value={passwordForm.new_password}
                      onChange={handlePasswordInputChange}
                      placeholder="New Password"
                      required
                      className="block w-full pl-10 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    />
                    <button
                      type="button"
                      onClick={() => togglePasswordVisibility('new')}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                    >
                      {showPasswords.new ? (
                        <EyeSlashIcon className="h-5 w-5" />
                      ) : (
                        <EyeIcon className="h-5 w-5" />
                      )}
                    </button>
                  </div>

                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <LockClosedIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="confirm_password"
                      name="confirm_password"
                      type={showPasswords.confirm ? "text" : "password"}
                      value={passwordForm.confirm_password}
                      onChange={handlePasswordInputChange}
                      placeholder="Confirm New Password"
                      required
                      className="block w-full pl-10 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    />
                    <button
                      type="button"
                      onClick={() => togglePasswordVisibility('confirm')}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                    >
                      {showPasswords.confirm ? (
                        <EyeSlashIcon className="h-5 w-5" />
                      ) : (
                        <EyeIcon className="h-5 w-5" />
                      )}
                    </button>
                  </div>

                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-lg text-white bg-gradient-to-r from-brand-primary to-brand-secondary hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-primary"
                  >
                    Update Password
                  </motion.button>
                </motion.form>
              )}
            </div>

            {/* Notifications Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md">
              <div className="flex items-center space-x-3 mb-4">
                <BellIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Notifications
                </h2>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-700 dark:text-gray-300">
                    Email Notifications
                  </span>
                  <label className="flex items-center cursor-pointer">
                    <div className="relative">
                      <input 
                        type="checkbox" 
                        className="sr-only" 
                        checked={notificationPreferences.emailNotifications}
                        onChange={() => handleNotificationToggle('emailNotifications')}
                      />
                      <div className={`w-10 h-4 rounded-full shadow-inner transition-colors ${
                        notificationPreferences.emailNotifications 
                          ? 'bg-brand-primary' 
                          : 'bg-gray-400'
                      }`}></div>
                      <div className={`dot absolute -left-1 -top-1 bg-white w-6 h-6 rounded-full shadow -mt-1 -ml-1 transition transform ${
                        notificationPreferences.emailNotifications 
                          ? 'translate-x-full' 
                          : ''
                      }`}></div>
                    </div>
                  </label>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-700 dark:text-gray-300">
                    SMS Notifications
                  </span>
                  <label className="flex items-center cursor-pointer">
                    <div className="relative">
                      <input 
                        type="checkbox" 
                        className="sr-only" 
                        checked={notificationPreferences.smsNotifications}
                        onChange={() => handleNotificationToggle('smsNotifications')}
                      />
                      <div className={`w-10 h-4 rounded-full shadow-inner transition-colors ${
                        notificationPreferences.smsNotifications 
                          ? 'bg-brand-primary' 
                          : 'bg-gray-400'
                      }`}></div>
                      <div className={`dot absolute -left-1 -top-1 bg-white w-6 h-6 rounded-full shadow -mt-1 -ml-1 transition transform ${
                        notificationPreferences.smsNotifications 
                          ? 'translate-x-full' 
                          : ''
                      }`}></div>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>
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

export default Settings; 