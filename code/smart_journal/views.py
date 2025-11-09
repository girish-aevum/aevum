from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import date, timedelta, datetime
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

from .models import (
    JournalCategory,
    JournalTemplate,
    JournalEntry,
    JournalTag,
    JournalAttachment,
    JournalStreak,
    JournalInsight,
    JournalReminder
)
from .serializers import (
    JournalCategorySerializer,
    JournalTemplateSerializer,
    JournalEntryCreateSerializer,
    JournalEntryListSerializer,
    JournalEntryDetailSerializer,
    JournalEntryUpdateSerializer,
    JournalEntryQuickCreateSerializer,
    JournalTagSerializer,
    JournalAttachmentSerializer,
    JournalStreakSerializer,
    JournalInsightSerializer,
    JournalReminderSerializer,
    JournalStatsSerializer,
    JournalCategoryCreateSerializer,
    JournalTemplateCreateSerializer
)

# Initialize logger
logger = logging.getLogger(__name__)


# Health Check
@extend_schema(tags=['Smart Journal'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health(request):
    """Health check endpoint for smart journal app"""
    return Response({"status": "ok", "app": "smart_journal"})


# Journal Entry Views
class JournalEntryListView(generics.ListAPIView):
    """List user's journal entries with filtering and search"""
    
    serializer_class = JournalEntryListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'mood_rating', 'energy_level', 'privacy_level', 'is_favorite', 'is_archived', 'is_draft']
    search_fields = ['title', 'content', 'location']
    ordering_fields = ['entry_date', 'created_at', 'updated_at', 'word_count']
    ordering = ['-entry_date', '-created_at']
    
    def get_queryset(self):
        """Get user's journal entries with advanced filtering"""
        queryset = JournalEntry.objects.filter(user=self.request.user).select_related(
            'category', 'template'
        ).prefetch_related('tags', 'attachments')
        
        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date and end_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(entry_date__range=[start_date, end_date])
            except ValueError:
                # Log invalid date format
                logger.warning(f"Invalid date format: start_date={start_date}, end_date={end_date}")
        
        return queryset
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="List Journal Entries",
        description="List user's journal entries with advanced filtering, search, and pagination",
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by category ID'
            ),
            OpenApiParameter(
                name='mood_rating',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by mood rating (1-5)'
            ),
            OpenApiParameter(
                name='is_favorite',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter favorite entries'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in title, content, or location'
            ),
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date for filtering entries (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date for filtering entries (YYYY-MM-DD)'
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class JournalEntryCreateView(generics.CreateAPIView):
    """Create a new journal entry"""
    
    serializer_class = JournalEntryCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Ensure the entry date is set correctly
        data = request.data.copy()
        
        # Use the date from the request, or default to today
        entry_date = data.get('entry_date', date.today())
        
        # Ensure the date is in the correct format
        if isinstance(entry_date, str):
            try:
                entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            except ValueError:
                entry_date = date.today()
        
        # Ensure the date is not in the future
        if entry_date > date.today():
            entry_date = date.today()
        
        data['entry_date'] = entry_date
        
        # Set the serializer context to include the user
        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Save the entry
        entry = serializer.save(user=request.user)
        
        # Update user's streak
        streak, _ = JournalStreak.objects.get_or_create(user=request.user)
        streak.update_streak(entry.entry_date)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="Create Journal Entry",
        description="Create a new journal entry with optional tags, category, and template"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class JournalEntryQuickCreateView(generics.CreateAPIView):
    """Quick create for simple journal entries"""
    
    serializer_class = JournalEntryQuickCreateSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="Quick Create Journal Entry",
        description="Quickly create a simple journal entry with minimal fields"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(
        tags=['Smart Journal'],
        summary="Get Journal Entry Details",
        description="Get detailed information about a specific journal entry"
    ),
    put=extend_schema(
        tags=['Smart Journal'],
        summary="Update Journal Entry",
        description="Update a journal entry completely"
    ),
    patch=extend_schema(
        tags=['Smart Journal'],
        summary="Partially Update Journal Entry",
        description="Partially update a journal entry"
    ),
    delete=extend_schema(
        tags=['Smart Journal'],
        summary="Delete Journal Entry",
        description="Delete a journal entry permanently"
    )
)
class JournalEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a journal entry"""
    
    permission_classes = [IsAuthenticated]
    lookup_field = 'entry_id'
    
    def get_queryset(self):
        """Get user's journal entries"""
        return JournalEntry.objects.filter(user=self.request.user).select_related(
            'category', 'template'
        ).prefetch_related('tags', 'attachments')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return JournalEntryDetailSerializer
        return JournalEntryUpdateSerializer


