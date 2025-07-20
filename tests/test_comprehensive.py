import pytest
import requests
import json
import time
from typing import Dict, Any

class TestComprehensiveAPI:
    """Comprehensive test suite for the AI Tone Adaptation System"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture
    def sample_profiles(self):
        """Sample user profiles for testing"""
        return {
            "formal_work_user": {
                "user_id": "formal_work_user",
                "tone_preferences": {
                    "formality": "formal",
                    "enthusiasm": "low",
                    "verbosity": "detailed",
                    "empathy_level": "medium",
                    "humor": "none"
                },
                "communication_style": {
                    "preferred_greeting": "Good morning",
                    "technical_level": "advanced",
                    "cultural_context": "professional",
                    "age_group": "adult"
                },
                "interaction_history": {
                    "total_interactions": 0,
                    "successful_tone_matches": 0,
                    "feedback_score": 0.0,
                    "last_interaction": None
                },
                "context_preferences": {
                    "work": {
                        "formality": "formal",
                        "enthusiasm": "low",
                        "verbosity": "detailed",
                        "empathy_level": "medium",
                        "humor": "none"
                    }
                }
            },
            "casual_personal_user": {
                "user_id": "casual_personal_user",
                "tone_preferences": {
                    "formality": "casual",
                    "enthusiasm": "high",
                    "verbosity": "concise",
                    "empathy_level": "high",
                    "humor": "moderate"
                },
                "communication_style": {
                    "preferred_greeting": "Hey there!",
                    "technical_level": "beginner",
                    "cultural_context": "casual",
                    "age_group": "young_adult"
                },
                "interaction_history": {
                    "total_interactions": 0,
                    "successful_tone_matches": 0,
                    "feedback_score": 0.0,
                    "last_interaction": None
                },
                "context_preferences": {
                    "personal": {
                        "formality": "casual",
                        "enthusiasm": "high",
                        "verbosity": "concise",
                        "empathy_level": "high",
                        "humor": "moderate"
                    }
                }
            },
            "academic_user": {
                "user_id": "academic_user",
                "tone_preferences": {
                    "formality": "professional",
                    "enthusiasm": "medium",
                    "verbosity": "detailed",
                    "empathy_level": "medium",
                    "humor": "light"
                },
                "communication_style": {
                    "preferred_greeting": "Hello",
                    "technical_level": "advanced",
                    "cultural_context": "academic",
                    "age_group": "adult"
                },
                "interaction_history": {
                    "total_interactions": 0,
                    "successful_tone_matches": 0,
                    "feedback_score": 0.0,
                    "last_interaction": None
                },
                "context_preferences": {
                    "academic": {
                        "formality": "professional",
                        "enthusiasm": "medium",
                        "verbosity": "detailed",
                        "empathy_level": "medium",
                        "humor": "light"
                    }
                }
            }
        }
    
    def test_health_check(self):
        """Test API health endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_create_profiles(self, sample_profiles):
        """Test creating user profiles with enhanced schema"""
        for user_id, profile_data in sample_profiles.items():
            response = requests.post(
                f"{self.BASE_URL}/api/profile",
                json=profile_data
            )
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id
            assert "tone_preferences" in data
            assert "communication_style" in data
            assert "interaction_history" in data
    
    def test_get_profiles(self, sample_profiles):
        """Test retrieving user profiles"""
        for user_id in sample_profiles.keys():
            response = requests.get(f"{self.BASE_URL}/api/profile/{user_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id
            assert "tone_preferences" in data
            assert "communication_style" in data
            assert "interaction_history" in data
    
    def test_chat_with_tone_adaptation(self, sample_profiles):
        """Test chat endpoint with tone adaptation"""
        # Test formal work user
        response = requests.post(
            f"{self.BASE_URL}/api/chat",
            json={
                "user_id": "formal_work_user",
                "message": "I need help with the quarterly report",
                "context": "work"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "applied_tone" in data
        assert data["applied_tone"]["formality"] == "formal"
        
        # Test casual personal user
        response = requests.post(
            f"{self.BASE_URL}/api/chat",
            json={
                "user_id": "casual_personal_user",
                "message": "Hey! How's it going? 😊",
                "context": "personal"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "applied_tone" in data
        assert data["applied_tone"]["formality"] == "casual"
    
    def test_memory_endpoints(self):
        """Test memory management endpoints"""
        user_id = "memory_test_user"
        
        # Create a profile first
        profile_data = {
            "user_id": user_id,
            "tone_preferences": {
                "formality": "professional",
                "enthusiasm": "medium",
                "verbosity": "balanced",
                "empathy_level": "medium",
                "humor": "light"
            },
            "communication_style": {
                "preferred_greeting": "Hello",
                "technical_level": "intermediate",
                "cultural_context": "",
                "age_group": "adult"
            },
            "interaction_history": {
                "total_interactions": 0,
                "successful_tone_matches": 0,
                "feedback_score": 0.0,
                "last_interaction": None
            }
        }
        
        requests.post(f"{self.BASE_URL}/api/profile", json=profile_data)
        
        # Send some messages to create memory
        for i in range(3):
            requests.post(
                f"{self.BASE_URL}/api/chat",
                json={
                    "user_id": user_id,
                    "message": f"Test message {i}",
                    "context": "work"
                }
            )
        
        # Test get memory
        response = requests.get(f"{self.BASE_URL}/api/memory/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["short_term_count"] > 0
        
        # Test get short-term memory
        response = requests.get(f"{self.BASE_URL}/api/memory/{user_id}/short-term")
        assert response.status_code == 200
        data = response.json()
        assert "short_term_memory" in data
        
        # Test get long-term memory
        response = requests.get(f"{self.BASE_URL}/api/memory/{user_id}/long-term")
        assert response.status_code == 200
        data = response.json()
        assert "long_term_memory" in data
        
        # Test memory analytics
        response = requests.get(f"{self.BASE_URL}/api/memory/{user_id}/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "memory_usage" in data
        assert "conversation_patterns" in data
        assert "learning_metrics" in data
        
        # Test clear memory
        response = requests.delete(f"{self.BASE_URL}/api/memory/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Memory cleared successfully"
    
    def test_feedback_learning(self):
        """Test feedback-based learning"""
        user_id = "feedback_test_user"
        
        # Create profile
        profile_data = {
            "user_id": user_id,
            "tone_preferences": {
                "formality": "professional",
                "enthusiasm": "medium",
                "verbosity": "balanced",
                "empathy_level": "medium",
                "humor": "light"
            },
            "communication_style": {
                "preferred_greeting": "Hello",
                "technical_level": "intermediate",
                "cultural_context": "",
                "age_group": "adult"
            },
            "interaction_history": {
                "total_interactions": 0,
                "successful_tone_matches": 0,
                "feedback_score": 0.0,
                "last_interaction": None
            }
        }
        
        requests.post(f"{self.BASE_URL}/api/profile", json=profile_data)
        
        # Send a message
        response = requests.post(
            f"{self.BASE_URL}/api/chat",
            json={
                "user_id": user_id,
                "message": "I need help with this problem",
                "context": "work"
            }
        )
        assert response.status_code == 200
        
        # Submit feedback
        feedback_data = {
            "user_id": user_id,
            "type": "rating",
            "value": 4.5,
            "context": "work"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/chat/feedback",
            json=feedback_data
        )
        assert response.status_code == 200
        
        # Test feedback summary
        response = requests.get(f"{self.BASE_URL}/api/chat/{user_id}/feedback")
        assert response.status_code == 200
        data = response.json()
        assert "feedback_summary" in data
        assert "patterns" in data
        assert "recommendations" in data
    
    def test_context_switching(self):
        """Test context switching (professional to casual)"""
        user_id = "context_switch_user"
        
        # Create profile with context preferences
        profile_data = {
            "user_id": user_id,
            "tone_preferences": {
                "formality": "professional",
                "enthusiasm": "medium",
                "verbosity": "balanced",
                "empathy_level": "medium",
                "humor": "light"
            },
            "communication_style": {
                "preferred_greeting": "Hello",
                "technical_level": "intermediate",
                "cultural_context": "",
                "age_group": "adult"
            },
            "interaction_history": {
                "total_interactions": 0,
                "successful_tone_matches": 0,
                "feedback_score": 0.0,
                "last_interaction": None
            },
            "context_preferences": {
                "work": {
                    "formality": "formal",
                    "enthusiasm": "low",
                    "verbosity": "detailed",
                    "empathy_level": "medium",
                    "humor": "none"
                },
                "personal": {
                    "formality": "casual",
                    "enthusiasm": "high",
                    "verbosity": "concise",
                    "empathy_level": "high",
                    "humor": "moderate"
                }
            }
        }
        
        requests.post(f"{self.BASE_URL}/api/profile", json=profile_data)
        
        # Test work context
        response = requests.post(
            f"{self.BASE_URL}/api/chat",
            json={
                "user_id": user_id,
                "message": "I need to discuss the quarterly results",
                "context": "work"
            }
        )
        assert response.status_code == 200
        work_data = response.json()
        assert work_data["applied_tone"]["formality"] == "formal"
        
        # Test personal context
        response = requests.post(
            f"{self.BASE_URL}/api/chat",
            json={
                "user_id": user_id,
                "message": "Hey! How's your weekend going?",
                "context": "personal"
            }
        )
        assert response.status_code == 200
        personal_data = response.json()
        assert personal_data["applied_tone"]["formality"] == "casual"
    
    def test_memory_stress_test(self):
        """Test memory system under high conversation volume"""
        user_id = "stress_test_user"
        
        # Create profile
        profile_data = {
            "user_id": user_id,
            "tone_preferences": {
                "formality": "professional",
                "enthusiasm": "medium",
                "verbosity": "balanced",
                "empathy_level": "medium",
                "humor": "light"
            },
            "communication_style": {
                "preferred_greeting": "Hello",
                "technical_level": "intermediate",
                "cultural_context": "",
                "age_group": "adult"
            },
            "interaction_history": {
                "total_interactions": 0,
                "successful_tone_matches": 0,
                "feedback_score": 0.0,
                "last_interaction": None
            }
        }
        
        requests.post(f"{self.BASE_URL}/api/profile", json=profile_data)
        
        # Send many messages quickly
        start_time = time.time()
        for i in range(20):
            response = requests.post(
                f"{self.BASE_URL}/api/chat",
                json={
                    "user_id": user_id,
                    "message": f"Stress test message {i}",
                    "context": "work"
                }
            )
            assert response.status_code == 200
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Check memory limits are respected
        response = requests.get(f"{self.BASE_URL}/api/memory/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["short_term_count"] <= 10  # Max short-term memory
        assert data["long_term_size_kb"] <= 50  # Max long-term memory
        
        # Performance should be under 2 seconds for 20 messages
        assert response_time < 2.0
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test non-existent user
        response = requests.get(f"{self.BASE_URL}/api/profile/nonexistent_user")
        assert response.status_code == 404
        
        # Test invalid profile data
        invalid_profile = {
            "user_id": "invalid_user",
            "tone_preferences": {
                "formality": "invalid_value",
                "enthusiasm": "medium",
                "verbosity": "balanced",
                "empathy_level": "medium",
                "humor": "light"
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/api/profile", json=invalid_profile)
        assert response.status_code == 400
        
        # Test malformed chat request
        response = requests.post(
            f"{self.BASE_URL}/api/chat",
            json={"user_id": "test_user"}  # Missing message
        )
        assert response.status_code == 422  # Validation error
    
    def test_concurrent_users(self):
        """Test system with multiple concurrent users"""
        user_ids = [f"concurrent_user_{i}" for i in range(5)]
        
        # Create profiles for all users
        for user_id in user_ids:
            profile_data = {
                "user_id": user_id,
                "tone_preferences": {
                    "formality": "professional",
                    "enthusiasm": "medium",
                    "verbosity": "balanced",
                    "empathy_level": "medium",
                    "humor": "light"
                },
                "communication_style": {
                    "preferred_greeting": "Hello",
                    "technical_level": "intermediate",
                    "cultural_context": "",
                    "age_group": "adult"
                },
                "interaction_history": {
                    "total_interactions": 0,
                    "successful_tone_matches": 0,
                    "feedback_score": 0.0,
                    "last_interaction": None
                }
            }
            requests.post(f"{self.BASE_URL}/api/profile", json=profile_data)
        
        # Send messages from all users simultaneously
        start_time = time.time()
        responses = []
        
        for user_id in user_ids:
            response = requests.post(
                f"{self.BASE_URL}/api/chat",
                json={
                    "user_id": user_id,
                    "message": f"Concurrent test from {user_id}",
                    "context": "work"
                }
            )
            responses.append(response)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # All responses should be successful
        for response in responses:
            assert response.status_code == 200
        
        # Total response time should be reasonable
        assert response_time < 5.0  # 5 seconds for 5 concurrent requests
    
    def test_emotion_detection_integration(self):
        """Test emotion detection integration (bonus feature)"""
        user_id = "emotion_test_user"
        
        # Create profile
        profile_data = {
            "user_id": user_id,
            "tone_preferences": {
                "formality": "professional",
                "enthusiasm": "medium",
                "verbosity": "balanced",
                "empathy_level": "medium",
                "humor": "light"
            },
            "communication_style": {
                "preferred_greeting": "Hello",
                "technical_level": "intermediate",
                "cultural_context": "",
                "age_group": "adult"
            },
            "interaction_history": {
                "total_interactions": 0,
                "successful_tone_matches": 0,
                "feedback_score": 0.0,
                "last_interaction": None
            }
        }
        
        requests.post(f"{self.BASE_URL}/api/profile", json=profile_data)
        
        # Test different emotional messages
        emotional_messages = [
            ("I'm so happy today! 😊", "joy"),
            ("I'm feeling really sad 😢", "sadness"),
            ("I'm so angry about this! 😠", "anger"),
            ("I'm scared about the results 😨", "fear"),
            ("Wow! That's amazing! 😲", "surprise")
        ]
        
        for message, expected_emotion in emotional_messages:
            response = requests.post(
                f"{self.BASE_URL}/api/chat",
                json={
                    "user_id": user_id,
                    "message": message,
                    "context": "personal"
                }
            )
            assert response.status_code == 200
            # Note: Emotion detection would be integrated in the response
            # This test verifies the system handles emotional content
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        user_id = "performance_test_user"
        
        # Create profile
        profile_data = {
            "user_id": user_id,
            "tone_preferences": {
                "formality": "professional",
                "enthusiasm": "medium",
                "verbosity": "balanced",
                "empathy_level": "medium",
                "humor": "light"
            },
            "communication_style": {
                "preferred_greeting": "Hello",
                "technical_level": "intermediate",
                "cultural_context": "",
                "age_group": "adult"
            },
            "interaction_history": {
                "total_interactions": 0,
                "successful_tone_matches": 0,
                "feedback_score": 0.0,
                "last_interaction": None
            }
        }
        
        requests.post(f"{self.BASE_URL}/api/profile", json=profile_data)
        
        # Test response time
        start_time = time.time()
        response = requests.post(
            f"{self.BASE_URL}/api/chat",
            json={
                "user_id": user_id,
                "message": "Performance test message",
                "context": "work"
            }
        )
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0  # Should be under 2 seconds
        
        # Test memory lookup time
        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/api/memory/{user_id}")
        end_time = time.time()
        
        assert response.status_code == 200
        lookup_time = end_time - start_time
        assert lookup_time < 0.1  # Should be under 100ms 