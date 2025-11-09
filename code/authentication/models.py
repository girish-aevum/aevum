import os
import secrets
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_image_size(image):
	"""Validate that the image is not too large (max 5MB)"""
	max_size = 5 * 1024 * 1024  # 5MB
	if image.size > max_size:
		raise ValidationError("Image file too large. Maximum size is 5MB.")


def user_profile_image_path(instance, filename):
	"""Generate upload path for user profile images"""
	# Get file extension
	ext = filename.split('.')[-1].lower()
	# Create filename: user_id_profile.extension
	filename = f"user_{instance.user.id}_profile.{ext}"
	# Return path: media/profile_images/user_id_profile.extension
	return os.path.join('profile_images', filename)


class PasswordResetToken(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
	token = models.CharField(max_length=100, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	used_at = models.DateTimeField(null=True, blank=True)
	is_used = models.BooleanField(default=False)
	
	class Meta:
		ordering = ['-created_at']
	
	def save(self, *args, **kwargs):
		if not self.token:
			self.token = secrets.token_urlsafe(32)
		super().save(*args, **kwargs)
	
	def is_valid(self):
		"""Check if token is valid (not used and not expired)"""
		if self.is_used:
			return False
		
		# Token expires after 1 hour
		expiry_time = self.created_at + timedelta(hours=1)
		return timezone.now() < expiry_time
	
	def mark_as_used(self):
		"""Mark token as used"""
		self.is_used = True
		self.used_at = timezone.now()
		self.save()
	
	def __str__(self):
		return f"PasswordResetToken for {self.user.username} - {'Used' if self.is_used else 'Active'}"


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

	# Profile Image
	profile_image = models.ImageField(
		upload_to=user_profile_image_path,
		null=True,
		blank=True,
		validators=[validate_image_size],
		help_text="Profile image (max 5MB, formats: JPG, PNG, GIF)"
	)

	# Demographics
	date_of_birth = models.DateField(null=True, blank=True)
	sex = models.CharField(max_length=50, null=True, blank=True)
	gender_identity = models.CharField(max_length=100, null=True, blank=True)
	blood_group = models.CharField(max_length=10, null=True, blank=True)

	# Physical metrics
	height_cm = models.FloatField(null=True, blank=True)
	weight_kg = models.FloatField(null=True, blank=True)
	waist_cm = models.FloatField(null=True, blank=True)
	hip_cm = models.FloatField(null=True, blank=True)

	# Contact & address
	phone_number = models.CharField(max_length=64, null=True, blank=True)
	address_line1 = models.CharField(max_length=255, null=True, blank=True)
	address_line2 = models.CharField(max_length=255, null=True, blank=True)
	city = models.CharField(max_length=100, null=True, blank=True)
	state = models.CharField(max_length=100, null=True, blank=True)
	country = models.CharField(max_length=100, null=True, blank=True)
	postal_code = models.CharField(max_length=20, null=True, blank=True)
	occupation = models.CharField(max_length=150, null=True, blank=True)

	# Lifestyle
	smoking_status = models.CharField(max_length=100, null=True, blank=True)
	alcohol_use = models.CharField(max_length=100, null=True, blank=True)
	physical_activity_level = models.CharField(max_length=100, null=True, blank=True)
	diet_type = models.CharField(max_length=100, null=True, blank=True)
	sleep_hours = models.FloatField(null=True, blank=True)
	stress_level = models.CharField(max_length=100, null=True, blank=True)

	# Medical history
	chronic_conditions = models.TextField(null=True, blank=True)
	surgeries = models.TextField(null=True, blank=True)
	allergies = models.TextField(null=True, blank=True)
	medications_current = models.TextField(null=True, blank=True)
	family_history = models.TextField(null=True, blank=True)
	vaccinations = models.TextField(null=True, blank=True)

	# Reproductive health
	reproductive_health_notes = models.TextField(null=True, blank=True)

	# Care team
	primary_physician_name = models.CharField(max_length=150, null=True, blank=True)
	primary_physician_contact = models.CharField(max_length=150, null=True, blank=True)

	# Insurance
	insurance_provider = models.CharField(max_length=150, null=True, blank=True)
	insurance_policy_number = models.CharField(max_length=150, null=True, blank=True)

	# Emergency contact
	emergency_contact_name = models.CharField(max_length=150, null=True, blank=True)
	emergency_contact_relationship = models.CharField(max_length=100, null=True, blank=True)
	emergency_contact_phone = models.CharField(max_length=64, null=True, blank=True)

	# Preferences & consents
	preferred_hospital = models.CharField(max_length=150, null=True, blank=True)
	communication_preferences = models.TextField(null=True, blank=True)
	language_preferences = models.TextField(null=True, blank=True)
	data_sharing_consent = models.BooleanField(default=False)
	research_consent = models.BooleanField(default=False)

	# Cross-domain IDs
	dna_profile_id = models.CharField(max_length=255, null=True, blank=True)

	# Timestamps
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"UserProfile(user_id={self.user_id})"


class SubscriptionPlan(models.Model):
	"""
	Subscription plans available for users
	"""
	PLAN_TYPES = [
		('FREE', 'Free'),
		('BASIC', 'Basic'),
		('PREMIUM', 'Premium'),
		('ENTERPRISE', 'Enterprise'),
	]
	
	BILLING_CYCLES = [
		('MONTHLY', 'Monthly'),
		('QUARTERLY', 'Quarterly'),
		('YEARLY', 'Yearly'),
		('LIFETIME', 'Lifetime'),
	]
	
	name = models.CharField(max_length=100, unique=True)
	plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default='FREE')
	description = models.TextField(blank=True, null=True)
	price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
	billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='MONTHLY')
	
	# Features and limits
	dna_kits_included = models.PositiveIntegerField(default=0, help_text="Number of DNA kits included")
	mood_entries_limit = models.PositiveIntegerField(default=0, help_text="Monthly mood entries limit (0 = unlimited)")
	ai_insights_enabled = models.BooleanField(default=False)
	priority_support = models.BooleanField(default=False)
	data_export_enabled = models.BooleanField(default=False)
	api_access_enabled = models.BooleanField(default=False)
	
	# Plan management
	is_active = models.BooleanField(default=True)
	is_featured = models.BooleanField(default=False)
	sort_order = models.PositiveIntegerField(default=0)
	
	# Timestamps
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['sort_order', 'price']
		verbose_name = 'Subscription Plan'
		verbose_name_plural = 'Subscription Plans'
	
	def __str__(self):
		return f"{self.name} ({self.get_plan_type_display()}) - ₹{self.price}/{self.get_billing_cycle_display().lower()}"
	
	@property
	def is_free(self):
		"""Check if this is a free plan"""
		return self.plan_type == 'FREE' or self.price == 0
	
	@property
	def monthly_price(self):
		"""Convert price to monthly equivalent for comparison"""
		if self.billing_cycle == 'MONTHLY':
			return self.price
		elif self.billing_cycle == 'QUARTERLY':
			return self.price / 3
		elif self.billing_cycle == 'YEARLY':
			return self.price / 12
		else:  # LIFETIME
			return 0