# Category Views
class JournalCategoryListView(generics.ListCreateAPIView):
    """List and create journal categories"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category_type', 'created_at']
    ordering = ['category_type', 'name']
    
    def get_queryset(self):
        """Get user's categories and system categories"""
        return JournalCategory.objects.filter(
            Q(user=self.request.user) | Q(is_system_category=True),
            is_active=True
        )
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JournalCategoryCreateSerializer
        return JournalCategorySerializer
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="List Journal Categories",
        description="List user's journal categories and system categories"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="Create Journal Category",
        description="Create a new journal category"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(
        tags=['Smart Journal'],
        summary="Get Category Details",
        description="Get detailed information about a journal category"
    ),
    put=extend_schema(
        tags=['Smart Journal'],
        summary="Update Category",
        description="Update a journal category"
    ),
    patch=extend_schema(
        tags=['Smart Journal'],
        summary="Partially Update Category",
        description="Partially update a journal category"
    ),
    delete=extend_schema(
        tags=['Smart Journal'],
        summary="Delete Category",
        description="Delete a journal category"
    )
)
class JournalCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a journal category"""
    
    serializer_class = JournalCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get user's categories only (not system categories)"""
        return JournalCategory.objects.filter(user=self.request.user, is_system_category=False)


# Template Views
class JournalTemplateListView(generics.ListCreateAPIView):
    """List and create journal templates"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'template_type', 'usage_count', 'created_at']
    ordering = ['template_type', 'name']
    
    def get_queryset(self):
        """Get user's templates and public templates"""
        return JournalTemplate.objects.filter(
            Q(user=self.request.user) | Q(is_public=True) | Q(is_system_template=True),
            is_active=True
        )
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JournalTemplateCreateSerializer
        return JournalTemplateSerializer
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="List Journal Templates",
        description="List available journal templates (user's own, public, and system templates)"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="Create Journal Template",
        description="Create a new journal template"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# Tag Views
class JournalTagListView(generics.ListCreateAPIView):
    """List and create journal tags"""
    
    serializer_class = JournalTagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'usage_count', 'created_at']
    ordering = ['-usage_count', 'name']
    
    def get_queryset(self):
        """Get user's tags"""
        return JournalTag.objects.filter(user=self.request.user)
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="List Journal Tags",
        description="List user's journal tags ordered by usage"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="Create Journal Tag",
        description="Create a new journal tag"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# Statistics and Analytics Views
class JournalStatsView(APIView):
    """Get comprehensive journal statistics"""
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="Get Journal Statistics",
        description="Get comprehensive statistics about user's journaling activity",
        responses={200: JournalStatsSerializer}
    )
    def get(self, request):
        user = request.user
        now = timezone.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Basic counts
        entries = JournalEntry.objects.filter(user=user, is_archived=False)
        total_entries = entries.count()
        entries_this_week = entries.filter(entry_date__gte=week_ago).count()
        entries_this_month = entries.filter(entry_date__gte=month_ago).count()
        favorite_entries = entries.filter(is_favorite=True).count()
        
        # Streak information
        streak = JournalStreak.objects.filter(user=user).first()
        current_streak = streak.current_streak if streak else 0
        longest_streak = streak.longest_streak if streak else 0
        
        # Word count and averages
        total_words = entries.aggregate(total=Sum('word_count'))['total'] or 0
        avg_mood = entries.filter(mood_rating__isnull=False).aggregate(avg=Avg('mood_rating'))['avg']
        avg_energy = entries.filter(energy_level__isnull=False).aggregate(avg=Avg('energy_level'))['avg']
        
        # Most used category
        most_used_category = entries.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count').first()
        most_used_category = most_used_category['category__name'] if most_used_category else None
        
        # Most used tags
        most_used_tags = JournalTag.objects.filter(
            user=user
        ).order_by('-usage_count')[:5].values_list('name', flat=True)
        
        # Writing frequency (last 30 days)
        writing_frequency = {}
        for i in range(30):
            day = today - timedelta(days=i)
            count = entries.filter(entry_date=day).count()
            writing_frequency[day.strftime('%Y-%m-%d')] = count
        
        # Mood trends (last 30 days)
        mood_entries = entries.filter(
            entry_date__gte=today - timedelta(days=30),
            mood_rating__isnull=False
        ).values('entry_date', 'mood_rating')
        
        mood_trends = {}
        for entry in mood_entries:
            day = entry['entry_date'].strftime('%Y-%m-%d')
            mood_trends[day] = entry['mood_rating']
        
        # Recent insights
        recent_insights = JournalInsight.objects.filter(
            user=user
        ).order_by('-generated_at')[:3].values(
            'title', 'description', 'insight_type', 'confidence_score'
        )
        
        data = {
            'total_entries': total_entries,
            'entries_this_week': entries_this_week,
            'entries_this_month': entries_this_month,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'favorite_entries': favorite_entries,
            'total_words': total_words,
            'average_mood': round(avg_mood, 2) if avg_mood else None,
            'average_energy': round(avg_energy, 2) if avg_energy else None,
            'most_used_category': most_used_category,
            'most_used_tags': list(most_used_tags),
            'writing_frequency': writing_frequency,
            'mood_trends': mood_trends,
            'recent_insights': list(recent_insights)
        }
        
        serializer = JournalStatsSerializer(data)
        return Response(serializer.data)


