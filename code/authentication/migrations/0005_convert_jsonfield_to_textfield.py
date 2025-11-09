from django.db import migrations
import json

def convert_json_to_text(apps, schema_editor):
    UserProfile = apps.get_model('authentication', 'UserProfile')
    
    # List of fields to convert
    json_fields = [
        'surgeries', 
        'allergies', 
        'vaccinations', 
        'communication_preferences', 
        'language_preferences',
        'chronic_conditions',
        'medications_current',
        'family_history'
    ]
    
    for profile in UserProfile.objects.all():
        for field in json_fields:
            value = getattr(profile, field)
            
            # If the value is a JSON string or list/dict, convert to text
            if value:
                try:
                    # If it's already a string, use it directly
                    if isinstance(value, str):
                        converted_value = value
                    # If it's a list or dict, convert to a comma-separated string or JSON-like string
                    elif isinstance(value, (list, dict)):
                        converted_value = ', '.join(str(item) for item in value) if isinstance(value, list) else json.dumps(value)
                    else:
                        converted_value = str(value)
                    
                    setattr(profile, field, converted_value)
                except Exception as e:
                    print(f"Error converting {field} for profile {profile.id}: {e}")
        
        profile.save()

def revert_text_to_json(apps, schema_editor):
    UserProfile = apps.get_model('authentication', 'UserProfile')
    
    # List of fields to convert back
    json_fields = [
        'surgeries', 
        'allergies', 
        'vaccinations', 
        'communication_preferences', 
        'language_preferences',
        'chronic_conditions',
        'medications_current',
        'family_history'
    ]
    
    for profile in UserProfile.objects.all():
        for field in json_fields:
            value = getattr(profile, field)
            
            # If the value is a string, try to convert back to a list or dict
            if value:
                try:
                    # Try parsing as JSON first
                    converted_value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # If JSON parsing fails, split by comma
                    converted_value = [item.strip() for item in value.split(',') if item.strip()]
                
                setattr(profile, field, converted_value)
        
        profile.save()

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0004_subscriptionplan_usersubscription_and_more'),  # Replace with your last migration
    ]

    operations = [
        migrations.RunPython(convert_json_to_text, revert_text_to_json),
    ] 