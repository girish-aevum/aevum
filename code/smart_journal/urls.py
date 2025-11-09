from django.urls import path
from .views import (
    health,
    JournalEntryListView,
    JournalEntryCreateView,
    JournalEntryQuickCreateView,
    JournalEntryDetailView,
    JournalCategoryListView,
    JournalCategoryDetailView,
    JournalTemplateListView,
    JournalTagListView,
    JournalStatsView,
    JournalStreakView,
    JournalInsightListView,
    JournalReminderListView,
    toggle_favorite,
    archive_entry,
    search_entries,
    journal_calendar
)

app_name = 'smart_journal'

urlpatterns = [
    # Health check
    path('health/', health, name='health'),
    
    # Journal Entry endpoints
    path('entries/', JournalEntryListView.as_view(), name='entry-list'),
    path('entries/create/', JournalEntryCreateView.as_view(), name='entry-create'),
    path('entries/quick-create/', JournalEntryQuickCreateView.as_view(), name='entry-quick-create'),
    path('entries/<uuid:entry_id>/', JournalEntryDetailView.as_view(), name='entry-detail'),
    
    # Entry utility endpoints
    path('entries/<uuid:entry_id>/favorite/', toggle_favorite, name='entry-toggle-favorite'),
    path('entries/<uuid:entry_id>/archive/', archive_entry, name='entry-archive'),
    
    # Search and calendar
    path('search/', search_entries, name='search-entries'),
    path('calendar/', journal_calendar, name='journal-calendar'),
    
    # Category endpoints
    path('categories/', JournalCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', JournalCategoryDetailView.as_view(), name='category-detail'),
    
    # Template endpoints
    path('templates/', JournalTemplateListView.as_view(), name='template-list'),
    
    # Tag endpoints
    path('tags/', JournalTagListView.as_view(), name='tag-list'),
    
    # Analytics and insights
    path('stats/', JournalStatsView.as_view(), name='journal-stats'),
    path('streak/', JournalStreakView.as_view(), name='journal-streak'),
    path('insights/', JournalInsightListView.as_view(), name='insight-list'),
    
    # Reminders
    path('reminders/', JournalReminderListView.as_view(), name='reminder-list'),
] 