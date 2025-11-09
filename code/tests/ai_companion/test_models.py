"""
Comprehensive Test Cases for AI Companion App
Tests chat functionality, QA testing system, user feedback, and AI integration
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import timedelta
import json
import uuid

from ai_companion.models import Thread, Message, ThreadSuggestion
from ai_companion.groq_client import GroqClient


class AICompanionModelTests(TestCase):
    """Test cases for AI Companion models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.qa_reviewer = User.objects.create_user(
            username='qa_reviewer',
            email='qa@example.com',
            password='qapass123',
            is_staff=True
        )
        
    def test_thread_creation(self):
        """Test Thread model creation and properties"""
        thread = Thread.objects.create(
            user=self.user,
            title="Test Thread",
            category='MENTAL_HEALTH'
        )
        
        self.assertEqual(thread.user, self.user)
        self.assertEqual(thread.title, "Test Thread")
        self.assertEqual(thread.category, 'MENTAL_HEALTH')
        self.assertFalse(thread.is_favorite)
        self.assertFalse(thread.is_archived)
        self.assertEqual(thread.message_count, 0)
        self.assertEqual(thread.total_messages, 0)
        
    def test_thread_str_representation(self):
        """Test Thread string representation"""
        thread = Thread.objects.create(user=self.user, title="Test Thread")
        self.assertEqual(str(thread), "Test Thread")
        
        thread_no_title = Thread.objects.create(user=self.user)
        expected = f"Thread {str(thread_no_title.thread_id)[:8]}..."
        self.assertEqual(str(thread_no_title), expected)
    
    def test_message_creation(self):
        """Test Message model creation"""
        thread = Thread.objects.create(user=self.user, title="Test Thread")
        
        # User message
        user_message = Message.objects.create(
            thread=thread,
            sender='USER',
            content="Hello, how are you?"
        )
        
        self.assertEqual(user_message.thread, thread)
        self.assertEqual(user_message.sender, 'USER')
        self.assertEqual(user_message.content, "Hello, how are you?")
        self.assertIsNone(user_message.is_helpful)
        
        # AI message
        ai_message = Message.objects.create(
            thread=thread,
            sender='AI',
            content="I'm doing well, thank you for asking!",
            confidence_score=0.85,
            processing_time_ms=1200,
            token_count=15
        )
        
        self.assertEqual(ai_message.sender, 'AI')
        self.assertEqual(ai_message.confidence_score, 0.85)
        self.assertEqual(ai_message.processing_time_ms, 1200)
        self.assertEqual(ai_message.token_count, 15)
    
    def test_message_qa_functionality(self):
        """Test Message QA testing functionality"""
        thread = Thread.objects.create(user=self.user, title="QA Test Thread")
        message = Message.objects.create(
            thread=thread,
            sender='AI',
            content="This is a test AI response for QA evaluation."
        )
        
        # Test selecting for QA
        self.assertFalse(message.is_selected_for_qa)
        message.select_for_qa()
        self.assertTrue(message.is_selected_for_qa)
        self.assertEqual(message.qa_status, 'PENDING')
        
        # Test completing QA review
        message.complete_qa_review(
            score=8.5,
            status='APPROVED',
            feedback='Great response with good empathy',
            reviewer=self.qa_reviewer,
            tags='empathy,helpful,accurate'
        )
        
        self.assertEqual(message.qa_score, 8.5)
        self.assertEqual(message.qa_status, 'APPROVED')
        self.assertEqual(message.qa_feedback, 'Great response with good empathy')
        self.assertEqual(message.qa_reviewer, self.qa_reviewer)
        self.assertEqual(message.qa_tags, 'empathy,helpful,accurate')
        self.assertIsNotNone(message.qa_reviewed_at)
    
    def test_message_qa_score_grade(self):
        """Test QA score grade calculation"""
        thread = Thread.objects.create(user=self.user)
        message = Message.objects.create(thread=thread, sender='AI', content="Test")
        
        # Test different score grades
        test_cases = [
            (9.5, 'A+'),
            (8.5, 'A'),
            (7.5, 'B'),
            (6.5, 'C'),
            (5.5, 'D'),
            (3.0, 'F')
        ]
        
        for score, expected_grade in test_cases:
            message.qa_score = score
            self.assertEqual(message.qa_score_grade, expected_grade)
    
    def test_message_feedback_functionality(self):
        """Test user feedback functionality"""
        thread = Thread.objects.create(user=self.user, title="Feedback Test")
        message = Message.objects.create(
            thread=thread,
            sender='AI',
            content="How can I help you today?"
        )
        
        # Test marking as helpful
        message.mark_as_helpful("Very helpful response!")
        self.assertTrue(message.is_helpful)
        self.assertEqual(message.user_feedback, "Very helpful response!")
        
        # Test marking as unhelpful
        message.mark_as_unhelpful("Not quite what I needed")
        self.assertFalse(message.is_helpful)
        self.assertEqual(message.user_feedback, "Not quite what I needed")
    
    def test_thread_analytics_methods(self):
        """Test Thread analytics methods"""
        thread = Thread.objects.create(user=self.user, title="Analytics Test")
        
        # Create some messages
        Message.objects.create(thread=thread, sender='USER', content="User message 1")
        Message.objects.create(thread=thread, sender='AI', content="AI response 1",
                             processing_time_ms=1000, token_count=20)
        Message.objects.create(thread=thread, sender='USER', content="User message 2")
        Message.objects.create(thread=thread, sender='AI', content="AI response 2",
                             processing_time_ms=1500, token_count=25)
        
        # Test counts
        self.assertEqual(thread.message_count, 2)  # Only user messages
        self.assertEqual(thread.total_messages, 4)  # All messages
        
        # Test analytics update
        thread.update_analytics(tokens_used=45, response_time_ms=1250)
        self.assertEqual(thread.total_ai_tokens_used, 45)
    
    def test_thread_suggestion_model(self):
        """Test ThreadSuggestion model"""
        thread = Thread.objects.create(user=self.user, title="Original Thread")
        
        suggestion = ThreadSuggestion.objects.create(
            user=self.user,
            suggestion_type='FOLLOW_UP',
            title='Follow up on mental health',
            description='Continue the mental health discussion',
            suggested_category='MENTAL_HEALTH',
            relevance_score=0.8,
            based_on_thread=thread
        )
        
        self.assertEqual(suggestion.user, self.user)
        self.assertEqual(suggestion.suggestion_type, 'FOLLOW_UP')
        self.assertEqual(suggestion.relevance_score, 0.8)
        self.assertEqual(suggestion.based_on_thread, thread)
        self.assertFalse(suggestion.is_dismissed)
        self.assertFalse(suggestion.is_used)
    
    def test_get_random_messages_for_qa(self):
        """Test getting random messages for QA"""
        thread = Thread.objects.create(user=self.user)
        
        # Create multiple AI messages
        for i in range(10):
            Message.objects.create(
                thread=thread,
                sender='AI',
                content=f"AI response {i}"
            )
        
        # Get random messages
        random_messages = Message.get_random_messages_for_qa(count=5)
        self.assertEqual(random_messages.count(), 5)
        
        # Select some for QA
        for msg in random_messages[:3]:
            msg.select_for_qa()
        
        # Try again - should only get unselected ones
        remaining_messages = Message.get_random_messages_for_qa(count=5)
        self.assertEqual(remaining_messages.count(), 5)


