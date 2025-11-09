from rest_framework import serializers
from django.utils import timezone
from .models import SubscriptionPlan, UserSubscription, SubscriptionHistory


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