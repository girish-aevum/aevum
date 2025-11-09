from django.urls import path, include
from .views import (
    health, 
    MyProfileView, 
    login, 
    logout, 
    register, 
    ProfileImageUpdateView,
    forgot_password,
    reset_password,
    change_password,
    validate_reset_token,
    UserListView,
    UserDetailView
)

# Import subscription views
from .subscription_views import (
    SubscriptionPlanListView,
    SubscriptionPlanDetailView,
    MySubscriptionView,
    subscription_usage,
    upgrade_subscription,
    cancel_subscription,
    SubscriptionHistoryListView,
    AdminSubscriptionListView,
    AdminSubscriptionPlanView,
    AdminSubscriptionPlanDetailView,
)

app_name = 'authentication'

urlpatterns = [
	path('health/', health, name='health'),
	path('register/', register, name='register'),
	path('login/', login, name='login'),
	path('logout/', logout, name='logout'),
	path('profile/', MyProfileView.as_view(), name='my-profile'),
	path('profile/image/', ProfileImageUpdateView.as_view(), name='profile-image-update'),
	path('forgot-password/', forgot_password, name='forgot-password'),
	path('validate-reset-token/', validate_reset_token, name='validate-reset-token'),
	path('reset-password/', reset_password, name='reset-password'),
	path('change-password/', change_password, name='change-password'),
	
	# Admin/Staff endpoints for user management
	path('users/', UserListView.as_view(), name='user-list'),
	path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
	
	# Subscription endpoints
	path('subscription/plans/', SubscriptionPlanListView.as_view(), name='subscription-plans'),
	path('subscription/plans/<int:pk>/', SubscriptionPlanDetailView.as_view(), name='subscription-plan-detail'),
	path('subscription/my-subscription/', MySubscriptionView.as_view(), name='my-subscription'),
	path('subscription/usage/', subscription_usage, name='subscription-usage'),
	path('subscription/upgrade/', upgrade_subscription, name='upgrade-subscription'),
	path('subscription/cancel/', cancel_subscription, name='cancel-subscription'),
	path('subscription/history/', SubscriptionHistoryListView.as_view(), name='subscription-history'),
	
	# Admin subscription endpoints
	path('subscription/admin/subscriptions/', AdminSubscriptionListView.as_view(), name='admin-subscriptions'),
	path('subscription/admin/plans/', AdminSubscriptionPlanView.as_view(), name='admin-subscription-plans'),
	path('subscription/admin/plans/<int:pk>/', AdminSubscriptionPlanDetailView.as_view(), name='admin-subscription-plan-detail'),
]
