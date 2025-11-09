from django.contrib import admin
from django.utils.html import format_html
from django.apps import apps

def get_model(model_name):
    """
    Safely get a model from the ai_companion app
    
    Args:
        model_name (str): Name of the model to retrieve
    
    Returns:
        Model class
    """
    return apps.get_model('ai_companion', model_name)

# Now import or define models using get_model
Thread = get_model('Thread')
Message = get_model('Message')
ThreadSuggestion = get_model('ThreadSuggestion')

from .workflow_models import (
    Workflow, 
    WorkflowStep, 
    WorkflowTemplate,
    WorkflowType,
    WorkflowState
)


class MessageInline(admin.TabularInline):
    """Inline for messages within threads"""
    model = Message
    extra = 0
    readonly_fields = ['message_id', 'created_at', 'processing_time_ms', 'token_count', 'confidence_score', 'qa_reviewed_at']
    fields = ['sender', 'content', 'is_helpful', 'user_feedback', 'is_selected_for_qa', 'qa_status', 'created_at']
    
    def has_add_permission(self, request, obj):
        return False  # Prevent adding messages through admin


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    """Admin interface for chat threads"""
    
    list_display = [
        'title_display',
        'user_display',
        'category_display',
        'status_badges',
        'message_count_display',
        'analytics_display',
        'created_at',
        'last_activity_at'
    ]
    
    list_filter = [
        'category',
        'is_favorite',
        'is_archived',
        'created_at',
        'last_activity_at'
    ]
    
    search_fields = ['title', 'user__username', 'user__email']
    
    readonly_fields = [
        'thread_id', 'created_at', 'updated_at', 'last_activity_at',
        'message_count', 'total_messages', 'total_ai_tokens_used', 'average_response_time_ms'
    ]
    
    fieldsets = [
        ('Thread Information', {
            'fields': [
                'thread_id',
                'user',
                'title',
                'category'
            ]
        }),
        ('Organization', {
            'fields': [
                'is_favorite',
                'is_archived'
            ]
        }),
        ('Statistics', {
            'fields': [
                'message_count',
                'total_messages',
                'total_ai_tokens_used',
                'average_response_time_ms'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at',
                'updated_at',
                'last_activity_at'
            ]
        })
    ]
    
    inlines = [MessageInline]
    ordering = ['-is_favorite', '-last_activity_at']
    
    actions = ['mark_as_favorite', 'archive_threads', 'unarchive_threads']
    
    def title_display(self, obj):
        """Display thread title with truncation"""
        title = obj.title or f"Thread {str(obj.thread_id)[:8]}..."
        if len(title) > 50:
            title = title[:50] + "..."
        return format_html('<strong>{}</strong>', title)
    title_display.short_description = 'Title'
    
    def user_display(self, obj):
        """Display user name"""
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'User'
    
    def category_display(self, obj):
        """Display category with color coding"""
        colors = {
            'MENTAL_HEALTH': '#ec4899',
            'NUTRITION': '#84cc16'
        }
        color = colors.get(obj.category, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_display.short_description = 'Category'
    
    def status_badges(self, obj):
        """Display status badges"""
        badges = []
        if obj.is_favorite:
            badges.append('<span style="background-color: #f59e0b; color: white; padding: 1px 4px; border-radius: 2px; font-size: 10px;">⭐ FAV</span>')
        if obj.is_archived:
            badges.append('<span style="background-color: #6b7280; color: white; padding: 1px 4px; border-radius: 2px; font-size: 10px;">📦 ARCH</span>')
        return format_html(' '.join(badges)) if badges else '-'
    status_badges.short_description = 'Status'
    
    def message_count_display(self, obj):
        """Display user message count and total message count"""
        user_count = obj.message_count  # Now only counts user messages
        total_count = obj.total_messages  # Total messages including AI
        return format_html(
            '<span style="background-color: #007cba; color: white; padding: 2px 6px; border-radius: 3px;">{} user</span> '
            '<span style="background-color: #6c757d; color: white; padding: 2px 6px; border-radius: 3px;">{} total</span>',
            user_count, total_count
        )
    message_count_display.short_description = 'Messages'
    
    def analytics_display(self, obj):
        """Display analytics information"""
        if obj.total_ai_tokens_used or obj.average_response_time_ms:
            return format_html(
                '<div style="font-size: 11px;">'
                '🎯 {} tokens<br>'
                '⏱️ {}ms avg'
                '</div>',
                obj.total_ai_tokens_used,
                f"{obj.average_response_time_ms:.0f}" if obj.average_response_time_ms else "N/A"
            )
        return '-'
    analytics_display.short_description = 'Analytics'
    
    def mark_as_favorite(self, request, queryset):
        """Mark selected threads as favorite"""
        updated = queryset.update(is_favorite=True)
        self.message_user(request, f'{updated} threads marked as favorite.')
    mark_as_favorite.short_description = 'Mark as favorite'
    
    def archive_threads(self, request, queryset):
        """Archive selected threads"""
        updated = queryset.update(is_archived=True)
        self.message_user(request, f'{updated} threads archived.')
    archive_threads.short_description = 'Archive threads'
    
    def unarchive_threads(self, request, queryset):
        """Unarchive selected threads"""
        updated = queryset.update(is_archived=False)
        self.message_user(request, f'{updated} threads unarchived.')
    unarchive_threads.short_description = 'Unarchive threads'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for chat messages"""
    
    list_display = [
        'sender_display',
        'content_preview',
        'thread_title',
        'user_display',
        'reaction_display',
        'qa_status',
        'quality_display',
        'created_at'
    ]
    
    list_filter = [
        'sender',
        'is_helpful',
        'is_selected_for_qa',
        'qa_status',
        'created_at'
    ]
    
    search_fields = ['content', 'thread__title', 'thread__user__username']
    
    readonly_fields = [
        'message_id', 'created_at', 'processing_time_ms', 'token_count', 'confidence_score', 'qa_reviewed_at'
    ]
    
    fieldsets = [
        ('Message Information', {
            'fields': [
                'message_id',
                'thread',
                'sender',
                'content'
            ]
        }),
        ('User Feedback', {
            'fields': [
                'is_helpful',
                'user_feedback'
            ]
        }),
        ('QA Testing', {
            'fields': [
                'is_selected_for_qa',
                'qa_score',
                'qa_status',
                'qa_feedback',
                'qa_reviewer',
                'qa_reviewed_at',
                'qa_tags'
            ]
        }),
        ('AI Quality Metrics', {
            'fields': [
                'confidence_score',
                'processing_time_ms',
                'token_count'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at'
            ]
        })
    ]
    
    ordering = ['-created_at']
    
    actions = ['select_for_qa', 'approve_qa', 'reject_qa']
    
    def sender_display(self, obj):
        """Display sender with color coding"""
        color = '#28a745' if obj.sender == 'USER' else '#007cba'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
            color,
            obj.get_sender_display()
        )
    sender_display.short_description = 'Sender'
    
    def content_preview(self, obj):
        """Display content preview"""
        content = obj.content
        if len(content) > 100:
            content = content[:100] + "..."
        return content
    content_preview.short_description = 'Content'
    
    def thread_title(self, obj):
        """Display thread title"""
        return obj.thread.title or f"Thread {str(obj.thread.thread_id)[:8]}..."
    thread_title.short_description = 'Thread'
    
    def user_display(self, obj):
        """Display user name"""
        return obj.thread.user.get_full_name() or obj.thread.user.username
    user_display.short_description = 'User'
    
    def reaction_display(self, obj):
        """Display user reaction"""
        if obj.sender == 'AI':
            if obj.is_helpful is True:
                return format_html('<span style="color: #28a745;">👍 Helpful</span>')
            elif obj.is_helpful is False:
                return format_html('<span style="color: #dc3545;">👎 Not Helpful</span>')
            else:
                return format_html('<span style="color: #6c757d;">No reaction</span>')
        return '-'
    reaction_display.short_description = 'Reaction'
    
    def qa_display(self, obj):
        """Display QA testing information"""
        if obj.is_selected_for_qa:
            status_colors = {
                'PENDING': '#ffc107',
                'APPROVED': '#28a745',
                'NEEDS_IMPROVEMENT': '#fd7e14',
                'REJECTED': '#dc3545',
                'SKIPPED': '#6c757d'
            }
            status_color = status_colors.get(obj.qa_status, '#6c757d')
            
            qa_info = f'<span style="background-color: {status_color}; color: white; padding: 1px 4px; border-radius: 2px; font-size: 10px;">{obj.qa_status or "PENDING"}</span>'
            
            if obj.qa_score is not None:
                grade = obj.qa_score_grade
                qa_info += f'<br><span style="font-size: 11px; font-weight: bold;">{obj.qa_score:.1f}/10 ({grade})</span>'
            
            if obj.qa_reviewer:
                qa_info += f'<br><span style="font-size: 10px; color: #6c757d;">by {obj.qa_reviewer.username}</span>'
            
            return format_html('<div style="font-size: 11px;">{}</div>', qa_info)
        return '-'
    qa_display.short_description = 'QA Status'
    
    def quality_display(self, obj):
        """Display AI quality metrics"""
        if obj.sender == 'AI' and (obj.confidence_score or obj.processing_time_ms):
            # Format percentage manually to avoid SafeString formatting issues
            confidence_pct = f"{(obj.confidence_score or 0) * 100:.1f}%"
            return format_html(
                '<div style="font-size: 11px;">'
                '📊 {} conf<br>'
                '⏱️ {}ms<br>'
                '🎯 {} tokens'
                '</div>',
                confidence_pct,
                obj.processing_time_ms or 0,
                obj.token_count or 0
            )
        return '-'
    quality_display.short_description = 'Quality'
    
    def select_for_qa(self, request, queryset):
        """Select messages for QA testing"""
        updated = 0
        for message in queryset:
            if not message.is_selected_for_qa:
                message.select_for_qa()
                updated += 1
        self.message_user(request, f'{updated} messages selected for QA testing.')
    select_for_qa.short_description = 'Select for QA testing'
    
    def approve_qa(self, request, queryset):
        """Approve selected QA messages"""
        updated = queryset.filter(is_selected_for_qa=True).update(qa_status='APPROVED')
        self.message_user(request, f'{updated} messages approved in QA.')
    approve_qa.short_description = 'Approve QA status'
    
    def reject_qa(self, request, queryset):
        """Reject selected QA messages"""
        updated = queryset.filter(is_selected_for_qa=True).update(qa_status='REJECTED')
        self.message_user(request, f'{updated} messages rejected in QA.')
    reject_qa.short_description = 'Reject QA status'


@admin.register(ThreadSuggestion)
class ThreadSuggestionAdmin(admin.ModelAdmin):
    """Admin interface for thread suggestions"""
    
    list_display = [
        'title_display',
        'user_display',
        'suggestion_type_display',
        'category_display',
        'relevance_display',
        'status_display',
        'created_at'
    ]
    
    list_filter = [
        'suggestion_type',
        'suggested_category',
        'is_dismissed',
        'is_used',
        'created_at'
    ]
    
    search_fields = ['title', 'description', 'user__username']
    
    readonly_fields = ['created_at', 'dismissed_at', 'used_at']
    
    fieldsets = [
        ('Suggestion Information', {
            'fields': [
                'user',
                'suggestion_type',
                'title',
                'description'
            ]
        }),
        ('Suggested Thread', {
            'fields': [
                'suggested_category',
                'suggested_first_message'
            ]
        }),
        ('Metadata', {
            'fields': [
                'relevance_score',
                'based_on_thread'
            ]
        }),
        ('Status', {
            'fields': [
                'is_dismissed',
                'is_used',
                'created_thread'
            ]
        }),
        ('Timestamps', {
            'fields': [
                'created_at',
                'dismissed_at',
                'used_at'
            ]
        })
    ]
    
    ordering = ['-relevance_score', '-created_at']
    
    def title_display(self, obj):
        """Display suggestion title"""
        return format_html('<strong>{}</strong>', obj.title)
    title_display.short_description = 'Title'
    
    def user_display(self, obj):
        """Display user name"""
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'User'
    
    def suggestion_type_display(self, obj):
        """Display suggestion type with color coding"""
        colors = {
            'TOPIC': '#3b82f6',
            'FOLLOW_UP': '#f59e0b',
            'RELATED': '#8b5cf6',
            'WELLNESS_CHECK': '#10b981'
        }
        color = colors.get(obj.suggestion_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_suggestion_type_display()
        )
    suggestion_type_display.short_description = 'Type'
    
    def category_display(self, obj):
        """Display suggested category"""
        colors = {
            'MENTAL_HEALTH': '#ec4899',
            'NUTRITION': '#84cc16'
        }
        color = colors.get(obj.suggested_category, '#6b7280')
        category_name = dict(Thread.CATEGORY_CHOICES).get(obj.suggested_category, obj.suggested_category)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            category_name
        )
    category_display.short_description = 'Category'
    
    def relevance_display(self, obj):
        """Display relevance score"""
        score = obj.relevance_score
        if score >= 0.8:
            color = '#28a745'
        elif score >= 0.6:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        # Format percentage manually to avoid SafeString formatting issues
        percentage = f"{score * 100:.1f}%"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            percentage
        )
    relevance_display.short_description = 'Relevance'
    
    def status_display(self, obj):
        """Display suggestion status"""
        if obj.is_used:
            return format_html('<span style="color: #28a745;">✅ Used</span>')
        elif obj.is_dismissed:
            return format_html('<span style="color: #dc3545;">❌ Dismissed</span>')
        else:
            return format_html('<span style="color: #007cba;">⏳ Active</span>')
    status_display.short_description = 'Status'

@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for Workflow Templates"""
    list_display = (
        'name', 
        'type', 
        'is_active', 
        'display_steps_count'
    )
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'description')
    
    def display_steps_count(self, obj):
        """Display number of steps in the template"""
        return len(obj.steps_config)
    display_steps_count.short_description = 'Steps'

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    """Admin configuration for Workflows"""
    list_display = (
        'id', 
        'user', 
        'type', 
        'state', 
        'created_at', 
        'current_progress'
    )
    list_filter = ('type', 'state', 'created_at')
    search_fields = ('user__username', 'thread__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def current_progress(self, obj):
        """Display workflow progress"""
        return f"{obj.current_step}/{obj.total_steps}"
    current_progress.short_description = 'Progress'
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields read-only"""
        if obj:  # editing an existing object
            return self.readonly_fields + ('user', 'thread')
        return self.readonly_fields

@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    """Admin configuration for Workflow Steps"""
    list_display = (
        'workflow', 
        'step_number', 
        'created_at', 
        'truncated_user_input', 
        'truncated_ai_response',
        'relevance_score'
    )
    list_filter = ('workflow__type', 'created_at')
    search_fields = ('user_input', 'ai_response')
    
    def truncated_user_input(self, obj):
        """Truncate long user inputs"""
        return obj.user_input[:50] + '...' if len(obj.user_input) > 50 else obj.user_input
    truncated_user_input.short_description = 'User Input'
    
    def truncated_ai_response(self, obj):
        """Truncate long AI responses"""
        return obj.ai_response[:50] + '...' if len(obj.ai_response) > 50 else obj.ai_response
    truncated_ai_response.short_description = 'AI Response'

# Optional: Custom admin views or actions can be added here
def reset_workflow(modeladmin, request, queryset):
    """
    Custom admin action to reset workflows
    """
    for workflow in queryset:
        workflow.current_step = 0
        workflow.state = WorkflowState.INITIALIZED
        workflow.save()

reset_workflow.short_description = "Reset selected workflows to initial state"

# Add the action to WorkflowAdmin
WorkflowAdmin.actions = [reset_workflow]
