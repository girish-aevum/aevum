from django.urls import path
from .views import (
    health,
    EarlyAccessRequestCreateView,
    EarlyAccessRequestListView,
    EarlyAccessRequestDetailView,
    ContactMessageCreateView,
    ContactMessageListView,
    ContactMessageDetailView,
    DashboardStatsView,
    StaffUsersListView
)

app_name = 'dashboard'

urlpatterns = [
    # Health check
    path('health/', health, name='health'),
    
    # Public endpoints for form submissions
    path('early-access/', EarlyAccessRequestCreateView.as_view(), name='early-access-create'),
    path('contact/', ContactMessageCreateView.as_view(), name='contact-create'),
    
    # Admin endpoints for early access requests
    path('admin/early-access/', EarlyAccessRequestListView.as_view(), name='admin-early-access-list'),
    path('admin/early-access/<uuid:request_id>/', EarlyAccessRequestDetailView.as_view(), name='admin-early-access-detail'),
    
    # Admin endpoints for contact messages
    path('admin/contact-messages/', ContactMessageListView.as_view(), name='admin-contact-messages-list'),
    path('admin/contact-messages/<uuid:message_id>/', ContactMessageDetailView.as_view(), name='admin-contact-message-detail'),
    
    # Dashboard statistics
    path('admin/stats/', DashboardStatsView.as_view(), name='admin-dashboard-stats'),
    
    # Utility endpoints
    path('admin/staff-users/', StaffUsersListView.as_view(), name='admin-staff-users'),
]
