import pytest
import asyncio
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
import statistics

class TestPerformance:
    """Performance tests for the Personalized Tone Adaptation System"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_single_user_response_time(self):
        """Test response time for single user requests"""
        # Create a test user
        user_id = "perf_test_user"
        profile_data = {
            "user_id": user_id,
            "preferences": {
                "formality": 0.7,
                "enthusiasm": 0.6,
                "verbosity": 0.5,
                "empathy": 0.8,
                "humor": 0.4
            }
        }
        
        # Create profile
        response = requests.post(f"{self.BASE_URL}/api/profile/", json=profile_data)
        assert response.status_code == 200
        
        # Test response times
        messages = [
            "Hello, how are you?",
            "I need help with my project",
            "Can you explain this concept?",
            "What's the weather like?",
            "I have a meeting tomorrow"
        ]
        
        response_times = []
        
        for message in messages:
            start_time = time.time()
            
            chat_data = {
                "user_id": user_id,
                "message": message
            }
            
            response = requests.post(f"{self.BASE_URL}/api/chat/", json=chat_data)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"\nSingle User Performance:")
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"Maximum response time: {max_response_time:.3f}s")
        print(f"Minimum response time: {min_response_time:.3f}s")
        
        # Assert performance requirements
        assert avg_response_time < 0.2, f"Average response time {avg_response_time:.3f}s exceeds 200ms limit"
        assert max_response_time < 0.5, f"Maximum response time {max_response_time:.3f}s exceeds 500ms limit"
    
    def test_concurrent_users(self):
        """Test system performance with 50 concurrent users"""
        num_users = 50
        messages_per_user = 3
        
        def user_workload(user_id):
            """Simulate a user workload"""
            # Create user profile
            profile_data = {
                "user_id": f"concurrent_user_{user_id}",
                "preferences": {
                    "formality": 0.5 + (user_id % 5) * 0.1,
                    "enthusiasm": 0.3 + (user_id % 7) * 0.1,
                    "verbosity": 0.4 + (user_id % 3) * 0.2,
                    "empathy": 0.6 + (user_id % 4) * 0.1,
                    "humor": 0.2 + (user_id % 6) * 0.1
                }
            }
            
            response = requests.post(f"{self.BASE_URL}/api/profile/", json=profile_data)
            if response.status_code != 200:
                return f"Failed to create profile for user {user_id}"
            
            # Send messages
            messages = [
                f"Hello from user {user_id}",
                f"I need help with task {user_id}",
                f"Can you assist user {user_id}?"
            ]
            
            response_times = []
            for message in messages:
                start_time = time.time()
                
                chat_data = {
                    "user_id": f"concurrent_user_{user_id}",
                    "message": message
                }
                
                response = requests.post(f"{self.BASE_URL}/api/chat/", json=chat_data)
                end_time = time.time()
                
                if response.status_code != 200:
                    return f"Failed to send message for user {user_id}"
                
                response_times.append(end_time - start_time)
            
            return {
                "user_id": user_id,
                "response_times": response_times,
                "avg_response_time": statistics.mean(response_times)
            }
        
        # Run concurrent users
        print(f"\nTesting {num_users} concurrent users...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_workload, i) for i in range(num_users)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_results = [r for r in results if isinstance(r, dict)]
        failed_results = [r for r in results if isinstance(r, str)]
        
        all_response_times = []
        for result in successful_results:
            all_response_times.extend(result["response_times"])
        
        if all_response_times:
            avg_response_time = statistics.mean(all_response_times)
            max_response_time = max(all_response_times)
            min_response_time = min(all_response_times)
            p95_response_time = statistics.quantiles(all_response_times, n=20)[18]  # 95th percentile
            
            print(f"\nConcurrent Users Performance:")
            print(f"Total test time: {total_time:.2f}s")
            print(f"Successful users: {len(successful_results)}/{num_users}")
            print(f"Failed users: {len(failed_results)}")
            print(f"Total requests: {len(all_response_times)}")
            print(f"Average response time: {avg_response_time:.3f}s")
            print(f"95th percentile response time: {p95_response_time:.3f}s")
            print(f"Maximum response time: {max_response_time:.3f}s")
            print(f"Minimum response time: {min_response_time:.3f}s")
            
            # Assert performance requirements
            assert len(successful_results) >= num_users * 0.95, f"Success rate {len(successful_results)/num_users:.1%} below 95%"
            assert avg_response_time < 0.3, f"Average response time {avg_response_time:.3f}s exceeds 300ms limit"
            assert p95_response_time < 0.5, f"95th percentile response time {p95_response_time:.3f}s exceeds 500ms limit"
        else:
            pytest.fail("No successful responses recorded")
    
    def test_memory_usage(self):
        """Test memory usage under load"""
        user_id = "memory_test_user"
        
        # Create user profile
        profile_data = {
            "user_id": user_id,
            "preferences": {
                "formality": 0.7,
                "enthusiasm": 0.6,
                "verbosity": 0.5,
                "empathy": 0.8,
                "humor": 0.4
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/api/profile/", json=profile_data)
        assert response.status_code == 200
        
        # Send many messages to test memory limits
        print(f"\nTesting memory usage...")
        
        for i in range(20):  # Send 20 messages
            chat_data = {
                "user_id": user_id,
                "message": f"Test message {i} with some content to test memory usage"
            }
            
            response = requests.post(f"{self.BASE_URL}/api/chat/", json=chat_data)
            assert response.status_code == 200
        
        # Check memory summary
        memory_response = requests.get(f"{self.BASE_URL}/api/chat/{user_id}/memory")
        assert memory_response.status_code == 200
        
        memory_data = memory_response.json()
        print(f"Short-term memory count: {memory_data['short_term_count']}")
        print(f"Long-term memory size: {memory_data['long_term_size_kb']:.2f} KB")
        
        # Assert memory limits
        assert memory_data['short_term_count'] <= 10, "Short-term memory exceeds limit"
        assert memory_data['long_term_size_kb'] <= 50, "Long-term memory exceeds 50KB limit"
    
    def test_feedback_processing_performance(self):
        """Test feedback processing performance"""
        user_id = "feedback_test_user"
        
        # Create user profile
        profile_data = {
            "user_id": user_id,
            "preferences": {
                "formality": 0.7,
                "enthusiasm": 0.6,
                "verbosity": 0.5,
                "empathy": 0.8,
                "humor": 0.4
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/api/profile/", json=profile_data)
        assert response.status_code == 200
        
        # Test feedback processing performance
        print(f"\nTesting feedback processing performance...")
        
        feedback_times = []
        
        for i in range(10):  # Submit 10 feedback entries
            start_time = time.time()
            
            feedback_data = {
                "user_id": user_id,
                "type": "rating",
                "value": 4.0 + (i % 2) * 0.5,
                "context": "work" if i % 2 == 0 else "personal"
            }
            
            response = requests.post(f"{self.BASE_URL}/api/chat/feedback", json=feedback_data)
            end_time = time.time()
            
            assert response.status_code == 200
            feedback_times.append(end_time - start_time)
        
        avg_feedback_time = statistics.mean(feedback_times)
        max_feedback_time = max(feedback_times)
        
        print(f"Average feedback processing time: {avg_feedback_time:.3f}s")
        print(f"Maximum feedback processing time: {max_feedback_time:.3f}s")
        
        # Assert performance requirements
        assert avg_feedback_time < 0.1, f"Average feedback processing time {avg_feedback_time:.3f}s exceeds 100ms limit"
        assert max_feedback_time < 0.2, f"Maximum feedback processing time {max_feedback_time:.3f}s exceeds 200ms limit"
    
    def test_database_performance(self):
        """Test database operations performance"""
        print(f"\nTesting database performance...")
        
        # Test profile creation performance
        creation_times = []
        for i in range(20):
            start_time = time.time()
            
            profile_data = {
                "user_id": f"db_test_user_{i}",
                "preferences": {
                    "formality": 0.5 + (i % 5) * 0.1,
                    "enthusiasm": 0.4 + (i % 3) * 0.2,
                    "verbosity": 0.6 + (i % 4) * 0.1,
                    "empathy": 0.7 + (i % 2) * 0.15,
                    "humor": 0.3 + (i % 6) * 0.1
                }
            }
            
            response = requests.post(f"{self.BASE_URL}/api/profile/", json=profile_data)
            end_time = time.time()
            
            assert response.status_code == 200
            creation_times.append(end_time - start_time)
        
        avg_creation_time = statistics.mean(creation_times)
        print(f"Average profile creation time: {avg_creation_time:.3f}s")
        
        # Test profile retrieval performance
        retrieval_times = []
        for i in range(20):
            start_time = time.time()
            
            response = requests.get(f"{self.BASE_URL}/api/profile/db_test_user_{i}")
            end_time = time.time()
            
            assert response.status_code == 200
            retrieval_times.append(end_time - start_time)
        
        avg_retrieval_time = statistics.mean(retrieval_times)
        print(f"Average profile retrieval time: {avg_retrieval_time:.3f}s")
        
        # Assert performance requirements
        assert avg_creation_time < 0.05, f"Average profile creation time {avg_creation_time:.3f}s exceeds 50ms limit"
        assert avg_retrieval_time < 0.02, f"Average profile retrieval time {avg_retrieval_time:.3f}s exceeds 20ms limit"

if __name__ == "__main__":
    # Run performance tests
    test_perf = TestPerformance()
    
    print("🚀 Running Performance Tests")
    print("=" * 40)
    
    test_perf.test_single_user_response_time()
    test_perf.test_concurrent_users()
    test_perf.test_memory_usage()
    test_perf.test_feedback_processing_performance()
    test_perf.test_database_performance()
    
    print("\n✅ All performance tests completed!") 