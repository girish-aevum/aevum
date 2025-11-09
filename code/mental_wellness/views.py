from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status, filters
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import date, timedelta
from drf_spectacular.utils import extend_schema
from aevum.pagination import StandardResultsPagination, SmallResultsPagination
import logging

logger = logging.getLogger(__name__)

from .models import (
    MoodCategory, Emotion, ActivityType, MoodTrigger, 
    MoodEntry, MoodInsight
)
from .serializers import (
    MoodCategorySerializer, EmotionSerializer, ActivityTypeSerializer,
    MoodTriggerSerializer, MoodEntryCreateSerializer, MoodEntryDetailSerializer,
    MoodEntryListSerializer, MoodEntryUpdateSerializer, MoodInsightSerializer,
    MoodStatisticsSerializer, MoodDashboardSerializer, QuickMoodEntrySerializer
)


# Using centralized pagination classes from aevum.pagination


# Health check endpoint
@extend_schema(tags=['Mental Wellness'])
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "app": "mental_wellness"})


# Mood Categories
@extend_schema(
    tags=['Mental Wellness'],
    summary='List Mood Categories',
    description='Get all available mood categories'
)
class MoodCategoryListView(generics.ListAPIView):
    serializer_class = MoodCategorySerializer
    permission_classes = [AllowAny]
    queryset = MoodCategory.objects.filter(is_active=True)
    ordering = ['name']
    pagination_class = SmallResultsPagination


# Emotions
@extend_schema(
    tags=['Mental Wellness'],
    summary='List Emotions',
    description='Get all available emotions for mood tracking'
)
class EmotionListView(generics.ListAPIView):
    serializer_class = EmotionSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'emotion_type']
    ordering = ['emotion_type', 'name']
    pagination_class = StandardResultsPagination
    
    def get_queryset(self):
        queryset = Emotion.objects.filter(is_active=True)
        emotion_type = self.request.query_params.get('type')
        if emotion_type:
            queryset = queryset.filter(emotion_type=emotion_type)
        return queryset


# Activity Types
@extend_schema(
    tags=['Mental Wellness'],
    summary='List Activity Types',
    description='Get all available activity types that can influence mood'
)
class ActivityTypeListView(generics.ListAPIView):
    serializer_class = ActivityTypeSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category']
    ordering = ['category', 'name']
    pagination_class = StandardResultsPagination
    
    def get_queryset(self):
        queryset = ActivityType.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


# Mood Triggers
@extend_schema(
    tags=['Mental Wellness'],
    summary='List Mood Triggers',
    description='Get all available mood triggers'
)
class MoodTriggerListView(generics.ListAPIView):
    serializer_class = MoodTriggerSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category']
    ordering = ['category', 'name']
    pagination_class = StandardResultsPagination
    
    def get_queryset(self):
        queryset = MoodTrigger.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


