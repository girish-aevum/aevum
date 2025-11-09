from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response
from rest_framework import generics, status, filters
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from aevum.pagination import StandardResultsPagination, SmallResultsPagination

from .models import SubscriptionPlan, UserSubscription, SubscriptionHistory


class IsSuperAdminOrStaff(BasePermission):
    """
    Custom permission to only allow superadmin or staff users to access admin endpoints
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_superuser or request.user.is_staff)
        )
from .subscription_serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
    SubscriptionUpgradeSerializer,
    SubscriptionHistorySerializer,
    SubscriptionUsageSerializer,
    CancelSubscriptionSerializer
)


# Subscription Plans Views

@extend_schema(
    tags=['Authentication'],
    summary='List Subscription Plans',
    description='Get all available subscription plans for users to choose from.'
)
class SubscriptionPlanListView(generics.ListAPIView):
    """
    List all available subscription plans - No authentication required
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]
    pagination_class = SmallResultsPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price', 'sort_order', 'name']
    ordering = ['sort_order', 'price']
    
    def get_queryset(self):
        """Get active subscription plans"""
        return SubscriptionPlan.objects.filter(is_active=True)


@extend_schema(
    tags=['Authentication'],
    summary='Get Subscription Plan Details',
    description='Get detailed information about a specific subscription plan.'
)
class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific subscription plan
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_active=True)


# User Subscription Views

@extend_schema(
    tags=['Authentication'],
    summary='Get My Subscription',
    description='Get the current user\'s subscription details and usage information.'
)
class MySubscriptionView(generics.RetrieveAPIView):
    """
    Get current user's subscription details
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get or create user subscription"""
        subscription, created = UserSubscription.objects.get_or_create(
            user=self.request.user,
            defaults={
                'plan': self._get_free_plan(),
                'status': 'ACTIVE',
                'payment_method': 'FREE'
            }
        )
        return subscription
    
    def _get_free_plan(self):
        """Get the default free plan"""
        free_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='FREE',
            defaults={
                'name': 'Free Plan',
                'description': 'Basic features at no cost',
                'price': 0.00,
                'billing_cycle': 'MONTHLY',
                'dna_kits_included': 1,
                'mood_entries_limit': 30,
                'ai_insights_enabled': False,
                'priority_support': False,
                'data_export_enabled': False,
                'api_access_enabled': False,
            }
        )
        return free_plan


