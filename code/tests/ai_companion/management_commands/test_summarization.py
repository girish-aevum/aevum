"""
Management command to test AI response summarization
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ai_companion.models import Thread, Message
from ai_companion.groq_client import GroqClient
from ai_companion.views import get_ai_response
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Test AI response summarization functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--message',
            type=str,
            default='How can I reduce stress and improve my mental health?',
            help='Test message to send to AI'
        )
        parser.add_argument(
            '--max-words',
            type=int,
            default=50,
            help='Maximum words for summary'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Testing AI Response Summarization'))
        
        # Initialize Groq client
        groq_client = GroqClient()
        
        if not groq_client.api_key:
            self.stdout.write(self.style.ERROR('❌ GROQ_API_KEY not configured'))
            return
        
        test_message = options['message']
        max_words = options['max_words']
        
        self.stdout.write(f"📝 Test message: {test_message}")
        self.stdout.write(f"📏 Max summary words: {max_words}")
        
        try:
            # Test 1: Get original response
            self.stdout.write(self.style.WARNING('\n1️⃣ Getting original AI response...'))
            conversation_history = [{"role": "user", "content": test_message}]
            original_response = groq_client.get_chat_response(conversation_history)
            original_word_count = len(original_response.split())
            
            self.stdout.write(f"📊 Original response ({original_word_count} words):")
            self.stdout.write(f"   {original_response[:200]}...")
            
            # Test 2: Test summarization
            self.stdout.write(self.style.WARNING('\n2️⃣ Testing summarization...'))
            summarized_response = groq_client.summarize_response(original_response, max_length=max_words)
            summarized_word_count = len(summarized_response.split())
            
            self.stdout.write(f"📊 Summarized response ({summarized_word_count} words):")
            self.stdout.write(f"   {summarized_response}")
            
            # Test 3: Test with actual user and thread
            self.stdout.write(self.style.WARNING('\n3️⃣ Testing with user and thread...'))
            
            # Get or create a test user
            test_user, created = User.objects.get_or_create(
                username='test_summarization_user',
                defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
            )
            
            # Create a test thread
            test_thread = Thread.objects.create(
                user=test_user,
                title='Summarization Test Thread',
                category='MENTAL_HEALTH'
            )
            
            # Test the full get_ai_response function
            final_response, metadata = get_ai_response(test_thread, test_message)
            
            self.stdout.write(f"📊 Final response ({len(final_response.split())} words):")
            self.stdout.write(f"   {final_response[:200]}...")
            
            # Display metadata
            self.stdout.write(self.style.SUCCESS('\n📈 Metadata:'))
            for key, value in metadata.items():
                self.stdout.write(f"   {key}: {value}")
            
            # Cleanup
            test_thread.delete()
            if created:
                test_user.delete()
            
            # Summary
            self.stdout.write(self.style.SUCCESS('\n✅ Summarization Test Results:'))
            self.stdout.write(f"   Original: {original_word_count} words")
            self.stdout.write(f"   Summarized: {summarized_word_count} words")
            self.stdout.write(f"   Final: {len(final_response.split())} words")
            self.stdout.write(f"   Reduction: {((original_word_count - len(final_response.split())) / original_word_count * 100):.1f}%")
            self.stdout.write(f"   Was summarized: {metadata.get('was_summarized', False)}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error during testing: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc()) 