# Mood Entry CRUD Operations
@extend_schema(
    tags=['Mental Wellness'],
    summary='Create Mood Entry',
    description='Log a new mood entry with detailed tracking information'
)
class MoodEntryCreateView(generics.CreateAPIView):
    serializer_class = MoodEntryCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Create mood entry and potentially generate insights"""
        mood_entry = serializer.save()
        
        # Trigger insight generation if user has enough entries
        self._check_and_generate_insights(mood_entry.user)
    
    def _check_and_generate_insights(self, user):
        """Check if we should generate new insights for the user"""
        entry_count = MoodEntry.objects.filter(user=user).count()
        
        # Generate insights after certain milestones
        if entry_count in [7, 14, 30] or entry_count % 30 == 0:
            # In production, this would be an async task
            self._generate_basic_insights(user)
    
    def _generate_basic_insights(self, user):
        """Generate basic insights for the user"""
        try:
            # Get recent entries for analysis
            recent_entries = MoodEntry.objects.filter(
                user=user,
                entry_date__gte=date.today() - timedelta(days=30)
            ).order_by('-entry_date')
            
            if recent_entries.count() >= 7:
                # Calculate average mood
                avg_mood = recent_entries.aggregate(avg=Avg('mood_level'))['avg']
                
                # Create a simple trend insight
                if avg_mood > 7:
                    title = "Great Mood Trend!"
                    description = f"Your average mood over the last 30 days is {avg_mood:.1f}/10. Keep up the great work!"
                elif avg_mood < 4:
                    title = "Mood Pattern Noticed"
                    description = f"Your average mood has been {avg_mood:.1f}/10. Consider reaching out for support."
                else:
                    title = "Steady Mood Pattern"
                    description = f"Your mood has been averaging {avg_mood:.1f}/10. Looking for consistent patterns."
                
                MoodInsight.objects.create(
                    user=user,
                    insight_type='TREND',
                    title=title,
                    description=description,
                    confidence_score=75.0,
                    date_range_start=date.today() - timedelta(days=30),
                    date_range_end=date.today(),
                    actionable=avg_mood < 5,
                    action_items=['Consider talking to a counselor', 'Try mood-boosting activities'] if avg_mood < 5 else []
                )
                
        except Exception as e:
            logger.error(f"Error generating insights for user {user.id}: {str(e)}")


@extend_schema(
    tags=['Mental Wellness'],
    summary='List Mood Entries',
    description='Get all mood entries for the authenticated user'
)
class MoodEntryListView(generics.ListAPIView):
    serializer_class = MoodEntryListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['notes', 'gratitude_note']
    ordering_fields = ['entry_date', 'mood_level', 'energy_level']
    ordering = ['-entry_date', '-entry_time']
    
    def get_queryset(self):
        queryset = MoodEntry.objects.filter(user=self.request.user)
        
        # Date filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(entry_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(entry_date__lte=date_to)
        
        # Mood level filtering
        mood_min = self.request.query_params.get('mood_min')
        mood_max = self.request.query_params.get('mood_max')
        
        if mood_min:
            queryset = queryset.filter(mood_level__gte=mood_min)
        if mood_max:
            queryset = queryset.filter(mood_level__lte=mood_max)
        
        # Quick filters
        filter_type = self.request.query_params.get('filter')
        if filter_type == 'today':
            queryset = queryset.filter(entry_date=date.today())
        elif filter_type == 'week':
            week_ago = date.today() - timedelta(days=7)
            queryset = queryset.filter(entry_date__gte=week_ago)
        elif filter_type == 'month':
            month_ago = date.today() - timedelta(days=30)
            queryset = queryset.filter(entry_date__gte=month_ago)
        
        return queryset


@extend_schema(
    tags=['Mental Wellness'],
    summary='Get Mood Entry Details',
    description='Get detailed information about a specific mood entry'
)
class MoodEntryDetailView(generics.RetrieveAPIView):
    serializer_class = MoodEntryDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user)


@extend_schema(
    tags=['Mental Wellness'],
    summary='Update Mood Entry',
    description='Update an existing mood entry'
)
class MoodEntryUpdateView(generics.UpdateAPIView):
    serializer_class = MoodEntryUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user)


@extend_schema(
    tags=['Mental Wellness'],
    summary='Delete Mood Entry',
    description='Delete a mood entry'
)
class MoodEntryDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user)


# Quick Mood Entry
@extend_schema(
    tags=['Mental Wellness'],
    summary='Quick Mood Entry',
    description='Create a quick mood entry with minimal required fields'
)
class QuickMoodEntryView(generics.CreateAPIView):
    serializer_class = QuickMoodEntrySerializer
    permission_classes = [IsAuthenticated]


# Mood Analytics and Statistics
@extend_schema(
    tags=['Mental Wellness'],
    summary='Mood Statistics',
    description='Get comprehensive mood statistics and analytics for the user'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mood_statistics(request):
    user = request.user
    
    # Get all user's mood entries
    all_entries = MoodEntry.objects.filter(user=user)
    
    # Date ranges
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Basic counts
    total_entries = all_entries.count()
    entries_this_week = all_entries.filter(entry_date__gte=week_ago).count()
    entries_this_month = all_entries.filter(entry_date__gte=month_ago).count()
    
    if total_entries == 0:
        return Response({
            'total_entries': 0,
            'message': 'No mood entries found. Start tracking your mood to see statistics!'
        })
    
    # Calculate averages
    averages = all_entries.aggregate(
        avg_mood=Avg('mood_level'),
        avg_energy=Avg('energy_level'),
        avg_anxiety=Avg('anxiety_level')
    )
    
    # Calculate average wellbeing score
    try:
        wellbeing_scores = []
        for entry in all_entries:
            try:
                score = entry.overall_wellbeing_score
                if score is not None and score > 0:
                    wellbeing_scores.append(score)
            except (TypeError, AttributeError):
                continue
        
        avg_wellbeing = sum(wellbeing_scores) / len(wellbeing_scores) if wellbeing_scores else 0
    except Exception as e:
        logger.warning(f"Error calculating wellbeing scores: {str(e)}")
        avg_wellbeing = 0
    
    # Determine mood trend
    recent_entries = all_entries.filter(entry_date__gte=week_ago).order_by('-entry_date')
    if recent_entries.count() >= 2:
        recent_avg = recent_entries.aggregate(avg=Avg('mood_level'))['avg']
        older_entries = all_entries.filter(
            entry_date__lt=week_ago,
            entry_date__gte=week_ago - timedelta(days=7)
        )
        if older_entries.exists():
            older_avg = older_entries.aggregate(avg=Avg('mood_level'))['avg']
            if recent_avg > older_avg + 0.5:
                mood_trend = 'IMPROVING'
            elif recent_avg < older_avg - 0.5:
                mood_trend = 'DECLINING'
            else:
                mood_trend = 'STABLE'
        else:
            mood_trend = 'STABLE'
    else:
        mood_trend = 'INSUFFICIENT_DATA'
    
    # Calculate streak
    streak_days = 0
    current_date = today
    while True:
        if all_entries.filter(entry_date=current_date).exists():
            streak_days += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    # Most common emotions, activities, triggers
    most_common_emotions = []
    most_common_activities = []
    most_common_triggers = []
    
    if total_entries > 0:
        # Get most common emotions
        emotion_counts = {}
        for entry in all_entries.prefetch_related('emotions'):
            for emotion in entry.emotions.all():
                emotion_counts[emotion.name] = emotion_counts.get(emotion.name, 0) + 1
        
        most_common_emotions = [
            {'name': name, 'count': count} 
            for name, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Similar for activities and triggers
        activity_counts = {}
        for entry in all_entries.prefetch_related('activities'):
            for activity in entry.activities.all():
                activity_counts[activity.name] = activity_counts.get(activity.name, 0) + 1
        
        most_common_activities = [
            {'name': name, 'count': count}
            for name, count in sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        trigger_counts = {}
        for entry in all_entries.prefetch_related('triggers'):
            for trigger in entry.triggers.all():
                trigger_counts[trigger.name] = trigger_counts.get(trigger.name, 0) + 1
        
        most_common_triggers = [
            {'name': name, 'count': count}
            for name, count in sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    # Recent entries
    recent_entries = all_entries.order_by('-entry_date', '-entry_time')[:10]
    
    # Latest insights
    latest_insights = MoodInsight.objects.filter(user=user, is_active=True).order_by('-generated_at')[:5]
    
    statistics_data = {
        'total_entries': total_entries,
        'entries_this_week': entries_this_week,
        'entries_this_month': entries_this_month,
        'avg_mood_level': round(averages['avg_mood'] or 0, 2),
        'avg_energy_level': round(averages['avg_energy'] or 0, 2),
        'avg_anxiety_level': round(averages['avg_anxiety'] or 0, 2),
        'avg_wellbeing_score': round(avg_wellbeing, 2),
        'mood_trend': mood_trend,
        'streak_days': streak_days,
        'most_common_emotions': most_common_emotions,
        'most_common_activities': most_common_activities,
        'most_common_triggers': most_common_triggers,
        'recent_entries': MoodEntryListSerializer(recent_entries, many=True).data,
        'latest_insights': MoodInsightSerializer(latest_insights, many=True).data
    }
    
    serializer = MoodStatisticsSerializer(statistics_data)
    return Response(serializer.data)


# Mood Dashboard
@extend_schema(
    tags=['Mental Wellness'],
    summary='Mood Dashboard',
    description='Get comprehensive dashboard data for mood tracking'
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mood_dashboard(request):
    user = request.user
    today = date.today()
    
    # Check if user has logged mood today
    todays_entry = MoodEntry.objects.filter(user=user, entry_date=today).first()
    has_logged_today = todays_entry is not None
    
    # Calculate current streak
    current_streak = 0
    check_date = today
    while True:
        if MoodEntry.objects.filter(user=user, entry_date=check_date).exists():
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # Total entries
    total_entries = MoodEntry.objects.filter(user=user).count()
    
    # Average mood this week
    week_ago = today - timedelta(days=7)
    this_week_entries = MoodEntry.objects.filter(user=user, entry_date__gte=week_ago)
    avg_mood_this_week = this_week_entries.aggregate(avg=Avg('mood_level'))['avg'] or 0
    
    # Mood trend
    if this_week_entries.count() >= 2:
        recent_avg = this_week_entries.aggregate(avg=Avg('mood_level'))['avg']
        prev_week_entries = MoodEntry.objects.filter(
            user=user,
            entry_date__gte=week_ago - timedelta(days=7),
            entry_date__lt=week_ago
        )
        if prev_week_entries.exists():
            prev_avg = prev_week_entries.aggregate(avg=Avg('mood_level'))['avg']
            if recent_avg > prev_avg + 0.5:
                mood_trend = 'IMPROVING'
            elif recent_avg < prev_avg - 0.5:
                mood_trend = 'DECLINING'
            else:
                mood_trend = 'STABLE'
        else:
            mood_trend = 'STABLE'
    else:
        mood_trend = 'INSUFFICIENT_DATA'
    
    # Recent entries
    recent_entries = MoodEntry.objects.filter(user=user).order_by('-entry_date', '-entry_time')[:7]
    
    # Active insights
    active_insights = MoodInsight.objects.filter(
        user=user, 
        is_active=True, 
        user_acknowledged=False
    ).order_by('-generated_at')[:3]
    
    insights_count = MoodInsight.objects.filter(user=user, is_active=True).count()
    
    # Suggested activities (based on user's most positive activities)
    user_activities = ActivityType.objects.filter(
        moodentry__user=user,
        moodentry__mood_level__gte=7
    ).distinct()[:5]
    
    if not user_activities:
        # Default suggestions
        user_activities = ActivityType.objects.filter(
            typical_mood_impact='POSITIVE',
            is_active=True
        )[:5]
    
    # Common emotions
    user_emotions = Emotion.objects.filter(
        moodentry__user=user
    ).annotate(
        usage_count=Count('moodentry')
    ).order_by('-usage_count')[:5]
    
    if not user_emotions:
        # Default emotions
        user_emotions = Emotion.objects.filter(is_active=True)[:5]
    
    dashboard_data = {
        'todays_entry': MoodEntryDetailSerializer(todays_entry).data if todays_entry else None,
        'has_logged_today': has_logged_today,
        'current_streak': current_streak,
        'total_entries': total_entries,
        'avg_mood_this_week': round(avg_mood_this_week, 2),
        'mood_trend': mood_trend,
        'recent_entries': MoodEntryListSerializer(recent_entries, many=True).data,
        'active_insights': MoodInsightSerializer(active_insights, many=True).data,
        'insights_count': insights_count,
        'suggested_activities': ActivityTypeSerializer(user_activities, many=True).data,
        'common_emotions': EmotionSerializer(user_emotions, many=True).data
    }
    
    serializer = MoodDashboardSerializer(dashboard_data)
    return Response(serializer.data)


# Mood Insights
@extend_schema(
    tags=['Mental Wellness'],
    summary='List Mood Insights',
    description='Get AI-generated insights and patterns from mood data'
)
class MoodInsightListView(generics.ListAPIView):
    serializer_class = MoodInsightSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['generated_at', 'confidence_score']
    ordering = ['-generated_at']
    
    def get_queryset(self):
        queryset = MoodInsight.objects.filter(user=self.request.user, is_active=True)
        
        # Filter by type
        insight_type = self.request.query_params.get('type')
        if insight_type:
            queryset = queryset.filter(insight_type=insight_type)
        
        # Filter by acknowledged status
        acknowledged = self.request.query_params.get('acknowledged')
        if acknowledged is not None:
            queryset = queryset.filter(user_acknowledged=acknowledged.lower() == 'true')
        
        return queryset


@extend_schema(
    tags=['Mental Wellness'],
    summary='Acknowledge Mood Insight',
    description='Mark a mood insight as acknowledged by the user'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def acknowledge_insight(request, insight_id):
    try:
        insight = MoodInsight.objects.get(id=insight_id, user=request.user)
        insight.user_acknowledged = True
        insight.acknowledged_at = timezone.now()
        insight.save()
        
        return Response({
            'message': 'Insight acknowledged successfully',
            'insight_id': insight_id
        })
    
    except MoodInsight.DoesNotExist:
        return Response({
            'error': 'Insight not found'
        }, status=status.HTTP_404_NOT_FOUND)