class UserSubscription(models.Model):
	"""
	User's subscription information
	"""
	STATUS_CHOICES = [
		('ACTIVE', 'Active'),
		('EXPIRED', 'Expired'),
		('CANCELLED', 'Cancelled'),
		('SUSPENDED', 'Suspended'),
		('PENDING', 'Pending'),
	]
	
	PAYMENT_METHODS = [
		('CREDIT_CARD', 'Credit Card'),
		('PAYPAL', 'PayPal'),
		('BANK_TRANSFER', 'Bank Transfer'),
		('CRYPTO', 'Cryptocurrency'),
		('FREE', 'Free Plan'),
	]
	
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
	plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
	
	# Subscription details
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
	start_date = models.DateTimeField(default=timezone.now)
	end_date = models.DateTimeField(null=True, blank=True)
	next_billing_date = models.DateTimeField(null=True, blank=True)
	
	# Payment information
	payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='FREE')
	last_payment_date = models.DateTimeField(null=True, blank=True)
	last_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	
	# Usage tracking
	dna_kits_used = models.PositiveIntegerField(default=0)
	mood_entries_this_month = models.PositiveIntegerField(default=0)
	last_usage_reset = models.DateTimeField(default=timezone.now)
	
	# Subscription management
	auto_renew = models.BooleanField(default=True)
	cancelled_at = models.DateTimeField(null=True, blank=True)
	cancellation_reason = models.TextField(blank=True, null=True)
	
	# External payment system references
	stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
	paypal_subscription_id = models.CharField(max_length=100, blank=True, null=True)
	
	# Timestamps
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		verbose_name = 'User Subscription'
		verbose_name_plural = 'User Subscriptions'
	
	def __str__(self):
		return f"{self.user.username} - {self.plan.name} ({self.get_status_display()})"
	
	@property
	def is_active(self):
		"""Check if subscription is currently active"""
		if self.status != 'ACTIVE':
			return False
		if self.end_date and timezone.now() > self.end_date:
			return False
		return True
	
	@property
	def days_remaining(self):
		"""Calculate days remaining in subscription"""
		if not self.end_date:
			return None
		remaining = self.end_date - timezone.now()
		return max(0, remaining.days)
	
	@property
	def usage_percentage(self):
		"""Calculate usage percentage for limited features"""
		usage_stats = {}
		
		if self.plan.dna_kits_included > 0:
			usage_stats['dna_kits'] = min(100, (self.dna_kits_used / self.plan.dna_kits_included) * 100)
		
		if self.plan.mood_entries_limit > 0:
			usage_stats['mood_entries'] = min(100, (self.mood_entries_this_month / self.plan.mood_entries_limit) * 100)
		
		return usage_stats
	
	def can_use_feature(self, feature):
		"""Check if user can use a specific feature"""
		if not self.is_active:
			return False
			
		feature_checks = {
			'dna_kits': self.plan.dna_kits_included == 0 or self.dna_kits_used < self.plan.dna_kits_included,
			'mood_entries': self.plan.mood_entries_limit == 0 or self.mood_entries_this_month < self.plan.mood_entries_limit,
			'ai_insights': self.plan.ai_insights_enabled,
			'priority_support': self.plan.priority_support,
			'data_export': self.plan.data_export_enabled,
			'api_access': self.plan.api_access_enabled,
		}
		
		return feature_checks.get(feature, False)
	
	def reset_monthly_usage(self):
		"""Reset monthly usage counters"""
		self.mood_entries_this_month = 0
		self.last_usage_reset = timezone.now()
		self.save()
	
	def upgrade_plan(self, new_plan):
		"""Upgrade to a new subscription plan"""
		self.plan = new_plan
		self.status = 'ACTIVE'
		self.save()
	
	def cancel_subscription(self, reason=None):
		"""Cancel the subscription"""
		self.status = 'CANCELLED'
		self.cancelled_at = timezone.now()
		self.auto_renew = False
		if reason:
			self.cancellation_reason = reason
		self.save()


class SubscriptionHistory(models.Model):
	"""
	Track subscription changes and payment history
	"""
	ACTION_TYPES = [
		('CREATED', 'Subscription Created'),
		('UPGRADED', 'Plan Upgraded'),
		('DOWNGRADED', 'Plan Downgraded'),
		('RENEWED', 'Subscription Renewed'),
		('CANCELLED', 'Subscription Cancelled'),
		('SUSPENDED', 'Subscription Suspended'),
		('REACTIVATED', 'Subscription Reactivated'),
		('PAYMENT_SUCCESS', 'Payment Successful'),
		('PAYMENT_FAILED', 'Payment Failed'),
	]
	
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription_history')
	subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='history')
	action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
	
	# Action details
	old_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='old_subscriptions')
	new_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_subscriptions')
	amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	
	# Additional information
	notes = models.TextField(blank=True, null=True)
	metadata = models.JSONField(default=dict, blank=True)
	
	# Timestamp
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Subscription History'
		verbose_name_plural = 'Subscription Histories'
	
	def __str__(self):
		return f"{self.user.username} - {self.get_action_type_display()} ({self.created_at.strftime('%Y-%m-%d')})"
