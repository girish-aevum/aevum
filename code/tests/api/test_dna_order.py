#!/usr/bin/env python3
"""
Test script for DNA Kit ordering API

This script demonstrates the correct format for creating DNA kit orders
and provides examples of valid shipping addresses.
"""

import json
import requests
from decimal import Decimal

# API Base URL (adjust if needed)
BASE_URL = "http://localhost:8000/api"

def test_order_format():
    """Show the correct format for DNA kit orders"""
    
    print("🧬 DNA Kit Order - Correct Format Examples")
    print("=" * 50)
    
    # Example 1: Complete US Address
    us_order = {
        "kit_type": 1,  # ID of the DNA kit type
        "quantity": 1,
        "shipping_method": "STANDARD",  # STANDARD, EXPRESS, or OVERNIGHT
        "shipping_address": {
            "street": "123 Main Street, Apt 4B",
            "city": "San Francisco", 
            "state": "CA",
            "zip_code": "94105",
            "country": "USA"
        },
        "special_instructions": "Please leave at front door if no answer"
    }
    
    print("✅ Example 1 - US Address:")
    print(json.dumps(us_order, indent=2))
    print()
    
    # Example 2: International Address
    international_order = {
        "kit_type": 2,
        "quantity": 1,
        "shipping_method": "EXPRESS",
        "shipping_address": {
            "street": "456 Queen Street West, Unit 12",
            "city": "Toronto",
            "state": "Ontario", 
            "zip_code": "M5V 2A9",
            "country": "Canada"
        }
    }
    
    print("✅ Example 2 - International Address:")
    print(json.dumps(international_order, indent=2))
    print()
    
    # Example 3: Minimal Required Fields
    minimal_order = {
        "kit_type": 3,
        "shipping_address": {
            "street": "789 Oak Avenue",
            "city": "Austin",
            "state": "TX",
            "zip_code": "73301",
            "country": "USA"
        }
        # quantity defaults to 1
        # shipping_method defaults to STANDARD
        # special_instructions is optional
    }
    
    print("✅ Example 3 - Minimal Required Fields:")
    print(json.dumps(minimal_order, indent=2))
    print()

def show_common_errors():
    """Show common validation errors and how to fix them"""
    
    print("❌ Common Validation Errors")
    print("=" * 30)
    
    errors = [
        {
            "error": "Shipping address is missing: Street address",
            "cause": "Missing 'street' field in shipping_address",
            "fix": "Add 'street': 'Your street address'"
        },
        {
            "error": "Shipping address is missing: City, ZIP/Postal code",
            "cause": "Missing multiple required fields",
            "fix": "Include all required fields: street, city, state, zip_code, country"
        },
        {
            "error": "Shipping address must be a valid object",
            "cause": "shipping_address is not a JSON object",
            "fix": "Ensure shipping_address is a proper object/dictionary"
        }
    ]
    
    for i, error in enumerate(errors, 1):
        print(f"{i}. Error: {error['error']}")
        print(f"   Cause: {error['cause']}")
        print(f"   Fix: {error['fix']}")
        print()

def get_available_kits():
    """Fetch and display available DNA kit types"""
    
    print("🧬 Available DNA Kit Types")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/dna-profile/kit-types/")
        if response.status_code == 200:
            kits = response.json().get('results', [])
            for kit in kits:
                print(f"ID: {kit['id']}")
                print(f"Name: {kit['name']}")
                print(f"Category: {kit['category']}")
                print(f"Price: ₹{kit['price']}")
                print(f"Processing Time: {kit['processing_time_days']} days")
                print("-" * 40)
        else:
            print(f"❌ Failed to fetch kits: {response.status_code}")
            print("Make sure the Django server is running on localhost:8000")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Make sure Django server is running:")
        print("   python manage.py runserver 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def validate_address_example():
    """Show how to validate an address before sending"""
    
    print("🔍 Address Validation Example")
    print("=" * 30)
    
    # Test address
    test_address = {
        "street": "123 Test Street",
        "city": "Test City", 
        "state": "TS",
        "zip_code": "12345",
        "country": "USA"
    }
    
    required_fields = ['street', 'city', 'state', 'zip_code', 'country']
    missing_fields = []
    
    for field in required_fields:
        if field not in test_address or not test_address[field]:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Address validation failed - Missing: {', '.join(missing_fields)}")
    else:
        print("✅ Address validation passed!")
        print(json.dumps(test_address, indent=2))

if __name__ == "__main__":
    print("🧬 Aevum Health - DNA Kit Order Testing")
    print("=" * 50)
    print()
    
    # Show correct formats
    test_order_format()
    
    # Show common errors
    show_common_errors()
    
    # Validate example address
    validate_address_example()
    
    print()
    
    # Try to fetch available kits
    get_available_kits()
    
    print("\n📝 Quick Reference:")
    print("Required shipping_address fields:")
    print("  - street: Street address")
    print("  - city: City name")
    print("  - state: State/Province")  
    print("  - zip_code: ZIP or postal code")
    print("  - country: Country name")
    print()
    print("Optional fields:")
    print("  - quantity: Number of kits (defaults to 1)")
    print("  - shipping_method: STANDARD/EXPRESS/OVERNIGHT (defaults to STANDARD)")
    print("  - special_instructions: Delivery instructions") 