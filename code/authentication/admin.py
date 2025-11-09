from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, PasswordResetToken, SubscriptionPlan, UserSubscription, SubscriptionHistory


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
	list_display = ('user', 'token', 'created_at', 'is_used', 'used_at', 'is_valid_display')
	list_filter = ('is_used', 'created_at')
	search_fields = ('user__username', 'user__email', 'token')
	readonly_fields = ('token', 'created_at', 'used_at')
	ordering = ['-created_at']

	def is_valid_display(self, obj):
		return obj.is_valid()
	is_valid_display.short_description = 'Is Valid'
	is_valid_display.boolean = True

	def has_add_permission(self, request):
		return False  # Prevent manual creation through admin


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'date_of_birth', 'blood_group', 'phone_number', 'created_at')
	search_fields = ('user__username', 'user__email', 'phone_number', 'blood_group')
	list_filter = ('blood_group', 'data_sharing_consent', 'research_consent')
	readonly_fields = ('created_at', 'updated_at')

	fieldsets = (
		('User Link', {
			'fields': ('user', 'profile_image'),
		}),
		('Demographics', {
			'fields': (
				'date_of_birth', 'sex', 'gender_identity', 'blood_group',
			)
		}),
		('Physical Metrics', {
			'fields': (
				'height_cm', 'weight_kg', 'waist_cm', 'hip_cm',
			)
		}),
		('Contact & Address', {
			'fields': (
				'phone_number', 'address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code', 'occupation',
			)
		}),
		('Lifestyle', {
			'fields': (
				'smoking_status', 'alcohol_use', 'physical_activity_level', 'diet_type', 'sleep_hours', 'stress_level',
			)
		}),
		('Medical History', {
			'fields': (
				'chronic_conditions', 'surgeries', 'allergies', 'medications_current', 'family_history', 'vaccinations',
			)
		}),
		('Reproductive Health', {
			'fields': ('reproductive_health_notes',),
		}),
		('Care Team', {
			'fields': ('primary_physician_name', 'primary_physician_contact'),
		}),
		('Insurance', {
			'fields': ('insurance_provider', 'insurance_policy_number'),
		}),
		('Emergency Contact', {
			'fields': ('emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone'),
		}),
		('Preferences & Consents', {
			'fields': ('preferred_hospital', 'communication_preferences', 'language_preferences', 'data_sharing_consent', 'research_consent'),
		}),
		('Cross-domain IDs', {
			'fields': ('dna_profile_id',),
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at'),
		}),
	)


