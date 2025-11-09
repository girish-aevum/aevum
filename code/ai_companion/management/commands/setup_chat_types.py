from django.core.management.base import BaseCommand
from ai_companion.models import AIPersonality


class Command(BaseCommand):
    help = 'Setup 3 simple chat types for AI Companion'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up 3 chat types...'))

        # Clear existing personalities
        AIPersonality.objects.all().delete()
        self.stdout.write('🗑️  Cleared existing AI personalities')

        # Create 3 simple chat types
        chat_types = [
            {
                'name': 'Mental Health Support',
                'personality_type': 'MENTAL_HEALTH',
                'description': 'Specialized support for mental wellness, stress management, and emotional health',
                'system_prompt': '''You are a compassionate mental health support AI. You provide empathetic, non-judgmental guidance for mental wellness, stress management, anxiety, depression, and emotional challenges. Always encourage professional help for serious concerns while offering supportive, evidence-based mental health strategies.''',
                'greeting_message': 'Hello! I\'m here to support your mental wellness journey. Whether you\'re dealing with stress, anxiety, or just need someone to talk to, I\'m here to listen and help. How are you feeling today? 🧠',
                'avatar_emoji': '🧠',
                'color_theme': '#ec4899',
                'max_response_length': 600,
                'temperature': 0.6,
                'is_active': True,
                'is_default': False
            },
            {
                'name': 'Nutrition & Diet',
                'personality_type': 'NUTRITION',
                'description': 'Expert guidance on nutrition, diet planning, and healthy eating habits',
                'system_prompt': '''You are a knowledgeable nutrition and diet specialist AI. You provide evidence-based advice on healthy eating, meal planning, nutritional requirements, weight management, and dietary restrictions. Focus on practical, sustainable nutrition advice while encouraging balanced, whole-food approaches.''',
                'greeting_message': 'Hi there! I\'m your nutrition and diet specialist. Whether you want to improve your eating habits, plan meals, or understand nutritional needs, I\'m here to help you make healthier food choices. What would you like to know about nutrition? 🥗',
                'avatar_emoji': '🥗',
                'color_theme': '#059669',
                'max_response_length': 500,
                'temperature': 0.5,
                'is_active': True,
                'is_default': False
            },
            {
                'name': 'General Healthcare',
                'personality_type': 'GENERAL',
                'description': 'Comprehensive health support for general wellness, symptoms, and health questions',
                'system_prompt': '''You are a knowledgeable general healthcare AI assistant. You provide helpful information about common health topics, symptoms, wellness practices, and general medical guidance. Always emphasize the importance of consulting healthcare professionals for serious concerns while offering educational health information.''',
                'greeting_message': 'Hello! I\'m your general healthcare assistant. I can help with health questions, wellness advice, and general medical information. Remember, I\'m here to educate and support, but always consult healthcare professionals for serious concerns. How can I help you today? 🏥',
                'avatar_emoji': '��',
                'color_theme': '#6366f1',
                'max_response_length': 550,
                'temperature': 0.7,
                'is_active': True,
                'is_default': True
            }
        ]

        created_count = 0
        for chat_type in chat_types:
            personality, created = AIPersonality.objects.get_or_create(
                name=chat_type['name'],
                defaults=chat_type
            )
            if created:
                created_count += 1
                self.stdout.write(f'✅ Created: {personality.name}')
            else:
                self.stdout.write(f'ℹ️  Already exists: {personality.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Chat Types Setup Complete!\n'
                f'Created: {created_count}\n'
                f'Total: {AIPersonality.objects.count()}\n'
                f'Active: {AIPersonality.objects.filter(is_active=True).count()}\n\n'
                f'Available Chat Types:\n'
                f'  🧠 Mental Health Support\n'
                f'  🥗 Nutrition & Diet\n'
                f'  🏥 General Healthcare (Default)'
            )
        )
