import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from '../components/Navbar';
import BackButton from '../components/BackButton';
import apiClient from '../apiClient';
import { 
  BeakerIcon,
  // Remove unused icons
} from '../utils/icons';
import { INDIAN_STATES } from '../utils/constants';

const ShippingAddressModal = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  initialUser,
  orderLoading  // Add new prop for loading state
}) => {
  const [address, setAddress] = useState({
    full_name: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'India',
    phone_number: ''
  });

  const [consent, setConsent] = useState({
    consented: false,
    consent_type: 'ANALYSIS'
  });

  const [errors, setErrors] = useState({});
  const [isEdited, setIsEdited] = useState(false);
  const [loading, setLoading] = useState(false);

  // Effect to pre-fill form when modal opens
  useEffect(() => {
    const fetchProfileData = async () => {
      if (isOpen) {
        try {
          setLoading(true);
          // Fetch user profile directly
          const profileResponse = await apiClient.get('/authentication/profile/');
          const userData = profileResponse.data;
          
          console.group('Profile Data for Shipping Modal');
          console.log('Full Profile Response:', userData);

          // Construct full name
          const fullName = userData.user.first_name && userData.user.last_name 
            ? `${userData.user.first_name} ${userData.user.last_name}`.trim()
            : userData.user.username || '';

          // Prepare address object using profile data
          const newAddress = {
            full_name: fullName,
            address_line1: userData.address_line1 || '',
            address_line2: userData.address_line2 || '',
            city: userData.city || '',
            state: userData.state || '',
            postal_code: userData.postal_code || '',
            country: userData.country || 'India',
            phone_number: userData.phone_number || 
                          userData.user.phone_number || ''
          };

          console.log('Prepared Address:', newAddress);
          console.groupEnd();

          // Validate that we're not setting empty values
          const filteredAddress = Object.fromEntries(
            Object.entries(newAddress).filter(([_, v]) => v !== '')
          );

          console.log('Filtered Address:', filteredAddress);

          // Update address state
          setAddress(prevAddress => ({
            ...prevAddress,
            ...filteredAddress
          }));

          setIsEdited(false);
          setErrors({});
        } catch (err) {
          console.error('Failed to fetch profile data:', err);
          
          // Fallback to initial user data if available
          if (initialUser) {
            const fallbackAddress = {
              full_name: initialUser.first_name && initialUser.last_name 
                ? `${initialUser.first_name} ${initialUser.last_name}`.trim()
                : initialUser.username || '',
              address_line1: initialUser.address_line1 || '',
              address_line2: initialUser.address_line2 || '',
              city: initialUser.city || '',
              state: initialUser.state || '',
              postal_code: initialUser.postal_code || '',
              country: initialUser.country || 'India',
              phone_number: initialUser.phone_number || ''
            };
            setAddress(fallbackAddress);
          }
        } finally {
          setLoading(false);
        }
      }
    };

    fetchProfileData();
  }, [isOpen, initialUser]);

  const validateForm = () => {
    const newErrors = {};
    
    if (!address.full_name.trim()) newErrors.full_name = 'Full name is required';
    if (!address.address_line1.trim()) newErrors.address_line1 = 'Address is required';
    if (!address.city.trim()) newErrors.city = 'City is required';
    if (!address.state) newErrors.state = 'State is required';
    if (!address.postal_code.trim() || !/^\d{6}$/.test(address.postal_code)) {
      newErrors.postal_code = 'Valid 6-digit postal code is required';
    }
    if (!address.phone_number.trim()) {
      newErrors.phone_number = 'Phone number is required';
    }
    if (!address.country) newErrors.country = 'Country is required';

    // Validate consent
    if (!consent.consented) {
      newErrors.consent = 'Consent is mandatory to proceed with the order';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleConsentChange = (e) => {
    const { name, checked } = e.target;
    setConsent(prev => ({
      ...prev,
      [name]: checked
    }));

    // Clear consent error when checkbox is checked
    if (checked && errors.consent) {
      setErrors(prev => ({
        ...prev,
        consent: undefined
      }));
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setAddress(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Mark as edited and clear specific error
    setIsEdited(true);
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const handleSubmitAddress = (e) => {
    e.preventDefault();
    if (validateForm()) {
      // Combine address and consent data
      onSubmit({
        ...address,
        ...consent
      });
    }
  };

  if (!isOpen) return null;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.9, y: 50 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 50 }}
        transition={{ 
          type: "spring", 
          stiffness: 300, 
          damping: 20 
        }}
        className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
      >
        <div className="bg-gradient-to-r from-brand-primary to-brand-secondary rounded-t-3xl p-6">
          <h2 className="text-3xl font-bold text-white text-center">
            Shipping Details
          </h2>
          <p className="text-center text-white/80 mt-2">
            {isEdited 
              ? "You've modified the address details" 
              : "Pre-filled from your profile. Edit if needed."}
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center p-8">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1 }}
              className="w-12 h-12 border-4 border-brand-primary border-t-transparent rounded-full"
            />
          </div>
        ) : (
          <form onSubmit={handleSubmitAddress} className="p-8 space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={address.full_name}
                  onChange={handleChange}
                  className={`
                    w-full px-4 py-3 rounded-xl 
                    border ${errors.full_name 
                      ? 'border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 dark:border-gray-600 focus:border-brand-primary'}
                    bg-white dark:bg-gray-700 
                    text-gray-900 dark:text-white
                    focus:outline-none focus:ring-2 focus:ring-opacity-50
                  `}
                  placeholder="Enter full name"
                />
                {errors.full_name && (
                  <p className="text-red-500 text-xs mt-1">{errors.full_name}</p>
                )}
              </div>

              {/* Phone Number */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone_number"
                  value={address.phone_number}
                  onChange={handleChange}
                  className={`
                    w-full px-4 py-3 rounded-xl 
                    border ${errors.phone_number 
                      ? 'border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 dark:border-gray-600 focus:border-brand-primary'}
                    bg-white dark:bg-gray-700 
                    text-gray-900 dark:text-white
                    focus:outline-none focus:ring-2 focus:ring-opacity-50
                  `}
                  placeholder="Phone number"
                />
                {errors.phone_number && (
                  <p className="text-red-500 text-xs mt-1">{errors.phone_number}</p>
                )}
              </div>
            </div>

            {/* Address Line 1 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Address Line 1
              </label>
              <input
                type="text"
                name="address_line1"
                value={address.address_line1}
                onChange={handleChange}
                className={`
                  w-full px-4 py-3 rounded-xl 
                  border ${errors.address_line1 
                    ? 'border-red-500 focus:ring-red-500' 
                    : 'border-gray-300 dark:border-gray-600 focus:border-brand-primary'}
                  bg-white dark:bg-gray-700 
                  text-gray-900 dark:text-white
                  focus:outline-none focus:ring-2 focus:ring-opacity-50
                `}
                placeholder="Street address, P.O. box, company name"
              />
              {errors.address_line1 && (
                <p className="text-red-500 text-xs mt-1">{errors.address_line1}</p>
              )}
            </div>

            {/* Address Line 2 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Address Line 2 (Optional)
              </label>
              <input
                type="text"
                name="address_line2"
                value={address.address_line2}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary focus:ring-opacity-50"
                placeholder="Apartment, suite, unit, building, floor"
              />
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {/* City */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  City
                </label>
                <input
                  type="text"
                  name="city"
                  value={address.city}
                  onChange={handleChange}
                  className={`
                    w-full px-4 py-3 rounded-xl 
                    border ${errors.city 
                      ? 'border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 dark:border-gray-600 focus:border-brand-primary'}
                    bg-white dark:bg-gray-700 
                    text-gray-900 dark:text-white
                    focus:outline-none focus:ring-2 focus:ring-opacity-50
                  `}
                  placeholder="Enter city"
                />
                {errors.city && (
                  <p className="text-red-500 text-xs mt-1">{errors.city}</p>
                )}
              </div>

              {/* State */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  State
                </label>
                <select
                  name="state"
                  value={address.state}
                  onChange={handleChange}
                  className={`
                    w-full px-4 py-3 rounded-xl 
                    border ${errors.state 
                      ? 'border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 dark:border-gray-600 focus:border-brand-primary'}
                    bg-white dark:bg-gray-700 
                    text-gray-900 dark:text-white
                    focus:outline-none focus:ring-2 focus:ring-opacity-50
                  `}
                >
                  <option value="">Select State</option>
                  {INDIAN_STATES.map(state => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
                {errors.state && (
                  <p className="text-red-500 text-xs mt-1">{errors.state}</p>
                )}
              </div>

              {/* Postal Code */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Postal Code
                </label>
                <input
                  type="text"
                  name="postal_code"
                  value={address.postal_code}
                  onChange={handleChange}
                  className={`
                    w-full px-4 py-3 rounded-xl 
                    border ${errors.postal_code 
                      ? 'border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 dark:border-gray-600 focus:border-brand-primary'}
                    bg-white dark:bg-gray-700 
                    text-gray-900 dark:text-white
                    focus:outline-none focus:ring-2 focus:ring-opacity-50
                  `}
                  placeholder="6-digit postal code"
                />
                {errors.postal_code && (
                  <p className="text-red-500 text-xs mt-1">{errors.postal_code}</p>
                )}
              </div>

              {/* Country Field */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Country
                </label>
                <select
                  name="country"
                  value={address.country}
                  onChange={handleChange}
                  className={`
                    w-full px-4 py-3 rounded-xl 
                    border ${errors.country 
                      ? 'border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 dark:border-gray-600 focus:border-brand-primary'}
                    bg-white dark:bg-gray-700 
                    text-gray-900 dark:text-white
                    focus:outline-none focus:ring-2 focus:ring-opacity-50
                  `}
                >
                  <option value="India">India</option>
                  <option value="United States">United States</option>
                  <option value="United Kingdom">United Kingdom</option>
                  <option value="Canada">Canada</option>
                  {/* Add more countries as needed */}
                </select>
                {errors.country && (
                  <p className="text-red-500 text-xs mt-1">{errors.country}</p>
                )}
              </div>
            </div>

            {/* Consent Section */}
            <div className="mt-4">
              <div className="space-y-2">
                <div className="flex items-center">
                  <input 
                    type="checkbox" 
                    id="consented"
                    name="consented"
                    checked={consent.consented}
                    onChange={handleConsentChange}
                    className="mr-2 rounded text-brand-primary focus:ring-brand-primary"
                  />
                  <label 
                    htmlFor="consented" 
                    className="text-sm text-gray-700 dark:text-gray-300"
                  >
                    I consent to the DNA analysis and data processing
                  </label>
                </div>
                
                <div className="flex items-center">
                  <select
                    name="consent_type"
                    value={consent.consent_type}
                    onChange={(e) => setConsent(prev => ({
                      ...prev,
                      consent_type: e.target.value
                    }))}
                    className={`
                      w-full px-4 py-3 rounded-xl 
                      border border-gray-300 dark:border-gray-600 
                      bg-white dark:bg-gray-700 
                      text-gray-900 dark:text-white
                      focus:outline-none focus:ring-2 focus:ring-brand-primary focus:ring-opacity-50
                    `}
                  >
                    <option value="ANALYSIS">DNA Analysis</option>
                    <option value="RESEARCH">Research Participation</option>
                    <option value="DATA_SHARING">Data Sharing</option>
                    <option value="STORAGE">Sample Storage</option>
                    <option value="FAMILY_MATCHING">Family Matching</option>
                  </select>
                </div>
              </div>
              
              {errors.consent && (
                <p className="text-red-500 text-xs mt-2">{errors.consent}</p>
              )}
            </div>

            <div className="flex justify-end space-x-4 mt-8">
              <motion.button
                type="button"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onClose}
                className="px-6 py-3 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-colors"
                disabled={orderLoading}  // Disable when order is in progress
              >
                Cancel
              </motion.button>
              <motion.button
                type="submit"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={orderLoading}  // Disable when order is in progress
                className={`px-6 py-3 bg-gradient-to-r from-brand-primary to-brand-secondary text-white rounded-xl hover:opacity-90 transition-all shadow-lg 
                  ${orderLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {orderLoading ? (
                  <div className="flex items-center justify-center">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 1 }}
                      className="w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"
                    />
                    Processing...
                  </div>
                ) : (
                  'Submit Order'
                )}
              </motion.button>
            </div>
          </form>
        )}
      </motion.div>
    </motion.div>
  );
};

const DNAKitCard = ({ kit, onOrder, userEmail }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.05, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)' }}
      className="flex-shrink-0 w-80 bg-white dark:bg-gray-800 rounded-3xl shadow-xl p-6 mr-6 border border-gray-200 dark:border-gray-700 transform transition-all duration-300"
    >
      <div className="flex items-center mb-4">
        <BeakerIcon className="h-10 w-10 text-brand-primary mr-4 bg-brand-primary/10 p-2 rounded-xl" />
        <div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {kit.name}
          </h3>
          <span className="ml-1 px-2 py-1 text-xs bg-brand-primary/20 text-brand-primary rounded-full">
            {kit.category}
          </span>
        </div>
      </div>
      
      <p className="text-gray-600 dark:text-gray-400 mb-4 h-24 overflow-hidden text-ellipsis">
        {kit.description}
      </p>
      
      <div className="mb-4 flex justify-between items-center">
        <p className="text-3xl font-bold text-brand-primary">
          ₹{kit.price}
        </p>
        <div className="flex items-center text-gray-500 dark:text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
          <span className="text-sm">{kit.processing_time_days} days</span>
        </div>
      </div>
      
      <div className="mb-6 max-h-40 overflow-y-auto custom-scrollbar">
        <ul className="space-y-2">
          {kit.features.map((feature, index) => (
            <li 
              key={index} 
              className="flex items-center text-gray-700 dark:text-gray-300"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-5 w-5 text-green-500 mr-2" 
                viewBox="0 0 20 20" 
                fill="currentColor"
              >
                <path 
                  fillRule="evenodd" 
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" 
                  clipRule="evenodd" 
                />
              </svg>
              {feature}
            </li>
          ))}
        </ul>
      </div>
      
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => onOrder(kit)}
        className="w-full bg-gradient-to-r from-brand-primary to-brand-secondary text-white py-3 rounded-xl hover:opacity-90 transition-all duration-300 shadow-lg hover:shadow-xl"
      >
        Order Now
      </motion.button>
    </motion.div>
  );
};

function DNAProfiling() {
  const [user, setUser] = useState(null);
  const [dnaKitTypes, setDNAKitTypes] = useState([]);
  const [dnaKitOrders, setDNAKitOrders] = useState([]);
  const [dnaReports, setDNAReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedKit, setSelectedKit] = useState(null);
  const [isShippingModalOpen, setIsShippingModalOpen] = useState(false);
  const [orderConfirmation, setOrderConfirmation] = useState(null);
  const scrollContainerRef = useRef(null);
  const [orderLoading, setOrderLoading] = useState(false);
  const [pdfUploadLoading, setPdfUploadLoading] = useState(false);
  const [pdfUploadError, setPdfUploadError] = useState(null);
  const fileInputRef = useRef(null);

  // Dynamic section expansion states
  const [isOrdersSectionExpanded, setIsOrdersSectionExpanded] = useState(false);
  const [isKitTypesSectionExpanded, setIsKitTypesSectionExpanded] = useState(true);
  const [isReportsSectionExpanded, setIsReportsSectionExpanded] = useState(false);

  // Fetch detailed reports for completed orders
  const fetchDNAReports = useCallback(async (orders) => {
    try {
      console.group('DNA Reports Fetch');
      console.log('Current DNA Kit Orders:', orders);

      // Find orders with 'RESULTS_GENERATED' status
      const completedOrders = orders.filter(order => order.status === 'RESULTS_GENERATED');
      console.log('Completed Orders:', completedOrders);

      // If no completed orders, log and return
      if (completedOrders.length === 0) {
        console.log('No orders with RESULTS_GENERATED status');
        setDNAReports([]);
        setIsReportsSectionExpanded(false);
      console.groupEnd();
        return;
      }

      // Fetch reports for completed orders
      const reportsPromises = completedOrders.map(order => {
        console.log(`Fetching report for order: ${order.id}`);
        return apiClient.get(`/dna-profile/reports/${order.id}/`)
          .catch(err => {
            console.error(`Failed to fetch report for order ${order.id}:`, err);
            return null;
          });
      });

      const reportsResponses = await Promise.all(reportsPromises);
      
      const reports = reportsResponses
        .filter(response => response && response.data)
        .map(response => response.data);

      console.log('Fetched Reports:', reports);

      setDNAReports(reports);
      
      // Expand reports section if reports exist
      setIsReportsSectionExpanded(reports.length > 0);
      
      console.groupEnd();
    } catch (err) {
      console.error('Comprehensive DNA Reports Fetch Error', err);
      setError(err.response?.data?.error || 'Failed to load DNA reports');
      
      // Ensure reports section is collapsed if there's an error
      setDNAReports([]);
      setIsReportsSectionExpanded(false);
    }
  }, []);

  // Fetch DNA Kit Data
  const fetchDNAKitData = useCallback(async () => {
      try {
        setLoading(true);
        
        // Fetch user profile
        const profileResponse = await apiClient.get('/authentication/profile/');
        const userData = profileResponse.data;
        
        // Combine user and profile data
        const combinedUserData = {
          first_name: userData.user.first_name,
          last_name: userData.user.last_name,
          username: userData.user.username,
          email: userData.user.email,
          phone_number: userData.phone_number || '',
          address_line1: userData.address_line1 || '',
          address_line2: userData.address_line2 || '',
          city: userData.city || '',
          state: userData.state || '',
          postal_code: userData.postal_code || '',
          country: userData.country || 'India'
        };
        
        setUser(combinedUserData);
        
        // Fetch DNA Kit Types
        const kitTypesResponse = await apiClient.get('/dna-profile/kit-types/');
        
        // Extract results from paginated response
        const rawKitTypes = kitTypesResponse.data?.results || [];
        
        // Transform kit types to ensure proper structure
        const transformedKitTypes = rawKitTypes.map(kit => ({
          id: kit.id,
          name: kit.name,
          category: kit.category,
          description: kit.description,
          price: parseFloat(kit.price),
          processing_time_days: kit.processing_time_days,
          features: Array.isArray(kit.features) 
            ? kit.features 
            : (typeof kit.features === 'string' 
              ? kit.features.split(',').map(f => f.trim())
              : ['No features available'])
        }));
        
        setDNAKitTypes(transformedKitTypes);

        // Fetch DNA Kit Orders
        const ordersResponse = await apiClient.get('/dna-profile/orders/');
        
        // Extract results from paginated response
        const ordersData = ordersResponse.data?.results || [];

        // Set orders data
        setDNAKitOrders(ordersData);

      // Dynamically set section visibility
      setIsOrdersSectionExpanded(ordersData.length > 0);
      setIsKitTypesSectionExpanded(ordersData.length === 0);

      // Fetch reports for completed orders
      if (ordersData.length > 0) {
        await fetchDNAReports(ordersData);
      }

        setLoading(false);
      } catch (err) {
        console.group('DNA Kit Orders Fetch Error');
        console.error('Failed to fetch DNA kit data', err);
        console.log('Error Response:', err.response);
        console.groupEnd();

        setError(err.response?.data?.error || 'Failed to load DNA kit information');
        setLoading(false);
        
        // Ensure we set empty arrays in case of error
        setDNAKitTypes([]);
        setDNAKitOrders([]);
      }
  }, [fetchDNAReports]);

  // Fetch data on component mount
  useEffect(() => {
    fetchDNAKitData();
  }, []); // Empty dependency array to run only once on mount

  // Horizontal scroll functionality
  const handleScroll = (direction) => {
    if (scrollContainerRef.current) {
      const { current } = scrollContainerRef;
      const scrollAmount = current.offsetWidth * 0.8;
      current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  const handleOrderKit = async (shippingData) => {
    try {
      // Set loading state before starting the order process
      setOrderLoading(true);

      // Destructure shipping and consent data
      const { 
        consented, 
        consent_type, 
        full_name, 
        address_line1, 
        address_line2, 
        city, 
        state, 
        postal_code, 
        country, 
        phone_number 
      } = shippingData;

      // Transform address to match backend requirements EXACTLY
      const transformedAddress = {
        street: `${address_line1} ${address_line2 || ''}`.trim(),
        city: city,
        state: state,
        zip_code: postal_code,
        country: country
      };

      console.group('DNA Kit Order Payload');
      console.log('Kit Type:', selectedKit);
      console.log('Shipping Address:', transformedAddress);
      console.log('Consent Data:', { consented, consent_type });
      console.groupEnd();

      const response = await apiClient.post('/dna-profile/orders/create/', {
        kit_type: selectedKit.id,
        shipping_address: transformedAddress,
        consented: consented,
        consent_type: consent_type
      });
      
      // Set order confirmation details
      setOrderConfirmation({
        kitName: selectedKit.name,
        orderNumber: response.data.order_number || 'N/A',
        processingTime: selectedKit.processing_time_days
      });
      
      // Close the shipping modal
      setIsShippingModalOpen(false);
      setSelectedKit(null);
    } catch (err) {
      console.group('DNA Kit Order Error');
      console.error('Failed to order DNA Kit', err);
      
      // More detailed error logging
      if (err.response) {
        console.log('Error Response:', err.response);
        console.log('Error Status:', err.response.status);
        console.log('Error Data:', err.response.data);
      }
      console.groupEnd();

      // More detailed error handling
      const errorMessage = err.response 
        ? (err.response.data.shipping_address 
          ? err.response.data.shipping_address[0] 
          : err.response.data.error || 'Failed to order DNA Kit')
        : err.message || 'Failed to order DNA Kit';
      
      // Set error state instead of using alert
      setError(errorMessage);
    } finally {
      // Ensure loading state is reset
      setOrderLoading(false);
    }
  };

  const initiateKitOrder = (kit) => {
    console.group('Initiating Kit Order');
    console.log('Selected Kit:', kit);
    console.log('Current User Data:', user);
    
    setSelectedKit(kit);
    setIsShippingModalOpen(true);
  };

  const handlePDFUpload = async (event, order) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'application/pdf') {
      setPdfUploadError('Please upload a PDF file.');
      return;
    }

    // Validate order/kit
    if (!order || !order.kit_id) {
      setPdfUploadError('Please select a valid DNA kit for this upload.');
      return;
    }

    const formData = new FormData();
    formData.append('kit_id', order.kit_id);
    formData.append('pdf_file', file);

    try {
      setPdfUploadLoading(true);
      setPdfUploadError(null);

      const response = await apiClient.post('/dna-profile/pdf/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Show success message with 20-minute processing time
      setOrderConfirmation({
        kitName: `PDF Upload for ${order.kit_type_name || 'DNA Kit'}`,
        orderNumber: response.data.upload_id,
        processingTime: 20  // Set to 20 minutes
      });

      // Update the specific order to mark PDF as uploaded
      const updatedOrders = dnaKitOrders.map(existingOrder => 
        existingOrder.id === order.id 
          ? { ...existingOrder, pdf_uploaded: true } 
          : existingOrder
      );
      setDNAKitOrders(updatedOrders);

      // Reset file input
      event.target.value = '';
    } catch (err) {
      console.error('PDF Upload Error:', err.response || err);
      setPdfUploadError(
        err.response?.data?.error || 
        'Failed to upload PDF. Please try again.'
      );
    } finally {
      setPdfUploadLoading(false);
    }
  };

  // Modify useEffect to log and handle reports fetching
  useEffect(() => {
    console.group('DNA Kit Orders Effect');
    console.log('Current DNA Kit Orders:', dnaKitOrders);
    
    // Fetch reports when orders are loaded and not empty
    if (dnaKitOrders.length > 0) {
      fetchDNAReports(dnaKitOrders);
    }
    
    console.groupEnd();
  }, [dnaKitOrders, fetchDNAReports]);

  // Render loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-brand-primary mb-4 mx-auto"></div>
          <p className="text-gray-600 dark:text-gray-300">Loading DNA Kit Orders...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative max-w-md" role="alert">
          <strong className="font-bold block mb-2">Error Loading DNA Kit Orders</strong>
          <span className="block">{error}</span>
        </div>
      </div>
    );
  }

  // Render main component
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

        {/* Shipping Address Modal */}
        <AnimatePresence>
          {isShippingModalOpen && (
            <ShippingAddressModal
              isOpen={isShippingModalOpen}
              onClose={() => {
                setIsShippingModalOpen(false);
                setSelectedKit(null);
              }}
              onSubmit={handleOrderKit}
              initialUser={user}
              orderLoading={orderLoading}
            />
          )}
        </AnimatePresence>

        {/* Order Confirmation Modal */}
        {orderConfirmation && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              className="bg-[#1E2029] rounded-2xl shadow-2xl p-8 max-w-md w-full border border-gray-700"
            >
              <div className="text-center">
                <h2 className="text-2xl font-bold text-[#6B7AFA] mb-6">
                  Order Confirmed
                </h2>
                <div className="space-y-4 mb-6">
                  <p className="text-white">
                    <span className="text-gray-400 mr-2">Kit:</span> 
                    {orderConfirmation.kitName}
                  </p>
                  <p className="text-white">
                    <span className="text-gray-400 mr-2">Order Number:</span> 
                    {orderConfirmation.orderNumber}
                  </p>
                  <p className="text-white">
                    <span className="text-gray-400 mr-2">Estimated Processing Time:</span> 
                    {orderConfirmation.processingTime} days
                  </p>
                </div>
                <button
                  onClick={() => {
                    // Trigger data refetch when closing the popup
                    setOrderConfirmation(null);
                    fetchDNAKitData();
                  }}
                  className="px-6 py-2 bg-[#6B7AFA] text-white rounded-xl hover:bg-[#5A69E2] transition-colors w-full"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* DNA Profiling Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-full mx-auto"
        >
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-primary to-brand-secondary bg-clip-text text-transparent">
              DNA Profiling
            </h1>
            <p className="mt-4 text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Unlock personalized insights into your genetic health and wellness
            </p>
          </div>

          {error && (
            <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 text-red-800 dark:text-red-200 px-4 py-3 rounded-xl mb-6 text-center">
              {error}
            </div>
          )}

          {/* DNA Kit Types Section */}
          <section className="mb-12">
            <div 
              className="flex justify-between items-center cursor-pointer"
              onClick={() => setIsKitTypesSectionExpanded(!isKitTypesSectionExpanded)}
            >
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                DNA Kits
              </h2>
              <motion.div
                animate={{ rotate: isKitTypesSectionExpanded ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  className="h-6 w-6 text-gray-600 dark:text-gray-300" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M19 9l-7 7-7-7" 
                  />
                </svg>
              </motion.div>
            </div>
            
            <AnimatePresence>
              {isKitTypesSectionExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ 
                    opacity: 1, 
                    height: 'auto',
                    transition: { 
                      duration: 0.3,
                      type: "tween"
                    }
                  }}
                  exit={{ 
                    opacity: 0, 
                    height: 0,
                    transition: { 
                      duration: 0.2,
                      type: "tween"
                    }
                  }}
                >
          {dnaKitTypes.length === 0 ? (
                    <div className="text-center text-gray-600 dark:text-gray-400 mt-4">
              No DNA kit types are currently available.
            </div>
          ) : (
            // Horizontally Scrollable DNA Kit Types
                    <div className="relative w-full mt-4">
              {/* Scroll Left Button */}
              <button 
                onClick={() => handleScroll('left')}
                className="absolute left-0 top-1/2 transform -translate-y-1/2 z-10 bg-white dark:bg-gray-800 shadow-lg rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-600 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              {/* Scroll Right Button */}
              <button 
                onClick={() => handleScroll('right')}
                className="absolute right-0 top-1/2 transform -translate-y-1/2 z-10 bg-white dark:bg-gray-800 shadow-lg rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-600 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>

              {/* Scrollable Container */}
              <div 
                ref={scrollContainerRef}
                className="w-full overflow-x-auto pb-6 no-scrollbar"
              >
                <div className="flex space-x-6 py-4">
                  {dnaKitTypes.map((kit, index) => (
                    <motion.div 
                      key={kit.id}
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
                    >
                      <DNAKitCard 
                        kit={kit} 
                        onOrder={initiateKitOrder} 
                        userEmail={user?.email}
                      />
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </motion.div>
              )}
            </AnimatePresence>
          </section>

        {/* DNA Kit Orders Section */}
        <section className="mb-12">
            <div 
              className="flex justify-between items-center cursor-pointer"
              onClick={() => setIsOrdersSectionExpanded(!isOrdersSectionExpanded)}
            >
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            Your DNA Kit Orders
          </h2>
              <motion.div
                animate={{ rotate: isOrdersSectionExpanded ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  className="h-6 w-6 text-gray-600 dark:text-gray-300" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M19 9l-7 7-7-7" 
                  />
                </svg>
              </motion.div>
            </div>
            
            <AnimatePresence>
              {isOrdersSectionExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ 
                    opacity: 1, 
                    height: 'auto',
                    transition: { 
                      duration: 0.3,
                      type: "tween"
                    }
                  }}
                  exit={{ 
                    opacity: 0, 
                    height: 0,
                    transition: { 
                      duration: 0.2,
                      type: "tween"
                    }
                  }}
                >
          {!Array.isArray(dnaKitOrders) || dnaKitOrders.length === 0 ? (
                    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 text-center mt-4">
              <p className="text-gray-600 dark:text-gray-300">
                You haven't ordered any DNA kits yet.
              </p>
            </div>
          ) : (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
              {dnaKitOrders.map((order) => (
                <motion.div
                  key={order.id || Math.random().toString()}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-6 relative"
                >
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-brand-primary">
                      {order.kit_type_name || 'Unknown Kit'}
                    </h3>
                    <span 
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        order.status === 'COMPLETED' 
                          ? 'bg-green-100 text-green-800' 
                          : order.status === 'PROCESSING' 
                          ? 'bg-yellow-100 text-yellow-800' 
                          : order.status === 'PENDING'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {order.status || 'Unknown'}
                    </span>
                  </div>
                  <div className="space-y-2 mb-4">
                    <p className="text-gray-600 dark:text-gray-300">
                      <strong>Order ID:</strong> {order.order_id || 'N/A'}
                    </p>
                    <p className="text-gray-600 dark:text-gray-300">
                              <strong>Amount:</strong> ₹{order.total_amount || 'N/A'}
                    </p>
                    <p className="text-gray-600 dark:text-gray-300">
                      <strong>Ordered On:</strong> {order.order_date ? new Date(order.order_date).toLocaleDateString() : 'N/A'}
                    </p>
                    <p className="text-gray-600 dark:text-gray-300">
                      <strong>Category:</strong> {order.kit_category || 'N/A'}
                    </p>
                    {order.estimated_completion_date && (
                      <p className="text-gray-600 dark:text-gray-300">
                        <strong>Est. Completion:</strong> {new Date(order.estimated_completion_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                          
                          {/* PDF Upload Section */}
                          <div className="mt-4 border-t border-gray-200 dark:border-gray-700 pt-4">
                            {order.status === 'RESULTS_GENERATED' ? (
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => {
                                    // Set the selected report to this order's report
                                    const selectedReport = dnaReports.find(
                                      report => report.kit_id === order.kit_id
                                    );
                                    
                                    // If report exists, scroll to and expand the reports section
                                    if (selectedReport) {
                                      // Ensure reports section is expanded
                                      setIsReportsSectionExpanded(true);
                                      
                                      // Optional: Scroll to the reports section
                                      const reportsSection = document.getElementById('dna-reports-section');
                                      if (reportsSection) {
                                        reportsSection.scrollIntoView({ 
                                          behavior: 'smooth', 
                                          block: 'start' 
                                        });
                                      }
                                    } else {
                                      // Optionally handle case where no report is found
                                      console.warn('No report found for this DNA kit order');
                                    }
                                  }}
                                  className="w-full px-4 py-2 bg-brand-primary text-white rounded-lg hover:bg-brand-secondary transition-colors text-sm font-medium"
                                >
                                  Show Report
                                </button>
                              </div>
                            ) : (
                              <>
                                <h4 className="text-md font-semibold mb-2 text-gray-700 dark:text-gray-300">
                                  Upload DNA Results
                                </h4>
                                <div className="flex items-center space-x-2">
                                  <input 
                                    type="file" 
                                    ref={fileInputRef}
                                    accept=".pdf"
                                    onChange={(e) => handlePDFUpload(e, order)}
                                    className="hidden"
                                    id={`pdf-upload-${order.id}`}
                                    disabled={
                                      pdfUploadLoading || 
                                      order.status !== 'COMPLETED' || 
                                      order.pdf_uploaded === true
                                    }
                                  />
                                  <label 
                                    htmlFor={`pdf-upload-${order.id}`}
                                    className={`
                                      w-full px-4 py-2 rounded-lg text-center cursor-pointer transition-all
                                      ${order.status === 'COMPLETED' && !order.pdf_uploaded
                                        ? 'bg-brand-primary text-white hover:bg-brand-secondary' 
                                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'}
                                    `}
                                  >
                                    {order.pdf_uploaded 
                                      ? 'Results Uploaded' 
                                      : (pdfUploadLoading 
                                        ? 'Uploading...' 
                                        : 'Upload PDF Results')
                                    }
                                  </label>
                                </div>
                                {pdfUploadError && (
                                  <p className="text-red-500 text-xs mt-2">{pdfUploadError}</p>
                                )}
                              </>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
                </motion.div>
              )}
            </AnimatePresence>
        </section>

          {/* DNA Reports Section */}
          <section 
            id="dna-reports-section"
            className="mb-12"
          >
            <div 
              className="flex justify-between items-center cursor-pointer"
              onClick={() => setIsReportsSectionExpanded(!isReportsSectionExpanded)}
            >
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                Your DNA Reports
              </h2>
              <motion.div
                animate={{ rotate: isReportsSectionExpanded ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  className="h-6 w-6 text-gray-600 dark:text-gray-300" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M19 9l-7 7-7-7" 
                  />
                </svg>
              </motion.div>
            </div>
            
            <AnimatePresence>
              {isReportsSectionExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ 
                    opacity: 1, 
                    height: 'auto',
                    transition: { 
                      duration: 0.3,
                      type: "tween"
                    }
                  }}
                  exit={{ 
                    opacity: 0, 
                    height: 0,
                    transition: { 
                      duration: 0.2,
                      type: "tween"
                    }
                  }}
                >
                  {dnaReports.length === 0 ? (
                    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 text-center mt-4">
                      <p className="text-gray-600 dark:text-gray-300">
                        No DNA reports are available yet.
                      </p>
                    </div>
                  ) : (
                    <div className="w-full grid grid-cols-1 gap-6 mt-4">
                      {dnaReports.map((report) => (
                        <motion.div
                          key={report.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3 }}
                          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8 w-full"
                        >
                          <div className="grid md:grid-cols-3 gap-8">
                            {/* Left Column: Detailed Personal & Kit Information */}
                            <div className="col-span-1 space-y-6">
                              <div>
                                <h3 className="text-2xl font-bold text-brand-primary mb-4">
                                  {report.kit_type_name || 'DNA Report'}
                                </h3>
                                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  <div className="space-y-3">
                                    <div>
                                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                                        Report ID
                                      </p>
                                      <p className="font-medium text-gray-800 dark:text-gray-200">
                                        {report.report_id}
                                      </p>
                                    </div>
                                    <div>
                                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                                        Generated Date
                                      </p>
                                      <p className="font-medium text-gray-800 dark:text-gray-200">
                                        {new Date(report.generated_date).toLocaleDateString()}
                                      </p>
                                    </div>
                                    <div>
                                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                                        Validated By
                                      </p>
                                      <p className="font-medium text-gray-800 dark:text-gray-200">
                                        {report.validated_by || 'Automated System'}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Risk Profile Summary */}
                              <div>
                                <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                  Risk Profile Overview
                                </h4>
                                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        High Risk Traits
                                      </span>
                                      <span className="font-medium text-red-600">
                                        {report.key_findings?.filter(f => 
                                          f.risk_score > 70
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Medium Risk Traits
                                      </span>
                                      <span className="font-medium text-yellow-600">
                                        {report.key_findings?.filter(f => 
                                          f.risk_score > 30 && f.risk_score <= 70
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Low Risk Traits
                                      </span>
                                      <span className="font-medium text-green-600">
                                        {report.key_findings?.filter(f => 
                                          f.risk_score <= 30
                                        ).length || 0}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Genetic Insights Box */}
                              <div>
                                <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                  Genetic Insights
                                </h4>
                                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Total Traits Analyzed
                                      </span>
                                      <span className="font-medium text-gray-800 dark:text-gray-200">
                                        {report.key_findings?.length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Unique Genetic Markers
                                      </span>
                                      <span className="font-medium text-gray-800 dark:text-gray-200">
                                        {report.key_findings?.reduce((acc, finding) => 
                                          acc + (finding.genetic_markers?.length || 0), 0) || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Analysis Methodology
                                      </span>
                                      <span className="font-medium text-gray-800 dark:text-gray-200">
                                        Comprehensive Genomic
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Confidence Level
                                      </span>
                                      <span 
                                        className={`font-medium ${
                                          report.quality_score > 80 
                                            ? 'text-green-600' 
                                            : report.quality_score > 60 
                                            ? 'text-yellow-600' 
                                            : 'text-red-600'
                                        }`}
                                      >
                                        {report.quality_score > 80 
                                          ? 'High' 
                                          : report.quality_score > 60 
                                          ? 'Medium' 
                                          : 'Low'}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Personal Health Insights Box */}
                              <div>
                                <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                  Personal Health Profile
                                </h4>
                                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
                                        </svg>
                                        High-Risk Conditions
                                      </span>
                                      <span className="font-medium text-red-600">
                                        {report.key_findings?.filter(f => 
                                          f.risk_score > 70
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-yellow-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                        </svg>
                                        Medium-Risk Conditions
                                      </span>
                                      <span className="font-medium text-yellow-600">
                                        {report.key_findings?.filter(f => 
                                          f.risk_score > 30 && f.risk_score <= 70
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                        </svg>
                                        Low-Risk Conditions
                                      </span>
                                      <span className="font-medium text-green-600">
                                        {report.key_findings?.filter(f => 
                                          f.risk_score <= 30
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Overall Health Risk
                                      </span>
                                      <span 
                                        className={`font-medium ${
                                          report.key_findings?.filter(f => f.risk_score > 70).length > 0
                                            ? 'text-red-600' 
                                            : report.key_findings?.filter(f => f.risk_score > 30).length > 0
                                            ? 'text-yellow-600' 
                                            : 'text-green-600'
                                        }`}
                                      >
                                        {report.key_findings?.filter(f => f.risk_score > 70).length > 0
                                          ? 'High' 
                                          : report.key_findings?.filter(f => f.risk_score > 30).length > 0
                                          ? 'Medium' 
                                          : 'Low'}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Lifestyle Impact Assessment */}
                              <div>
                                <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                  Lifestyle Impact Analysis
                                </h4>
                                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                                          <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                                        </svg>
                                        Nutrition Sensitivity
                                      </span>
                                      <span className="font-medium text-blue-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'NUTRITION'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
                                        </svg>
                                        Exercise Response
                                      </span>
                                      <span className="font-medium text-green-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'FITNESS'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-purple-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                                        </svg>
                                        Metabolism Markers
                                      </span>
                                      <span className="font-medium text-purple-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'METABOLISM'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Lifestyle Adaptability
                                      </span>
                                      <span 
                                        className={`font-medium ${
                                          report.key_findings?.filter(f => f.risk_score > 70).length > 2
                                            ? 'text-red-600' 
                                            : report.key_findings?.filter(f => f.risk_score > 30).length > 2
                                            ? 'text-yellow-600' 
                                            : 'text-green-600'
                                        }`}
                                      >
                                        {report.key_findings?.filter(f => f.risk_score > 70).length > 2
                                          ? 'Low' 
                                          : report.key_findings?.filter(f => f.risk_score > 30).length > 2
                                          ? 'Moderate' 
                                          : 'High'}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Ancestry and Ethnicity Insights */}
                              <div>
                                <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                  Ancestry Composition
                                </h4>
                                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  <div className="space-y-3">
                                    {report.ancestry_composition?.map((ancestry, index) => (
                                      <div key={index} className="flex justify-between items-center">
                                        <span className="text-sm text-gray-600 dark:text-gray-400">
                                          {ancestry.region}
                                        </span>
                                        <div className="flex items-center">
                                          <div 
                                            className="h-2 rounded-full mr-2"
                                            style={{
                                              width: `${ancestry.percentage}%`,
                                              backgroundColor: ancestry.color || '#4A90E2'
                                            }}
                                          />
                                          <span className="font-medium text-gray-800 dark:text-gray-200">
                                            {ancestry.percentage}%
                                          </span>
                                        </div>
                                      </div>
                                    )) || (
                                      <p className="text-sm text-gray-500 text-center">
                                        Ancestry data not available
                                      </p>
                                    )}
                                    <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
                                      Genetic Diversity Score: {report.genetic_diversity_score || 'N/A'}
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Genetic Predisposition Screening */}
                              <div>
                                <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                  Genetic Predisposition
                                </h4>
                                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                        </svg>
                                        High-Risk Genetic Markers
                                      </span>
                                      <span className="font-medium text-red-600">
                                        {report.key_findings?.filter(f => 
                                          f.risk_score > 70 && f.category === 'PREDISPOSITION'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-yellow-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                        </svg>
                                        Medium-Risk Genetic Markers
                                      </span>
                                      <span className="font-medium text-yellow-600">
                                        {report.key_findings?.filter(f => 
                                          f.risk_score > 30 && f.risk_score <= 70 && f.category === 'PREDISPOSITION'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                        </svg>
                                        Low-Risk Genetic Markers
                                      </span>
                                      <span className="font-medium text-green-600">
                                        {report.key_findings?.filter(f => 
                                          f.risk_score <= 30 && f.category === 'PREDISPOSITION'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Genetic Risk Profile
                                      </span>
                                      <span 
                                        className={`font-medium ${
                                          report.key_findings?.filter(f => 
                                            f.risk_score > 70 && f.category === 'PREDISPOSITION'
                                          ).length > 0
                                            ? 'text-red-600' 
                                            : report.key_findings?.filter(f => 
                                              f.risk_score > 30 && f.category === 'PREDISPOSITION'
                                            ).length > 0
                                            ? 'text-yellow-600' 
                                            : 'text-green-600'
                                        }`}
                                      >
                                        {report.key_findings?.filter(f => 
                                          f.risk_score > 70 && f.category === 'PREDISPOSITION'
                                        ).length > 0
                                          ? 'High' 
                                          : report.key_findings?.filter(f => 
                                            f.risk_score > 30 && f.category === 'PREDISPOSITION'
                                          ).length > 0
                                          ? 'Medium' 
                                          : 'Low'}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Environmental Interaction Profile */}
                              <div>
                                <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                  Environmental Interactions
                                </h4>
                                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-teal-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 002 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
                                        </svg>
                                        Climate Sensitivity
                                      </span>
                                      <span className="font-medium text-teal-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'CLIMATE'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-indigo-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
                                        </svg>
                                        Pollution Exposure
                                      </span>
                                      <span className="font-medium text-indigo-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'POLLUTION'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-orange-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                                        </svg>
                                        Seasonal Adaptability
                                      </span>
                                      <span className="font-medium text-orange-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'SEASONAL'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Environmental Resilience
                                      </span>
                                      <span 
                                        className={`font-medium ${
                                          report.key_findings?.filter(f => f.risk_score > 70 && 
                                            ['CLIMATE', 'POLLUTION', 'SEASONAL'].includes(f.category)
                                          ).length > 1
                                            ? 'text-red-600' 
                                            : report.key_findings?.filter(f => f.risk_score > 30 && 
                                              ['CLIMATE', 'POLLUTION', 'SEASONAL'].includes(f.category)
                                            ).length > 1
                                            ? 'text-yellow-600' 
                                            : 'text-green-600'
                                        }`}
                                      >
                                        {report.key_findings?.filter(f => f.risk_score > 70 && 
                                          ['CLIMATE', 'POLLUTION', 'SEASONAL'].includes(f.category)
                                        ).length > 1
                                          ? 'Low' 
                                          : report.key_findings?.filter(f => f.risk_score > 30 && 
                                            ['CLIMATE', 'POLLUTION', 'SEASONAL'].includes(f.category)
                                          ).length > 1
                                          ? 'Moderate' 
                                          : 'High'}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Pharmacogenomic Insights */}
                              <div>
                                <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                  Pharmacogenomic Profile
                                </h4>
                                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.757 2.635a1 1 0 01-.894 1.591h-.001a1 1 0 01-.895-.557l-1.757-2.635-1.055.528A1 1 0 0111 12h2a1 1 0 100-2h-2a1 1 0 01-.895-1.447l1.105-2.21L4 5.475V13a1 1 0 001 1h10a1 1 0 001-1V6a1 1 0 00-1-1h-1V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v1h-1a1 1 0 00-1 1v3a1 1 0 002 0V7h1v1a1 1 0 001 1h4a3 3 0 013 3v4a3 3 0 01-3 3H5a3 3 0 01-3-3V5a3 3 0 013-3h5z" clipRule="evenodd" />
                                        </svg>
                                        Medication Metabolism
                                      </span>
                                      <span className="font-medium text-blue-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'DRUG_METABOLISM'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-purple-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356.257c.604.6.654 1.57.655 2.072.001.529-.055 1.517-.654 2.117l-4.708 4.654a1 1 0 00.708 1.707H7a1 1 0 001-1v-4.764a4.8 4.8 0 01.105-1.085L14.723 4.9a1 1 0 00-.5-1.94l-4.829 1.233z" />
                                        </svg>
                                        Drug Sensitivity
                                      </span>
                                      <span className="font-medium text-purple-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'DRUG_SENSITIVITY'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
                                        </svg>
                                        Treatment Efficacy
                                      </span>
                                      <span className="font-medium text-green-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'TREATMENT_EFFICACY'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Pharmacogenomic Risk
                                      </span>
                                      <span 
                                        className={`font-medium ${
                                          report.key_findings?.filter(f => 
                                            f.risk_score > 70 && 
                                            ['DRUG_METABOLISM', 'DRUG_SENSITIVITY', 'TREATMENT_EFFICACY'].includes(f.category)
                                          ).length > 0
                                            ? 'text-red-600' 
                                            : report.key_findings?.filter(f => 
                                              f.risk_score > 30 && 
                                              ['DRUG_METABOLISM', 'DRUG_SENSITIVITY', 'TREATMENT_EFFICACY'].includes(f.category)
                                            ).length > 0
                                            ? 'text-yellow-600' 
                                            : 'text-green-600'
                                        }`}
                                      >
                                        {report.key_findings?.filter(f => 
                                          f.risk_score > 70 && 
                                          ['DRUG_METABOLISM', 'DRUG_SENSITIVITY', 'TREATMENT_EFFICACY'].includes(f.category)
                                        ).length > 0
                                          ? 'High' 
                                          : report.key_findings?.filter(f => 
                                            f.risk_score > 30 && 
                                            ['DRUG_METABOLISM', 'DRUG_SENSITIVITY', 'TREATMENT_EFFICACY'].includes(f.category)
                                          ).length > 0
                                          ? 'Medium' 
                                          : 'Low'}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Genetic Wellness Indicators */}
                              <div>
                                <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                  Wellness Genetic Markers
                                </h4>
                                <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
                                        </svg>
                                        Stress Resilience
                                      </span>
                                      <span className="font-medium text-red-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'STRESS_RESILIENCE'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                        </svg>
                                        Sleep Quality Markers
                                      </span>
                                      <span className="font-medium text-green-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'SLEEP_QUALITY'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                                          <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                                        </svg>
                                        Mental Wellness
                                      </span>
                                      <span className="font-medium text-blue-600">
                                        {report.key_findings?.filter(f => 
                                          f.category === 'MENTAL_WELLNESS'
                                        ).length || 0}
                                      </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-sm text-gray-600 dark:text-gray-400">
                                        Overall Wellness Score
                                      </span>
                                      <span 
                                        className={`font-medium ${
                                          report.key_findings?.filter(f => 
                                            f.risk_score > 70 && 
                                            ['STRESS_RESILIENCE', 'SLEEP_QUALITY', 'MENTAL_WELLNESS'].includes(f.category)
                                          ).length > 1
                                            ? 'text-red-600' 
                                            : report.key_findings?.filter(f => 
                                              f.risk_score > 30 && 
                                              ['STRESS_RESILIENCE', 'SLEEP_QUALITY', 'MENTAL_WELLNESS'].includes(f.category)
                                            ).length > 1
                                            ? 'text-yellow-600' 
                                            : 'text-green-600'
                                        }`}
                                      >
                                        {report.key_findings?.filter(f => 
                                          f.risk_score > 70 && 
                                          ['STRESS_RESILIENCE', 'SLEEP_QUALITY', 'MENTAL_WELLNESS'].includes(f.category)
                                        ).length > 1
                                          ? 'Low' 
                                          : report.key_findings?.filter(f => 
                                            f.risk_score > 30 && 
                                            ['STRESS_RESILIENCE', 'SLEEP_QUALITY', 'MENTAL_WELLNESS'].includes(f.category)
                                          ).length > 1
                                          ? 'Moderate' 
                                          : 'High'}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Download Report Section */}
                              {report.report_file_url && (
                                <div>
                                  <a 
                                    href={report.report_file_url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="w-full block px-4 py-3 bg-brand-primary text-white rounded-lg hover:bg-brand-secondary transition-colors text-center font-medium"
                                  >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 inline-block mr-2" viewBox="0 0 20 20" fill="currentColor">
                                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                                    </svg>
                                    Download Full Report
                                  </a>
                                </div>
                              )}
                            </div>

                            {/* Right Columns: Detailed Findings */}
                            <div className="col-span-2 space-y-6">
                              {/* Summary Section */}
                              <div>
                                <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                  Report Summary
                                </h4>
                                <p className="text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                  {report.summary || 'No summary available'}
                                </p>
                              </div>

                              {/* Key Findings Section */}
                              {report.key_findings && report.key_findings.length > 0 && (
                                <div>
                                  <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                    Key Findings
                                  </h4>
                                  <div className="grid md:grid-cols-2 gap-4">
                                    {report.key_findings.map((finding, index) => (
                                      <div 
                                        key={index} 
                                        className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg"
                                      >
                                        <p className="font-medium text-gray-800 dark:text-gray-200 mb-2">
                                          {finding.trait || 'Unknown Trait'}
                                        </p>
                                        <p className="text-gray-600 dark:text-gray-400 mb-2">
                                          Value: {finding.value || 'N/A'}
                                        </p>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* Recommendations Section */}
                              {report.recommendations && (
                                <div>
                                  <h4 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">
                                    Recommendations
                                  </h4>
                                  <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                    {report.recommendations.split('\n').map((rec, index) => (
                                      <li key={index}>{rec.trim()}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </section>

        </motion.div>

      </main>

      {/* Custom Styles */}
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(59, 130, 246, 0.5);
          border-radius: 10px;
        }
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
}

export default DNAProfiling;
