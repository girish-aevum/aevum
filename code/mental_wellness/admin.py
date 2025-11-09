from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from .models import (
    MoodCategory, Emotion, ActivityType, MoodTrigger, 
    MoodEntry, MoodInsight
)


@admin.register(MoodCategory)
class MoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_preview', 'icon', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Display Settings', {
            'fields': ('color_hex', 'icon')
        }),
    )
    
    def color_preview(self, obj):
        if obj.color_hex:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
                obj.color_hex
            )
        return '-'
    color_preview.short_description = 'Color'


@admin.register(Emotion)
class EmotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'emotion_type', 'color_preview', 'intensity_scale', 'is_active')
    list_filter = ('emotion_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('emotion_type', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'emotion_type', 'description', 'is_active')
        }),
        ('Measurement', {
            'fields': ('intensity_scale',)
        }),
        ('Display Settings', {
            'fields': ('color_hex',)
        }),
    )
    
    def color_preview(self, obj):
        if obj.color_hex:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
                obj.color_hex
            )
        return '-'
    color_preview.short_description = 'Color'


@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'typical_mood_impact', 'is_active', 'usage_count')
    list_filter = ('category', 'typical_mood_impact', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('Mood Impact', {
            'fields': ('typical_mood_impact',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            usage_count=Count('moodentry')
        )
    
    def usage_count(self, obj):
        return obj.usage_count
    usage_count.short_description = 'Usage Count'
    usage_count.admin_order_field = 'usage_count'


@admin.register(MoodTrigger)
class MoodTriggerAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'typical_impact', 'is_active', 'usage_count')
    list_filter = ('category', 'typical_impact', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('Mood Impact', {
            'fields': ('typical_impact',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            usage_count=Count('moodentry')
        )
    
    def usage_count(self, obj):
        return obj.usage_count
    usage_count.short_description = 'Usage Count'
    usage_count.admin_order_field = 'usage_count'


class MoodEntryEmotionInline(admin.TabularInline):
    model = MoodEntry.emotions.through
    extra = 0
    verbose_name = "Emotion"
    verbose_name_plural = "Emotions"


class MoodEntryActivityInline(admin.TabularInline):
    model = MoodEntry.activities.through
    extra = 0
    verbose_name = "Activity"
    verbose_name_plural = "Activities"


class MoodEntryTriggerInline(admin.TabularInline):
    model = MoodEntry.triggers.through
    extra = 0
    verbose_name = "Trigger"
    verbose_name_plural = "Triggers"


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'entry_date', 'entry_time', 'mood_level_display', 
        'energy_level_display', 'anxiety_level_display', 'wellbeing_score', 
        'trend_indicator', 'emotions_count'
    )
    list_filter = (
        'entry_date', 'mood_level', 'energy_level', 'anxiety_level',
        'mood_category', 'created_at'
    )
    search_fields = ('user__username', 'user__email', 'notes', 'gratitude_note')
    readonly_fields = ('entry_id', 'wellbeing_score', 'trend_indicator', 'created_at', 'updated_at')
    ordering = ('-entry_date', '-entry_time')
    date_hierarchy = 'entry_date'
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('entry_id', 'user', 'entry_date', 'entry_time', 'mood_category')
        }),
        ('Core Metrics', {
            'fields': ('mood_level', 'energy_level', 'anxiety_level', 'stress_level')
        }),
        ('Sleep & Health', {
            'fields': ('sleep_quality', 'sleep_hours'),
            'classes': ('collapse',)
        }),
        ('Context', {
            'fields': ('weather_condition', 'location'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes', 'gratitude_note', 'goals_tomorrow'),
            'classes': ('collapse',)
        }),
        ('Calculated Fields', {
            'fields': ('wellbeing_score', 'trend_indicator'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MoodEntryEmotionInline, MoodEntryActivityInline, MoodEntryTriggerInline]
    
    def mood_level_display(self, obj):
        color = '#4CAF50' if obj.mood_level >= 7 else '#FF9800' if obj.mood_level >= 4 else '#F44336'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/10</span>',
            color, obj.mood_level
        )
    mood_level_display.short_description = 'Mood'
    mood_level_display.admin_order_field = 'mood_level'
    
    def energy_level_display(self, obj):
        color = '#4CAF50' if obj.energy_level >= 7 else '#FF9800' if obj.energy_level >= 4 else '#F44336'
        return format_html(
            '<span style="color: {};">{}/10</span>',
            color, obj.energy_level
        )
    energy_level_display.short_description = 'Energy'
    energy_level_display.admin_order_field = 'energy_level'
    
    def anxiety_level_display(self, obj):
        color = '#F44336' if obj.anxiety_level >= 7 else '#FF9800' if obj.anxiety_level >= 4 else '#4CAF50'
        return format_html(
            '<span style="color: {};">{}/10</span>',
            color, obj.anxiety_level
        )
    anxiety_level_display.short_description = 'Anxiety'
    anxiety_level_display.admin_order_field = 'anxiety_level'
    
    def wellbeing_score(self, obj):
        try:
            score = obj.overall_wellbeing_score
            if score is None or score == 0.0:
                return format_html('<span style="color: #9E9E9E;">N/A</span>')
            
            color = '#4CAF50' if score >= 7 else '#FF9800' if score >= 5 else '#F44336'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, score
            )
        except (TypeError, AttributeError):
            return format_html('<span style="color: #9E9E9E;">Error</span>')
    wellbeing_score.short_description = 'Wellbeing Score'
    
    def trend_indicator(self, obj):
        try:
            trend = obj.mood_trend_indicator
            colors = {
                'IMPROVING': '#4CAF50',
                'STABLE': '#2196F3',
                'DECLINING': '#F44336',
                'NEUTRAL': '#9E9E9E'
            }
            icons = {
                'IMPROVING': '↗',
                'STABLE': '→',
                'DECLINING': '↘',
                'NEUTRAL': '•'
            }
            return format_html(
                '<span style="color: {};">{} {}</span>',
                colors.get(trend, '#9E9E9E'),
                icons.get(trend, '•'),
                trend
            )
        except (TypeError, AttributeError):
            return format_html('<span style="color: #9E9E9E;">• ERROR</span>')
    trend_indicator.short_description = 'Trend'
    
    def emotions_count(self, obj):
        return obj.emotions.count()
    emotions_count.short_description = 'Emotions'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'mood_category')


@admin.register(MoodInsight)
class MoodInsightAdmin(admin.ModelAdmin):
    list_display = (
        'title_short', 'user', 'insight_type', 'confidence_score',
        'actionable', 'user_acknowledged', 'generated_at'
    )
    list_filter = (
        'insight_type', 'actionable', 'user_acknowledged', 
        'is_active', 'generated_at'
    )
    search_fields = ('user__username', 'title', 'description')
    readonly_fields = ('generated_at',)
    ordering = ('-generated_at',)
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Insight Information', {
            'fields': ('user', 'insight_type', 'title', 'description')
        }),
        ('Analysis', {
            'fields': ('confidence_score', 'date_range_start', 'date_range_end')
        }),
        ('Actions', {
            'fields': ('actionable', 'action_items')
        }),
        ('Status', {
            'fields': ('is_active', 'user_acknowledged', 'acknowledged_at')
        }),
        ('Metadata', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def title_short(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Admin actions
def mark_insights_acknowledged(modeladmin, request, queryset):
    queryset.update(user_acknowledged=True)
mark_insights_acknowledged.short_description = "Mark selected insights as acknowledged"

def deactivate_insights(modeladmin, request, queryset):
    queryset.update(is_active=False)
deactivate_insights.short_description = "Deactivate selected insights"

MoodInsightAdmin.actions = [mark_insights_acknowledged, deactivate_insights]