class AICompanionAPITests(APITestCase):
    """Test cases for AI Companion API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.qa_reviewer = User.objects.create_user(
            username='qa_reviewer',
            email='qa@example.com',
            password='qapass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_thread_list_endpoint(self):
        """Test thread list endpoint"""
        # Create some threads
        Thread.objects.create(user=self.user, title="Thread 1", category='MENTAL_HEALTH')
        Thread.objects.create(user=self.user, title="Thread 2", category='NUTRITION')
        Thread.objects.create(user=self.user, title="Thread 3", is_favorite=True)
        
        url = reverse('ai_companion:thread-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_thread_filtering(self):
        """Test thread filtering"""
        # Clear any existing threads
        Thread.objects.filter(user=self.user).delete()
        
        # Create threads with specific conditions
        Thread.objects.create(user=self.user, title="Mental Health Thread", 
                            category='MENTAL_HEALTH')
        Thread.objects.create(user=self.user, title="Nutrition Thread", 
                            category='NUTRITION')
        favorite_thread = Thread.objects.create(user=self.user, title="Favorite Thread", 
                            is_favorite=True, category='MENTAL_HEALTH')
        
        url = reverse('ai_companion:thread-list')
        
        # Filter by category
        response = self.client.get(url, {'category': 'MENTAL_HEALTH'})
        self.assertEqual(len(response.data['results']), 2)  # Mental Health Thread and Favorite Thread
        
        # Filter by favorite
        response = self.client.get(url, {'is_favorite': 'true'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['thread_id'], str(favorite_thread.thread_id))
    
    def test_thread_detail_endpoint(self):
        """Test thread detail endpoint"""
        thread = Thread.objects.create(user=self.user, title="Detail Test Thread")
        Message.objects.create(thread=thread, sender='USER', content="Hello")
        Message.objects.create(thread=thread, sender='AI', content="Hi there!")
        
        url = reverse('ai_companion:thread-detail', kwargs={'thread_id': thread.thread_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Detail Test Thread")
        self.assertEqual(len(response.data['messages']), 2)
    
    @patch('ai_companion.groq_client.GroqClient.get_chat_response')
    def test_chat_endpoint(self, mock_generate):
        """Test chat endpoint with mocked AI response"""
        # Create a thread first
        thread = Thread.objects.create(user=self.user, title="Test Thread")
        
        mock_generate.return_value = 'This is a mocked AI response'
        
        url = reverse('ai_companion:chat')
        data = {
            'thread_id': str(thread.thread_id),
            'message': 'Hello, how are you?'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('thread_id', response.data)
        self.assertIn('user_message', response.data)
        self.assertIn('ai_response', response.data)
        self.assertEqual(response.data['ai_response']['content'], 'This is a mocked AI response')
        
        # Verify thread and messages were created
        thread.refresh_from_db()
        self.assertEqual(thread.messages.count(), 2)  # User + AI message
    
    def test_message_reaction_endpoint(self):
        """Test message reaction endpoint"""
        thread = Thread.objects.create(user=self.user, title="Reaction Test")
        ai_message = Message.objects.create(
            thread=thread,
            sender='AI',
            content="How can I help you today?"
        )
        
        url = reverse('ai_companion:react-to-message')
        data = {
            'message_id': str(ai_message.message_id),
            'is_helpful': True,
            'feedback_comment': 'Very helpful response!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify message was updated
        ai_message.refresh_from_db()
        self.assertTrue(ai_message.is_helpful)
        self.assertEqual(ai_message.user_feedback, 'Very helpful response!')
    
    def test_toggle_favorite_endpoint(self):
        """Test toggle favorite endpoint"""
        thread = Thread.objects.create(user=self.user, title="Favorite Test")
        
        url = reverse('ai_companion:toggle-favorite', kwargs={'thread_id': thread.thread_id})
        
        # Toggle to favorite
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        thread.refresh_from_db()
        self.assertTrue(thread.is_favorite)
        
        # Toggle back
        response = self.client.post(url)
        thread.refresh_from_db()
        self.assertFalse(thread.is_favorite)
    
    def test_user_feedback_endpoint(self):
        """Test user feedback submission endpoint"""
        thread = Thread.objects.create(user=self.user, title="Feedback Test")
        ai_message = Message.objects.create(
            thread=thread,
            sender='AI',
            content="Test AI response"
        )
        
        url = reverse('ai_companion:submit-user-feedback')
        data = {
            'message_id': str(ai_message.message_id),
            'is_helpful': True,
            'feedback_comment': 'Great response!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['data']['is_helpful'], True)
        
        # Verify message was updated
        ai_message.refresh_from_db()
        self.assertTrue(ai_message.is_helpful)
        self.assertEqual(ai_message.user_feedback, 'Great response!')
    
    def test_user_feedback_history_endpoint(self):
        """Test user feedback history endpoint"""
        thread = Thread.objects.create(user=self.user, title="History Test")
        
        # Create messages with feedback
        for i in range(5):
            msg = Message.objects.create(
                thread=thread,
                sender='AI',
                content=f"AI response {i}"
            )
            msg.mark_as_helpful(f"Feedback {i}")
        
        url = reverse('ai_companion:user-feedback-history')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('feedback_history', response.data)
        self.assertEqual(response.data['summary']['total_feedback'], 5)
        self.assertEqual(len(response.data['feedback_history']), 5)


class AICompanionQATests(APITestCase):
    """Test cases for QA functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.qa_reviewer = User.objects.create_user(
            username='qa_reviewer',
            email='qa@example.com',
            password='qapass123',
            is_staff=True
        )
    
    def test_qa_feedback_endpoint_staff_only(self):
        """Test QA feedback endpoint requires staff permission"""
        # Regular user should be denied
        self.client.force_authenticate(user=self.user)
        url = reverse('ai_companion:submit-qa-feedback')
        
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Staff user should be allowed
        self.client.force_authenticate(user=self.qa_reviewer)
        # Test with invalid data first
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_qa_feedback_submission(self):
        """Test QA feedback submission"""
        self.client.force_authenticate(user=self.qa_reviewer)
        
        thread = Thread.objects.create(user=self.user, title="QA Test")
        ai_message = Message.objects.create(
            thread=thread,
            sender='AI',
            content="Test AI response for QA"
        )
        ai_message.select_for_qa()
        
        url = reverse('ai_companion:submit-qa-feedback')
        data = {
            'message_id': str(ai_message.message_id),
            'qa_score': 8.5,
            'qa_status': 'APPROVED',
            'qa_feedback': 'Excellent response with good empathy',
            'qa_tags': 'empathy,helpful,accurate'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['qa_score'], 8.5)
        self.assertEqual(response.data['data']['qa_score_grade'], 'A')
        
        # Verify message was updated
        ai_message.refresh_from_db()
        self.assertEqual(ai_message.qa_score, 8.5)
        self.assertEqual(ai_message.qa_status, 'APPROVED')
        self.assertEqual(ai_message.qa_reviewer, self.qa_reviewer)
    
    def test_get_qa_messages_endpoint(self):
        """Test getting QA messages endpoint"""
        self.client.force_authenticate(user=self.qa_reviewer)
        
        thread = Thread.objects.create(user=self.user, title="QA Messages Test")
        
        # Create messages and select some for QA
        for i in range(5):
            msg = Message.objects.create(
                thread=thread,
                sender='AI',
                content=f"AI response {i}"
            )
            if i < 3:  # Select first 3 for QA
                msg.select_for_qa()
                if i < 2:  # Review first 2
                    msg.complete_qa_review(
                        score=8.0 + i,
                        status='APPROVED',
                        reviewer=self.qa_reviewer
                    )
        
        url = reverse('ai_companion:get-qa-messages')
        
        # Get all QA messages
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        
        # Filter by status
        response = self.client.get(url, {'status': 'PENDING'})
        self.assertEqual(response.data['count'], 1)  # Only 1 pending
        
        # Filter by reviewed
        response = self.client.get(url, {'reviewed': 'true'})
        self.assertEqual(response.data['count'], 2)  # 2 reviewed
    
    def test_qa_stats_endpoint(self):
        """Test QA statistics endpoint"""
        self.client.force_authenticate(user=self.qa_reviewer)
        
        thread = Thread.objects.create(user=self.user, title="QA Stats Test")
        
        # Create and review some messages
        for i in range(10):
            msg = Message.objects.create(
                thread=thread,
                sender='AI',
                content=f"AI response {i}"
            )
            if i < 5:  # Select 5 for QA
                msg.select_for_qa()
                if i < 3:  # Review 3
                    msg.complete_qa_review(
                        score=7.0 + i,
                        status='APPROVED' if i < 2 else 'NEEDS_IMPROVEMENT',
                        reviewer=self.qa_reviewer
                    )
        
        url = reverse('ai_companion:qa-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overview', response.data)
        self.assertIn('status_breakdown', response.data)
        self.assertIn('score_statistics', response.data)
        
        # Check overview stats
        overview = response.data['overview']
        self.assertEqual(overview['ai_messages'], 10)
        self.assertEqual(overview['selected_for_qa'], 5)
        self.assertEqual(overview['qa_reviewed'], 3)


