from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, time
from .models import (
    MoodCategory, Emotion, ActivityType, MoodTrigger, 
    MoodEntry, MoodInsight
)


class MoodCategorySerializer(serializers.ModelSerializer):
    """Serializer for mood categories"""
    
    class Meta:
        model = MoodCategory
        fields = ['id', 'name', 'description', 'color_hex', 'icon', 'is_active']
        read_only_fields = ('id',)


class EmotionSerializer(serializers.ModelSerializer):
    """Serializer for emotions"""
    
    class Meta:
        model = Emotion
        fields = [
            'id', 'name', 'emotion_type', 'description', 
            'intensity_scale', 'color_hex', 'is_active'
        ]
        read_only_fields = ('id',)


class ActivityTypeSerializer(serializers.ModelSerializer):
    """Serializer for activity types"""
    
    class Meta:
        model = ActivityType
        fields = [
            'id', 'name', 'category', 'description', 
            'typical_mood_impact', 'is_active'
        ]
        read_only_fields = ('id',)


class MoodTriggerSerializer(serializers.ModelSerializer):
    """Serializer for mood triggers"""
    
    class Meta:
        model = MoodTrigger
        fields = [
            'id', 'name', 'category', 'description', 
            'typical_impact', 'is_active'
        ]
        read_only_fields = ('id',)


class MoodEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating mood entries"""
    
    emotion_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="List of emotion IDs"
    )
    activity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="List of activity type IDs"
    )
    trigger_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="List of mood trigger IDs"
    )
    
    class Meta:
        model = MoodEntry
        fields = [
            'entry_date', 'entry_time', 'mood_level', 'energy_level', 
            'anxiety_level', 'stress_level', 'sleep_quality', 'sleep_hours',
            'mood_category', 'emotion_ids', 'activity_ids', 'trigger_ids',
            'notes', 'gratitude_note', 'goals_tomorrow', 'weather_condition', 
            'location'
        ]
    
    def validate_entry_date(self, value):
        """Validate entry date is not in the future"""
        if value > date.today():
            raise serializers.ValidationError("Entry date cannot be in the future.")
        return value
    
    def validate_entry_time(self, value):
        """Validate entry time"""
        entry_date = self.initial_data.get('entry_date', date.today())
        if isinstance(entry_date, str):
            entry_date = serializers.DateField().to_internal_value(entry_date)
        
        # If entry is for today, time cannot be in the future
        if entry_date == date.today():
            current_time = timezone.now().time()
            if value > current_time:
                raise serializers.ValidationError("Entry time cannot be in the future for today's date.")
        
        return value
    
    def validate_emotion_ids(self, value):
        """Validate emotion IDs exist"""
        if value:
            existing_ids = Emotion.objects.filter(id__in=value, is_active=True).values_list('id', flat=True)
            missing_ids = set(value) - set(existing_ids)
            if missing_ids:
                raise serializers.ValidationError(f"Invalid emotion IDs: {list(missing_ids)}")
        return value
    
    def validate_activity_ids(self, value):
        """Validate activity IDs exist"""
        if value:
            existing_ids = ActivityType.objects.filter(id__in=value, is_active=True).values_list('id', flat=True)
            missing_ids = set(value) - set(existing_ids)
            if missing_ids:
                raise serializers.ValidationError(f"Invalid activity IDs: {list(missing_ids)}")
        return value
    
    def validate_trigger_ids(self, value):
        """Validate trigger IDs exist"""
        if value:
            existing_ids = MoodTrigger.objects.filter(id__in=value, is_active=True).values_list('id', flat=True)
            missing_ids = set(value) - set(existing_ids)
            if missing_ids:
                raise serializers.ValidationError(f"Invalid trigger IDs: {list(missing_ids)}")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        user = self.context['request'].user
        entry_date = data.get('entry_date', date.today())
        entry_time = data.get('entry_time', timezone.now().time())
        
        # Check for duplicate entries (same user, date, and time)
        if MoodEntry.objects.filter(
            user=user, 
            entry_date=entry_date, 
            entry_time=entry_time
        ).exists():
            raise serializers.ValidationError(
                "A mood entry already exists for this date and time. Please choose a different time."
            )
        
        return data
    
    def create(self, validated_data):
        """Create mood entry with relationships"""
        emotion_ids = validated_data.pop('emotion_ids', [])
        activity_ids = validated_data.pop('activity_ids', [])
        trigger_ids = validated_data.pop('trigger_ids', [])
        
        # Set user from request context
        validated_data['user'] = self.context['request'].user
        
        # Create the mood entry
        mood_entry = MoodEntry.objects.create(**validated_data)
        
        # Set many-to-many relationships
        if emotion_ids:
            mood_entry.emotions.set(emotion_ids)
        if activity_ids:
            mood_entry.activities.set(activity_ids)
        if trigger_ids:
            mood_entry.triggers.set(trigger_ids)
        
        return mood_entry


class MoodEntryDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for mood entries with nested relationships"""
    
    mood_category = MoodCategorySerializer(read_only=True)
    emotions = EmotionSerializer(many=True, read_only=True)
    activities = ActivityTypeSerializer(many=True, read_only=True)
    triggers = MoodTriggerSerializer(many=True, read_only=True)
    
    # Additional computed fields
    overall_wellbeing_score = serializers.ReadOnlyField()
    mood_trend_indicator = serializers.ReadOnlyField()
    mood_level_display = serializers.CharField(source='get_mood_level_display', read_only=True)
    energy_level_display = serializers.CharField(source='get_energy_level_display', read_only=True)
    anxiety_level_display = serializers.CharField(source='get_anxiety_level_display', read_only=True)
    
    class Meta:
        model = MoodEntry
        fields = [
            'id', 'entry_id', 'entry_date', 'entry_time', 
            'mood_level', 'mood_level_display', 'energy_level', 'energy_level_display',
            'anxiety_level', 'anxiety_level_display', 'stress_level', 
            'sleep_quality', 'sleep_hours', 'mood_category', 'emotions', 
            'activities', 'triggers', 'notes', 'gratitude_note', 
            'goals_tomorrow', 'weather_condition', 'location',
            'overall_wellbeing_score', 'mood_trend_indicator',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'entry_id', 'created_at', 'updated_at')


class MoodEntryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing mood entries"""
    
    mood_level_display = serializers.CharField(source='get_mood_level_display', read_only=True)
    energy_level_display = serializers.CharField(source='get_energy_level_display', read_only=True)
    overall_wellbeing_score = serializers.ReadOnlyField()
    mood_trend_indicator = serializers.ReadOnlyField()
    emotions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MoodEntry
        fields = [
            'id', 'entry_id', 'entry_date', 'entry_time',
            'mood_level', 'mood_level_display', 'energy_level', 'energy_level_display',
            'anxiety_level', 'overall_wellbeing_score', 'mood_trend_indicator',
            'emotions_count', 'notes'
        ]
    
    def get_emotions_count(self, obj):
        """Get count of emotions for this entry"""
        return obj.emotions.count()


class MoodEntryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating mood entries"""
    
    emotion_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    activity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    trigger_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = MoodEntry
        fields = [
            'mood_level', 'energy_level', 'anxiety_level', 'stress_level',
            'sleep_quality', 'sleep_hours', 'mood_category', 'emotion_ids',
            'activity_ids', 'trigger_ids', 'notes', 'gratitude_note',
            'goals_tomorrow', 'weather_condition', 'location'
        ]
    
    def update(self, instance, validated_data):
        """Update mood entry with relationships"""
        emotion_ids = validated_data.pop('emotion_ids', None)
        activity_ids = validated_data.pop('activity_ids', None)
        trigger_ids = validated_data.pop('trigger_ids', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update many-to-many relationships if provided
        if emotion_ids is not None:
            instance.emotions.set(emotion_ids)
        if activity_ids is not None:
            instance.activities.set(activity_ids)
        if trigger_ids is not None:
            instance.triggers.set(trigger_ids)
        
        return instance


class MoodInsightSerializer(serializers.ModelSerializer):
    """Serializer for mood insights"""
    
    insight_type_display = serializers.CharField(source='get_insight_type_display', read_only=True)
    related_entries_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MoodInsight
        fields = [
            'id', 'insight_type', 'insight_type_display', 'title', 
            'description', 'confidence_score', 'date_range_start', 
            'date_range_end', 'related_entries_count', 'actionable', 
            'action_items', 'is_active', 'user_acknowledged', 
            'acknowledged_at', 'generated_at'
        ]
        read_only_fields = ('id', 'generated_at')
    
    def get_related_entries_count(self, obj):
        """Get count of related mood entries"""
        return obj.related_entries.count()


class MoodStatisticsSerializer(serializers.Serializer):
    """Serializer for mood statistics and analytics"""
    
    total_entries = serializers.IntegerField()
    entries_this_week = serializers.IntegerField()
    entries_this_month = serializers.IntegerField()
    
    # Average scores
    avg_mood_level = serializers.DecimalField(max_digits=4, decimal_places=2)
    avg_energy_level = serializers.DecimalField(max_digits=4, decimal_places=2)
    avg_anxiety_level = serializers.DecimalField(max_digits=4, decimal_places=2)
    avg_wellbeing_score = serializers.DecimalField(max_digits=4, decimal_places=2)
    
    # Trends
    mood_trend = serializers.CharField()  # IMPROVING, DECLINING, STABLE
    streak_days = serializers.IntegerField()  # Days of consecutive logging
    
    # Most common
    most_common_emotions = serializers.ListField(child=serializers.DictField())
    most_common_activities = serializers.ListField(child=serializers.DictField())
    most_common_triggers = serializers.ListField(child=serializers.DictField())
    
    # Recent data
    recent_entries = MoodEntryListSerializer(many=True)
    latest_insights = MoodInsightSerializer(many=True)


class MoodDashboardSerializer(serializers.Serializer):
    """Comprehensive dashboard data for mood tracking"""
    
    # Today's data
    todays_entry = MoodEntryDetailSerializer(allow_null=True)
    has_logged_today = serializers.BooleanField()
    
    # Quick stats
    current_streak = serializers.IntegerField()
    total_entries = serializers.IntegerField()
    avg_mood_this_week = serializers.DecimalField(max_digits=4, decimal_places=2)
    mood_trend = serializers.CharField()
    
    # Recent entries
    recent_entries = MoodEntryListSerializer(many=True)
    
    # Insights
    active_insights = MoodInsightSerializer(many=True)
    insights_count = serializers.IntegerField()
    
    # Quick actions
    suggested_activities = ActivityTypeSerializer(many=True)
    common_emotions = EmotionSerializer(many=True)


class QuickMoodEntrySerializer(serializers.ModelSerializer):
    """Simplified serializer for quick mood logging"""
    
    class Meta:
        model = MoodEntry
        fields = ['mood_level', 'energy_level', 'anxiety_level', 'notes']
    
    def create(self, validated_data):
        """Create a quick mood entry with minimal data"""
        validated_data['user'] = self.context['request'].user
        validated_data['entry_date'] = date.today()
        validated_data['entry_time'] = timezone.now().time()
        
        return MoodEntry.objects.create(**validated_data) 