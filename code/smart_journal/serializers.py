from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta, datetime
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


class JournalCategorySerializer(serializers.ModelSerializer):
    """Serializer for journal categories"""
    
    entry_count = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalCategory
        fields = [
            'id',
            'name',
            'category_type',
            'description',
            'color_hex',
            'icon',
            'is_active',
            'entry_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_entry_count(self, obj):
        """Get count of entries in this category"""
        return obj.journal_entries.filter(is_archived=False).count()
    
    def validate_color_hex(self, value):
        """Validate hex color format"""
        if value and not value.startswith('#'):
            value = f"#{value}"
        if len(value) != 7:
            raise serializers.ValidationError("Color must be in hex format (#RRGGBB)")
        return value


class JournalTemplateSerializer(serializers.ModelSerializer):
    """Serializer for journal templates"""
    
    usage_count = serializers.ReadOnlyField()
    
    class Meta:
        model = JournalTemplate
        fields = [
            'id',
            'name',
            'template_type',
            'description',
            'prompt_questions',
            'default_structure',
            'is_public',
            'is_active',
            'usage_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['usage_count', 'created_at', 'updated_at']
    
    def validate_prompt_questions(self, value):
        """Validate prompt questions format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Prompt questions must be a list")
        return value


class JournalTagSerializer(serializers.ModelSerializer):
    """Serializer for journal tags"""
    
    usage_count = serializers.ReadOnlyField()
    
    class Meta:
        model = JournalTag
        fields = [
            'id',
            'name',
            'color_hex',
            'usage_count',
            'created_at'
        ]
        read_only_fields = ['usage_count', 'created_at']
    
    def validate_name(self, value):
        """Validate tag name"""
        if value:
            value = value.strip().lower()
            if len(value) < 2:
                raise serializers.ValidationError("Tag name must be at least 2 characters long")
        return value


class JournalAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for journal attachments"""
    
    file_url = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalAttachment
        fields = [
            'id',
            'file',
            'file_url',
            'file_name',
            'file_size',
            'file_size_display',
            'file_type',
            'description',
            'uploaded_at'
        ]
        read_only_fields = ['file_name', 'file_size', 'file_type', 'uploaded_at']
    
    def get_file_url(self, obj):
        """Get file URL"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_size_display(self, obj):
        """Get human-readable file size"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "Unknown"


class JournalEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating journal entries"""
    
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        write_only=True,
        help_text="List of tag names to associate with this entry"
    )
    
    class Meta:
        model = JournalEntry
        fields = [
            'title',
            'content',
            'category',
            'template',
            'entry_date',
            'mood_rating',
            'energy_level',
            'structured_data',
            'location',
            'weather',
            'privacy_level',
            'is_favorite',
            'is_draft',
            'tag_names'
        ]
    
    def validate_entry_date(self, value):
        # If no date is provided, use today's date
        if not value:
            return date.today()
        
        # If a string is provided, convert it to a date
        if isinstance(value, str):
            try:
                # Parse the date string, ensuring it's in the correct format
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD.")
        
        # If it's already a date object, return it
        if isinstance(value, date):
            return value
        
        raise serializers.ValidationError("Invalid date format.")
    
    def validate_content(self, value):
        """Validate content length"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Journal entry must be at least 10 characters long")
        return value.strip()
    
    def create(self, validated_data):
        # Extract tag names if present
        tag_names = validated_data.pop('tag_names', []) if 'tag_names' in validated_data else []
        
        # Always use today's date for the entry
        validated_data['entry_date'] = date.today()
        
        # Get the user from the context
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Create the journal entry
        entry = JournalEntry.objects.create(**validated_data)
        
        # Handle tags
        if tag_names:
            for tag_name in tag_names:
                tag, created = JournalTag.objects.get_or_create(
                    name=tag_name.strip().lower(),
                    user=user,
                    defaults={'color_hex': '#6b7280'}
                )
                JournalEntryTag.objects.create(entry=entry, tag=tag)
                tag.increment_usage()
        
        # Update template usage if used
        if entry.template:
            entry.template.increment_usage()
        
        # Update user's streak
        streak, _ = JournalStreak.objects.get_or_create(user=user)
        streak.update_streak(entry.entry_date)
        
        return entry


class JournalEntryListSerializer(serializers.ModelSerializer):
    """Serializer for listing journal entries"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color_hex', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    mood_emoji = serializers.CharField(read_only=True)
    energy_emoji = serializers.CharField(read_only=True)
    content_preview = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()
    days_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalEntry
        fields = [
            'entry_id',
            'title',
            'content_preview',
            'category_name',
            'category_color',
            'template_name',
            'entry_date',
            'mood_rating',
            'mood_emoji',
            'energy_level',
            'energy_emoji',
            'location',
            'privacy_level',
            'is_favorite',
            'is_archived',
            'is_draft',
            'word_count',
            'estimated_reading_time',
            'tags',
            'attachment_count',
            'days_ago',
            'created_at',
            'updated_at'
        ]
    
    def get_content_preview(self, obj):
        """Get preview of content"""
        if obj.content:
            return obj.content[:200] + "..." if len(obj.content) > 200 else obj.content
        return ""
    
    def get_tags(self, obj):
        """Get list of tag names"""
        return [tag.name for tag in obj.tags.all()]
    
    def get_attachment_count(self, obj):
        """Get count of attachments"""
        return obj.attachments.count()
    
    def get_days_ago(self, obj):
        """Calculate days since entry date"""
        delta = date.today() - obj.entry_date
        if delta.days == 0:
            return "Today"
        elif delta.days == 1:
            return "Yesterday"
        else:
            return f"{delta.days} days ago"


class JournalEntryDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed journal entry view"""
    
    category = JournalCategorySerializer(read_only=True)
    template = JournalTemplateSerializer(read_only=True)
    tags = JournalTagSerializer(many=True, read_only=True)
    attachments = JournalAttachmentSerializer(many=True, read_only=True)
    mood_emoji = serializers.CharField(read_only=True)
    energy_emoji = serializers.CharField(read_only=True)
    days_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalEntry
        fields = '__all__'
        read_only_fields = [
            'entry_id', 'user', 'word_count', 'estimated_reading_time',
            'ai_insights', 'sentiment_score', 'created_at', 'updated_at'
        ]
    
    def get_days_ago(self, obj):
        """Calculate days since entry date"""
        delta = date.today() - obj.entry_date
        if delta.days == 0:
            return "Today"
        elif delta.days == 1:
            return "Yesterday"
        else:
            return f"{delta.days} days ago"


class JournalEntryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating journal entries"""
    
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        write_only=True,
        help_text="List of tag names to associate with this entry"
    )
    
    class Meta:
        model = JournalEntry
        fields = [
            'title',
            'content',
            'category',
            'template',
            'entry_date',
            'mood_rating',
            'energy_level',
            'structured_data',
            'location',
            'weather',
            'privacy_level',
            'is_favorite',
            'is_archived',
            'is_draft',
            'tag_names'
        ]
    
    def update(self, instance, validated_data):
        """Update journal entry with tags"""
        tag_names = validated_data.pop('tag_names', None)
        
        # Update the entry
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle tags if provided
        if tag_names is not None:
            # Clear existing tags
            instance.tags.clear()
            
            # Add new tags
            for tag_name in tag_names:
                tag, created = JournalTag.objects.get_or_create(
                    name=tag_name.strip().lower(),
                    user=instance.user,
                    defaults={'color_hex': '#6b7280'}
                )
                JournalEntryTag.objects.create(entry=instance, tag=tag)
                tag.increment_usage()
        
        return instance


class JournalStreakSerializer(serializers.ModelSerializer):
    """Serializer for journal streaks"""
    
    streak_status = serializers.SerializerMethodField()
    next_milestone = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalStreak
        fields = [
            'current_streak',
            'longest_streak',
            'total_entries',
            'last_entry_date',
            'milestones_achieved',
            'streak_status',
            'next_milestone',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_streak_status(self, obj):
        """Get current streak status"""
        if not obj.last_entry_date:
            return "No entries yet"
        
        days_since_last = (date.today() - obj.last_entry_date).days
        if days_since_last == 0:
            return "On track today!"
        elif days_since_last == 1:
            return "Write today to continue streak"
        else:
            return f"Streak broken {days_since_last} days ago"
    
    def get_next_milestone(self, obj):
        """Get next milestone to achieve"""
        milestones = [1, 7, 30, 100, 365]
        for milestone in milestones:
            if obj.current_streak < milestone:
                return {
                    'target': milestone,
                    'remaining': milestone - obj.current_streak,
                    'type': 'streak'
                }
        return None


class JournalInsightSerializer(serializers.ModelSerializer):
    """Serializer for journal insights"""
    
    insight_type_display = serializers.CharField(source='get_insight_type_display', read_only=True)
    
    class Meta:
        model = JournalInsight
        fields = [
            'id',
            'insight_type',
            'insight_type_display',
            'title',
            'description',
            'insight_data',
            'confidence_score',
            'analysis_start_date',
            'analysis_end_date',
            'entries_analyzed',
            'is_acknowledged',
            'is_helpful',
            'user_feedback',
            'generated_at'
        ]
        read_only_fields = [
            'insight_data', 'confidence_score', 'analysis_start_date',
            'analysis_end_date', 'entries_analyzed', 'generated_at'
        ]


class JournalReminderSerializer(serializers.ModelSerializer):
    """Serializer for journal reminders"""
    
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    reminder_type_display = serializers.CharField(source='get_reminder_type_display', read_only=True)
    next_reminder_display = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalReminder
        fields = [
            'id',
            'title',
            'message',
            'reminder_type',
            'reminder_type_display',
            'frequency',
            'frequency_display',
            'reminder_time',
            'days_of_week',
            'is_active',
            'last_sent',
            'next_reminder',
            'next_reminder_display',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['last_sent', 'next_reminder', 'created_at', 'updated_at']
    
    def get_next_reminder_display(self, obj):
        """Get human-readable next reminder time"""
        if obj.next_reminder:
            delta = obj.next_reminder - timezone.now()
            if delta.days == 0:
                return "Today"
            elif delta.days == 1:
                return "Tomorrow"
            else:
                return f"In {delta.days} days"
        return "Not scheduled"
    
    def validate_days_of_week(self, value):
        """Validate days of week format"""
        if value:
            if not isinstance(value, list):
                raise serializers.ValidationError("Days of week must be a list")
            if not all(isinstance(day, int) and 0 <= day <= 6 for day in value):
                raise serializers.ValidationError("Days must be integers between 0 (Monday) and 6 (Sunday)")
        return value


class JournalStatsSerializer(serializers.Serializer):
    """Serializer for journal statistics"""
    
    total_entries = serializers.IntegerField()
    entries_this_week = serializers.IntegerField()
    entries_this_month = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    favorite_entries = serializers.IntegerField()
    total_words = serializers.IntegerField()
    average_mood = serializers.FloatField()
    average_energy = serializers.FloatField()
    most_used_category = serializers.CharField()
    most_used_tags = serializers.ListField()
    writing_frequency = serializers.DictField()
    mood_trends = serializers.DictField()
    recent_insights = serializers.ListField()
    
    class Meta:
        fields = [
            'total_entries', 'entries_this_week', 'entries_this_month',
            'current_streak', 'longest_streak', 'favorite_entries',
            'total_words', 'average_mood', 'average_energy',
            'most_used_category', 'most_used_tags', 'writing_frequency',
            'mood_trends', 'recent_insights'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for journal context"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']
        read_only_fields = ['username', 'email']


# Specialized serializers for different use cases
class JournalEntryQuickCreateSerializer(serializers.ModelSerializer):
    # Add tag_names as a write-only field
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )

    class Meta:
        model = JournalEntry
        fields = [
            'id', 'content', 'mood_rating', 'entry_date', 
            'tag_names'
        ]
        read_only_fields = ['id', 'entry_date']

    def create(self, validated_data):
        # Extract tag names if present
        tag_names = validated_data.pop('tag_names', []) if 'tag_names' in validated_data else []
        
        # Always use today's date for the entry
        validated_data['entry_date'] = date.today()
        
        # Get the user from the context
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Create the journal entry
        entry = JournalEntry.objects.create(**validated_data)
        
        # Handle tags
        if tag_names:
            for tag_name in tag_names:
                tag, created = JournalTag.objects.get_or_create(
                    name=tag_name.strip().lower(),
                    user=user,
                    defaults={'color_hex': '#6b7280'}
                )
                JournalEntryTag.objects.create(entry=entry, tag=tag)
                tag.increment_usage()
        
        # Update user's streak
        streak, _ = JournalStreak.objects.get_or_create(user=user)
        streak.update_streak(entry.entry_date)
        
        return entry


class JournalCategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating journal categories"""
    
    class Meta:
        model = JournalCategory
        fields = ['name', 'category_type', 'description', 'color_hex', 'icon']
    
    def create(self, validated_data):
        """Create journal category"""
        user = self.context['request'].user
        return JournalCategory.objects.create(user=user, **validated_data)


class JournalTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating journal templates"""
    
    class Meta:
        model = JournalTemplate
        fields = [
            'name', 'template_type', 'description',
            'prompt_questions', 'default_structure', 'is_public'
        ]
    
    def create(self, validated_data):
        """Create journal template"""
        user = self.context['request'].user
        return JournalTemplate.objects.create(user=user, **validated_data) 