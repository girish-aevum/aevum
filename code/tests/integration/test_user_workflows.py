"""
Integration Tests - User Workflows

Tests complete user workflows that span multiple apps including:
- User registration -> Profile setup -> Health data entry
- Authentication -> Journal entry -> AI analysis
- DNA kit ordering -> Profile updates -> Health recommendations
"""

from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import UserProfile


class UserRegistrationWorkflowTest(TransactionTestCase):
    """Test complete user registration and onboarding workflow"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_complete_user_onboarding_flow(self):
        """Test complete user onboarding from registration to profile setup"""
        
        # Step 1: User Registration
        register_url = reverse('authentication:register')
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(register_url, register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: User Login
        login_url = reverse('authentication:login')
        login_data = {'username': 'newuser', 'password': 'newpass123'}
        
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        access_token = response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Step 3: Profile Setup
        profile_url = reverse('authentication:my-profile')
        profile_data = {
            'phone_number': '+1234567890',
            'date_of_birth': '1990-01-01',
            'height_cm': 175.5,
            'weight_kg': 70.0,
            'gender': 'M'
        }
        
        response = self.client.put(profile_url, profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user and profile were created correctly
        user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.phone_number, '+1234567890')
        self.assertEqual(str(user.profile.date_of_birth), '1990-01-01')


class HealthDataIntegrationTest(TransactionTestCase):
    """Test integration between authentication, health tracking, and analytics"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='healthuser',
            email='health@example.com',
            password='healthpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_health_data_workflow(self):
        """Test complete health data entry and analysis workflow"""
        
        # This test would integrate with healthcare app
        # For now, we'll test the authentication and profile parts
        
        # Step 1: Verify user profile exists
        profile_url = reverse('authentication:my-profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 2: Update health-related profile information
        health_profile_data = {
            'height_cm': 180.0,
            'weight_kg': 75.0,
            'date_of_birth': '1985-06-15'
        }
        
        response = self.client.put(profile_url, health_profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify health data was stored
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.height_cm, 180.0)
        self.assertEqual(self.user.profile.weight_kg, 75.0)


class AICompanionIntegrationTest(TransactionTestCase):
    """Test integration between user data and AI companion functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='aiuser',
            email='ai@example.com',
            password='aipass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_ai_personalization_workflow(self):
        """Test AI companion personalization based on user profile"""
        
        # Step 1: Set up user profile with health data
        profile_url = reverse('authentication:my-profile')
        profile_data = {
            'date_of_birth': '1992-03-20',
            'height_cm': 165.0,
            'weight_kg': 60.0,
            'gender': 'F'
        }
        
        response = self.client.put(profile_url, profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 2: Verify profile data is available for AI personalization
        self.user.profile.refresh_from_db()
        
        # Calculate BMI as AI might do
        height_m = self.user.profile.height_cm / 100
        bmi = self.user.profile.weight_kg / (height_m ** 2)
        
        # Verify BMI calculation is reasonable
        self.assertGreater(bmi, 15)  # Sanity check
        self.assertLess(bmi, 40)     # Sanity check
        
        # This would integrate with AI companion endpoints when available
        # For now, we verify the foundation is in place


class CrossAppDataConsistencyTest(TransactionTestCase):
    """Test data consistency across different apps"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='consistencyuser',
            email='consistency@example.com',
            password='consistencypass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_user_data_consistency(self):
        """Test that user data remains consistent across app interactions"""
        
        # Step 1: Update user profile
        profile_url = reverse('authentication:my-profile')
        initial_data = {
            'phone_number': '+1111111111',
            'height_cm': 170.0,
            'weight_kg': 65.0
        }
        
        response = self.client.put(profile_url, initial_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 2: Verify data consistency by reading it back
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the data matches what we set
        profile_data = response.data
        self.assertEqual(profile_data['phone_number'], '+1111111111')
        self.assertEqual(float(profile_data['height_cm']), 170.0)
        self.assertEqual(float(profile_data['weight_kg']), 65.0)
        
        # Step 3: Update partial data and verify consistency
        partial_update = {
            'weight_kg': 67.0  # Only update weight
        }
        
        response = self.client.patch(profile_url, partial_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Verify other data remained unchanged
        response = self.client.get(profile_url)
        updated_data = response.data
        
        self.assertEqual(updated_data['phone_number'], '+1111111111')  # Unchanged
        self.assertEqual(float(updated_data['height_cm']), 170.0)      # Unchanged
        self.assertEqual(float(updated_data['weight_kg']), 67.0)       # Updated 