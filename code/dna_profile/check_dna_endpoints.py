#!/usr/bin/env python3
"""
Script to verify DNA Profile endpoints are properly registered
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aevum.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

def check_endpoints():
    """Check if all DNA profile endpoints are properly registered"""
    
    endpoints = [
        # Public endpoints
        ('dna_profile:health', 'Health check'),
        ('dna_profile:kit-types-list', 'List DNA kit types'),
        ('dna_profile:kit-type-detail', 'DNA kit type detail', {'pk': 1}),
        
        # User endpoints
        ('dna_profile:orders-list', 'List user orders'),
        ('dna_profile:order-create', 'Create DNA kit order'),
        ('dna_profile:order-detail', 'Order detail', {'pk': 1}),
        ('dna_profile:kit-activate', 'Activate DNA kit'),
        ('dna_profile:results-list', 'List DNA results'),
        ('dna_profile:result-detail', 'DNA result detail', {'pk': 1}),
        ('dna_profile:reports-list', 'List DNA reports'),
        ('dna_profile:report-detail', 'DNA report detail', {'pk': 1}),
        ('dna_profile:consent', 'DNA consent management'),
        ('dna_profile:dashboard', 'DNA dashboard'),
        
        # PDF Upload endpoints
        ('dna_profile:pdf-upload', 'Upload DNA PDF'),
        ('dna_profile:pdf-uploads-list', 'List PDF uploads'),
        ('dna_profile:pdf-upload-detail', 'PDF upload detail', {'pk': 1}),
        
        # Lab endpoints
        ('dna_profile:lab-result-create', 'Create DNA result (Lab)'),
        ('dna_profile:lab-result-update', 'Update DNA result (Lab)', {'pk': 1}),
        ('dna_profile:lab-report-create', 'Create DNA report (Lab)'),
        ('dna_profile:lab-report-update', 'Update DNA report (Lab)', {'pk': 1}),
        ('dna_profile:lab-order-status', 'Update order status (Lab)', {'order_id': '12345678-1234-5678-9012-123456789012'}),
        ('dna_profile:lab-extracted-data-list', 'List extracted data (Lab)'),
        ('dna_profile:lab-process-extracted-data', 'Process extracted data (Lab)'),
    ]
    
    print("🧬 DNA Profile Endpoints Verification")
    print("=" * 50)
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint_data in endpoints:
        if len(endpoint_data) == 2:
            url_name, description = endpoint_data
            kwargs = {}
        else:
            url_name, description, kwargs = endpoint_data
        
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"✅ {description}")
            print(f"   URL: {url}")
            success_count += 1
        except NoReverseMatch as e:
            print(f"❌ {description}")
            print(f"   Error: {e}")
        except Exception as e:
            print(f"⚠️  {description}")
            print(f"   Unexpected error: {e}")
        
        print()
    
    print(f"📊 Summary: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All DNA Profile endpoints are properly configured!")
        return True
    else:
        print(f"⚠️  {total_count - success_count} endpoints need attention")
        return False

def show_api_summary():
    """Show a summary of all available API endpoints"""
    
    print("\n🔗 DNA Profile API Summary")
    print("=" * 30)
    
    api_groups = {
        "Public Endpoints (No Auth Required)": [
            "GET /api/dna-profile/health/",
            "GET /api/dna-profile/kit-types/",
            "GET /api/dna-profile/kit-types/{id}/",
        ],
        "User Endpoints (Auth Required)": [
            "GET /api/dna-profile/orders/",
            "POST /api/dna-profile/orders/create/",
            "GET /api/dna-profile/orders/{id}/",
            "POST /api/dna-profile/kits/activate/",
            "GET /api/dna-profile/results/",
            "GET /api/dna-profile/results/{id}/",
            "GET /api/dna-profile/reports/",
            "GET /api/dna-profile/reports/{id}/",
            "GET /api/dna-profile/consent/",
            "POST /api/dna-profile/consent/",
            "GET /api/dna-profile/dashboard/",
            "POST /api/dna-profile/pdf/upload/",
            "GET /api/dna-profile/pdf/uploads/",
            "GET /api/dna-profile/pdf/uploads/{id}/",
        ],
        "Lab Endpoints (Restricted Access)": [
            "POST /api/dna-profile/lab/results/create/",
            "PUT /api/dna-profile/lab/results/{id}/update/",
            "POST /api/dna-profile/lab/reports/create/",
            "PUT /api/dna-profile/lab/reports/{id}/update/",
            "PATCH /api/dna-profile/lab/orders/{order_id}/status/",
            "GET /api/dna-profile/lab/extracted-data/",
            "POST /api/dna-profile/lab/process-extracted-data/",
        ]
    }
    
    for group_name, endpoints in api_groups.items():
        print(f"\n{group_name}:")
        for endpoint in endpoints:
            print(f"  {endpoint}")

if __name__ == "__main__":
    success = check_endpoints()
    show_api_summary()
    
    if success:
        print("\n✅ All endpoints are ready for use!")
        print("\nNext steps:")
        print("1. Start the Django server: python manage.py runserver")
        print("2. Visit http://localhost:8000/api/schema/swagger-ui/ to see the API docs")
        print("3. Use the lab endpoints to create DNA results and reports")
    else:
        print("\n❌ Some endpoints need fixing before use")
        sys.exit(1) 