class AICompanionIntegrationTests(TransactionTestCase):
    """Integration tests for AI Companion workflows"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.qa_reviewer = User.objects.create_user(
            username='qa_reviewer',
            email='qa@example.com',
            password='qapass123',
            is_staff=True
        )
    
    @patch('ai_companion.groq_client.GroqClient.get_chat_response')
    def test_complete_chat_workflow(self, mock_generate):
        """Test complete chat workflow with QA and feedback"""
        mock_generate.return_value = 'I understand you are feeling stressed. Here are some techniques...'
        
        self.client.force_authenticate(user=self.user)
        
        # 1. Start chat
        chat_url = reverse('ai_companion:chat')
        thread = Thread.objects.create(user=self.user, title="Stress Management")
        chat_data = {
            'thread_id': str(thread.thread_id),
            'message': 'I am feeling very stressed lately'
        }
        
        response = self.client.post(chat_url, chat_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        thread_id = response.data['thread_id']
        ai_message_id = response.data['ai_response']['message_id']
        
        # 2. User provides feedback
        feedback_url = reverse('ai_companion:submit-user-feedback')
        feedback_data = {
            'message_id': ai_message_id,
            'is_helpful': True,
            'feedback_comment': 'Very helpful techniques!'
        }
        
        response = self.client.post(feedback_url, feedback_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Message gets selected for QA (simulate management command)
        ai_message = Message.objects.get(message_id=ai_message_id)
        ai_message.select_for_qa()
        
        # 4. QA reviewer reviews the message
        self.client.force_authenticate(user=self.qa_reviewer)
        qa_url = reverse('ai_companion:submit-qa-feedback')
        qa_data = {
            'message_id': ai_message_id,
            'qa_score': 9.0,
            'qa_status': 'APPROVED',
            'qa_feedback': 'Excellent empathetic response with practical advice',
            'qa_tags': 'empathy,practical,mental-health'
        }
        
        response = self.client.post(qa_url, qa_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. Verify complete workflow
        ai_message.refresh_from_db()
        self.assertTrue(ai_message.is_helpful)  # User feedback
        self.assertEqual(ai_message.user_feedback, 'Very helpful techniques!')
        self.assertEqual(ai_message.qa_score, 9.0)  # QA review
        self.assertEqual(ai_message.qa_status, 'APPROVED')
        self.assertEqual(ai_message.qa_score_grade, 'A+')
    
    def test_thread_management_workflow(self):
        """Test complete thread management workflow"""
        self.client.force_authenticate(user=self.user)
        
        # 1. Create multiple threads
        threads = []
        for i in range(3):
            thread = Thread.objects.create(
                user=self.user,
                title=f"Thread {i+1}",
                category='MENTAL_HEALTH' if i % 2 == 0 else 'NUTRITION'
            )
            threads.append(thread)
            
            # Add some messages
            Message.objects.create(thread=thread, sender='USER', content=f"User message {i}")
            Message.objects.create(thread=thread, sender='AI', content=f"AI response {i}")
        
        # 2. Mark one as favorite
        fav_url = reverse('ai_companion:toggle-favorite', 
                         kwargs={'thread_id': threads[0].thread_id})
        response = self.client.post(fav_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Archive one thread
        arch_url = reverse('ai_companion:toggle-archive', 
                          kwargs={'thread_id': threads[1].thread_id})
        response = self.client.post(arch_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. List threads and verify filtering
        list_url = reverse('ai_companion:thread-list')
        
        # All threads (including archived)
        response = self.client.get(list_url)
        self.assertEqual(len(response.data['results']), 3)
        
        # Only favorites
        response = self.client.get(list_url, {'is_favorite': 'true'})
        self.assertEqual(len(response.data['results']), 1)
        
        # Exclude archived
        response = self.client.get(list_url, {'is_archived': 'false'})
        self.assertEqual(len(response.data['results']), 2)


class AICompanionPerformanceTests(TestCase):
    """Performance tests for AI Companion"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='perfuser',
            email='perf@example.com',
            password='perfpass123'
        )
    
    def test_bulk_message_creation(self):
        """Test creating many messages efficiently"""
        thread = Thread.objects.create(user=self.user, title="Performance Test")
        
        # Create many messages
        messages = []
        for i in range(1000):
            messages.append(Message(
                thread=thread,
                sender='AI' if i % 2 == 0 else 'USER',
                content=f"Message {i}"
            ))
        
        # Bulk create
        import time
        start_time = time.time()
        Message.objects.bulk_create(messages)
        end_time = time.time()
        
        duration = end_time - start_time
        self.assertLess(duration, 5.0)  # Should complete within 5 seconds
        self.assertEqual(Message.objects.filter(thread=thread).count(), 1000)
    
    def test_qa_selection_performance(self):
        """Test QA message selection performance"""
        thread = Thread.objects.create(user=self.user, title="QA Performance Test")
        
        # Create many AI messages
        messages = []
        for i in range(500):
            messages.append(Message(
                thread=thread,
                sender='AI',
                content=f"AI message {i}"
            ))
        
        Message.objects.bulk_create(messages)
        
        # Test random selection performance
        import time
        start_time = time.time()
        
        random_messages = Message.get_random_messages_for_qa(count=50)
        selected_count = random_messages.count()
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.assertEqual(selected_count, 50)
        self.assertLess(duration, 1.0)  # Should complete within 1 second


# Test runner command
if __name__ == '__main__':
    import sys
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'rest_framework',
                'ai_companion',
            ],
            SECRET_KEY='test-secret-key',
        )
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['ai_companion'])
    sys.exit(bool(failures))
