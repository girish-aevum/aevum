import os
import sys
import django
import requests
import json

# Set up Django environment
sys.path.append('/home/girish/project/aevum/code')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aevum.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ai_companion.models import Thread

class AIChatAPITester:
    def __init__(self):
        self.base_url = 'http://localhost:8000/api/ai-companion'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.token = None
        self.user = None

    def setup_test_user(self):
        """Create or retrieve a test user and generate token"""
        try:
            self.user = User.objects.get(username=self.username)
        except User.DoesNotExist:
            self.user = User.objects.create_user(
                username=self.username, 
                email='test@example.com', 
                password=self.password
            )
        
        # Generate or retrieve token
        token, _ = Token.objects.get_or_create(user=self.user)
        self.token = token.key

    def create_thread(self):
        """Create a new thread for testing"""
        thread = Thread.objects.create(
            user=self.user, 
            title="Test Chat Thread"
        )
        return thread

    def test_chat_endpoint(self):
        """Test the chat endpoint"""
        # Ensure test user and token are set up
        self.setup_test_user()
        
        # Create a thread
        thread = self.create_thread()
        
        # Prepare chat request
        headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
        
        chat_data = {
            'thread_id': str(thread.thread_id),
            'message': 'Hello, how are you feeling today?'
        }
        
        # Send chat request
        response = requests.post(
            f'{self.base_url}/chat/', 
            headers=headers, 
            data=json.dumps(chat_data)
        )
        
        # Validate response
        print("Chat Endpoint Test Results:")
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
        
        # Assertions
        assert response.status_code == 200, "Chat endpoint should return 200 OK"
        response_data = response.json()
        assert 'thread_id' in response_data, "Response should contain thread_id"
        assert 'user_message' in response_data, "Response should contain user_message"
        assert 'ai_response' in response_data, "Response should contain ai_response"

    def run_tests(self):
        """Run all chat API tests"""
        try:
            self.test_chat_endpoint()
            print("\n✅ All Chat API Tests Passed Successfully!")
        except AssertionError as e:
            print(f"\n❌ Test Failed: {e}")
        except Exception as e:
            print(f"\n❌ Unexpected Error: {e}")

def main():
    tester = AIChatAPITester()
    tester.run_tests()

if __name__ == '__main__':
    main() 