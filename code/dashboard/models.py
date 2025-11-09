from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
import uuid


class EarlyAccessRequest(models.Model):
    """
    Model to track early access requests from potential users
    """
    
    INTEREST_CHOICES = [
        ('DNA_ANALYSIS', 'DNA Analysis & Genetic Insights'),
        ('MENTAL_WELLNESS', 'Mental Wellness & Mood Tracking'),
        ('NUTRITION', 'Nutrition & Dietary Planning'),
        ('FITNESS', 'Fitness & Health Monitoring'),
        ('AI_COMPANION', 'AI Health Companion'),
        ('COMPREHENSIVE', 'Complete Health Platform'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('CONTACTED', 'Initial Contact Made'),
        ('INTERESTED', 'Showed Interest'),
        ('ONBOARDED', 'Successfully Onboarded'),
        ('NOT_INTERESTED', 'Not Interested'),
        ('INVALID', 'Invalid Request'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('HIGH', 'High Priority'),
        ('URGENT', 'Urgent'),
    ]
    
    # Unique identifier
    request_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Form fields
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Email address for early access notifications"
    )
    full_name = models.CharField(
        max_length=150,
        help_text="Full name of the person requesting access"
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )],
        blank=True,
        null=True,
        help_text="Optional phone number for priority notifications"
    )
    primary_interest = models.CharField(
        max_length=20,
        choices=INTEREST_CHOICES,
        help_text="Primary area of interest in the platform"
    )
    
    # Tracking fields
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    
    # Additional information
    source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Source of the request (e.g., website, referral, etc.)"
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the requester"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="Browser/device information"
    )
    
    # Follow-up tracking
    contacted_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the user was first contacted"
    )
    contacted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='contacted_early_access_requests',
        help_text="Staff member who contacted the user"
    )
    
    # Notes and comments
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes for tracking and follow-up"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Early Access Request"
        verbose_name_plural = "Early Access Requests"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.email} ({self.get_status_display()})"
    
    def mark_as_contacted(self, contacted_by_user=None):
        """Mark the request as contacted"""
        self.status = 'CONTACTED'
        self.contacted_at = timezone.now()
        if contacted_by_user:
            self.contacted_by = contacted_by_user
        self.save()
    
    def get_interest_display_name(self):
        """Get a user-friendly display name for the interest"""
        return dict(self.INTEREST_CHOICES).get(self.primary_interest, self.primary_interest)


class ContactMessage(models.Model):
    """
    Model to track contact messages from website visitors
    """
    
    STATUS_CHOICES = [
        ('NEW', 'New Message'),
        ('READ', 'Message Read'),
        ('IN_PROGRESS', 'Response In Progress'),
        ('RESPONDED', 'Response Sent'),
        ('RESOLVED', 'Issue Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('HIGH', 'High Priority'),
        ('URGENT', 'Urgent'),
    ]
    
    CATEGORY_CHOICES = [
        ('GENERAL', 'General Inquiry'),
        ('SUPPORT', 'Technical Support'),
        ('BILLING', 'Billing & Pricing'),
        ('FEATURE', 'Feature Request'),
        ('BUG', 'Bug Report'),
        ('PARTNERSHIP', 'Partnership Inquiry'),
        ('MEDIA', 'Media & Press'),
        ('OTHER', 'Other'),
    ]
    
    # Unique identifier
    message_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Form fields
    full_name = models.CharField(
        max_length=150,
        help_text="Full name of the person sending the message"
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Email address for response"
    )
    subject = models.CharField(
        max_length=200,
        help_text="Brief description of the inquiry"
    )
    message = models.TextField(
        help_text="Detailed message content"
    )
    
    # Classification and tracking
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='GENERAL',
        help_text="Category of the message for better organization"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    
    # Technical tracking
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the sender"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="Browser/device information"
    )
    referrer = models.URLField(
        blank=True,
        null=True,
        help_text="Page from which the contact form was submitted"
    )
    
    # Response tracking
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='assigned_contact_messages',
        help_text="Staff member assigned to handle this message"
    )
    first_read_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the message was first read"
    )
    first_read_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='first_read_contact_messages',
        help_text="Staff member who first read the message"
    )
    responded_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When a response was sent"
    )
    responded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='responded_contact_messages',
        help_text="Staff member who sent the response"
    )
    
    # Internal tracking
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes for tracking and follow-up"
    )
    response_sent = models.TextField(
        blank=True,
        null=True,
        help_text="Copy of the response sent to the user"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.subject} ({self.get_status_display()})"
    
    def mark_as_read(self, read_by_user=None):
        """Mark the message as read"""
        if self.status == 'NEW':
            self.status = 'READ'
            self.first_read_at = timezone.now()
            if read_by_user:
                self.first_read_by = read_by_user
            self.save()
    
    def mark_as_responded(self, responded_by_user=None, response_text=None):
        """Mark the message as responded"""
        self.status = 'RESPONDED'
        self.responded_at = timezone.now()
        if responded_by_user:
            self.responded_by = responded_by_user
        if response_text:
            self.response_sent = response_text
        self.save()
    
    def get_category_display_name(self):
        """Get a user-friendly display name for the category"""
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