@extend_schema(
    tags=['Authentication'],
    summary='Get Subscription Usage',
    description='Get detailed usage statistics for the current user\'s subscription.'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_usage(request):
    """
    Get subscription usage statistics
    """
    try:
        subscription = request.user.subscription
    except UserSubscription.DoesNotExist:
        return Response({
            'error': 'No subscription found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Calculate usage statistics
    dna_kits_limit = subscription.plan.dna_kits_included
    dna_kits_remaining = max(0, dna_kits_limit - subscription.dna_kits_used) if dna_kits_limit > 0 else -1
    
    mood_entries_limit = subscription.plan.mood_entries_limit
    mood_entries_remaining = max(0, mood_entries_limit - subscription.mood_entries_this_month) if mood_entries_limit > 0 else -1
    
    # Features availability
    features_available = {
        'dna_kits': subscription.can_use_feature('dna_kits'),
        'mood_entries': subscription.can_use_feature('mood_entries'),
        'ai_insights': subscription.can_use_feature('ai_insights'),
        'priority_support': subscription.can_use_feature('priority_support'),
        'data_export': subscription.can_use_feature('data_export'),
        'api_access': subscription.can_use_feature('api_access'),
    }
    
    usage_data = {
        'dna_kits_used': subscription.dna_kits_used,
        'dna_kits_limit': dna_kits_limit,
        'dna_kits_remaining': dna_kits_remaining,
        'mood_entries_this_month': subscription.mood_entries_this_month,
        'mood_entries_limit': mood_entries_limit,
        'mood_entries_remaining': mood_entries_remaining,
        'features_available': features_available,
        'usage_percentages': subscription.usage_percentage
    }
    
    serializer = SubscriptionUsageSerializer(usage_data)
    return Response(serializer.data)


@extend_schema(
    tags=['Authentication'],
    summary='Upgrade Subscription',
    description='Upgrade or change the current user\'s subscription plan.'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upgrade_subscription(request):
    """
    Upgrade user's subscription plan
    """
    serializer = SubscriptionUpgradeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    plan_id = serializer.validated_data['plan_id']
    payment_method = serializer.validated_data['payment_method']
    
    try:
        new_plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        return Response({
            'error': 'Invalid subscription plan'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get or create user subscription
    subscription, created = UserSubscription.objects.get_or_create(
        user=request.user,
        defaults={
            'plan': new_plan,
            'status': 'ACTIVE',
            'payment_method': payment_method
        }
    )
    
    if not created:
        # Update existing subscription
        old_plan = subscription.plan
        subscription.upgrade_plan(new_plan)
        subscription.payment_method = payment_method
        subscription.save()
        
        # Create history record
        SubscriptionHistory.objects.create(
            user=request.user,
            subscription=subscription,
            action_type='UPGRADED',
            old_plan=old_plan,
            new_plan=new_plan,
            amount=new_plan.price,
            notes=f"Upgraded from {old_plan.name} to {new_plan.name}"
        )
    else:
        # Create history record for new subscription
        SubscriptionHistory.objects.create(
            user=request.user,
            subscription=subscription,
            action_type='CREATED',
            new_plan=new_plan,
            amount=new_plan.price,
            notes=f"Created new subscription with {new_plan.name}"
        )
    
    # In a real implementation, you would integrate with payment processor here
    # For now, we'll simulate successful payment for non-free plans
    if not new_plan.is_free:
        subscription.last_payment_date = timezone.now()
        subscription.last_payment_amount = new_plan.price
        subscription.save()
    
    return Response({
        'message': 'Subscription upgraded successfully',
        'subscription': UserSubscriptionSerializer(subscription).data
    })


@extend_schema(
    tags=['Authentication'],
    summary='Cancel Subscription',
    description='Cancel the current user\'s subscription.'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """
    Cancel user's subscription
    """
    try:
        subscription = request.user.subscription
    except UserSubscription.DoesNotExist:
        return Response({
            'error': 'No active subscription found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CancelSubscriptionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    reason = serializer.validated_data.get('reason', '')
    immediate = serializer.validated_data.get('immediate', False)
    
    # Cancel the subscription
    subscription.cancel_subscription(reason)
    
    # Create history record
    SubscriptionHistory.objects.create(
        user=request.user,
        subscription=subscription,
        action_type='CANCELLED',
        old_plan=subscription.plan,
        notes=f"Subscription cancelled. Reason: {reason}" if reason else "Subscription cancelled"
    )
    
    return Response({
        'message': 'Subscription cancelled successfully',
        'immediate': immediate,
        'access_until': subscription.end_date
    })


@extend_schema(
    tags=['Authentication'],
    summary='Subscription History',
    description='Get the current user\'s subscription history and payment records.'
)
class SubscriptionHistoryListView(generics.ListAPIView):
    """
    Get user's subscription history
    """
    serializer_class = SubscriptionHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    ordering = ['-created_at']
    
    def get_queryset(self):
        return SubscriptionHistory.objects.filter(user=self.request.user)


# Admin Views for Subscription Management

@extend_schema(
    tags=['Authentication'],
    summary='Admin - List All Subscriptions',
    description='Admin endpoint to list all user subscriptions with filtering options. Requires superadmin or staff privileges.'
)
class AdminSubscriptionListView(generics.ListAPIView):
    """
    Admin view to list all user subscriptions
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsSuperAdminOrStaff]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'plan__name']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = UserSubscription.objects.select_related('user', 'plan')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by plan type
        plan_type = self.request.query_params.get('plan_type')
        if plan_type:
            queryset = queryset.filter(plan__plan_type=plan_type)
        
        # Filter by active/inactive
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() == 'true':
                queryset = queryset.filter(
                    status='ACTIVE',
                    end_date__gte=timezone.now()
                )
            else:
                queryset = queryset.exclude(
                    status='ACTIVE',
                    end_date__gte=timezone.now()
                )
        
        return queryset


@extend_schema(
    tags=['Authentication'],
    summary='Admin - Create/Update Subscription Plan',
    description='Admin endpoint to create or update subscription plans. Requires superadmin or staff privileges.'
)
class AdminSubscriptionPlanView(generics.ListCreateAPIView):
    """
    Admin view to manage subscription plans
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsSuperAdminOrStaff]
    pagination_class = SmallResultsPagination
    ordering = ['sort_order', 'price']
    
    def get_queryset(self):
        return SubscriptionPlan.objects.all()


@extend_schema(
    tags=['Authentication'],
    summary='Admin - Update Subscription Plan',
    description='Admin endpoint to update or delete subscription plans. Requires superadmin or staff privileges.'
)
class AdminSubscriptionPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin view to manage individual subscription plans
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsSuperAdminOrStaff]
    queryset = SubscriptionPlan.objects.all() 