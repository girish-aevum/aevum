"""
Authentication API Tests
Tests for authentication API endpoints including login, registration, profile management, etc.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import tempfile
from PIL import Image
import os

from authentication.models import UserProfile, PasswordResetToken


class AuthenticationAPITests(APITestCase):
    """Test cases for Authentication API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        url = reverse('authentication:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Registration failed with status {response.status_code}")
            print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        url = reverse('authentication:register')
        data = self.user_data.copy()
        data['email'] = 'different@example.com'
        data['password_confirm'] = data['password']
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test user login endpoint"""
        url = reverse('authentication:login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('authentication:login')
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_logout(self):
        """Test user logout endpoint"""
        # First login to get tokens
        login_url = reverse('authentication:login')
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['tokens']['refresh']
        access_token = login_response.data['tokens']['access']
        
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Now logout
        logout_url = reverse('authentication:logout')
        logout_data = {'refresh_token': refresh_token}
        response = self.client.post(logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_get_user_profile(self):
        """Test getting user profile"""
        self.client.force_authenticate(user=self.user)
        url = reverse('authentication:my-profile')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['id'], self.user.id)
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        self.client.force_authenticate(user=self.user)
        url = reverse('authentication:my-profile')
        
        data = {
            'phone_number': '+1234567890',
            'height_cm': 175.5,
            'weight_kg': 70.0
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify changes
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.phone_number, '+1234567890')
        self.assertEqual(self.user.profile.height_cm, 175.5)
        self.assertEqual(self.user.profile.weight_kg, 70.0)
    
    def test_profile_image_upload(self):
        """Test profile image upload"""
        self.client.force_authenticate(user=self.user)
        url = reverse('authentication:profile-image-update')
        
        # Create a temporary image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            image = Image.new('RGB', (100, 100), color='red')
            image.save(tmp_file, format='JPEG')
            tmp_file.seek(0)
            
            with open(tmp_file.name, 'rb') as img_file:
                data = {'profile_image': img_file}
                response = self.client.patch(url, data, format='multipart')
        
        # Cleanup
        os.unlink(tmp_file.name)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.profile_image)
    
    def test_password_reset_request(self):
        """Test password reset request"""
        url = reverse('authentication:forgot-password')
        data = {'email': 'test@example.com'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check token was created
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())
    
    def test_password_reset_confirm(self):
        """Test password reset confirmation"""
        # Create reset token
        reset_token = PasswordResetToken.objects.create(user=self.user)
        
        url = reverse('authentication:reset-password')
        data = {
            'token': reset_token.token,
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        
        # Verify token was marked as used
        reset_token.refresh_from_db()
        self.assertTrue(reset_token.is_used) 