"""
Authentication Models Tests
Tests for UserProfile, PasswordResetToken, SubscriptionPlan, and UserSubscription models
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from authentication.models import UserProfile, PasswordResetToken, SubscriptionPlan, UserSubscription


class AuthenticationModelTests(TestCase):
    """Test cases for Authentication models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_creation(self):
        """Test UserProfile is created automatically when User is created"""
        profile = UserProfile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(str(profile), f"UserProfile(user_id={self.user.id})")
    
    def test_user_profile_fields(self):
        """Test UserProfile field access"""
        profile = self.user.profile
        
        # Test setting profile fields
        profile.phone_number = '+1234567890'
        profile.date_of_birth = '1990-01-01'
        profile.save()
        
        profile.refresh_from_db()
        self.assertEqual(profile.phone_number, '+1234567890')
        self.assertEqual(str(profile.date_of_birth), '1990-01-01')
    
    def test_password_reset_token_creation(self):
        """Test PasswordResetToken creation and validation"""
        token = PasswordResetToken.objects.create(user=self.user)
        self.assertIsNotNone(token.token)
        self.assertGreater(len(token.token), 30)  # URL-safe token should be reasonably long
        self.assertFalse(token.is_used)
        self.assertTrue(token.is_valid())
    
    def test_password_reset_token_expiry(self):
        """Test PasswordResetToken expiry"""
        token = PasswordResetToken.objects.create(user=self.user)
        # Manually set created_at to past
        token.created_at = timezone.now() - timedelta(hours=25)
        token.save()
        self.assertFalse(token.is_valid())
    
    def test_subscription_plan_model(self):
        """Test SubscriptionPlan model"""
        plan = SubscriptionPlan.objects.create(
            name="Premium",
            plan_type="PREMIUM",
            description="Premium features",
            price=29.99,
            billing_cycle="MONTHLY"
        )
        self.assertIn("Premium", str(plan))
        self.assertTrue(plan.is_active) 