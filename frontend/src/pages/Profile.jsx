import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../apiClient';
import Navbar from '../components/Navbar';
import BackButton from '../components/BackButton';
import { motion } from 'framer-motion';
import { 
  EnvelopeIcon, 
  PhoneIcon,
  UserIcon,
  ShieldCheckIcon,
  BeakerIcon,
  HeartIcon,
  DocumentTextIcon,
  UserGroupIcon,
  BuildingLibraryIcon,
  LanguageIcon,
  SparklesIcon,
  MapPinIcon
} from '../utils/icons';
import apiClient from '../apiClient';
import { 
  INDIAN_STATES, 
  // Remove unused imports or comment them out if you plan to use later
  // BLOOD_GROUPS, 
  // PHYSICAL_ACTIVITY_LEVELS, 
  // DIET_TYPES, 
  // STRESS_LEVELS, 
  // SMOKING_STATUS, 
  // ALCOHOL_USE, 
  // GENDER_IDENTITIES 
} from '../utils/constants';

function Profile() {
  const [profileData, setProfileData] = useState({
    user: {
      id: null,
      username: '',
      email: '',
    first_name: '',
    last_name: '',
      is_active: false,
      date_joined: null,
      last_login: null
    },

    // Profile Image
    profile_image: null,
    profile_image_url: null,

    // Demographics
    date_of_birth: '',
    sex: '',
    gender_identity: '',
    blood_group: '',

    // Physical metrics
    height_cm: null,
    weight_kg: null,
    waist_cm: null,
    hip_cm: null,

    // Contact & address
    phone_number: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
    occupation: '',

    // Lifestyle
    smoking_status: '',
    alcohol_use: '',
    physical_activity_level: '',
    diet_type: '',
    sleep_hours: null,
    stress_level: '',

    // Medical history (JSON fields)
    chronic_conditions: '',
    surgeries: '',
    allergies: '',
    medications_current: '',
    family_history: '',
    vaccinations: '',

    // Reproductive health
    reproductive_health_notes: '',

    // Care team
    primary_physician_name: '',
    primary_physician_contact: '',

    // Insurance
    insurance_provider: '',
    insurance_policy_number: '',

    // Emergency contact
    emergency_contact_name: '',
    emergency_contact_relationship: '',
    emergency_contact_phone: '',

    // Preferences & consents
    preferred_hospital: '',
    communication_preferences: null,
    language_preferences: null,
    data_sharing_consent: false,
    research_consent: false,

    // Cross-domain IDs
    dna_profile_id: '',

    // Timestamps
    created_at: null,
    updated_at: null
  });

  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const navigate = useNavigate();

  // Predefined lists for dropdowns
  const stressLevels = ['Low', 'Moderate', 'High', 'Very High'];
  const countries = ['India', 'United States', 'United Kingdom', 'Canada', 'Australia', 'Other'];
  // const indianStates = INDIAN_STATES; // Remove this line if not used

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const currentUser = authService.getCurrentUser();
        if (!currentUser) {
          navigate('/login');
          return;
        }

        // Fetch actual user profile data
        const response = await apiClient.get('/authentication/profile/');
        const userProfile = response.data;

        // Ensure date_of_birth is formatted correctly
        if (userProfile.date_of_birth) {
          userProfile.date_of_birth = formatDateForInput(userProfile.date_of_birth);
        }

        setProfileData(userProfile);
      } catch (error) {
        console.error('Failed to fetch user data', error);
        setErrorMessage('Failed to load user profile');
      }
    };

    fetchUserData();
  }, [navigate]);

  // Helper function to format date for input field
  const formatDateForInput = (dateString) => {
    if (!dateString) return '';
    
    // Try to handle different date formats
    const date = new Date(dateString);
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      console.error('Invalid date:', dateString);
      return '';
    }

    // Format as YYYY-MM-DD
    return date.toISOString().split('T')[0];
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked, files } = e.target;
    
    // Handle file upload for profile image
    if (name === 'profile_image' && files && files[0]) {
      const file = files[0];
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileData(prev => ({
          ...prev,
          profile_image: file,
          profile_image_url: reader.result
        }));
      };
      reader.readAsDataURL(file);
      return;
    }

    // Handle nested user object
    if (name.startsWith('user.')) {
      const userField = name.split('.')[1];
      setProfileData(prev => ({
        ...prev,
        user: {
          ...prev.user,
          [userField]: type === 'checkbox' ? checked : value
        }
      }));
    } else {
      // Handle JSON fields
      if (['chronic_conditions', 'surgeries', 'allergies', 'medications_current', 'family_history', 'vaccinations', 'communication_preferences', 'language_preferences'].includes(name)) {
        try {
          const parsedValue = value ? JSON.parse(value) : null;
          setProfileData(prev => ({
            ...prev,
            [name]: parsedValue
          }));
        } catch (error) {
          console.error('Invalid JSON', error);
        }
      } else {
        // Handle other fields
        setProfileData(prev => ({
      ...prev,
          [name]: type === 'checkbox' ? checked : value
    }));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form before submission
    if (!validateForm()) {
      return;
    }

    // Transform address fields to match backend requirements
    const transformedAddress = {
      street: `${profileData.address_line1} ${profileData.address_line2}`.trim(),
      city: profileData.city,
      state: profileData.state,
      zip_code: profileData.postal_code,
      country: profileData.country
    };

    // Prepare payload with transformed address
    const payload = {
      ...profileData,
      address: transformedAddress
    };

    // Remove original address fields
    delete payload.address_line1;
    delete payload.address_line2;
    delete payload.city;
    delete payload.state;
    delete payload.postal_code;
    delete payload.country;

    // Convert payload to FormData
    const formData = new FormData();
    Object.keys(payload).forEach(key => {
      // Handle file uploads
      if (key === 'profile_image' && payload[key] instanceof File) {
        formData.append(key, payload[key]);
      } 
      // Handle JSON-like fields
      else if (['chronic_conditions', 'surgeries', 'allergies', 'medications_current', 'family_history', 'vaccinations', 'communication_preferences', 'language_preferences'].includes(key)) {
        formData.append(key, payload[key] || '');
      } 
      // Handle other fields
      else if (payload[key] !== null && payload[key] !== undefined) {
        formData.append(key, payload[key]);
      }
    });

    try {
      // eslint-disable-next-line no-unused-vars
      const loading = true;
      
      // Log payload for debugging
      console.group('Profile Update Payload');
      for (let [key, value] of formData.entries()) {
        console.log(`${key}:`, value);
      }
      console.groupEnd();

      // Submit profile update
      const response = await apiClient.put('/authentication/profile/update/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Update local storage with new user data
      const updatedUser = {
        ...authService.getCurrentUser(),
        first_name: response.data.user.first_name,
        last_name: response.data.user.last_name
      };
      localStorage.setItem('user', JSON.stringify(updatedUser));

      // Show success message
      alert('Profile updated successfully!');
      
      // Refresh profile data
      setProfileData(response.data);
      setIsEditing(false);
    } catch (error) {
      console.error('Profile update error:', error);
      
      // More detailed error handling
      const errorMessage = error.response 
        ? (error.response.data.error || 'Failed to update profile') 
        : 'Network error. Please try again.';
      
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!profileData.user) return null;

  // Add validateForm method
  const validateForm = () => {
    // Implement form validation logic
    // Return true if form is valid, false otherwise
    let isValid = true;
    
    // Example validation (customize as needed)
    if (!profileData.user.first_name) {
      setErrorMessage('First name is required');
      isValid = false;
    }

    // Add more validation as needed

    return isValid;
  };

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

        {errorMessage && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            {errorMessage}
          </div>
        )}

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl mx-auto"
        >
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-primary to-brand-secondary bg-clip-text text-transparent">
              My Profile
            </h1>
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                <span>All fields are optional</span>
              </div>
            <button 
              onClick={() => setIsEditing(!isEditing)}
              className="px-4 py-2 bg-brand-primary/10 text-brand-primary rounded-lg hover:bg-brand-primary/20 transition-colors"
            >
              {isEditing ? 'Cancel' : 'Edit Profile'}
            </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Profile Image Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md">
              <div className="flex items-center space-x-3 mb-4">
                <UserIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Profile Image
                </h2>
              </div>
              <div>
                {profileData.profile_image_url ? (
                  <img 
                    src={profileData.profile_image_url} 
                    alt="Profile" 
                    className="w-32 h-32 rounded-full object-cover mx-auto mb-4"
                  />
                ) : (
                  <div className="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center mx-auto mb-4">
                    <UserIcon className="w-16 h-16 text-gray-400" />
                  </div>
                )}
                {isEditing && (
                  <input
                    type="file"
                    name="profile_image"
                    onChange={handleInputChange}
                    accept="image/jpeg,image/png,image/gif"
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-brand-primary/10 file:text-brand-primary hover:file:bg-brand-primary/20"
                  />
                )}
              </div>
            </div>

            {/* Personal Information Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md">
              <div className="flex items-center space-x-3 mb-4">
                <UserIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Personal Information
                </h2>
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="user.first_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    First Name
                  </label>
                  <input
                    id="user.first_name"
                    name="user.first_name"
                    type="text"
                    value={profileData.user.first_name}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                  />
                </div>
                <div>
                  <label htmlFor="user.last_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Last Name
                  </label>
                  <input
                    id="user.last_name"
                    name="user.last_name"
                    type="text"
                    value={profileData.user.last_name}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                  />
                </div>
                <div>
                  <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Date of Birth
                  </label>
                  <input
                    id="date_of_birth"
                    name="date_of_birth"
                    type="date"
                    value={profileData.date_of_birth || ''}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                  />
                </div>
              </div>
              <div className="grid md:grid-cols-3 gap-4 mt-4">
                <div>
                  <label htmlFor="sex" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Sex
                  </label>
                  <select
                    id="sex"
                    name="sex"
                    value={profileData.sex}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                  >
                    <option value="">Select Sex</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="gender_identity" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Gender Identity
                  </label>
                  <input
                    id="gender_identity"
                    name="gender_identity"
                    type="text"
                    value={profileData.gender_identity}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Your gender identity"
                  />
                </div>
                <div>
                  <label htmlFor="blood_group" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Blood Group
                  </label>
                  <input
                    id="blood_group"
                    name="blood_group"
                    type="text"
                    value={profileData.blood_group}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="e.g., A+"
                  />
                </div>
              </div>
            </div>

            {/* Contact & Address Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md">
              <div className="flex items-center space-x-3 mb-4">
                <MapPinIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Contact & Address
                </h2>
              </div>
              
              {/* Email and Phone Number */}
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="user.email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="user.email"
                      name="user.email"
                      type="email"
                      value={profileData.user.email}
                      disabled
                      className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                      placeholder="Your email address"
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Phone Number
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <PhoneIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="phone_number"
                      name="phone_number"
                      type="tel"
                      value={profileData.phone_number}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                      placeholder="Enter phone number"
                    />
                  </div>
                </div>
              </div>

              {/* Address Lines */}
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label htmlFor="address_line1" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Address Line 1
                  </label>
                  <input
                    id="address_line1"
                    name="address_line1"
                    type="text"
                    value={profileData.address_line1}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Street address"
                  />
                </div>
                <div>
                  <label htmlFor="address_line2" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Address Line 2
                  </label>
                  <input
                    id="address_line2"
                    name="address_line2"
                    type="text"
                    value={profileData.address_line2}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Apartment, suite, unit, etc."
                  />
                </div>
              </div>

              {/* City, Postal Code */}
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label htmlFor="city" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    City
                  </label>
                  <input
                    id="city"
                    name="city"
                    type="text"
                    value={profileData.city}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Your city"
                  />
                </div>
                <div>
                  <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Postal Code
                  </label>
                  <input
                    id="postal_code"
                    name="postal_code"
                    type="text"
                    value={profileData.postal_code}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Postal code"
                  />
                </div>
              </div>

              {/* State and Country */}
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label htmlFor="state" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    State
                  </label>
                  <select
                    name="state"
                    value={profileData.state}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary focus:ring-opacity-50"
                  >
                    <option value="">Select State</option>
                    {INDIAN_STATES.map(state => (
                      <option key={state} value={state}>{state}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="country" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Country
                  </label>
                  <select
                    id="country"
                    name="country"
                    value={profileData.country}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                  >
                    <option value="">Select Country</option>
                    {countries.map(country => (
                      <option key={country} value={country}>{country}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Consent & Preferences Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md">
              <div className="flex items-center space-x-3 mb-4">
                <ShieldCheckIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Consent & Preferences
                </h2>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-center">
                  <input
                    id="data_sharing_consent"
                    name="data_sharing_consent"
                    type="checkbox"
                    checked={profileData.data_sharing_consent}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="h-4 w-4 text-brand-primary focus:ring-brand-primary border-gray-300 rounded"
                  />
                  <label htmlFor="data_sharing_consent" className="ml-2 block text-sm text-gray-900 dark:text-gray-100">
                    Consent to Data Sharing
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    id="research_consent"
                    name="research_consent"
                    type="checkbox"
                    checked={profileData.research_consent}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="h-4 w-4 text-brand-primary focus:ring-brand-primary border-gray-300 rounded"
                  />
                  <label htmlFor="research_consent" className="ml-2 block text-sm text-gray-900 dark:text-gray-100">
                    Consent to Research Participation
                  </label>
                </div>
              </div>
            </div>

            {/* Physical Metrics Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md mt-6">
              <div className="flex items-center space-x-3 mb-4">
                <BeakerIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Physical Metrics
                </h2>
              </div>
              <div className="grid md:grid-cols-4 gap-4">
                <div>
                  <label htmlFor="height_cm" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Height (cm)
                  </label>
                  <input
                    id="height_cm"
                    name="height_cm"
                    type="number"
                    value={profileData.height_cm}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Your height"
                  />
                </div>
                <div>
                  <label htmlFor="weight_kg" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Weight (kg)
                  </label>
                  <input
                    id="weight_kg"
                    name="weight_kg"
                    type="number"
                    value={profileData.weight_kg}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Your weight"
                  />
                </div>
                <div>
                  <label htmlFor="waist_cm" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Waist (cm)
                  </label>
                  <input
                    id="waist_cm"
                    name="waist_cm"
                    type="number"
                    value={profileData.waist_cm}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Waist circumference"
                  />
                </div>
                <div>
                  <label htmlFor="hip_cm" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Hip (cm)
                  </label>
                  <input
                    id="hip_cm"
                    name="hip_cm"
                    type="number"
                    value={profileData.hip_cm}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Hip circumference"
                  />
                </div>
              </div>
            </div>

            {/* Lifestyle Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md mt-6">
              <div className="flex items-center space-x-3 mb-4">
                <HeartIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Lifestyle & Occupation
                </h2>
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="occupation" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Occupation
                  </label>
                  <input
                    id="occupation"
                    name="occupation"
                    type="text"
                    value={profileData.occupation}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Your profession"
                  />
                </div>
                <div>
                  <label htmlFor="physical_activity_level" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Physical Activity
                  </label>
                  <select
                    id="physical_activity_level"
                    name="physical_activity_level"
                    value={profileData.physical_activity_level}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                  >
                    <option value="">Select Activity Level</option>
                    <option value="Sedentary">Sedentary</option>
                    <option value="Light">Light</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Active">Active</option>
                    <option value="Very Active">Very Active</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="sleep_hours" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Average Sleep Hours
                  </label>
                  <input
                    id="sleep_hours"
                    name="sleep_hours"
                    type="number"
                    value={profileData.sleep_hours}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Hours of sleep"
                  />
                </div>
              </div>
              <div className="grid md:grid-cols-3 gap-4 mt-4">
                <div>
                  <label htmlFor="smoking_status" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Smoking Status
                  </label>
                  <select
                    id="smoking_status"
                    name="smoking_status"
                    value={profileData.smoking_status}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                  >
                    <option value="">Select Smoking Status</option>
                    <option value="Non-Smoker">Non-Smoker</option>
                    <option value="Current Smoker">Current Smoker</option>
                    <option value="Ex-Smoker">Ex-Smoker</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="alcohol_use" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Alcohol Consumption
                  </label>
                  <select
                    id="alcohol_use"
                    name="alcohol_use"
                    value={profileData.alcohol_use}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                  >
                    <option value="">Select Alcohol Use</option>
                    <option value="Non-Drinker">Non-Drinker</option>
                    <option value="Occasional">Occasional</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Heavy">Heavy</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="diet_type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Diet Type
                  </label>
                  <select
                    id="diet_type"
                    name="diet_type"
                    value={profileData.diet_type}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                  >
                    <option value="">Select Diet Type</option>
                    <option value="Omnivore">Omnivore</option>
                    <option value="Vegetarian">Vegetarian</option>
                    <option value="Vegan">Vegan</option>
                    <option value="Pescatarian">Pescatarian</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Medical History Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md mt-6">
              <div className="flex items-center space-x-3 mb-4">
                <DocumentTextIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Medical History
                </h2>
              </div>
              
              {/* Surgeries */}
              <div className="mb-4">
                <label htmlFor="surgeries" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Surgeries
                </label>
                <textarea
                  id="surgeries"
                  name="surgeries"
                  value={profileData.surgeries || ''}
                  onChange={(e) => {
                    setProfileData(prev => ({
                      ...prev,
                      surgeries: e.target.value
                    }));
                  }}
                  disabled={!isEditing}
                  placeholder="List your surgeries, e.g., Appendectomy in 2020 at City Hospital"
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500 h-24"
                />
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Enter surgeries as a comma-separated list or brief descriptions.
                </p>
              </div>

              {/* Allergies */}
              <div className="mb-4">
                <label htmlFor="allergies" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Allergies
                </label>
                <textarea
                  id="allergies"
                  name="allergies"
                  value={profileData.allergies || ''}
                  onChange={(e) => {
                    setProfileData(prev => ({
                      ...prev,
                      allergies: e.target.value
                    }));
                  }}
                  disabled={!isEditing}
                  placeholder="List your allergies, e.g., Peanuts, Penicillin"
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500 h-24"
                />
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Enter allergies as a comma-separated list.
                </p>
              </div>

              {/* Vaccinations */}
              <div>
                <label htmlFor="vaccinations" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Vaccinations
                </label>
                <textarea
                  id="vaccinations"
                  name="vaccinations"
                  value={profileData.vaccinations || ''}
                  onChange={(e) => {
                    setProfileData(prev => ({
                      ...prev,
                      vaccinations: e.target.value
                    }));
                  }}
                  disabled={!isEditing}
                  placeholder="List your vaccinations, e.g., COVID-19 first dose on 2021-05-15"
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500 h-24"
                />
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Enter vaccinations as a comma-separated list or brief descriptions.
                </p>
              </div>

              {/* Chronic Conditions */}
              <div className="mt-4">
                <label htmlFor="chronic_conditions" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Chronic Conditions
                </label>
                <textarea
                  id="chronic_conditions"
                  name="chronic_conditions"
                  value={profileData.chronic_conditions || ''}
                  onChange={(e) => {
                    setProfileData(prev => ({
                      ...prev,
                      chronic_conditions: e.target.value
                    }));
                  }}
                  disabled={!isEditing}
                  placeholder="List your chronic conditions, e.g., Diabetes Type 2, Hypertension"
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500 h-24"
                />
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Enter chronic conditions as a comma-separated list or brief descriptions.
                </p>
              </div>

              {/* Current Medications */}
              <div className="mt-4">
                <label htmlFor="medications_current" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Current Medications
                </label>
                <textarea
                  id="medications_current"
                  name="medications_current"
                  value={profileData.medications_current || ''}
                  onChange={(e) => {
                    setProfileData(prev => ({
                      ...prev,
                      medications_current: e.target.value
                    }));
                  }}
                  disabled={!isEditing}
                  placeholder="List your current medications, e.g., Metformin 500mg daily, Lisinopril 10mg"
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500 h-24"
                />
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Enter current medications as a comma-separated list or brief descriptions.
                </p>
              </div>

              {/* Family History */}
              <div className="mt-4">
                <label htmlFor="family_history" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Family Medical History
                </label>
                <textarea
                  id="family_history"
                  name="family_history"
                  value={profileData.family_history || ''}
                  onChange={(e) => {
                    setProfileData(prev => ({
                      ...prev,
                      family_history: e.target.value
                    }));
                  }}
                  disabled={!isEditing}
                  placeholder="List significant family medical history, e.g., Father - Heart Disease, Mother - Diabetes"
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500 h-24"
                />
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Enter family medical history as a comma-separated list or brief descriptions.
                </p>
              </div>
            </div>

            {/* Emergency Contact Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md mt-6">
              <div className="flex items-center space-x-3 mb-4">
                <UserGroupIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Emergency Contact
                </h2>
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label htmlFor="emergency_contact_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Name
                  </label>
                  <input
                    id="emergency_contact_name"
                    name="emergency_contact_name"
                    type="text"
                    value={profileData.emergency_contact_name}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Emergency contact name"
                  />
                </div>
                <div>
                  <label htmlFor="emergency_contact_relationship" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Relationship
                  </label>
                  <input
                    id="emergency_contact_relationship"
                    name="emergency_contact_relationship"
                    type="text"
                    value={profileData.emergency_contact_relationship}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Relationship to contact"
                  />
                </div>
                <div>
                  <label htmlFor="emergency_contact_phone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Phone Number
                  </label>
                  <input
                    id="emergency_contact_phone"
                    name="emergency_contact_phone"
                    type="tel"
                    value={profileData.emergency_contact_phone}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Emergency contact phone"
                  />
                </div>
              </div>
            </div>

            {/* Reproductive Health Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md mt-6">
              <div className="flex items-center space-x-3 mb-4">
                <SparklesIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Reproductive Health
                </h2>
              </div>
              <div>
                <label htmlFor="reproductive_health_notes" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Reproductive Health Notes
                </label>
                <textarea
                  id="reproductive_health_notes"
                  name="reproductive_health_notes"
                  value={profileData.reproductive_health_notes || ''}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500 h-24"
                  placeholder="Additional reproductive health information"
                />
              </div>
            </div>

            {/* Care Team Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md mt-6">
              <div className="flex items-center space-x-3 mb-4">
                <BuildingLibraryIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Care Team
                </h2>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="primary_physician_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Primary Physician Name
                  </label>
                  <input
                    id="primary_physician_name"
                    name="primary_physician_name"
                    type="text"
                    value={profileData.primary_physician_name}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Primary physician's name"
                  />
                </div>
                <div>
                  <label htmlFor="primary_physician_contact" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Primary Physician Contact
                  </label>
                  <input
                    id="primary_physician_contact"
                    name="primary_physician_contact"
                    type="text"
                    value={profileData.primary_physician_contact}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Primary physician's contact"
                  />
                </div>
              </div>
            </div>

            {/* Insurance Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md mt-6">
              <div className="flex items-center space-x-3 mb-4">
                <ShieldCheckIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Insurance Details
                </h2>
                    </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="insurance_provider" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Insurance Provider
                  </label>
                    <input
                    id="insurance_provider"
                    name="insurance_provider"
                    type="text"
                    value={profileData.insurance_provider}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Insurance provider name"
                    />
                  </div>
                <div>
                  <label htmlFor="insurance_policy_number" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Policy Number
                  </label>
                  <input
                    id="insurance_policy_number"
                    name="insurance_policy_number"
                    type="text"
                    value={profileData.insurance_policy_number}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                    placeholder="Insurance policy number"
                  />
                </div>
              </div>
            </div>

            {/* Preferences Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md mt-6">
              <div className="flex items-center space-x-3 mb-4">
                <LanguageIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Preferences
                </h2>
              </div>
              
              {/* Communication Preferences */}
              <div className="mb-4">
                <label htmlFor="communication_preferences" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Communication Preferences
                </label>
                <textarea
                  id="communication_preferences"
                  name="communication_preferences"
                  value={profileData.communication_preferences || ''}
                  onChange={(e) => {
                    setProfileData(prev => ({
                      ...prev,
                      communication_preferences: e.target.value
                    }));
                  }}
                  disabled={!isEditing}
                  placeholder="List your preferred communication methods, e.g., Email, SMS"
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500 h-24"
                />
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Enter communication preferences as a comma-separated list.
                </p>
              </div>

              {/* Language Preferences */}
              <div>
                <label htmlFor="language_preferences" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Language Preferences
                </label>
                <textarea
                  id="language_preferences"
                  name="language_preferences"
                  value={profileData.language_preferences || ''}
                  onChange={(e) => {
                    setProfileData(prev => ({
                      ...prev,
                      language_preferences: e.target.value
                    }));
                  }}
                  disabled={!isEditing}
                  placeholder="List your preferred languages, e.g., English, Spanish"
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500 h-24"
                />
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Enter language preferences as a comma-separated list.
                </p>
              </div>
            </div>

            {/* Subscription History Section */}
            {profileData.subscription_history && profileData.subscription_history.length > 0 && (
              <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md mt-6">
                <div className="flex items-center space-x-3 mb-4">
                  <DocumentTextIcon className="h-6 w-6 text-brand-primary" />
                  <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                    Subscription History
                  </h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                    <thead className="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-700 dark:text-gray-400">
                      <tr>
                        <th className="px-4 py-2">Date</th>
                        <th className="px-4 py-2">Action</th>
                        <th className="px-4 py-2">Plan</th>
                        <th className="px-4 py-2">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {profileData.subscription_history.map((history, index) => (
                        <tr key={index} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                          <td className="px-4 py-2">{new Date(history.created_at).toLocaleDateString()}</td>
                          <td className="px-4 py-2">{history.action_type}</td>
                          <td className="px-4 py-2">{history.new_plan?.name || 'N/A'}</td>
                          <td className="px-4 py-2">{history.amount ? `₹${history.amount}` : 'N/A'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Stress Level Section */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 shadow-md mt-6">
              <div className="flex items-center space-x-3 mb-4">
                <HeartIcon className="h-6 w-6 text-brand-primary" />
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  Stress Management
                </h2>
              </div>
              <div>
                <label htmlFor="stress_level" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Stress Level
                </label>
                <select
                  id="stress_level"
                  name="stress_level"
                  value={profileData.stress_level}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-500"
                >
                  <option value="">Select Stress Level</option>
                  {stressLevels.map(level => (
                    <option key={level} value={level}>{level}</option>
                  ))}
                </select>
              </div>
            </div>

            {isEditing && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-lg text-white bg-gradient-to-r from-brand-primary to-brand-secondary hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-primary mt-6"
              >
                Save Changes
              </motion.button>
            )}
          </form>
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

export default Profile; 