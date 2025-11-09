"""
Performance Tests - API and Database Performance

Tests for performance benchmarks including:
- API response times
- Database query performance
- Bulk operations
- Memory usage
"""

import time
import statistics
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.utils import override_settings
from rest_framework.test import APIClient
from rest_framework import status

from authentication.models import UserProfile


class APIPerformanceTest(TestCase):
    """Performance tests for API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='perfuser',
            email='perf@example.com',
            password='perfpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def measure_response_time(self, url, method='GET', data=None, iterations=10):
        """Measure average response time for an endpoint"""
        times = []
        
        for _ in range(iterations):
            start_time = time.time()
            
            if method == 'GET':
                response = self.client.get(url)
            elif method == 'POST':
                response = self.client.post(url, data, format='json')
            elif method == 'PUT':
                response = self.client.put(url, data, format='json')
            elif method == 'PATCH':
                response = self.client.patch(url, data, format='json')
            
            end_time = time.time()
            times.append((end_time - start_time) * 1000)  # Convert to milliseconds
            
            # Ensure the request was successful
            self.assertIn(response.status_code, [200, 201, 204])
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        
        return {
            'average': avg_time,
            'max': max_time,
            'min': min_time,
            'all_times': times
        }
    
    def test_profile_get_performance(self):
        """Test profile GET endpoint performance"""
        url = reverse('authentication:my-profile')
        
        performance = self.measure_response_time(url, 'GET', iterations=20)
        
        print(f"\n📊 Profile GET Performance:")
        print(f"  Average: {performance['average']:.2f}ms")
        print(f"  Max: {performance['max']:.2f}ms")
        print(f"  Min: {performance['min']:.2f}ms")
        
        # Assert reasonable performance (adjust thresholds as needed)
        self.assertLess(performance['average'], 500)  # Should be under 500ms on average
        self.assertLess(performance['max'], 1000)     # Should never exceed 1 second
    
    def test_profile_update_performance(self):
        """Test profile UPDATE endpoint performance"""
        url = reverse('authentication:my-profile')
        data = {
            'phone_number': '+1234567890',
            'height_cm': 175.0,
            'weight_kg': 70.0
        }
        
        performance = self.measure_response_time(url, 'PUT', data, iterations=10)
        
        print(f"\n📊 Profile UPDATE Performance:")
        print(f"  Average: {performance['average']:.2f}ms")
        print(f"  Max: {performance['max']:.2f}ms")
        print(f"  Min: {performance['min']:.2f}ms")
        
        # Update operations should be reasonably fast
        self.assertLess(performance['average'], 1000)  # Should be under 1 second on average
        self.assertLess(performance['max'], 2000)      # Should never exceed 2 seconds


class DatabasePerformanceTest(TransactionTestCase):
    """Performance tests for database operations"""
    
    def test_bulk_user_creation_performance(self):
        """Test bulk user creation performance"""
        user_count = 100
        
        # Test individual creation
        start_time = time.time()
        for i in range(user_count):
            User.objects.create_user(
                username=f'user_{i}',
                email=f'user_{i}@example.com',
                password='testpass123'
            )
        individual_time = time.time() - start_time
        
        # Clean up
        User.objects.filter(username__startswith='user_').delete()
        
        # Test bulk creation
        users_data = []
        for i in range(user_count):
            users_data.append(User(
                username=f'bulk_user_{i}',
                email=f'bulk_user_{i}@example.com'
            ))
        
        start_time = time.time()
        User.objects.bulk_create(users_data)
        bulk_time = time.time() - start_time
        
        print(f"\n📊 User Creation Performance ({user_count} users):")
        print(f"  Individual creation: {individual_time:.2f}s")
        print(f"  Bulk creation: {bulk_time:.2f}s")
        print(f"  Speedup: {individual_time/bulk_time:.1f}x")
        
        # Bulk should be significantly faster
        self.assertLess(bulk_time, individual_time / 2)
    
    def test_profile_query_performance(self):
        """Test profile querying performance with various data sizes"""
        
        # Create test users with profiles
        users = []
        for i in range(50):
            user = User.objects.create_user(
                username=f'query_user_{i}',
                email=f'query_user_{i}@example.com',
                password='testpass123'
            )
            users.append(user)
            
            # Update profile with some data
            profile = user.profile
            profile.height_cm = 170.0 + (i % 20)  # Vary height
            profile.weight_kg = 60.0 + (i % 30)   # Vary weight
            profile.phone_number = f'+123456789{i:02d}'
            profile.save()
        
        # Test single profile query
        start_time = time.time()
        for _ in range(100):
            profile = UserProfile.objects.get(user=users[0])
        single_query_time = time.time() - start_time
        
        # Test bulk profile query
        start_time = time.time()
        profiles = list(UserProfile.objects.filter(
            user__username__startswith='query_user_'
        ).select_related('user'))
        bulk_query_time = time.time() - start_time
        
        print(f"\n📊 Profile Query Performance:")
        print(f"  100 single queries: {single_query_time:.3f}s")
        print(f"  1 bulk query (50 profiles): {bulk_query_time:.3f}s")
        print(f"  Profiles retrieved: {len(profiles)}")
        
        # Verify we got the expected number of profiles
        self.assertEqual(len(profiles), 50)
        
        # Single queries should complete within reasonable time
        self.assertLess(single_query_time, 1.0)  # 100 queries under 1 second
        self.assertLess(bulk_query_time, 0.1)    # Bulk query under 100ms


class MemoryPerformanceTest(TestCase):
    """Memory usage performance tests"""
    
    def test_profile_memory_usage(self):
        """Test memory efficiency of profile operations"""
        import gc
        import sys
        
        # Force garbage collection
        gc.collect()
        
        # Get initial memory usage (approximate)
        initial_objects = len(gc.get_objects())
        
        # Create and work with profiles
        users = []
        for i in range(100):
            user = User.objects.create_user(
                username=f'mem_user_{i}',
                email=f'mem_user_{i}@example.com',
                password='testpass123'
            )
            users.append(user)
            
            # Access profile to ensure it's created
            profile = user.profile
            profile.phone_number = f'+123456789{i:02d}'
            profile.save()
        
        # Force garbage collection again
        gc.collect()
        final_objects = len(gc.get_objects())
        
        objects_created = final_objects - initial_objects
        
        print(f"\n📊 Memory Usage Test:")
        print(f"  Objects before: {initial_objects}")
        print(f"  Objects after: {final_objects}")
        print(f"  Objects created: {objects_created}")
        print(f"  Objects per user+profile: {objects_created/100:.1f}")
        
        # Ensure we're not creating an excessive number of objects
        # This is a rough check - adjust threshold as needed
        self.assertLess(objects_created / 100, 50)  # Less than 50 objects per user+profile


class ConcurrencyPerformanceTest(TransactionTestCase):
    """Test performance under concurrent access"""
    
    def test_concurrent_profile_access(self):
        """Test profile access performance under simulated concurrent load"""
        
        # Create a test user
        user = User.objects.create_user(
            username='concurrent_user',
            email='concurrent@example.com',
            password='testpass123'
        )
        
        # Simulate concurrent profile updates
        update_times = []
        
        for i in range(20):
            start_time = time.time()
            
            # Simulate what might happen with concurrent access
            profile = user.profile
            profile.weight_kg = 70.0 + (i % 10)  # Vary the weight
            profile.save()
            
            # Immediately read it back (simulating another request)
            profile.refresh_from_db()
            
            end_time = time.time()
            update_times.append((end_time - start_time) * 1000)
        
        avg_time = statistics.mean(update_times)
        max_time = max(update_times)
        
        print(f"\n📊 Concurrent Access Performance:")
        print(f"  Average update time: {avg_time:.2f}ms")
        print(f"  Max update time: {max_time:.2f}ms")
        print(f"  Total operations: {len(update_times)}")
        
        # Ensure reasonable performance under load
        self.assertLess(avg_time, 100)   # Average under 100ms
        self.assertLess(max_time, 500)   # Max under 500ms 