class JournalStreakView(generics.RetrieveAPIView):
    """Get user's journal streak information"""
    
    serializer_class = JournalStreakSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get or create user's streak"""
        streak, created = JournalStreak.objects.get_or_create(user=self.request.user)
        return streak
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="Get Journal Streak",
        description="Get user's current journaling streak and milestones"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class JournalInsightListView(generics.ListAPIView):
    """List user's journal insights"""
    
    serializer_class = JournalInsightSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['insight_type', 'is_acknowledged', 'is_helpful']
    ordering_fields = ['generated_at', 'confidence_score']
    ordering = ['-generated_at']
    
    def get_queryset(self):
        """Get user's insights"""
        return JournalInsight.objects.filter(user=self.request.user)
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="List Journal Insights",
        description="List AI-generated insights about user's journaling patterns"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class JournalReminderListView(generics.ListCreateAPIView):
    """List and create journal reminders"""
    
    serializer_class = JournalReminderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['reminder_time', 'created_at']
    ordering = ['reminder_time']
    
    def get_queryset(self):
        """Get user's reminders"""
        return JournalReminder.objects.filter(user=self.request.user)
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="List Journal Reminders",
        description="List user's journal reminders"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Smart Journal'],
        summary="Create Journal Reminder",
        description="Create a new journal reminder"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# Utility Views
@extend_schema(
    tags=['Smart Journal'],
    summary="Mark Entry as Favorite",
    description="Toggle favorite status of a journal entry"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, entry_id):
    """Toggle favorite status of a journal entry"""
    try:
        entry = JournalEntry.objects.get(
            entry_id=entry_id,
            user=request.user
        )
        entry.is_favorite = not entry.is_favorite
        entry.save(update_fields=['is_favorite'])
        
        return Response({
            'message': f"Entry {'added to' if entry.is_favorite else 'removed from'} favorites",
            'is_favorite': entry.is_favorite
        })
    except JournalEntry.DoesNotExist:
        return Response(
            {'error': 'Journal entry not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    tags=['Smart Journal'],
    summary="Archive Entry",
    description="Archive a journal entry"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def archive_entry(request, entry_id):
    """Archive a journal entry"""
    try:
        entry = JournalEntry.objects.get(
            entry_id=entry_id,
            user=request.user
        )
        entry.archive()
        
        return Response({
            'message': 'Entry archived successfully',
            'is_archived': entry.is_archived
        })
    except JournalEntry.DoesNotExist:
        return Response(
            {'error': 'Journal entry not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    tags=['Smart Journal'],
    summary="Search Journal Entries",
    description="Advanced search across journal entries with filters"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_entries(request):
    """Advanced search for journal entries"""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    mood_min = request.GET.get('mood_min')
    mood_max = request.GET.get('mood_max')
    
    entries = JournalEntry.objects.filter(user=request.user, is_archived=False)
    
    # Apply filters
    if query:
        entries = entries.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(location__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    if category_id:
        entries = entries.filter(category_id=category_id)
    
    if date_from:
        entries = entries.filter(entry_date__gte=date_from)
    
    if date_to:
        entries = entries.filter(entry_date__lte=date_to)
    
    if mood_min:
        entries = entries.filter(mood_rating__gte=mood_min)
    
    if mood_max:
        entries = entries.filter(mood_rating__lte=mood_max)
    
    # Serialize results
    serializer = JournalEntryListSerializer(
        entries.order_by('-entry_date')[:50],  # Limit to 50 results
        many=True,
        context={'request': request}
    )
    
    return Response({
        'query': query,
        'total_results': entries.count(),
        'results': serializer.data
    })


@extend_schema(
    tags=['Smart Journal'],
    summary="Get Journal Calendar",
    description="Get journal entries organized by calendar dates"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def journal_calendar(request):
    """Get journal entries organized by calendar dates"""
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid year or month parameter'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get entries for the specified month
    entries = JournalEntry.objects.filter(
        user=request.user,
        entry_date__year=year,
        entry_date__month=month,
        is_archived=False
    ).select_related('category').prefetch_related('tags')
    
    # Organize by date
    calendar_data = {}
    for entry in entries:
        date_str = entry.entry_date.strftime('%Y-%m-%d')
        if date_str not in calendar_data:
            calendar_data[date_str] = []
        
        calendar_data[date_str].append({
            'entry_id': str(entry.entry_id),
            'title': entry.title,
            'mood_rating': entry.mood_rating,
            'mood_emoji': entry.mood_emoji,
            'category': entry.category.name if entry.category else None,
            'category_color': entry.category.color_hex if entry.category else None,
            'is_favorite': entry.is_favorite,
            'word_count': entry.word_count
        })
    
    return Response({
        'year': year,
        'month': month,
        'calendar_data': calendar_data,
        'total_entries': entries.count()
    })
