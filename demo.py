#!/usr/bin/env python3
"""
Demonstration script for the Personalized Tone Adaptation System
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def create_user_profile(user_id, tone_preferences, communication_style=None, interaction_history=None, context_preferences=None):
    """Create a user profile"""
    profile_data = {
        "user_id": user_id,
        "tone_preferences": tone_preferences,
        "communication_style": communication_style or {},
        "interaction_history": interaction_history or {},
        "context_preferences": context_preferences
    }
    
    response = requests.post(f"{BASE_URL}/api/profile/", json=profile_data)
    if response.status_code == 200:
        print(f"✅ Profile created for user: {user_id}")
        return response.json()
    else:
        print(f"❌ Failed to create profile: {response.text}")
        return None

def send_chat_message(user_id, message, context=None, feedback=None):
    """Send a chat message and get tone-adapted response"""
    chat_data = {
        "user_id": user_id,
        "message": message,
        "context": context,
        "feedback": feedback
    }
    
    response = requests.post(f"{BASE_URL}/api/chat/", json=chat_data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to send chat message: {response.text}")
        return None

def submit_feedback(user_id, feedback_type, value=None, corrections=None, preferences=None, context=None):
    """Submit feedback for learning"""
    feedback_data = {
        "user_id": user_id,
        "type": feedback_type,
        "value": value,
        "corrections": corrections,
        "preferences": preferences,
        "context": context
    }
    
    response = requests.post(f"{BASE_URL}/api/chat/feedback", json=feedback_data)
    if response.status_code == 200:
        print(f"✅ Feedback submitted successfully")
        return response.json()
    else:
        print(f"❌ Failed to submit feedback: {response.text}")
        return None

def get_memory_summary(user_id):
    """Get user's memory summary"""
    response = requests.get(f"{BASE_URL}/api/chat/{user_id}/memory")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get memory: {response.text}")
        return None

def demo_basic_usage():
    """Demonstrate basic usage of the system"""
    print("🚀 Personalized Tone Adaptation System Demo")
    print("=" * 50)
    
    # Create different user profiles
    print("\n1. Creating User Profiles...")
    
    # Formal work user
    formal_user = "formal_work_user"
    create_user_profile(
        formal_user,
        {
            "formality": "formal",
            "enthusiasm": "low",
            "verbosity": "detailed",
            "empathy_level": "medium",
            "humor": "none"
        },
        {
            "preferred_greeting": "Good morning",
            "technical_level": "advanced",
            "cultural_context": "Corporate",
            "age_group": "adult"
        },
        {
            "total_interactions": 0,
            "successful_tone_matches": 0,
            "feedback_score": 0.0,
            "last_interaction": None
        },
        {
            "work": {
                "formality": "formal",
                "enthusiasm": "low",
                "verbosity": "detailed",
                "empathy_level": "low",
                "humor": "none"
            },
            "personal": {
                "formality": "professional",
                "enthusiasm": "medium",
                "verbosity": "balanced",
                "empathy_level": "high",
                "humor": "light"
            }
        }
    )
    
    # Casual personal user
    casual_user = "casual_personal_user"
    create_user_profile(
        casual_user,
        {
            "formality": "casual",
            "enthusiasm": "high",
            "verbosity": "concise",
            "empathy_level": "high",
            "humor": "moderate"
        },
        {
            "preferred_greeting": "Hey there!",
            "technical_level": "intermediate",
            "cultural_context": "Casual",
            "age_group": "young_adult"
        },
        {
            "total_interactions": 0,
            "successful_tone_matches": 0,
            "feedback_score": 0.0,
            "last_interaction": None
        },
        {
            "work": {
                "formality": "professional",
                "enthusiasm": "medium",
                "verbosity": "balanced",
                "empathy_level": "medium",
                "humor": "light"
            },
            "personal": {
                "formality": "casual",
                "enthusiasm": "high",
                "verbosity": "concise",
                "empathy_level": "high",
                "humor": "moderate"
            }
        }
    )
    
    # Test messages
    test_messages = [
        ("I have a meeting with the client tomorrow", "work"),
        ("How are you doing today?", "personal"),
        ("Can you help me with this project?", "work"),
        ("I'm going to a party this weekend!", "personal")
    ]
    
    print("\n2. Testing Tone Adaptation...")
    
    for user_id in [formal_user, casual_user]:
        print(f"\n--- {user_id.upper()} ---")
        
        for message, context in test_messages:
            print(f"\nMessage: '{message}' (Context: {context})")
            
            response_data = send_chat_message(user_id, message, context)
            if response_data:
                print(f"Response: {response_data['response']}")
                print(f"Detected Context: {response_data['context']}")
                print(f"Applied Tone: {response_data['applied_tone']}")
                print(f"Context Confidence: {response_data['context_confidence']}")
    
    print("\n3. Testing Memory Management...")
    
    # Send multiple messages to build memory
    for i in range(3):
        send_chat_message(formal_user, f"Test message {i+1}", "work")
        time.sleep(0.1)
    
    # Get memory summary
    memory = get_memory_summary(formal_user)
    if memory:
        print(f"Short-term memory count: {memory['short_term_count']}")
        print(f"Long-term memory size: {memory['long_term_size_kb']:.2f} KB")
    
    print("\n4. Testing Feedback Learning...")
    
    # Submit some feedback
    submit_feedback(
        formal_user,
        "rating",
        value=4.5,
        context="work"
    )
    
    submit_feedback(
        casual_user,
        "correction",
        corrections={
            "formality": -0.1,
            "enthusiasm": 0.1
        },
        context="personal"
    )
    
    # Send another message to see if feedback affected the response
    print("\nSending follow-up message after feedback...")
    response_data = send_chat_message(formal_user, "Another work question", "work")
    if response_data:
        print(f"Response after feedback: {response_data['response']}")

def demo_advanced_features():
    """Demonstrate advanced features"""
    print("\n🔧 Advanced Features Demo")
    print("=" * 30)
    
    # Create academic user
    academic_user = "academic_user"
    create_user_profile(
        academic_user,
        {
            "formality": "formal",
            "enthusiasm": "medium",
            "verbosity": "detailed",
            "empathy_level": "medium",
            "humor": "light"
        },
        {
            "preferred_greeting": "Good day",
            "technical_level": "advanced",
            "cultural_context": "Academic",
            "age_group": "adult"
        },
        {
            "total_interactions": 0,
            "successful_tone_matches": 0,
            "feedback_score": 0.0,
            "last_interaction": None
        },
        {
            "academic": {
                "formality": "formal",
                "enthusiasm": "low",
                "verbosity": "detailed",
                "empathy_level": "low",
                "humor": "none"
            }
        }
    )
    
    # Test academic context
    academic_messages = [
        "I need to finish my research paper for the conference",
        "Can you help me understand this methodology?",
        "What do you think about this statistical analysis?"
    ]
    
    print("\nTesting Academic Context...")
    for message in academic_messages:
        response_data = send_chat_message(academic_user, message, "academic")
        if response_data:
            print(f"\nMessage: {message}")
            print(f"Response: {response_data['response']}")
            print(f"Context: {response_data['context']}")
            print(f"Indicators: {response_data['context_indicators']}")

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print("❌ API is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running with:")
        print("   uvicorn main:app --reload")
        return False

if __name__ == "__main__":
    # Check API health first
    if not check_api_health():
        exit(1)
    
    # Run demos
    demo_basic_usage()
    demo_advanced_features()
    
    print("\n🎉 Demo completed!")
    print("\nTo explore the API further:")
    print(f"- Interactive docs: {BASE_URL}/docs")
    print(f"- API documentation: {BASE_URL}/redoc") 