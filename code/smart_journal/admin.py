from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from .models import (
    JournalCategory,
    JournalTemplate,
    JournalEntry,
    JournalTag,
    JournalEntryTag,
    JournalAttachment,
    JournalStreak,
    JournalInsight,
    JournalReminder
)


class JournalAttachmentInline(admin.TabularInline):
    """Inline admin for journal attachments"""
    model = JournalAttachment
    extra = 0
    readonly_fields = ['file_name', 'file_size', 'file_type', 'uploaded_at']


class JournalEntryTagInline(admin.TabularInline):
    """Inline admin for journal entry tags"""
    model = JournalEntryTag
    extra = 0


@admin.register(JournalCategory)
class JournalCategoryAdmin(admin.ModelAdmin):
    """Admin interface for Journal Categories"""
    
    list_display = [
        'name',
        'category_type_badge',
        'user_display',
        'color_preview',
        'entry_count',
        'is_system_category',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'category_type',
        'is_system_category',
        'is_active',
        'created_at'
    ]
    
    search_fields = ['name', 'description', 'user__username']
    
    fieldsets = [
        ('Category Information', {
            'fields': ['name', 'category_type', 'description']
        }),
        ('Appearance', {
            'fields': ['color_hex', 'icon']
        }),
        ('Settings', {
            'fields': ['user', 'is_system_category', 'is_active']
        })
    ]
    
    ordering = ['category_type', 'name']
    
    def category_type_badge(self, obj):
        """Display category type with color coding"""
        colors = {
            'PERSONAL': '#3b82f6',
            'WORK': '#f59e0b',
            'HEALTH': '#10b981',
            'RELATIONSHIPS': '#ef4444',
            'GOALS': '#8b5cf6',
            'TRAVEL': '#06b6d4',
            'LEARNING': '#84cc16',
            'CREATIVITY': '#f97316',
            'FINANCE': '#22c55e',
            'GRATITUDE': '#ec4899',
            'DREAMS': '#6366f1',
            'DAILY': '#64748b',
            'CUSTOM': '#94a3b8'
        }
        color = colors.get(obj.category_type, '#94a3b8')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_category_type_display()
        )
    category_type_badge.short_description = 'Type'
    
    def user_display(self, obj):
        """Display user or system indicator"""
        if obj.is_system_category:
            return format_html('<span style="color: #059669; font-weight: bold;">🌐 System</span>')
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'Owner'
    
    def color_preview(self, obj):
        """Display color preview"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color_hex
        )
    color_preview.short_description = 'Color'
    
    def entry_count(self, obj):
        """Count of entries in this category"""
        count = obj.journal_entries.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    entry_count.short_description = 'Entries'


@admin.register(JournalTemplate)
class JournalTemplateAdmin(admin.ModelAdmin):
    """Admin interface for Journal Templates"""
    
    list_display = [
        'name',
        'template_type_badge',
        'user_display',
        'usage_count_display',
        'is_public',
        'is_system_template',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'template_type',
        'is_system_template',
        'is_public',
        'is_active',
        'created_at'
    ]
    
    search_fields = ['name', 'description', 'user__username']
    
    fieldsets = [
        ('Template Information', {
            'fields': ['name', 'template_type', 'description']
        }),
        ('Template Structure', {
            'fields': ['prompt_questions', 'default_structure']
        }),
        ('Settings', {
            'fields': ['user', 'is_system_template', 'is_public', 'is_active']
        }),
        ('Statistics', {
            'fields': ['usage_count'],
            'classes': ['collapse']
        })
    ]
    
    readonly_fields = ['usage_count']
    ordering = ['template_type', 'name']
    
    def template_type_badge(self, obj):
        """Display template type with badge"""
        return format_html(
            '<span style="background-color: #6366f1; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.get_template_type_display()
        )
    template_type_badge.short_description = 'Type'
    
    def user_display(self, obj):
        """Display user or system indicator"""
        if obj.is_system_template:
            return format_html('<span style="color: #059669; font-weight: bold;">🌐 System</span>')
        return obj.user.get_full_name() or obj.user.username if obj.user else 'System'
    user_display.short_description = 'Owner'
    
    def usage_count_display(self, obj):
        """Display usage count with styling"""
        return format_html('<span style="font-weight: bold; color: #059669;">{}</span>', obj.usage_count)
    usage_count_display.short_description = 'Usage'


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    """Admin interface for Journal Entries"""
    
    list_display = [
        'title_truncated',
        'user_display',
        'entry_date',
        'category_badge',
        'mood_display',
        'energy_display',
        'word_count_display',
        'is_favorite',
        'is_archived',
        'created_at'
    ]
    
    list_filter = [
        'entry_date',
        'category',
        'mood_rating',
        'energy_level',
        'privacy_level',
        'is_favorite',
        'is_archived',
        'is_draft',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'content',
        'user__username',
        'user__first_name',
        'user__last_name',
        'location'
    ]
    
    readonly_fields = [
        'entry_id',
        'word_count',
        'estimated_reading_time',
        'sentiment_score',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = [
        ('Entry Information', {
            'fields': [
                'entry_id',
                'user',
                'title',
                'content',
                'entry_date'
            ]
        }),
        ('Categorization', {
            'fields': [
                'category',
                'template'
            ]
        }),
        ('Mood & Energy', {
            'fields': [
                'mood_rating',
                'energy_level'
            ]
        }),
        ('Context', {
            'fields': [
                'location',
                'weather',
                'structured_data'
            ]
        }),
        ('Settings', {
            'fields': [
                'privacy_level',
                'is_favorite',
                'is_archived',
                'is_draft'
            ]
        }),
        ('AI Analysis', {
            'fields': [
                'ai_insights',
                'sentiment_score'
            ],
            'classes': ['collapse']
        }),
        ('Statistics', {
            'fields': [
                'word_count',
                'estimated_reading_time'
            ],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': [
                'created_at',
                'updated_at'
            ],
            'classes': ['collapse']
        })
    ]
    
    inlines = [JournalAttachmentInline, JournalEntryTagInline]
    ordering = ['-entry_date', '-created_at']
    date_hierarchy = 'entry_date'
    
    actions = [
        'mark_as_favorite',
        'archive_entries',
        'mark_as_public',
        'export_to_csv'
    ]
    
    def title_truncated(self, obj):
        """Display truncated title"""
        if len(obj.title) > 50:
            return obj.title[:50] + '...'
        return obj.title
    title_truncated.short_description = 'Title'
    
    def user_display(self, obj):
        """Display user name"""
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'User'
    
    def category_badge(self, obj):
        """Display category with color"""
        if obj.category:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{}</span>',
                obj.category.color_hex,
                obj.category.name
            )
        return format_html('<span style="color: #94a3b8;">No Category</span>')
    category_badge.short_description = 'Category'
    
    def mood_display(self, obj):
        """Display mood with emoji"""
        if obj.mood_rating:
            return format_html(
                '<span style="font-size: 16px;">{}</span>',
                obj.mood_emoji
            )
        return format_html('<span style="color: #94a3b8;">-</span>')
    mood_display.short_description = 'Mood'
    
    def energy_display(self, obj):
        """Display energy with emoji"""
        if obj.energy_level:
            return format_html(
                '<span style="font-size: 14px;">{}</span>',
                obj.energy_emoji
            )
        return format_html('<span style="color: #94a3b8;">-</span>')
    energy_display.short_description = 'Energy'
    
    def word_count_display(self, obj):
        """Display word count with formatting"""
        if obj.word_count > 0:
            return format_html('<span style="font-weight: bold;">{}</span>', obj.word_count)
        return format_html('<span style="color: #94a3b8;">0</span>')
    word_count_display.short_description = 'Words'
    
    # Admin Actions
    def mark_as_favorite(self, request, queryset):
        """Mark selected entries as favorite"""
        updated = queryset.update(is_favorite=True)
        self.message_user(request, f'{updated} entries marked as favorite.')
    mark_as_favorite.short_description = 'Mark as favorite'
    
    def archive_entries(self, request, queryset):
        """Archive selected entries"""
        updated = queryset.update(is_archived=True)
        self.message_user(request, f'{updated} entries archived.')
    archive_entries.short_description = 'Archive entries'
    
    def mark_as_public(self, request, queryset):
        """Mark selected entries as public"""
        updated = queryset.update(privacy_level='PUBLIC')
        self.message_user(request, f'{updated} entries marked as public.')
    mark_as_public.short_description = 'Mark as public'


@admin.register(JournalTag)
class JournalTagAdmin(admin.ModelAdmin):
    """Admin interface for Journal Tags"""
    
    list_display = [
        'name',
        'user_display',
        'color_preview',
        'usage_count_display',
        'created_at'
    ]
    
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['usage_count']
    ordering = ['-usage_count', 'name']
    
    def user_display(self, obj):
        """Display user name"""
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'User'
    
    def color_preview(self, obj):
        """Display color preview"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color_hex
        )
    color_preview.short_description = 'Color'
    
    def usage_count_display(self, obj):
        """Display usage count with styling"""
        return format_html('<span style="font-weight: bold; color: #059669;">{}</span>', obj.usage_count)
    usage_count_display.short_description = 'Usage'


