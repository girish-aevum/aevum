from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

from .models import EarlyAccessRequest, ContactMessage
from .serializers import (
    EarlyAccessRequestCreateSerializer,
    EarlyAccessRequestListSerializer,
    EarlyAccessRequestDetailSerializer,
    EarlyAccessRequestUpdateSerializer,
    ContactMessageCreateSerializer,
    ContactMessageListSerializer,
    ContactMessageDetailSerializer,
    ContactMessageUpdateSerializer,
    DashboardStatsSerializer,
    UserSerializer
)
from .email_utils import send_dashboard_emails

# Initialize logger
logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_info(request):
    """Get client information from request"""
    return {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERER', '')
    }


def get_early_access_client_info(request):
    """Get client information for EarlyAccessRequest model"""
    return {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')
    }


def get_contact_message_client_info(request):
    """Get client information for ContactMessage model"""
    return {
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERER', '')
    }


# Health Check
@extend_schema(tags=['Dashboard'])
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """Health check endpoint for dashboard app"""
    return Response({"status": "ok", "app": "dashboard"})


# Early Access Request Views
class EarlyAccessRequestCreateView(generics.CreateAPIView):
    """
    Public endpoint for submitting early access requests
    """
    queryset = EarlyAccessRequest.objects.all()
    serializer_class = EarlyAccessRequestCreateSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['Dashboard'],
        summary="Submit Early Access Request",
        description="Submit a request for early access to the Aevum Health platform",
        responses={
            201: {
                'description': 'Early access request submitted successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Thank you for your interest! We have received your early access request.',
                            'request_id': 'uuid-string',
                            'status': 'success'
                        }
                    }
                }
            }
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Get client information
            client_info = get_early_access_client_info(request)
            
            # Save the early access request
            early_access_request = serializer.save(**client_info)
            
            # Send email notifications
            email_results = send_dashboard_emails(early_access_request, 'early_access')
            
            # Log email results
            if email_results['user_email_sent']:
                logger.info(f"Confirmation email sent to user: {early_access_request.email}")
            else:
                logger.warning(f"Failed to send confirmation email to user: {early_access_request.email}")
                
            if email_results['admin_email_sent']:
                logger.info(f"Admin notification sent for early access request: {early_access_request.email}")
            else:
                logger.warning(f"Failed to send admin notification for early access request: {early_access_request.email}")
            
            if email_results['errors']:
                logger.error(f"Email errors for early access request {early_access_request.email}: {email_results['errors']}")
            
            return Response({
                'message': 'Thank you for your interest! We have received your early access request.',
                'request_id': str(early_access_request.request_id),
                'status': 'success',
                'emails_sent': {
                    'user_confirmation': email_results['user_email_sent'],
                    'admin_notification': email_results['admin_email_sent']
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': 'There were errors in your submission.',
            'errors': serializer.errors,
            'status': 'error'
        }, status=status.HTTP_400_BAD_REQUEST)


class EarlyAccessRequestListView(generics.ListAPIView):
    """
    Admin endpoint for listing early access requests
    """
    queryset = EarlyAccessRequest.objects.all()
    serializer_class = EarlyAccessRequestListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'primary_interest']
    search_fields = ['email', 'full_name', 'phone_number']
    ordering_fields = ['created_at', 'updated_at', 'contacted_at']
    ordering = ['-created_at']
    
    @extend_schema(
        tags=['Dashboard'],
        summary="List Early Access Requests (Admin)",
        description="List all early access requests with filtering and search capabilities",
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by status'
            ),
            OpenApiParameter(
                name='priority',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by priority'
            ),
            OpenApiParameter(
                name='primary_interest',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by primary interest'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in email, full name, or phone number'
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(
        tags=['Dashboard'],
        summary="Get Early Access Request Details (Admin)",
        description="Get detailed information about a specific early access request"
    ),
    put=extend_schema(
        tags=['Dashboard'],
        summary="Update Early Access Request (Admin)",
        description="Update the status and tracking information of an early access request"
    ),
    patch=extend_schema(
        tags=['Dashboard'],
        summary="Update Early Access Request (Admin)",
        description="Update the status and tracking information of an early access request"
    )
)
class EarlyAccessRequestDetailView(generics.RetrieveUpdateAPIView):
    """
    Admin endpoint for viewing and updating early access requests
    """
    queryset = EarlyAccessRequest.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = 'request_id'
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EarlyAccessRequestDetailSerializer
        return EarlyAccessRequestUpdateSerializer


