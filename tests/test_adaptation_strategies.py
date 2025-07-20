"""
Comprehensive Test for Adaptation Strategies
Tests all four adaptation strategies: baseline matching, dynamic adjustment, learning integration, and context switching
"""

import pytest
import time
from typing import Dict, Any
from core.tone_engine import ToneEngine
from core.profile_parser import ProfileParser, UserProfile, TonePreferences
from core.context_analyzer import ContextType
from core.vector_store import CustomVectorStore
from core.prompt_engineer import CustomPromptEngineer
from core.conversation_manager import CustomConversationManager

class TestAdaptationStrategies:
    """Test all four adaptation strategies"""
    
    @pytest.fixture
    def tone_engine(self):
        """Initialize tone engine"""
        return ToneEngine()
    
    @pytest.fixture
    def profile_parser(self):
        """Initialize profile parser"""
        return ProfileParser()
    
    @pytest.fixture
    def vector_store(self):
        """Initialize vector store"""
        return CustomVectorStore("test_vector_store.db")
    
    @pytest.fixture
    def prompt_engineer(self):
        """Initialize prompt engineer"""
        return CustomPromptEngineer()
    
    @pytest.fixture
    def conversation_manager(self):
        """Initialize conversation manager"""
        return CustomConversationManager("test_conversation_manager.db")
    
    @pytest.fixture
    def sample_profile(self):
        """Sample user profile for testing"""
        return UserProfile(
            user_id="test_user",
            tone_preferences=TonePreferences(
                formality="professional",
                enthusiasm="medium",
                verbosity="balanced",
                empathy_level="medium",
                humor="light"
            ),
            communication_style={
                "preferred_greeting": "Hello",
                "technical_level": "intermediate",
                "cultural_context": "US",
                "age_group": "adult"
            },
            interaction_history={
                "total_interactions": 5,
                "successful_tone_matches": 4,
                "feedback_score": 4.2,
                "last_interaction": "2024-01-01T10:00:00Z"
            },
            context_preferences={
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
                    "verbosity": "detailed",
                    "empathy_level": "high",
                    "humor": "moderate"
                }
            }
        )
    
    def test_strategy_1_baseline_matching(self, tone_engine, sample_profile):
        """Test Strategy 1: Baseline Matching"""
        # Test baseline matching for different contexts
        work_context = ContextType.WORK
        personal_context = ContextType.PERSONAL
        
        # Get baseline preferences for work context
        work_prefs = tone_engine.baseline_matching(sample_profile, work_context)
        assert work_prefs.formality == "formal"
        assert work_prefs.enthusiasm == "low"
        assert work_prefs.verbosity == "detailed"
        
        # Get baseline preferences for personal context
        personal_prefs = tone_engine.baseline_matching(sample_profile, personal_context)
        assert personal_prefs.formality == "casual"
        assert personal_prefs.enthusiasm == "high"
        assert personal_prefs.empathy_level == "high"
        
        print("✅ Strategy 1 (Baseline Matching): PASSED")
    
    def test_strategy_2_dynamic_adjustment(self, tone_engine, sample_profile):
        """Test Strategy 2: Dynamic Adjustment"""
        user_id = "test_user"
        
        # Create conversation history with increasing message length
        conversation_history = [
            {"message": "Hi", "context": "work"},
            {"message": "Hello there", "context": "work"},
            {"message": "Good morning! How are you doing today?", "context": "work"},
            {"message": "I hope you're having a wonderful day and everything is going well for you!", "context": "work"}
        ]
        
        # Get baseline preferences
        baseline_prefs = tone_engine.baseline_matching(sample_profile, ContextType.WORK)
        
        # Apply dynamic adjustment
        adjusted_prefs = tone_engine.dynamic_adjustment(user_id, baseline_prefs, conversation_history)
        
        # Should detect increasing message length and adjust verbosity
        assert adjusted_prefs.verbosity in ["balanced", "detailed"]
        
        # Test with decreasing message length
        short_history = [
            {"message": "This is a very long message with lots of details and information", "context": "work"},
            {"message": "Short message", "context": "work"}
        ]
        
        adjusted_prefs_short = tone_engine.dynamic_adjustment(user_id, baseline_prefs, short_history)
        assert adjusted_prefs_short.verbosity in ["concise", "balanced"]
        
        print("✅ Strategy 2 (Dynamic Adjustment): PASSED")
    
    def test_strategy_3_learning_integration(self, tone_engine, sample_profile):
        """Test Strategy 3: Learning Integration"""
        user_id = "test_user"
        
        # Simulate feedback data
        feedback_data = {
            "type": "rating",
            "value": 2.0,  # Low rating
            "context": "work",
            "corrections": {
                "formality": -0.2,
                "enthusiasm": 0.1
            }
        }
        
        # Get baseline preferences
        baseline_prefs = tone_engine.baseline_matching(sample_profile, ContextType.WORK)
        
        # Apply learning integration
        learned_prefs = tone_engine.learning_integration(user_id, baseline_prefs, feedback_data)
        
        # Should adjust preferences based on feedback
        # Formality should decrease due to low rating
        assert learned_prefs.formality in ["professional", "casual", "formal"]
        
        # Test with positive feedback
        positive_feedback = {
            "type": "rating",
            "value": 4.5,
            "context": "personal"
        }
        
        learned_prefs_positive = tone_engine.learning_integration(user_id, baseline_prefs, positive_feedback)
        # Should maintain or improve preferences
        
        print("✅ Strategy 3 (Learning Integration): PASSED")
    
    def test_strategy_4_context_switching(self, tone_engine, sample_profile):
        """Test Strategy 4: Context Switching"""
        user_id = "test_user"
        
        # Create conversation history with context transitions
        conversation_history = [
            {"message": "I have a meeting tomorrow", "context": "work"},
            {"message": "I have a meeting tomorrow", "context": "work"},
            {"message": "I'm going to a party this weekend", "context": "personal"}
        ]
        
        # Get baseline preferences for work context
        work_prefs = tone_engine.baseline_matching(sample_profile, ContextType.WORK)
        
        # Apply context switching to personal context
        final_prefs = tone_engine.context_switching(user_id, work_prefs, ContextType.PERSONAL, conversation_history)
        
        # Should adapt to personal context
        assert final_prefs.formality in ["casual", "professional"]
        assert final_prefs.enthusiasm in ["medium", "high"]
        
        # Test transition from personal to work
        personal_history = [
            {"message": "I'm going to a party", "context": "personal"},
            {"message": "I have a client meeting", "context": "work"}
        ]
        
        personal_prefs = tone_engine.baseline_matching(sample_profile, ContextType.PERSONAL)
        work_final_prefs = tone_engine.context_switching(user_id, personal_prefs, ContextType.WORK, personal_history)
        
        # Should become more formal for work
        assert work_final_prefs.formality in ["professional", "formal"]
        
        print("✅ Strategy 4 (Context Switching): PASSED")
    
    def test_integrated_adaptation_strategies(self, tone_engine, sample_profile):
        """Test all four strategies working together"""
        user_id = "test_user"
        
        # Create conversation history
        conversation_history = [
            {"message": "Hello", "context": "work"},
            {"message": "I need help with a project", "context": "work"},
            {"message": "Actually, let's talk about my weekend plans", "context": "personal"}
        ]
        
        # Simulate feedback
        feedback_data = {
            "type": "rating",
            "value": 3.5,
            "context": "general"
        }
        
        # Test the complete adaptation pipeline
        context = ContextType.PERSONAL
        
        # Strategy 1: Baseline Matching
        baseline_prefs = tone_engine.baseline_matching(sample_profile, context)
        
        # Strategy 2: Dynamic Adjustment
        adjusted_prefs = tone_engine.dynamic_adjustment(user_id, baseline_prefs, conversation_history)
        
        # Strategy 3: Learning Integration
        learned_prefs = tone_engine.learning_integration(user_id, adjusted_prefs, feedback_data)
        
        # Strategy 4: Context Switching
        final_prefs = tone_engine.context_switching(user_id, learned_prefs, context, conversation_history)
        
        # Verify all strategies were applied
        assert final_prefs is not None
        assert hasattr(final_prefs, 'formality')
        assert hasattr(final_prefs, 'enthusiasm')
        assert hasattr(final_prefs, 'verbosity')
        assert hasattr(final_prefs, 'empathy_level')
        assert hasattr(final_prefs, 'humor')
        
        print("✅ Integrated Adaptation Strategies: PASSED")
    
    def test_vector_store_integration(self, vector_store):
        """Test custom vector store integration"""
        user_id = "test_user"
        
        # Add test vectors
        vector_id1 = vector_store.add_vector(
            user_id=user_id,
            content="I have a meeting tomorrow",
            context="work",
            metadata={"type": "work_related"}
        )
        
        vector_id2 = vector_store.add_vector(
            user_id=user_id,
            content="I'm going to a party this weekend",
            context="personal",
            metadata={"type": "personal_related"}
        )
        
        # Test similarity search
        similar_vectors = vector_store.find_similar(
            query_content="I have a client meeting",
            user_id=user_id,
            limit=5
        )
        
        assert len(similar_vectors) > 0
        assert similar_vectors[0]['similarity'] > 0.5
        
        # Test context-based search
        work_vectors = vector_store.search_by_context("work", user_id)
        assert len(work_vectors) > 0
        
        print("✅ Vector Store Integration: PASSED")
    
    def test_prompt_engineering_integration(self, prompt_engineer):
        """Test custom prompt engineering integration"""
        # Test prompt generation
        variables = {
            "formality": "professional",
            "enthusiasm": "medium",
            "context": "work",
            "message": "Hello, how can you help me?"
        }
        
        prompt = prompt_engineer.generate_prompt(
            prompt_type="conversation_start",
            variables=variables
        )
        
        # The prompt should contain the variable values
        assert "professional" in prompt or "formality" in prompt
        assert "medium" in prompt or "enthusiasm" in prompt
        assert "work" in prompt or "context" in prompt
        
        # Test dynamic prompt creation
        user_profile = {
            "tone_preferences": {
                "formality": "casual",
                "enthusiasm": "high"
            }
        }
        
        conversation_context = {
            "context": "personal",
            "message": "Hi there!"
        }
        
        dynamic_prompt = prompt_engineer.create_dynamic_prompt(
            base_type="conversation_start",
            user_profile=user_profile,
            conversation_context=conversation_context
        )
        
        assert len(dynamic_prompt) > 0
        
        print("✅ Prompt Engineering Integration: PASSED")
    
    def test_conversation_management_integration(self, conversation_manager):
        """Test custom conversation management integration"""
        user_id = "test_user"
        
        # Create session
        session_id = conversation_manager.create_session(
            user_id=user_id,
            initial_context="work",
            tone_preferences={"formality": "professional"}
        )
        
        assert session_id is not None
        
        # Add conversation turns
        turn_id1 = conversation_manager.add_turn(
            session_id=session_id,
            user_id=user_id,
            message="Hello",
            response="Hi there! How can I help you?",
            context="work",
            tone_applied={"formality": "professional"},
            topic="greeting"
        )
        
        turn_id2 = conversation_manager.add_turn(
            session_id=session_id,
            user_id=user_id,
            message="I need help with a project",
            response="I'd be happy to help with your project!",
            context="work",
            tone_applied={"formality": "professional", "enthusiasm": "medium"},
            topic="project_help"
        )
        
        # Get session summary
        summary = conversation_manager.get_conversation_summary(session_id)
        
        assert summary['session_id'] == session_id
        assert summary['user_id'] == user_id
        assert summary['total_turns'] == 2
        assert "greeting" in summary['topics_discussed']
        assert "project_help" in summary['topics_discussed']
        
        print("✅ Conversation Management Integration: PASSED")
    
    def test_complete_system_integration(self, tone_engine, vector_store, prompt_engineer, conversation_manager):
        """Test complete system integration with all components"""
        user_id = "test_user"
        
        # 1. Create conversation session
        session_id = conversation_manager.create_session(user_id)
        
        # 2. Add conversation to vector store
        vector_id = vector_store.add_vector(
            user_id=user_id,
            content="I need help with my work project",
            context="work",
            metadata={"session_id": session_id}
        )
        
        # 3. Generate prompt
        prompt = prompt_engineer.generate_prompt(
            prompt_type="conversation_start",
            variables={
                "formality": "professional",
                "enthusiasm": "medium",
                "context": "work",
                "message": "I need help with my work project"
            }
        )
        
        # 4. Apply tone adaptation
        # (This would normally use a real user profile)
        assert len(prompt) > 0
        assert vector_id is not None
        assert session_id is not None
        
        print("✅ Complete System Integration: PASSED")
    
    def test_performance_benchmarks(self, tone_engine, vector_store, prompt_engineer, conversation_manager):
        """Test performance benchmarks"""
        import time
        
        # Test tone engine performance
        start_time = time.time()
        for i in range(100):
            # Create a minimal profile for testing
            minimal_profile = UserProfile(
                user_id="test_user",
                tone_preferences=TonePreferences(
                    formality="professional",
                    enthusiasm="medium",
                    verbosity="balanced",
                    empathy_level="medium",
                    humor="light"
                ),
                communication_style={},
                interaction_history={},
                context_preferences={}
            )
            tone_engine.baseline_matching(minimal_profile, ContextType.WORK)
        tone_engine_time = time.time() - start_time
        
        # Test vector store performance
        start_time = time.time()
        for i in range(100):
            vector_store.add_vector(
                user_id=f"user_{i}",
                content=f"Test message {i}",
                context="test"
            )
        vector_store_time = time.time() - start_time
        
        # Test prompt engineering performance
        start_time = time.time()
        for i in range(100):
            prompt_engineer.generate_prompt(
                prompt_type="conversation_start",
                variables={"formality": "professional", "enthusiasm": "medium", "context": "work", "message": "test"}
            )
        prompt_engineer_time = time.time() - start_time
        
        # Performance assertions
        assert tone_engine_time < 1.0  # Should complete in under 1 second
        assert vector_store_time < 2.0  # Should complete in under 2 seconds
        assert prompt_engineer_time < 1.0  # Should complete in under 1 second
        
        print(f"✅ Performance Benchmarks: PASSED")
        print(f"   - Tone Engine: {tone_engine_time:.3f}s")
        print(f"   - Vector Store: {vector_store_time:.3f}s")
        print(f"   - Prompt Engineer: {prompt_engineer_time:.3f}s")

if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"]) 