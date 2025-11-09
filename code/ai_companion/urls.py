from django.urls import path
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

from .views import (
    health,
    ThreadListView,
    ThreadDetailView,
    chat,
    react_to_message,
    toggle_favorite,
    toggle_archive,
    ThreadSuggestionListView,
    handle_suggestion,
    stats,
    qa_stats,
    submit_user_feedback,
    submit_qa_feedback,
    get_qa_messages,
    get_user_feedback_history,
    summarize_text,
    ai_companion_raw  # Add the new view
)

app_name = 'ai_companion'

urlpatterns = [
    # Health check
    path('health/', health, name='health'),
    
    # Thread management
    path('threads/', ThreadListView.as_view(), name='thread-list'),
    path('threads/<uuid:thread_id>/', ThreadDetailView.as_view(), name='thread-detail'),
    
    # Thread actions
    path('threads/<uuid:thread_id>/favorite/', toggle_favorite, name='toggle-favorite'),
    path('threads/<uuid:thread_id>/archive/', toggle_archive, name='toggle-archive'),
    
    # Chat functionality
    path('chat/', chat, name='chat'),
    path('messages/react/', react_to_message, name='react-to-message'),
    
    # Suggestions
    path('suggestions/', ThreadSuggestionListView.as_view(), name='suggestions'),
    path('suggestions/handle/', handle_suggestion, name='handle-suggestion'),
    
    # Statistics
    path('stats/', stats, name='stats'),
    path('qa-stats/', qa_stats, name='qa-stats'),
    
    # Feedback endpoints
    path('feedback/user/', submit_user_feedback, name='submit-user-feedback'),
    path('feedback/qa/', submit_qa_feedback, name='submit-qa-feedback'),
    path('feedback/user/history/', get_user_feedback_history, name='user-feedback-history'),
    
    # QA management endpoints
    path('qa/messages/', get_qa_messages, name='get-qa-messages'),
    
    # New summarization endpoint
    path('summarize/', summarize_text, name='summarize-text'),
    
    # New raw AI companion endpoint
    path('ai-companion-raw/', ai_companion_raw, name='ai-companion-raw'),
]
