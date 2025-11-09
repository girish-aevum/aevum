from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import UserProfile, PasswordResetToken, SubscriptionPlan, UserSubscription, SubscriptionHistory


class UserRegistrationSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, min_length=8)
	password_confirm = serializers.CharField(write_only=True)
	phone_number = serializers.CharField(required=False, allow_blank=True, max_length=64)
	
	class Meta:
		model = User
		fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'phone_number')
		extra_kwargs = {
			'email': {'required': True},
			'first_name': {'required': True},
			'last_name': {'required': True},
		}
	
	def validate_email(self, value):
		"""Check if email is already registered"""
		if User.objects.filter(email=value).exists():
			raise serializers.ValidationError("A user with this email already exists.")
		return value
	
	def validate_username(self, value):
		"""Check if username is already taken"""
		if User.objects.filter(username=value).exists():
			raise serializers.ValidationError("A user with this username already exists.")
		return value
	
	def validate_password(self, value):
		"""Validate password using Django's password validators"""
		try:
			validate_password(value)
		except ValidationError as e:
			raise serializers.ValidationError(e.messages)
		return value
	
	def validate(self, attrs):
		"""Check if passwords match"""
		if attrs['password'] != attrs['password_confirm']:
			raise serializers.ValidationError("Passwords do not match.")
		return attrs
	
	def create(self, validated_data):
		"""Create user and UserProfile"""
		# Remove password_confirm and phone_number from validated_data
		validated_data.pop('password_confirm')
		phone_number = validated_data.pop('phone_number', None)
		
		# Create user
		user = User.objects.create_user(**validated_data)
		
		# Create UserProfile with phone number
		if phone_number:
			UserProfile.objects.update_or_create(
				user=user,
				defaults={'phone_number': phone_number}
			)
		
		return user


class ForgotPasswordSerializer(serializers.Serializer):
	email = serializers.EmailField()
	
	def validate_email(self, value):
		"""Check if email exists in the system"""
		if not User.objects.filter(email=value).exists():
			raise serializers.ValidationError("No account found with this email address.")
		return value


class PasswordResetSerializer(serializers.Serializer):
	token = serializers.CharField(max_length=100)
	new_password = serializers.CharField(write_only=True, min_length=8)
	confirm_password = serializers.CharField(write_only=True)
	
	def validate_new_password(self, value):
		"""Validate password using Django's password validators"""
		try:
			validate_password(value)
		except ValidationError as e:
			raise serializers.ValidationError(e.messages)
		return value
	
	def validate(self, attrs):
		"""Validate token and password confirmation"""
		token = attrs.get('token')
		new_password = attrs.get('new_password')
		confirm_password = attrs.get('confirm_password')
		
		# Check if passwords match
		if new_password != confirm_password:
			raise serializers.ValidationError("Passwords do not match.")
		
		# Validate token
		try:
			reset_token = PasswordResetToken.objects.get(token=token)
			if not reset_token.is_valid():
				raise serializers.ValidationError("Invalid or expired reset token.")
			attrs['reset_token'] = reset_token
		except PasswordResetToken.DoesNotExist:
			raise serializers.ValidationError("Invalid reset token.")
		
		return attrs


class ChangePasswordSerializer(serializers.Serializer):
	current_password = serializers.CharField(write_only=True)
	new_password = serializers.CharField(write_only=True, min_length=8)
	confirm_password = serializers.CharField(write_only=True)
	
	def validate_new_password(self, value):
		"""Validate password using Django's password validators"""
		try:
			validate_password(value)
		except ValidationError as e:
			raise serializers.ValidationError(e.messages)
		return value
	
	def validate(self, attrs):
		"""Validate current password and password confirmation"""
		new_password = attrs.get('new_password')
		confirm_password = attrs.get('confirm_password')
		
		# Check if new passwords match
		if new_password != confirm_password:
			raise serializers.ValidationError("New passwords do not match.")
		
		return attrs
	
	def validate_current_password(self, value):
		"""Validate current password"""
		user = self.context['request'].user
		if not user.check_password(value):
			raise serializers.ValidationError("Current password is incorrect.")
		return value


class ProfileImageSerializer(serializers.ModelSerializer):
	profile_image_url = serializers.SerializerMethodField()
	
	class Meta:
		model = UserProfile
		fields = ('profile_image', 'profile_image_url')
	
	def get_profile_image_url(self, obj):
		"""Return the full URL for the profile image"""
		if obj.profile_image:
			request = self.context.get('request')
			if request:
				return request.build_absolute_uri(obj.profile_image.url)
			return obj.profile_image.url
		return None
	
	def validate_profile_image(self, value):
		"""Validate profile image"""
		if value:
			# Check file size (max 5MB)
			max_size = 5 * 1024 * 1024
			if value.size > max_size:
				raise serializers.ValidationError("Image file too large. Maximum size is 5MB.")
			
			# Check file format
			allowed_formats = ['jpeg', 'jpg', 'png', 'gif']
			file_extension = value.name.split('.')[-1].lower()
			if file_extension not in allowed_formats:
				raise serializers.ValidationError(
					f"Invalid file format. Allowed formats: {', '.join(allowed_formats)}"
				)
		
		return value


