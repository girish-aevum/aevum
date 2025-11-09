from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from .models import EarlyAccessRequest, ContactMessage


@admin.register(EarlyAccessRequest)
class EarlyAccessRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for Early Access Requests
    """
    
    list_display = [
        'full_name',
        'email',
        'phone_number',
        'primary_interest_display',
        'status_badge',
        'priority_badge',
        'days_since_request',
        'contacted_status',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'priority',
        'primary_interest',
        'contacted_by',
        'created_at',
        'contacted_at'
    ]
    
    search_fields = [
        'email',
        'full_name',
        'phone_number',
        'admin_notes'
    ]
    
    readonly_fields = [
        'request_id',
        'created_at',
        'updated_at',
        'ip_address',
        'user_agent',
        'days_since_request_display'
    ]
    
    fieldsets = [
        ('Request Information', {
            'fields': [
                'request_id',
                'email',
                'full_name',
                'phone_number',
                'primary_interest'
            ]
        }),
        ('Status & Priority', {
            'fields': [
                'status',
                'priority',
                'contacted_at',
                'contacted_by'
            ]
        }),
        ('Technical Information', {
            'fields': [
                'source',
                'ip_address',
                'user_agent'
            ],
            'classes': ['collapse']
        }),
        ('Notes & Follow-up', {
            'fields': [
                'admin_notes'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at',
                'updated_at',
                'days_since_request_display'
            ],
            'classes': ['collapse']
        })
    ]
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    actions = [
        'mark_as_contacted',
        'mark_as_interested',
        'mark_as_high_priority',
        'export_to_csv'
    ]
    
    def primary_interest_display(self, obj):
        """Display primary interest with color coding"""
        colors = {
            'DNA_ANALYSIS': '#e74c3c',
            'MENTAL_WELLNESS': '#3498db',
            'NUTRITION': '#2ecc71',
            'FITNESS': '#f39c12',
            'AI_COMPANION': '#9b59b6',
            'COMPREHENSIVE': '#34495e',
            'OTHER': '#95a5a6'
        }
        color = colors.get(obj.primary_interest, '#95a5a6')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_interest_display_name()
        )
    primary_interest_display.short_description = 'Interest'
    
    def status_badge(self, obj):
        """Display status with badge styling"""
        colors = {
            'PENDING': '#f39c12',
            'CONTACTED': '#3498db',
            'INTERESTED': '#2ecc71',
            'ONBOARDED': '#27ae60',
            'NOT_INTERESTED': '#e74c3c',
            'INVALID': '#95a5a6'
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        """Display priority with badge styling"""
        colors = {
            'LOW': '#95a5a6',
            'MEDIUM': '#f39c12',
            'HIGH': '#e67e22',
            'URGENT': '#e74c3c'
        }
        color = colors.get(obj.priority, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def days_since_request(self, obj):
        """Calculate days since request"""
        if not obj.created_at:
            return 'New'
        delta = timezone.now() - obj.created_at
        days = delta.days
        if days == 0:
            return 'Today'
        elif days == 1:
            return '1 day ago'
        else:
            return f'{days} days ago'
    days_since_request.short_description = 'Age'
    
    def days_since_request_display(self, obj):
        """Detailed days since request for readonly field"""
        if not obj.created_at:
            return 'Not created yet'
        delta = timezone.now() - obj.created_at
        return f'{delta.days} days, {delta.seconds // 3600} hours'
    days_since_request_display.short_description = 'Time Since Request'
    
    def contacted_status(self, obj):
        """Display contacted status"""
        if obj.contacted_at:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                obj.contacted_at.strftime('%m/%d/%Y')
            )
        return format_html('<span style="color: red;">✗ Not contacted</span>')
    contacted_status.short_description = 'Contacted'
    
    # Admin Actions
    def mark_as_contacted(self, request, queryset):
        """Mark selected requests as contacted"""
        updated = queryset.update(
            status='CONTACTED',
            contacted_at=timezone.now(),
            contacted_by=request.user
        )
        self.message_user(request, f'{updated} requests marked as contacted.')
    mark_as_contacted.short_description = 'Mark as contacted'
    
    def mark_as_interested(self, request, queryset):
        """Mark selected requests as interested"""
        updated = queryset.update(status='INTERESTED')
        self.message_user(request, f'{updated} requests marked as interested.')
    mark_as_interested.short_description = 'Mark as interested'
    
    def mark_as_high_priority(self, request, queryset):
        """Mark selected requests as high priority"""
        updated = queryset.update(priority='HIGH')
        self.message_user(request, f'{updated} requests marked as high priority.')
    mark_as_high_priority.short_description = 'Mark as high priority'
    
    def export_to_csv(self, request, queryset):
        """Export selected requests to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="early_access_requests.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Email', 'Full Name', 'Phone', 'Interest', 'Status', 
            'Priority', 'Created At', 'Contacted At', 'Notes'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.email,
                obj.full_name,
                obj.phone_number or '',
                obj.get_interest_display_name(),
                obj.get_status_display(),
                obj.get_priority_display(),
                obj.created_at.strftime('%Y-%m-%d %H:%M'),
                obj.contacted_at.strftime('%Y-%m-%d %H:%M') if obj.contacted_at else '',
                obj.admin_notes or ''
            ])
        
        return response
    export_to_csv.short_description = 'Export to CSV'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for Contact Messages
    """
    
    list_display = [
        'full_name',
        'email',
        'subject_truncated',
        'category_badge',
        'status_badge',
        'priority_badge',
        'assigned_to_display',
        'response_status',
        'days_since_message',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'priority',
        'category',
        'assigned_to',
        'first_read_by',
        'responded_by',
        'created_at',
        'first_read_at',
        'responded_at'
    ]
    
    search_fields = [
        'email',
        'full_name',
        'subject',
        'message',
        'admin_notes'
    ]
    
    readonly_fields = [
        'message_id',
        'created_at',
        'updated_at',
        'ip_address',
        'user_agent',
        'referrer',
        'first_read_at',
        'first_read_by',
        'responded_at',
        'responded_by',
        'days_since_message_display'
    ]
    
    fieldsets = [
        ('Message Information', {
            'fields': [
                'message_id',
                'full_name',
                'email',
                'subject',
                'message'
            ]
        }),
        ('Classification & Status', {
            'fields': [
                'category',
                'status',
                'priority',
                'assigned_to'
            ]
        }),
        ('Response Tracking', {
            'fields': [
                'first_read_at',
                'first_read_by',
                'responded_at',
                'responded_by',
                'response_sent'
            ]
        }),
        ('Technical Information', {
            'fields': [
                'ip_address',
                'user_agent',
                'referrer'
            ],
            'classes': ['collapse']
        }),
        ('Notes & Follow-up', {
            'fields': [
                'admin_notes'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at',
                'updated_at',
                'days_since_message_display'
            ],
            'classes': ['collapse']
        })
    ]
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    actions = [
        'mark_as_read',
        'mark_as_responded',
        'mark_as_high_priority',
        'assign_to_me',
        'export_to_csv'
    ]
    
    def subject_truncated(self, obj):
        """Display truncated subject"""
        if len(obj.subject) > 50:
            return obj.subject[:50] + '...'
        return obj.subject
    subject_truncated.short_description = 'Subject'
    
    def category_badge(self, obj):
        """Display category with badge styling"""
        colors = {
            'GENERAL': '#95a5a6',
            'SUPPORT': '#e74c3c',
            'BILLING': '#f39c12',
            'FEATURE': '#3498db',
            'BUG': '#e67e22',
            'PARTNERSHIP': '#9b59b6',
            'MEDIA': '#2ecc71',
            'OTHER': '#34495e'
        }
        color = colors.get(obj.category, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    
    def status_badge(self, obj):
        """Display status with badge styling"""
        colors = {
            'NEW': '#e74c3c',
            'READ': '#f39c12',
            'IN_PROGRESS': '#3498db',
            'RESPONDED': '#2ecc71',
            'RESOLVED': '#27ae60',
            'CLOSED': '#95a5a6'
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        """Display priority with badge styling"""
        colors = {
            'LOW': '#95a5a6',
            'MEDIUM': '#f39c12',
            'HIGH': '#e67e22',
            'URGENT': '#e74c3c'
        }
        color = colors.get(obj.priority, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def assigned_to_display(self, obj):
        """Display assigned user"""
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return format_html('<span style="color: #e74c3c;">Unassigned</span>')
    assigned_to_display.short_description = 'Assigned To'
    
    def response_status(self, obj):
        """Display response status"""
        if obj.responded_at:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                obj.responded_at.strftime('%m/%d/%Y')
            )
        elif obj.first_read_at:
            return format_html('<span style="color: orange;">👁 Read</span>')
        return format_html('<span style="color: red;">✗ New</span>')
    response_status.short_description = 'Response'
    
    def days_since_message(self, obj):
        """Calculate days since message"""
        if not obj.created_at:
            return 'New'
        delta = timezone.now() - obj.created_at
        days = delta.days
        if days == 0:
            return 'Today'
        elif days == 1:
            return '1 day ago'
        else:
            return f'{days} days ago'
    days_since_message.short_description = 'Age'
    
    def days_since_message_display(self, obj):
        """Detailed days since message for readonly field"""
        if not obj.created_at:
            return 'Not created yet'
        delta = timezone.now() - obj.created_at
        return f'{delta.days} days, {delta.seconds // 3600} hours'
    days_since_message_display.short_description = 'Time Since Message'
    
    # Admin Actions
    def mark_as_read(self, request, queryset):
        """Mark selected messages as read"""
        updated = 0
        for obj in queryset.filter(status='NEW'):
            obj.mark_as_read(request.user)
            updated += 1
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = 'Mark as read'
    
    def mark_as_responded(self, request, queryset):
        """Mark selected messages as responded"""
        updated = 0
        for obj in queryset:
            obj.mark_as_responded(request.user)
            updated += 1
        self.message_user(request, f'{updated} messages marked as responded.')
    mark_as_responded.short_description = 'Mark as responded'
    
    def mark_as_high_priority(self, request, queryset):
        """Mark selected messages as high priority"""
        updated = queryset.update(priority='HIGH')
        self.message_user(request, f'{updated} messages marked as high priority.')
    mark_as_high_priority.short_description = 'Mark as high priority'
    
    def assign_to_me(self, request, queryset):
        """Assign selected messages to current user"""
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f'{updated} messages assigned to you.')
    assign_to_me.short_description = 'Assign to me'
    
    def export_to_csv(self, request, queryset):
        """Export selected messages to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_messages.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Email', 'Full Name', 'Subject', 'Category', 'Status', 
            'Priority', 'Created At', 'First Read At', 'Responded At', 'Message'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.email,
                obj.full_name,
                obj.subject,
                obj.get_category_display(),
                obj.get_status_display(),
                obj.get_priority_display(),
                obj.created_at.strftime('%Y-%m-%d %H:%M'),
                obj.first_read_at.strftime('%Y-%m-%d %H:%M') if obj.first_read_at else '',
                obj.responded_at.strftime('%Y-%m-%d %H:%M') if obj.responded_at else '',
                obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
            ])
        
        return response
    export_to_csv.short_description = 'Export to CSV'
