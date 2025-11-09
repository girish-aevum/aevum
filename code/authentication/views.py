from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import generics, status, filters
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from aevum.pagination import StandardResultsPagination
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
import re

from .serializers import (
    UserProfileSerializer, 
    UserRegistrationSerializer, 
    ProfileImageSerializer,
    ForgotPasswordSerializer,
    PasswordResetSerializer,
    ChangePasswordSerializer,
    UserListSerializer,
    UserDetailSerializer
)
from .models import PasswordResetToken
from .schemas import (
    get_health_schema,
    get_register_schema,
    get_login_schema,
    get_logout_schema,
    get_forgot_password_schema,
    get_validate_reset_token_schema,
    get_reset_password_schema,
    get_change_password_schema,
    get_profile_schema,
    get_profile_image_update_schema,
    get_profile_image_delete_schema
)
from .models import SubscriptionPlan, UserSubscription, SubscriptionHistory


@get_health_schema()
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
	return Response({"status": "ok", "app": request.resolver_match.app_name or request.resolver_match.namespace or "unknown"})


@get_register_schema()
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Registration endpoint that creates a new user account and returns JWT tokens
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create the user
        user = serializer.save()
        
        # Get or create free plan
        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            plan_type='FREE',
            defaults={
                'name': 'Free Plan',
                'description': 'Basic features at no cost',
                'price': 0.00,
                'billing_cycle': 'MONTHLY',
                'is_active': True
            }
        )
        
        # Create user subscription
        subscription, created = UserSubscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': free_plan,
                'status': 'ACTIVE',
                'payment_method': 'FREE'
            }
        )
        
        # Create subscription history
        SubscriptionHistory.objects.create(
            user=user,
            subscription=subscription,
            action_type='CREATED',
            new_plan=free_plan,
            amount=0.00,
            notes='Initial free plan on registration'
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            "message": "Registration successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "tokens": {
                "access": str(access_token),
                "refresh": str(refresh)
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "error": "Validation failed",
        "details": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@get_login_schema()
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
	"""
	Login endpoint that authenticates user and returns JWT tokens
	"""
	username = request.data.get('username')
	password = request.data.get('password')
	
	if not username or not password:
		return Response(
			{"error": "Username and password are required"}, 
			status=status.HTTP_400_BAD_REQUEST
		)
	
	user = authenticate(username=username, password=password)
	
	if user is None:
		return Response(
			{"error": "Invalid credentials"}, 
			status=status.HTTP_401_UNAUTHORIZED
		)
	
	if not user.is_active:
		return Response(
			{"error": "User account is disabled"}, 
			status=status.HTTP_401_UNAUTHORIZED
		)
	
	# Update last_login field
	user.last_login = timezone.now()
	user.save(update_fields=['last_login'])
	
	# Generate JWT tokens
	refresh = RefreshToken.for_user(user)
	access_token = refresh.access_token
	
	return Response({
		"message": "Login successful",
		"user": {
			"id": user.id,
			"username": user.username,
			"email": user.email,
			"first_name": user.first_name,
			"last_name": user.last_name,
		},
		"tokens": {
			"access": str(access_token),
			"refresh": str(refresh)
		}
	}, status=status.HTTP_200_OK)


@get_logout_schema()
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
	"""
	Logout endpoint that blacklists the refresh token
	"""
	try:
		refresh_token = request.data.get('refresh_token')
		
		if not refresh_token:
			return Response(
				{"error": "Refresh token is required"}, 
				status=status.HTTP_400_BAD_REQUEST
			)
		
		# Blacklist the refresh token
		token = RefreshToken(refresh_token)
		token.blacklist()
		
		return Response({
			"message": "Logout successful"
		}, status=status.HTTP_200_OK)
		
	except Exception as e:
		return Response(
			{"error": "Invalid refresh token"}, 
			status=status.HTTP_400_BAD_REQUEST
		)


@get_forgot_password_schema()
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Send password reset email to user
    """
    serializer = ForgotPasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Create password reset token
        reset_token = PasswordResetToken.objects.create(user=user)
        
        # Prepare email content
        reset_url = f"{settings.SITE_URL or 'http://localhost:3000'}/reset-password?token={reset_token.token}"
        
        # Email context for templates
        from datetime import datetime
        context = {
            'user_name': user.first_name or user.username,
            'reset_url': reset_url,
            'current_year': datetime.now().year,
            'user': user,
            'token': reset_token.token
        }
        
        subject = 'Password Reset - Aevum Health'
        
        # Render email templates
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = render_to_string('emails/password_reset.txt', context)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({
                'message': 'Password reset email sent successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to send email. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@get_validate_reset_token_schema()
@api_view(['GET'])
@permission_classes([AllowAny])
def validate_reset_token(request):
    """
    Validate if a password reset token is valid
    """
    token = request.query_params.get('token')
    
    if not token:
        return Response({
            'valid': False,
            'error': 'Token parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if reset_token.is_valid():
            return Response({
                'valid': True,
                'message': 'Token is valid',
                'user_info': {
                    'email': reset_token.user.email,
                    'username': reset_token.user.username
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'valid': False,
                'error': 'Invalid or expired reset token'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except PasswordResetToken.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Invalid reset token'
        }, status=status.HTTP_400_BAD_REQUEST)


@get_reset_password_schema()
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset password using token
    """
    serializer = PasswordResetSerializer(data=request.data)
    
    if serializer.is_valid():
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['new_password']
        
        # Reset the password
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token.mark_as_used()
        
        # Invalidate all existing password reset tokens for this user
        PasswordResetToken.objects.filter(
            user=user, 
            is_used=False
        ).exclude(id=reset_token.id).update(is_used=True)
        
        return Response({
            'message': 'Password reset successful'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@get_change_password_schema()
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user's password after verifying current password
    """
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    # Validate input
    if not current_password or not new_password:
        return Response({
            'error': 'Current password and new password are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if current password is correct
    user = request.user
    if not user.check_password(current_password):
        return Response({
            'error': 'Current password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate new password complexity
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(password_regex, new_password):
        return Response({
            'error': 'Password must be at least 8 characters long and include uppercase, lowercase, number, and special character'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Set new password
    user.set_password(new_password)
    user.save()

    return Response({
        'message': 'Password changed successfully'
    }, status=status.HTTP_200_OK)


@get_profile_schema()
class MyProfileView(generics.RetrieveUpdateAPIView):
	serializer_class = UserProfileSerializer
	permission_classes = [IsAuthenticated]

	def get_object(self):
		return self.request.user.profile


@get_profile_image_update_schema()
class ProfileImageUpdateView(generics.UpdateAPIView):
	serializer_class = ProfileImageSerializer
	permission_classes = [IsAuthenticated]
	http_method_names = ['put', 'patch', 'delete']

	def get_object(self):
		return self.request.user.profile

	def update(self, request, *args, **kwargs):
		partial = kwargs.pop('partial', False)
		instance = self.get_object()
		
		# Delete old image if a new one is being uploaded
		if 'profile_image' in request.data and instance.profile_image:
			# Delete the old image file
			instance.profile_image.delete(save=False)
		
		serializer = self.get_serializer(instance, data=request.data, partial=partial)
		serializer.is_valid(raise_exception=True)
		self.perform_update(serializer)

		return Response({
			'message': 'Profile image updated successfully',
			'profile_image': serializer.data.get('profile_image'),
			'profile_image_url': serializer.data.get('profile_image_url')
		})

	@get_profile_image_delete_schema()
	def delete(self, request, *args, **kwargs):
		"""Delete the user's profile image"""
		instance = self.get_object()
		
		if not instance.profile_image:
			return Response({
				'error': 'No profile image found'
			}, status=status.HTTP_404_NOT_FOUND)
		
		# Delete the image file and clear the field
		instance.profile_image.delete(save=True)
		
		return Response({
			'message': 'Profile image deleted successfully'
		}, status=status.HTTP_200_OK)

	def perform_update(self, serializer):
		serializer.save()


# Import schema decorators
from drf_spectacular.utils import extend_schema


@extend_schema(
	tags=['Authentication'],
	summary='List Users',
	description='Get a paginated list of all users (excludes superadmin users). Requires admin privileges.'
)
class UserListView(generics.ListAPIView):
	"""
	List all users with pagination, filtering, and search capabilities
	Excludes superadmin users for security
	"""
	serializer_class = UserListSerializer
	permission_classes = [IsAuthenticated, IsAdminUser]
	pagination_class = StandardResultsPagination
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = ['username', 'email', 'first_name', 'last_name']
	ordering_fields = ['username', 'email', 'date_joined', 'last_login', 'is_active']
	ordering = ['-date_joined']
	
	def get_queryset(self):
		"""
		Get all users except superadmin users
		"""
		queryset = User.objects.filter(
			is_superuser=False  # Exclude superadmin users
		).select_related('profile')
		
		# Additional filtering options
		is_active = self.request.query_params.get('is_active')
		if is_active is not None:
			queryset = queryset.filter(is_active=is_active.lower() == 'true')
		
		is_staff = self.request.query_params.get('is_staff')
		if is_staff is not None:
			queryset = queryset.filter(is_staff=is_staff.lower() == 'true')
		
		# Date range filtering
		date_joined_after = self.request.query_params.get('date_joined_after')
		if date_joined_after:
			queryset = queryset.filter(date_joined__gte=date_joined_after)
		
		date_joined_before = self.request.query_params.get('date_joined_before')
		if date_joined_before:
			queryset = queryset.filter(date_joined__lte=date_joined_before)
		
		return queryset


@extend_schema(
	tags=['Authentication'],
	summary='Get User Details',
	description='Get detailed information about a specific user including profile data. Requires admin privileges.'
)
class UserDetailView(generics.RetrieveAPIView):
	"""
	Get detailed information about a specific user
	"""
	serializer_class = UserDetailSerializer
	permission_classes = [IsAuthenticated, IsAdminUser]
	
	def get_queryset(self):
		"""
		Get user queryset excluding superadmin users
		"""
		return User.objects.filter(
			is_superuser=False  # Exclude superadmin users
		).select_related('profile')