class UserProfileSerializer(serializers.ModelSerializer):
	profile_image_url = serializers.SerializerMethodField()
	user = serializers.SerializerMethodField()
	
	class Meta:
		model = UserProfile
		read_only_fields = ('id', 'created_at', 'updated_at')
		fields = '__all__'
	
	def get_profile_image_url(self, obj):
		"""Return the full URL for the profile image"""
		if obj.profile_image:
			request = self.context.get('request')
			if request:
				return request.build_absolute_uri(obj.profile_image.url)
			return obj.profile_image.url
		return None
	
	def get_user(self, obj):
		"""Return user details"""
		user = obj.user
		return {
			'id': user.id,
			'username': user.username,
			'email': user.email,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'full_name': (f"{user.first_name} {user.last_name}").strip() or user.username,
			'is_active': user.is_active,
			'date_joined': user.date_joined,
			'last_login': user.last_login,
		}
	
	def validate_profile_image(self, value):
		"""Validate profile image"""
		if value:
			# Check file size (max 5MB)
			max_size = 5 * 1024 * 1024
			if value.size > max_size:
				raise serializers.ValidationError("Image file too large. Maximum size is 5MB.")
			
			# Check file format
			allowed_formats = ['jpeg', 'jpg', 'png', 'gif']
			file_extension = value.name.split('.')[-1].lower()
			if file_extension not in allowed_formats:
				raise serializers.ValidationError(
					f"Invalid file format. Allowed formats: {', '.join(allowed_formats)}"
				)
		
		return value


class UserListSerializer(serializers.ModelSerializer):
	"""
	Serializer for user listing - excludes sensitive information
	"""
	profile_image_url = serializers.SerializerMethodField()
	full_name = serializers.SerializerMethodField()
	profile_completion = serializers.SerializerMethodField()
	last_login_formatted = serializers.SerializerMethodField()
	date_joined_formatted = serializers.SerializerMethodField()
	is_active_status = serializers.SerializerMethodField()
	
	class Meta:
		model = User
		fields = [
			'id',
			'username',
			'email',
			'first_name',
			'last_name',
			'full_name',
			'is_active',
			'is_active_status',
			'date_joined',
			'date_joined_formatted',
			'last_login',
			'last_login_formatted',
			'profile_image_url',
			'profile_completion'
		]
		read_only_fields = ['id', 'date_joined', 'last_login']
	
	def get_profile_image_url(self, obj):
		"""Get profile image URL if exists"""
		try:
			if obj.profile.profile_image:
				request = self.context.get('request')
				if request:
					return request.build_absolute_uri(obj.profile.profile_image.url)
				return obj.profile.profile_image.url
		except UserProfile.DoesNotExist:
			pass
		return None
	
	def get_full_name(self, obj):
		"""Get user's full name"""
		if obj.first_name and obj.last_name:
			return f"{obj.first_name} {obj.last_name}"
		elif obj.first_name:
			return obj.first_name
		elif obj.last_name:
			return obj.last_name
		return obj.username
	
	def get_profile_completion(self, obj):
		"""Calculate profile completion percentage"""
		try:
			profile = obj.profile
			total_fields = 15  # Key profile fields to check
			completed_fields = 0
			
			# Check basic user fields
			if obj.first_name:
				completed_fields += 1
			if obj.last_name:
				completed_fields += 1
			if obj.email:
				completed_fields += 1
			
			# Check profile fields
			if profile.profile_image:
				completed_fields += 1
			if profile.date_of_birth:
				completed_fields += 1
			if profile.sex:
				completed_fields += 1
			if profile.phone_number:
				completed_fields += 1
			if profile.address_line1:
				completed_fields += 1
			if profile.city:
				completed_fields += 1
			if profile.state:
				completed_fields += 1
			if profile.country:
				completed_fields += 1
			if profile.postal_code:
				completed_fields += 1
			if profile.height_cm:
				completed_fields += 1
			if profile.weight_kg:
				completed_fields += 1
			if profile.occupation:
				completed_fields += 1
			
			return round((completed_fields / total_fields) * 100, 1)
		except UserProfile.DoesNotExist:
			# Only basic user fields completed
			basic_completed = sum([1 for field in [obj.first_name, obj.last_name, obj.email] if field])
			return round((basic_completed / total_fields) * 100, 1)
	
	def get_last_login_formatted(self, obj):
		"""Get formatted last login date"""
		if obj.last_login:
			return obj.last_login.strftime("%Y-%m-%d %H:%M")
		return "Never"
	
	def get_date_joined_formatted(self, obj):
		"""Get formatted date joined"""
		return obj.date_joined.strftime("%Y-%m-%d %H:%M")
	
	def get_is_active_status(self, obj):
		"""Get user active status as text"""
		return "Active" if obj.is_active else "Inactive"


