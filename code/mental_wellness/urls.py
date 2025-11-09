from django.urls import path
from .views import (
    health,
    MoodCategoryListView, EmotionListView, ActivityTypeListView, MoodTriggerListView,
    MoodEntryCreateView, MoodEntryListView, MoodEntryDetailView, MoodEntryUpdateView, 
    MoodEntryDeleteView, QuickMoodEntryView,
    mood_statistics, mood_dashboard,
    MoodInsightListView, acknowledge_insight
)

app_name = 'mental_wellness'

urlpatterns = [
    # Health check
    path('health/', health, name='health'),
    
    # Reference data endpoints (public)
    path('mood-categories/', MoodCategoryListView.as_view(), name='mood-categories'),
    path('emotions/', EmotionListView.as_view(), name='emotions'),
    path('activities/', ActivityTypeListView.as_view(), name='activities'),
    path('triggers/', MoodTriggerListView.as_view(), name='triggers'),
    
    # Mood entry management
    path('mood-entries/', MoodEntryListView.as_view(), name='mood-entries-list'),
    path('mood-entries/create/', MoodEntryCreateView.as_view(), name='mood-entry-create'),
    path('mood-entries/<int:pk>/', MoodEntryDetailView.as_view(), name='mood-entry-detail'),
    path('mood-entries/<int:pk>/update/', MoodEntryUpdateView.as_view(), name='mood-entry-update'),
    path('mood-entries/<int:pk>/delete/', MoodEntryDeleteView.as_view(), name='mood-entry-delete'),
    
    # Quick mood entry
    path('quick-mood/', QuickMoodEntryView.as_view(), name='quick-mood'),
    
    # Analytics and dashboard
    path('statistics/', mood_statistics, name='statistics'),
    path('dashboard/', mood_dashboard, name='dashboard'),
    
    # Insights
    path('insights/', MoodInsightListView.as_view(), name='insights'),
    path('insights/<int:insight_id>/acknowledge/', acknowledge_insight, name='acknowledge-insight'),
]