# Contact Message Views
class ContactMessageCreateView(generics.CreateAPIView):
    """
    Public endpoint for submitting contact messages
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageCreateSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['Dashboard'],
        summary="Submit Contact Message",
        description="Submit a contact message through the website contact form",
        responses={
            201: {
                'description': 'Contact message submitted successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Thank you for contacting us! We will respond to your message soon.',
                            'message_id': 'uuid-string',
                            'status': 'success'
                        }
                    }
                }
            }
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Get client information
            client_info = get_contact_message_client_info(request)
            
            # Auto-categorize based on subject/message content
            subject_lower = serializer.validated_data.get('subject', '').lower()
            message_lower = serializer.validated_data.get('message', '').lower()
            
            category = 'GENERAL'
            if any(word in subject_lower or word in message_lower for word in ['support', 'help', 'problem', 'issue', 'bug', 'error']):
                category = 'SUPPORT'
            elif any(word in subject_lower or word in message_lower for word in ['price', 'cost', 'billing', 'payment', 'subscription']):
                category = 'BILLING'
            elif any(word in subject_lower or word in message_lower for word in ['feature', 'request', 'suggestion', 'improvement']):
                category = 'FEATURE'
            elif any(word in subject_lower or word in message_lower for word in ['partner', 'collaboration', 'business']):
                category = 'PARTNERSHIP'
            elif any(word in subject_lower or word in message_lower for word in ['media', 'press', 'journalist', 'interview']):
                category = 'MEDIA'
            
            # Save the contact message
            contact_message = serializer.save(category=category, **client_info)
            
            # Send email notifications
            email_results = send_dashboard_emails(contact_message, 'contact_message')
            
            # Log email results
            if email_results['user_email_sent']:
                logger.info(f"Confirmation email sent to user: {contact_message.email}")
            else:
                logger.warning(f"Failed to send confirmation email to user: {contact_message.email}")
                
            if email_results['admin_email_sent']:
                logger.info(f"Admin notification sent for contact message: {contact_message.email}")
            else:
                logger.warning(f"Failed to send admin notification for contact message: {contact_message.email}")
            
            if email_results['errors']:
                logger.error(f"Email errors for contact message {contact_message.email}: {email_results['errors']}")
            
            return Response({
                'message': 'Thank you for contacting us! We will respond to your message soon.',
                'message_id': str(contact_message.message_id),
                'status': 'success',
                'emails_sent': {
                    'user_confirmation': email_results['user_email_sent'],
                    'admin_notification': email_results['admin_email_sent']
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': 'There were errors in your submission.',
            'errors': serializer.errors,
            'status': 'error'
        }, status=status.HTTP_400_BAD_REQUEST)


class ContactMessageListView(generics.ListAPIView):
    """
    Admin endpoint for listing contact messages
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'assigned_to']
    search_fields = ['email', 'full_name', 'subject', 'message']
    ordering_fields = ['created_at', 'updated_at', 'first_read_at', 'responded_at']
    ordering = ['-created_at']
    
    @extend_schema(
        tags=['Dashboard'],
        summary="List Contact Messages (Admin)",
        description="List all contact messages with filtering and search capabilities",
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by status'
            ),
            OpenApiParameter(
                name='priority',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by priority'
            ),
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by category'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in email, name, subject, or message content'
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(
        tags=['Dashboard'],
        summary="Get Contact Message Details (Admin)",
        description="Get detailed information about a specific contact message"
    ),
    put=extend_schema(
        tags=['Dashboard'],
        summary="Update Contact Message (Admin)",
        description="Update the status and tracking information of a contact message"
    ),
    patch=extend_schema(
        tags=['Dashboard'],
        summary="Update Contact Message (Admin)",
        description="Update the status and tracking information of a contact message"
    )
)
class ContactMessageDetailView(generics.RetrieveUpdateAPIView):
    """
    Admin endpoint for viewing and updating contact messages
    """
    queryset = ContactMessage.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = 'message_id'
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ContactMessageDetailSerializer
        return ContactMessageUpdateSerializer
    
    def get_object(self):
        """Override to mark message as read when accessed"""
        obj = super().get_object()
        if self.request.method == 'GET' and obj.status == 'NEW':
            obj.mark_as_read(self.request.user)
        return obj