class UserDetailSerializer(UserListSerializer):
	"""
	Extended serializer for user details with profile information
	"""
	profile = UserProfileSerializer(read_only=True)
	
	class Meta(UserListSerializer.Meta):
		fields = UserListSerializer.Meta.fields + [
			'profile',
			'is_staff',
		]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
	"""
	Serializer for subscription plans
	"""
	is_free = serializers.ReadOnlyField()
	monthly_price = serializers.ReadOnlyField()
	features = serializers.SerializerMethodField()
	
	class Meta:
		model = SubscriptionPlan
		fields = [
			'id',
			'name',
			'plan_type',
			'description',
			'price',
			'billing_cycle',
			'monthly_price',
			'is_free',
			'dna_kits_included',
			'mood_entries_limit',
			'ai_insights_enabled',
			'priority_support',
			'data_export_enabled',
			'api_access_enabled',
			'is_featured',
			'features'
		]
	
	def get_features(self, obj):
		"""Get formatted feature list"""
		features = []
		
		if obj.dna_kits_included > 0:
			features.append(f"{obj.dna_kits_included} DNA kits included")
		elif obj.dna_kits_included == 0 and obj.plan_type != 'FREE':
			features.append("Unlimited DNA kits")
		
		if obj.mood_entries_limit > 0:
			features.append(f"{obj.mood_entries_limit} mood entries per month")
		elif obj.mood_entries_limit == 0 and obj.plan_type != 'FREE':
			features.append("Unlimited mood entries")
		
		if obj.ai_insights_enabled:
			features.append("AI-powered insights")
		
		if obj.priority_support:
			features.append("Priority customer support")
		
		if obj.data_export_enabled:
			features.append("Data export capabilities")
		
		if obj.api_access_enabled:
			features.append("API access")
		
		return features


class UserSubscriptionSerializer(serializers.ModelSerializer):
	"""
	Serializer for user subscriptions
	"""
	plan = SubscriptionPlanSerializer(read_only=True)
	is_active = serializers.ReadOnlyField()
	days_remaining = serializers.ReadOnlyField()
	usage_percentage = serializers.ReadOnlyField()
	status_display = serializers.CharField(source='get_status_display', read_only=True)
	payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
	
	class Meta:
		model = UserSubscription
		fields = [
			'id',
			'plan',
			'status',
			'status_display',
			'start_date',
			'end_date',
			'next_billing_date',
			'payment_method',
			'payment_method_display',
			'last_payment_date',
			'last_payment_amount',
			'dna_kits_used',
			'mood_entries_this_month',
			'auto_renew',
			'is_active',
			'days_remaining',
			'usage_percentage'
		]
		read_only_fields = [
			'id', 'start_date', 'dna_kits_used', 'mood_entries_this_month',
			'last_payment_date', 'last_payment_amount'
		]


class SubscriptionUpgradeSerializer(serializers.Serializer):
	"""
	Serializer for subscription upgrades/changes
	"""
	plan_id = serializers.IntegerField()
	payment_method = serializers.ChoiceField(choices=UserSubscription.PAYMENT_METHODS, default='CREDIT_CARD')
	
	def validate_plan_id(self, value):
		"""Validate that the plan exists and is active"""
		try:
			plan = SubscriptionPlan.objects.get(id=value, is_active=True)
		except SubscriptionPlan.DoesNotExist:
			raise serializers.ValidationError("Invalid or inactive subscription plan.")
		return value


class SubscriptionHistorySerializer(serializers.ModelSerializer):
	"""
	Serializer for subscription history
	"""
	action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
	old_plan_name = serializers.CharField(source='old_plan.name', read_only=True)
	new_plan_name = serializers.CharField(source='new_plan.name', read_only=True)
	
	class Meta:
		model = SubscriptionHistory
		fields = [
			'id',
			'action_type',
			'action_type_display',
			'old_plan_name',
			'new_plan_name',
			'amount',
			'notes',
			'created_at'
		]


class SubscriptionUsageSerializer(serializers.Serializer):
	"""
	Serializer for subscription usage statistics
	"""
	dna_kits_used = serializers.IntegerField()
	dna_kits_limit = serializers.IntegerField()
	dna_kits_remaining = serializers.IntegerField()
	
	mood_entries_this_month = serializers.IntegerField()
	mood_entries_limit = serializers.IntegerField()
	mood_entries_remaining = serializers.IntegerField()
	
	features_available = serializers.DictField()
	usage_percentages = serializers.DictField()


class CancelSubscriptionSerializer(serializers.Serializer):
	"""
	Serializer for subscription cancellation
	"""
	reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
	immediate = serializers.BooleanField(default=False, help_text="Cancel immediately or at end of billing period") 