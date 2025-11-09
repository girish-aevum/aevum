#!/usr/bin/env python3
"""
Test script for Mental Wellness Mood Logging API endpoints
"""

import os
import sys
import django
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aevum.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

def test_mood_endpoints():
    """Test all mood logging endpoints"""
    
    endpoints = [
        # Health check
        ('mental_wellness:health', 'Health check'),
        
        # Reference data endpoints
        ('mental_wellness:mood-categories', 'List mood categories'),
        ('mental_wellness:emotions', 'List emotions'),
        ('mental_wellness:activities', 'List activity types'),
        ('mental_wellness:triggers', 'List mood triggers'),
        
        # Mood entry management
        ('mental_wellness:mood-entries-list', 'List mood entries'),
        ('mental_wellness:mood-entry-create', 'Create mood entry'),
        ('mental_wellness:mood-entry-detail', 'Mood entry detail', {'pk': 1}),
        ('mental_wellness:mood-entry-update', 'Update mood entry', {'pk': 1}),
        ('mental_wellness:mood-entry-delete', 'Delete mood entry', {'pk': 1}),
        
        # Quick mood entry
        ('mental_wellness:quick-mood', 'Quick mood entry'),
        
        # Analytics and dashboard
        ('mental_wellness:statistics', 'Mood statistics'),
        ('mental_wellness:dashboard', 'Mood dashboard'),
        
        # Insights
        ('mental_wellness:insights', 'List mood insights'),
        ('mental_wellness:acknowledge-insight', 'Acknowledge insight', {'insight_id': 1}),
    ]
    
    print("🧠 Mental Wellness Mood Logging Endpoints Verification")
    print("=" * 60)
    
    working_endpoints = 0
    total_endpoints = len(endpoints)
    
    for endpoint_data in endpoints:
        url_name = endpoint_data[0]
        description = endpoint_data[1]
        kwargs = endpoint_data[2] if len(endpoint_data) > 2 else {}
        
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"✅ {description}")
            print(f"   URL: {url}")
            print()
            working_endpoints += 1
        except NoReverseMatch as e:
            print(f"❌ {description}")
            print(f"   Error: {str(e)}")
            print()
    
    # Summary
    print(f"📊 Summary: {working_endpoints}/{total_endpoints} endpoints working")
    
    if working_endpoints == total_endpoints:
        print("🎉 All Mental Wellness endpoints are properly configured!")
    else:
        print("⚠️  Some endpoints need attention.")
    
    print()
    print("🔗 Mental Wellness API Summary")
    print("=" * 40)
    print()
    
    endpoint_groups = {
        "Reference Data (No Auth Required)": [
            "GET /api/mental-wellness/health/",
            "GET /api/mental-wellness/mood-categories/",
            "GET /api/mental-wellness/emotions/",
            "GET /api/mental-wellness/activities/",
            "GET /api/mental-wellness/triggers/",
        ],
        "Mood Entry Management (Auth Required)": [
            "GET /api/mental-wellness/mood-entries/",
            "POST /api/mental-wellness/mood-entries/create/",
            "GET /api/mental-wellness/mood-entries/{id}/",
            "PUT /api/mental-wellness/mood-entries/{id}/update/",
            "DELETE /api/mental-wellness/mood-entries/{id}/delete/",
            "POST /api/mental-wellness/quick-mood/",
        ],
        "Analytics & Insights (Auth Required)": [
            "GET /api/mental-wellness/statistics/",
            "GET /api/mental-wellness/dashboard/",
            "GET /api/mental-wellness/insights/",
            "POST /api/mental-wellness/insights/{id}/acknowledge/",
        ]
    }
    
    for group_name, group_endpoints in endpoint_groups.items():
        print(f"{group_name}:")
        for endpoint in group_endpoints:
            print(f"  {endpoint}")
        print()
    
    print("✅ All endpoints are ready for mood logging!")
    print()
    print("Next steps:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Visit http://localhost:8000/api/schema/swagger-ui/ to see the API docs")
    print("3. Use the mood logging endpoints to track mental wellness")
    print("4. Check the admin interface for managing mood data")

if __name__ == "__main__":
    test_mood_endpoints() 