@admin.register(JournalStreak)
class JournalStreakAdmin(admin.ModelAdmin):
    """Admin interface for Journal Streaks"""
    
    list_display = [
        'user_display',
        'current_streak_display',
        'longest_streak_display',
        'total_entries_display',
        'last_entry_date',
        'streak_status'
    ]
    
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['milestones_achieved', 'created_at', 'updated_at']
    ordering = ['-current_streak', '-longest_streak']
    
    def user_display(self, obj):
        """Display user name"""
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'User'
    
    def current_streak_display(self, obj):
        """Display current streak with styling"""
        if obj.current_streak >= 30:
            color = '#059669'  # Green for 30+ days
        elif obj.current_streak >= 7:
            color = '#d97706'  # Orange for 7+ days
        else:
            color = '#6b7280'  # Gray for less than 7 days
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} days</span>',
            color,
            obj.current_streak
        )
    current_streak_display.short_description = 'Current Streak'
    
    def longest_streak_display(self, obj):
        """Display longest streak"""
        return format_html('<span style="font-weight: bold;">{} days</span>', obj.longest_streak)
    longest_streak_display.short_description = 'Longest Streak'
    
    def total_entries_display(self, obj):
        """Display total entries"""
        return format_html('<span style="font-weight: bold;">{}</span>', obj.total_entries)
    total_entries_display.short_description = 'Total Entries'
    
    def streak_status(self, obj):
        """Display streak status"""
        if not obj.last_entry_date:
            return format_html('<span style="color: #94a3b8;">No entries</span>')
        
        from datetime import date
        days_since = (date.today() - obj.last_entry_date).days
        
        if days_since == 0:
            return format_html('<span style="color: #059669;">✅ Active today</span>')
        elif days_since == 1:
            return format_html('<span style="color: #d97706;">⚠️ Due today</span>')
        else:
            return format_html('<span style="color: #ef4444;">❌ Broken {} days ago</span>', days_since)
    streak_status.short_description = 'Status'


