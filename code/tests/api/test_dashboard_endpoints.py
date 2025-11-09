#!/usr/bin/env python3
"""
Test script for Dashboard API endpoints
Tests both public and admin endpoints to ensure they work after tag consolidation
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/dashboard"

def test_public_endpoints():
    """Test public endpoints (no authentication required)"""
    print("🧪 Testing Public Dashboard Endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health/")
        print(f"✅ Health Check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
    
    # Test early access request submission
    try:
        early_access_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "phone_number": "+1234567890",
            "primary_interest": "COMPREHENSIVE"
        }
        response = requests.post(f"{BASE_URL}/early-access/", json=early_access_data)
        print(f"✅ Early Access Request: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"   Request ID: {result.get('request_id')}")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Early Access Request Failed: {e}")
    
    # Test contact message submission
    try:
        contact_data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "subject": "Test Message",
            "message": "This is a test message to verify the contact form endpoint is working correctly."
        }
        response = requests.post(f"{BASE_URL}/contact/", json=contact_data)
        print(f"✅ Contact Message: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"   Message ID: {result.get('message_id')}")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Contact Message Failed: {e}")

def test_admin_endpoints():
    """Test admin endpoints (authentication required)"""
    print("\n🔐 Testing Admin Dashboard Endpoints...")
    print("Note: These endpoints require JWT authentication and will return 401 without proper tokens.")
    
    admin_endpoints = [
        "/admin/early-access/",
        "/admin/contact-messages/",
        "/admin/stats/",
        "/admin/staff-users/"
    ]
    
    for endpoint in admin_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"✅ {endpoint}: Properly protected (401 Unauthorized)")
            else:
                print(f"⚠️  {endpoint}: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ {endpoint} Failed: {e}")

def test_swagger_schema():
    """Test that the Swagger schema is accessible"""
    print("\n📚 Testing API Documentation...")
    
    try:
        # Test schema endpoint
        response = requests.get("http://localhost:8000/api/schema/")
        if response.status_code == 200:
            print("✅ OpenAPI Schema: Accessible")
            
            # Check if Dashboard tag is present
            schema = response.json()
            tags = [tag.get('name') for tag in schema.get('tags', [])]
            if 'Dashboard' in tags:
                print("✅ Dashboard Tag: Found in schema")
                dashboard_tag = next((tag for tag in schema.get('tags', []) if tag.get('name') == 'Dashboard'), None)
                if dashboard_tag:
                    print(f"   Description: {dashboard_tag.get('description')}")
            else:
                print("❌ Dashboard Tag: Not found in schema")
        else:
            print(f"❌ OpenAPI Schema: {response.status_code}")
    except Exception as e:
        print(f"❌ Schema Test Failed: {e}")
    
    try:
        # Test Swagger UI
        response = requests.get("http://localhost:8000/api/docs/")
        if response.status_code == 200:
            print("✅ Swagger UI: Accessible")
        else:
            print(f"❌ Swagger UI: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger UI Test Failed: {e}")

if __name__ == "__main__":
    print("🚀 Dashboard API Endpoint Tests")
    print("=" * 50)
    
    test_public_endpoints()
    test_admin_endpoints()
    test_swagger_schema()
    
    print("\n" + "=" * 50)
    print("✅ Test Summary:")
    print("- Public endpoints should work without authentication")
    print("- Admin endpoints should return 401 without JWT tokens")
    print("- Swagger documentation should show single 'Dashboard' group")
    print("\n📖 Access Swagger UI at: http://localhost:8000/api/docs/") 