# Dashboard Statistics View
class DashboardStatsView(APIView):
    """
    Admin endpoint for dashboard statistics
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        tags=['Dashboard'],
        summary="Get Dashboard Statistics (Admin)",
        description="Get comprehensive statistics for the admin dashboard",
        responses={200: DashboardStatsSerializer}
    )
    def get(self, request):
        # Calculate date ranges
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Early Access Request Statistics
        early_access_stats = {
            'total': EarlyAccessRequest.objects.count(),
            'today': EarlyAccessRequest.objects.filter(created_at__date=today).count(),
            'this_week': EarlyAccessRequest.objects.filter(created_at__gte=week_ago).count(),
            'this_month': EarlyAccessRequest.objects.filter(created_at__gte=month_ago).count(),
            'by_status': dict(EarlyAccessRequest.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'by_interest': dict(EarlyAccessRequest.objects.values('primary_interest').annotate(count=Count('id')).values_list('primary_interest', 'count')),
            'pending_count': EarlyAccessRequest.objects.filter(status='PENDING').count(),
            'high_priority_count': EarlyAccessRequest.objects.filter(priority='HIGH').count(),
        }
        
        # Contact Message Statistics
        contact_stats = {
            'total': ContactMessage.objects.count(),
            'today': ContactMessage.objects.filter(created_at__date=today).count(),
            'this_week': ContactMessage.objects.filter(created_at__gte=week_ago).count(),
            'this_month': ContactMessage.objects.filter(created_at__gte=month_ago).count(),
            'by_status': dict(ContactMessage.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'by_category': dict(ContactMessage.objects.values('category').annotate(count=Count('id')).values_list('category', 'count')),
            'unread_count': ContactMessage.objects.filter(status='NEW').count(),
            'urgent_count': ContactMessage.objects.filter(priority='URGENT').count(),
        }
        
        # Recent Activity (last 10 items)
        recent_early_access = EarlyAccessRequest.objects.order_by('-created_at')[:5]
        recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
        
        recent_activity = []
        
        for req in recent_early_access:
            recent_activity.append({
                'type': 'early_access',
                'id': str(req.request_id),
                'title': f'Early Access Request from {req.full_name}',
                'description': f'Interested in {req.get_interest_display_name()}',
                'created_at': req.created_at,
                'status': req.status
            })
        
        for msg in recent_messages:
            recent_activity.append({
                'type': 'contact_message',
                'id': str(msg.message_id),
                'title': f'Contact Message from {msg.full_name}',
                'description': msg.subject,
                'created_at': msg.created_at,
                'status': msg.status
            })
        
        # Sort by created_at
        recent_activity.sort(key=lambda x: x['created_at'], reverse=True)
        recent_activity = recent_activity[:10]
        
        data = {
            'early_access_requests': early_access_stats,
            'contact_messages': contact_stats,
            'recent_activity': recent_activity
        }
        
        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)


# Utility Views
class StaffUsersListView(generics.ListAPIView):
    """
    Admin endpoint for listing staff users (for assignments)
    """
    queryset = User.objects.filter(is_staff=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        tags=['Dashboard'],
        summary="List Staff Users (Admin)",
        description="Get list of staff users for assignment purposes"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
