from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ai_companion.models import Thread, Message
from ai_companion.groq_client import GroqClient


class Command(BaseCommand):
    help = 'Test the simplified AI companion chat functionality'
    
    def handle(self, *args, **options):
        self.stdout.write('Testing simplified AI companion...')
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created test user'))
        else:
            self.stdout.write('✓ Using existing test user')
        
        # Create a new thread
        thread = Thread.objects.create(
            user=user,
            title="Test Chat Thread"
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Created thread: {thread.thread_id}'))
        
        # Create a test user message
        user_message = Message.objects.create(
            thread=thread,
            sender='USER',
            content='Hello! Can you tell me about healthy eating?'
        )
        self.stdout.write(f'✓ Created user message: {user_message.content}')
        
        # Test Groq client
        groq_client = GroqClient()
        
        if not groq_client.api_key:
            self.stdout.write(
                self.style.WARNING('⚠ GROQ_API_KEY not configured - AI responses will be fallback messages')
            )
        else:
            self.stdout.write('✓ Groq API key configured')
        
        # Get AI response
        conversation_history = [
            {"role": "user", "content": user_message.content}
        ]
        
        ai_response_content = groq_client.get_chat_response(conversation_history)
        
        # Create AI message
        ai_message = Message.objects.create(
            thread=thread,
            sender='AI',
            content=ai_response_content
        )
        
        self.stdout.write(f'✓ Created AI message: {ai_response_content[:100]}...')
        
        # Verify thread properties
        self.stdout.write(f'✓ Thread message count: {thread.message_count}')
        self.stdout.write(f'✓ Thread title: {thread.title}')
        
        # Display conversation
        self.stdout.write('\n' + '='*50)
        self.stdout.write('CONVERSATION:')
        self.stdout.write('='*50)
        
        for message in thread.messages.all():
            sender_label = "👤 USER" if message.sender == 'USER' else "🤖 AI"
            self.stdout.write(f'\n{sender_label}: {message.content}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Simplified AI companion test completed successfully!'))
        
        # Clean up
        if self.confirm_cleanup():
            thread.delete()
            if created:
                user.delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleaned up test data'))
    
    def confirm_cleanup(self):
        """Ask user if they want to clean up test data"""
        response = input('\nClean up test data? (y/N): ')
        return response.lower() in ['y', 'yes'] 