@admin.register(JournalInsight)
class JournalInsightAdmin(admin.ModelAdmin):
    """Admin interface for Journal Insights"""
    
    list_display = [
        'title_truncated',
        'user_display',
        'insight_type_badge',
        'confidence_display',
        'entries_analyzed',
        'is_acknowledged',
        'is_helpful',
        'generated_at'
    ]
    
    list_filter = [
        'insight_type',
        'is_acknowledged',
        'is_helpful',
        'generated_at'
    ]
    
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = [
        'insight_data',
        'confidence_score',
        'analysis_start_date',
        'analysis_end_date',
        'entries_analyzed',
        'generated_at'
    ]
    
    ordering = ['-generated_at']
    date_hierarchy = 'generated_at'
    
    def title_truncated(self, obj):
        """Display truncated title"""
        if len(obj.title) > 40:
            return obj.title[:40] + '...'
        return obj.title
    title_truncated.short_description = 'Title'
    
    def user_display(self, obj):
        """Display user name"""
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'User'
    
    def insight_type_badge(self, obj):
        """Display insight type with badge"""
        colors = {
            'MOOD_PATTERN': '#3b82f6',
            'WORD_FREQUENCY': '#10b981',
            'TOPIC_ANALYSIS': '#f59e0b',
            'SENTIMENT_TREND': '#ef4444',
            'WRITING_STYLE': '#8b5cf6',
            'TIME_PATTERN': '#06b6d4',
            'CATEGORY_ANALYSIS': '#84cc16',
            'GOAL_PROGRESS': '#f97316'
        }
        color = colors.get(obj.insight_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_insight_type_display()
        )
    insight_type_badge.short_description = 'Type'
    
    def confidence_display(self, obj):
        """Display confidence score with color coding"""
        if obj.confidence_score >= 0.8:
            color = '#059669'
        elif obj.confidence_score >= 0.6:
            color = '#d97706'
        else:
            color = '#ef4444'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1%}</span>',
            color,
            obj.confidence_score
        )
    confidence_display.short_description = 'Confidence'


@admin.register(JournalReminder)
class JournalReminderAdmin(admin.ModelAdmin):
    """Admin interface for Journal Reminders"""
    
    list_display = [
        'title',
        'user_display',
        'reminder_type_badge',
        'frequency_badge',
        'reminder_time',
        'is_active',
        'last_sent',
        'next_reminder'
    ]
    
    list_filter = [
        'reminder_type',
        'frequency',
        'is_active',
        'created_at'
    ]
    
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['last_sent', 'next_reminder', 'created_at', 'updated_at']
    ordering = ['reminder_time']
    
    def user_display(self, obj):
        """Display user name"""
        return obj.user.get_full_name() or obj.user.username
    user_display.short_description = 'User'
    
    def reminder_type_badge(self, obj):
        """Display reminder type with badge"""
        return format_html(
            '<span style="background-color: #6366f1; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.get_reminder_type_display()
        )
    reminder_type_badge.short_description = 'Type'
    
    def frequency_badge(self, obj):
        """Display frequency with badge"""
        colors = {
            'DAILY': '#059669',
            'WEEKLY': '#d97706',
            'MONTHLY': '#3b82f6',
            'CUSTOM': '#8b5cf6'
        }
        color = colors.get(obj.frequency, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_frequency_display()
        )
    frequency_badge.short_description = 'Frequency'


# Register remaining models with simple admin
admin.site.register(JournalAttachment)
admin.site.register(JournalEntryTag)