# Import subscription models
from .models import SubscriptionPlan, UserSubscription, SubscriptionHistory
from django.utils.html import format_html


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
	list_display = ('name', 'plan_type', 'price_display', 'billing_cycle', 'is_active', 'is_featured', 'subscribers_count')
	list_filter = ('plan_type', 'billing_cycle', 'is_active', 'is_featured')
	search_fields = ('name', 'description')
	ordering = ['sort_order', 'price']
	
	fieldsets = (
		('Basic Information', {
			'fields': ('name', 'plan_type', 'description', 'price', 'billing_cycle')
		}),
		('Features & Limits', {
			'fields': (
				'dna_kits_included', 'mood_entries_limit', 'ai_insights_enabled',
				'priority_support', 'data_export_enabled', 'api_access_enabled'
			)
		}),
		('Plan Management', {
			'fields': ('is_active', 'is_featured', 'sort_order')
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
	
	readonly_fields = ('created_at', 'updated_at')
	
	def price_display(self, obj):
		if obj.is_free:
			return format_html('<span style="color: green; font-weight: bold;">FREE</span>')
		return f"₹{obj.price}/{obj.get_billing_cycle_display().lower()}"
	price_display.short_description = 'Price'
	
	def subscribers_count(self, obj):
		count = obj.subscriptions.filter(status='ACTIVE').count()
		return format_html(f'<strong>{count}</strong>')
	subscribers_count.short_description = 'Active Subscribers'


class SubscriptionHistoryInline(admin.TabularInline):
	model = SubscriptionHistory
	extra = 0
	readonly_fields = ('action_type', 'old_plan', 'new_plan', 'amount', 'created_at')
	fields = ('action_type', 'old_plan', 'new_plan', 'amount', 'notes', 'created_at')
	ordering = ['-created_at']
	
	def has_add_permission(self, request, obj=None):
		return False


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
	list_display = ('user', 'plan', 'status_display', 'is_active_display', 'start_date', 'end_date', 'days_remaining_display')
	list_filter = ('status', 'plan__plan_type', 'payment_method', 'auto_renew')
	search_fields = ('user__username', 'user__email', 'plan__name')
	ordering = ['-created_at']
	inlines = [SubscriptionHistoryInline]
	
	fieldsets = (
		('Subscription Details', {
			'fields': ('user', 'plan', 'status', 'start_date', 'end_date', 'next_billing_date')
		}),
		('Payment Information', {
			'fields': ('payment_method', 'last_payment_date', 'last_payment_amount')
		}),
		('Usage Tracking', {
			'fields': ('dna_kits_used', 'mood_entries_this_month', 'last_usage_reset')
		}),
		('Subscription Management', {
			'fields': ('auto_renew', 'cancelled_at', 'cancellation_reason')
		}),
		('External References', {
			'fields': ('stripe_subscription_id', 'paypal_subscription_id'),
			'classes': ('collapse',)
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
	
	readonly_fields = ('created_at', 'updated_at')
	
	def status_display(self, obj):
		colors = {
			'ACTIVE': 'green',
			'EXPIRED': 'orange',
			'CANCELLED': 'red',
			'SUSPENDED': 'purple',
			'PENDING': 'blue'
		}
		color = colors.get(obj.status, 'black')
		return format_html(f'<span style="color: {color}; font-weight: bold;">{obj.get_status_display()}</span>')
	status_display.short_description = 'Status'
	
	def is_active_display(self, obj):
		return obj.is_active
	is_active_display.boolean = True
	is_active_display.short_description = 'Currently Active'
	
	def days_remaining_display(self, obj):
		days = obj.days_remaining
		if days is None:
			return 'N/A'
		elif days == 0:
			return format_html('<span style="color: red; font-weight: bold;">Expired</span>')
		elif days <= 7:
			return format_html(f'<span style="color: orange; font-weight: bold;">{days} days</span>')
		else:
			return f'{days} days'
	days_remaining_display.short_description = 'Days Remaining'


@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
	list_display = ('user', 'action_type_display', 'old_plan', 'new_plan', 'amount', 'created_at')
	list_filter = ('action_type', 'created_at')
	search_fields = ('user__username', 'user__email', 'old_plan__name', 'new_plan__name')
	ordering = ['-created_at']
	readonly_fields = ('created_at',)
	
	fieldsets = (
		('Action Details', {
			'fields': ('user', 'subscription', 'action_type', 'old_plan', 'new_plan', 'amount')
		}),
		('Additional Information', {
			'fields': ('notes', 'metadata')
		}),
		('Timestamp', {
			'fields': ('created_at',)
		}),
	)
	
	def action_type_display(self, obj):
		colors = {
			'CREATED': 'green',
			'UPGRADED': 'blue',
			'DOWNGRADED': 'orange',
			'RENEWED': 'green',
			'CANCELLED': 'red',
			'SUSPENDED': 'purple',
			'REACTIVATED': 'green',
			'PAYMENT_SUCCESS': 'green',
			'PAYMENT_FAILED': 'red',
		}
		color = colors.get(obj.action_type, 'black')
		return format_html(f'<span style="color: {color}; font-weight: bold;">{obj.get_action_type_display()}</span>')
	action_type_display.short_description = 'Action'
	
	def has_add_permission(self, request):
		return False  # History records should be created automatically
