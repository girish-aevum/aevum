import axios from 'axios';

// Attempt to import jwt-decode, provide fallback if not available
let jwtDecode;
try {
  jwtDecode = require('jwt-decode').default;
} catch (error) {
  console.warn('jwt-decode not available, using basic token validation');
  jwtDecode = null;
}

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Function to handle token expiration and logout
const handleTokenExpiration = () => {
  // Clear authentication tokens
  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');

  // Redirect to login page
  window.location.href = '/login';
};

// Function to check if token is expired
const isTokenExpired = (token) => {
  // If jwt-decode is not available, assume token is valid
  if (!jwtDecode) {
    return false;
  }

  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch (error) {
    console.error('Error decoding token:', error);
    return true;
  }
};

// Function to refresh token
const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  if (!refreshToken) {
    handleTokenExpiration();
    return null;
  }

  try {
    const response = await axios.post('/api/authentication/token/refresh/', { 
      refresh: refreshToken 
    });

    const { access } = response.data;
    localStorage.setItem('token', access);
    return access;
  } catch (error) {
    console.error('Token refresh failed', error);
    handleTokenExpiration();
    return null;
  }
};

// Request interceptor for adding auth token and handling token refresh
apiClient.interceptors.request.use(
  async config => {
    let token = localStorage.getItem('token');
    
    // Check if token is expired or about to expire (within 5 minutes)
    if (token && isTokenExpired(token)) {
      try {
        token = await refreshToken();
        if (!token) {
          handleTokenExpiration();
          return Promise.reject(new Error('Token refresh failed'));
        }
      } catch (error) {
        handleTokenExpiration();
        return Promise.reject(error);
      }
    }

    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor for handling authentication errors
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // Check for unauthorized or token expired errors
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.error('Token expired or unauthorized access');
      
      // Prevent infinite refresh loop
      if (!originalRequest._retry) {
        originalRequest._retry = true;
        
        try {
          const newToken = await refreshToken();
          if (newToken) {
            // Retry the original request with the new token
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            return apiClient(originalRequest);
          }
        } catch (refreshError) {
          handleTokenExpiration();
        }
      }
      
      handleTokenExpiration();
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email, password) => {
    try {
      const response = await apiClient.post('/authentication/login/', { 
        username: email,
        password: password 
      });
      
      const { tokens, user } = response.data;
      
      // Ensure all necessary fields are present
      const userToStore = {
        id: user.id,
        username: user.username,
        email: user.email,
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        is_active: user.is_active,
        date_joined: user.date_joined,
        last_login: user.last_login
      };
      
      localStorage.setItem('token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      localStorage.setItem('user', JSON.stringify(userToStore));
      
      return userToStore;
    } catch (error) {
      // Standardize error handling
      if (error.response) {
        // The request was made and the server responded with a status code
        if (error.response.status === 401) {
          throw new Error('Invalid email or password');
        }
        throw new Error(error.response.data.error || 'Login failed');
      } else if (error.request) {
        // The request was made but no response was received
        throw new Error('No response from server. Please check your network connection.');
      } else {
        // Something happened in setting up the request
        throw new Error(error.message || 'An unexpected error occurred');
      }
    }
  },

  register: async (registrationData) => {
    try {
      // Add username field using email
      const registrationPayload = {
        ...registrationData,
        username: registrationData.email
      };

      const response = await apiClient.post('/authentication/register/', registrationPayload);
      return response.data;
    } catch (error) {
      console.error('Registration failed', error);
      throw error;
    }
  },

  logout: () => {
    handleTokenExpiration();
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    return !!token;
  },

  // Enhanced token validation
  isTokenValid: () => {
    const token = localStorage.getItem('token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!token || !refreshToken) {
      return false;
    }

    // If jwt-decode is not available, do a basic check
    if (!jwtDecode) {
      return !!token;
    }

    try {
      // Check if token is expired
      return !isTokenExpired(token);
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  }
};

export default apiClient; 