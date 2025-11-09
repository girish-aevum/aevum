from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EarlyAccessRequest, ContactMessage


class EarlyAccessRequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating early access requests (public endpoint)
    """
    
    class Meta:
        model = EarlyAccessRequest
        fields = [
            'email',
            'full_name', 
            'phone_number',
            'primary_interest'
        ]
        
    def validate_email(self, value):
        """Validate email format and check for duplicates"""
        if value:
            value = value.lower().strip()
            # Check for recent duplicate requests (within last 24 hours)
            from django.utils import timezone
            from datetime import timedelta
            
            recent_request = EarlyAccessRequest.objects.filter(
                email=value,
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).exists()
            
            if recent_request:
                raise serializers.ValidationError(
                    "An early access request with this email was already submitted recently. "
                    "Please wait 24 hours before submitting another request."
                )
        return value
    
    def validate_full_name(self, value):
        """Validate full name"""
        if value:
            value = value.strip()
            if len(value) < 2:
                raise serializers.ValidationError("Full name must be at least 2 characters long.")
        return value
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value:
            value = value.strip()
            # Remove spaces and common formatting
            cleaned_number = ''.join(filter(str.isdigit, value.replace('+', '+')))
            if len(cleaned_number) < 10:
                raise serializers.ValidationError("Please enter a valid phone number with at least 10 digits.")
        return value


class EarlyAccessRequestListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing early access requests (admin endpoint)
    """
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    interest_display = serializers.CharField(source='get_interest_display_name', read_only=True)
    contacted_by_name = serializers.CharField(source='contacted_by.get_full_name', read_only=True)
    days_since_request = serializers.SerializerMethodField()
    
    class Meta:
        model = EarlyAccessRequest
        fields = [
            'request_id',
            'email',
            'full_name',
            'phone_number',
            'primary_interest',
            'interest_display',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'contacted_at',
            'contacted_by_name',
            'days_since_request',
            'created_at',
            'updated_at'
        ]
    
    def get_days_since_request(self, obj):
        """Calculate days since the request was made"""
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        return delta.days


class EarlyAccessRequestDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed early access request view (admin endpoint)
    """
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    interest_display = serializers.CharField(source='get_interest_display_name', read_only=True)
    contacted_by_name = serializers.CharField(source='contacted_by.get_full_name', read_only=True)
    
    class Meta:
        model = EarlyAccessRequest
        fields = '__all__'
        read_only_fields = ['request_id', 'created_at', 'updated_at', 'ip_address', 'user_agent']


class EarlyAccessRequestUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating early access requests (admin endpoint)
    """
    
    class Meta:
        model = EarlyAccessRequest
        fields = [
            'status',
            'priority',
            'contacted_at',
            'contacted_by',
            'admin_notes'
        ]


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating contact messages (public endpoint)
    """
    
    class Meta:
        model = ContactMessage
        fields = [
            'full_name',
            'email',
            'subject',
            'message'
        ]
        
    def validate_email(self, value):
        """Validate email format"""
        if value:
            value = value.lower().strip()
        return value
    
    def validate_full_name(self, value):
        """Validate full name"""
        if value:
            value = value.strip()
            if len(value) < 2:
                raise serializers.ValidationError("Full name must be at least 2 characters long.")
        return value
    
    def validate_subject(self, value):
        """Validate subject"""
        if value:
            value = value.strip()
            if len(value) < 5:
                raise serializers.ValidationError("Subject must be at least 5 characters long.")
        return value
    
    def validate_message(self, value):
        """Validate message content"""
        if value:
            value = value.strip()
            if len(value) < 10:
                raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value


class ContactMessageListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing contact messages (admin endpoint)
    """
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    message_preview = serializers.SerializerMethodField()
    days_since_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactMessage
        fields = [
            'message_id',
            'full_name',
            'email',
            'subject',
            'message_preview',
            'category',
            'category_display',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'assigned_to_name',
            'first_read_at',
            'responded_at',
            'days_since_message',
            'created_at',
            'updated_at'
        ]
    
    def get_message_preview(self, obj):
        """Get a preview of the message content"""
        if obj.message:
            return obj.message[:150] + "..." if len(obj.message) > 150 else obj.message
        return ""
    
    def get_days_since_message(self, obj):
        """Calculate days since the message was sent"""
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        return delta.days


class ContactMessageDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed contact message view (admin endpoint)
    """
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    first_read_by_name = serializers.CharField(source='first_read_by.get_full_name', read_only=True)
    responded_by_name = serializers.CharField(source='responded_by.get_full_name', read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = '__all__'
        read_only_fields = ['message_id', 'created_at', 'updated_at', 'ip_address', 'user_agent', 'referrer']


class ContactMessageUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating contact messages (admin endpoint)
    """
    
    class Meta:
        model = ContactMessage
        fields = [
            'category',
            'status',
            'priority',
            'assigned_to',
            'admin_notes',
            'response_sent'
        ]


# Statistics Serializers
class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for dashboard statistics
    """
    
    early_access_requests = serializers.DictField()
    contact_messages = serializers.DictField()
    recent_activity = serializers.ListField()
    
    class Meta:
        fields = ['early_access_requests', 'contact_messages', 'recent_activity']


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for staff assignments
    """
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']
        read_only_fields = ['username', 'email'] 