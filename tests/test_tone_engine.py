import pytest
from core.tone_engine import ToneEngine
from core.profile_parser import UserProfile, TonePreferences, ContextPreferences

class TestToneEngine:
    @pytest.fixture
    def tone_engine(self):
        """Create a tone engine instance"""
        return ToneEngine()
    
    @pytest.fixture
    def sample_profile(self):
        """Create a sample user profile"""
        preferences = TonePreferences(
            formality=0.7,
            enthusiasm=0.8,
            verbosity=0.6,
            empathy=0.9,
            humor=0.4
        )
        
        context_preferences = ContextPreferences()
        context_preferences.work = TonePreferences(
            formality=0.9,
            enthusiasm=0.5,
            verbosity=0.7,
            empathy=0.8,
            humor=0.2
        )
        context_preferences.personal = TonePreferences(
            formality=0.3,
            enthusiasm=0.9,
            verbosity=0.5,
            empathy=0.9,
            humor=0.6
        )
        
        return UserProfile(
            user_id="test_user",
            preferences=preferences,
            context_preferences=context_preferences
        )
    
    def test_context_analysis(self, tone_engine):
        """Test context analysis functionality"""
        # Test work context
        work_message = "I have a meeting with the client tomorrow at 2pm"
        context = tone_engine.context_analyzer.analyze_context(work_message)
        assert context.value == "work"
        
        # Test personal context
        personal_message = "I'm going to a birthday party this weekend"
        context = tone_engine.context_analyzer.analyze_context(personal_message)
        assert context.value == "personal"
        
        # Test academic context
        academic_message = "I need to finish my research paper for the conference"
        context = tone_engine.context_analyzer.analyze_context(academic_message)
        assert context.value == "academic"
        
        # Test unknown context
        unknown_message = "Hello there"
        context = tone_engine.context_analyzer.analyze_context(unknown_message)
        assert context.value == "unknown"
    
    def test_tone_adaptation(self, tone_engine, sample_profile):
        """Test tone adaptation functionality"""
        base_response = "Hello! How can I help you today?"
        
        # Test work context adaptation
        from core.context_analyzer import ContextType
        adapted_response = tone_engine.adapt_response(
            base_response, sample_profile, ContextType.WORK
        )
        
        # Should be more formal for work context
        assert "Hello" in adapted_response or "Good" in adapted_response
        
        # Test personal context adaptation
        adapted_response = tone_engine.adapt_response(
            base_response, sample_profile, ContextType.PERSONAL
        )
        
        # Should be more casual for personal context
        assert len(adapted_response) > len(base_response)  # Should have some adaptation
    
    def test_formality_adaptation(self, tone_engine):
        """Test formality adaptation specifically"""
        base_response = "Hi there! How are you doing?"
        
        # Create profiles with different formality levels
        high_formal_profile = UserProfile(
            user_id="formal_user",
            preferences=TonePreferences(
                formality=0.9,
                enthusiasm=0.5,
                verbosity=0.5,
                empathy=0.5,
                humor=0.3
            )
        )
        
        low_formal_profile = UserProfile(
            user_id="casual_user",
            preferences=TonePreferences(
                formality=0.2,
                enthusiasm=0.5,
                verbosity=0.5,
                empathy=0.5,
                humor=0.3
            )
        )
        
        from core.context_analyzer import ContextType
        
        # Test high formality
        formal_response = tone_engine.adapt_response(
            base_response, high_formal_profile, ContextType.WORK
        )
        
        # Test low formality
        casual_response = tone_engine.adapt_response(
            base_response, low_formal_profile, ContextType.PERSONAL
        )
        
        # Responses should be different
        assert formal_response != casual_response
    
    def test_enthusiasm_adaptation(self, tone_engine):
        """Test enthusiasm adaptation specifically"""
        base_response = "That's a great idea"
        
        # Create profiles with different enthusiasm levels
        high_enthusiasm_profile = UserProfile(
            user_id="enthusiastic_user",
            preferences=TonePreferences(
                formality=0.5,
                enthusiasm=0.9,
                verbosity=0.5,
                empathy=0.5,
                humor=0.3
            )
        )
        
        low_enthusiasm_profile = UserProfile(
            user_id="calm_user",
            preferences=TonePreferences(
                formality=0.5,
                enthusiasm=0.2,
                verbosity=0.5,
                empathy=0.5,
                humor=0.3
            )
        )
        
        from core.context_analyzer import ContextType
        
        # Test high enthusiasm
        enthusiastic_response = tone_engine.adapt_response(
            base_response, high_enthusiasm_profile, ContextType.PERSONAL
        )
        
        # Test low enthusiasm
        calm_response = tone_engine.adapt_response(
            base_response, low_enthusiasm_profile, ContextType.WORK
        )
        
        # Responses should be different
        assert enthusiastic_response != calm_response
    
    def test_generate_response_with_tone(self, tone_engine, sample_profile):
        """Test complete response generation with tone adaptation"""
        user_message = "Hello, I need help with my project"
        
        response_data = tone_engine.generate_response_with_tone(
            user_message, sample_profile
        )
        
        # Check response structure
        assert "response" in response_data
        assert "context" in response_data
        assert "context_confidence" in response_data
        assert "context_indicators" in response_data
        assert "applied_tone" in response_data
        assert "base_response" in response_data
        
        # Check that response is not empty
        assert len(response_data["response"]) > 0
        
        # Check context analysis
        assert response_data["context"] in ["work", "personal", "academic", "unknown"]
        
        # Check tone levels
        assert "formality" in response_data["applied_tone"]
        assert "enthusiasm" in response_data["applied_tone"]
        assert "verbosity" in response_data["applied_tone"]
        assert "empathy" in response_data["applied_tone"]
        assert "humor" in response_data["applied_tone"]
    
    def test_context_confidence(self, tone_engine):
        """Test context confidence calculation"""
        work_message = "I have a meeting with the team about the quarterly report"
        
        confidence = tone_engine.context_analyzer.get_context_confidence(work_message)
        
        assert "work" in confidence
        assert "personal" in confidence
        assert "academic" in confidence
        assert "unknown" in confidence
        
        # Work confidence should be highest for work-related message
        assert confidence["work"] > confidence["personal"]
        assert confidence["work"] > confidence["academic"]
    
    def test_context_indicators(self, tone_engine):
        """Test context indicator extraction"""
        work_message = "I need to schedule a meeting with the client and prepare the presentation"
        
        indicators = tone_engine.context_analyzer.extract_context_indicators(work_message)
        
        assert "work" in indicators
        assert "personal" in indicators
        assert "academic" in indicators
        
        # Should find work-related indicators
        assert len(indicators["work"]) > 0
        assert "meeting" in indicators["work"] or "client" in indicators["work"] or "presentation" in indicators["work"]
    
    def test_tone_level_conversion(self, tone_engine):
        """Test conversion of numeric values to tone levels"""
        assert tone_engine._get_tone_level(0.1) == "low"
        assert tone_engine._get_tone_level(0.5) == "medium"
        assert tone_engine._get_tone_level(0.9) == "high"
    
    def test_conversation_history_integration(self, tone_engine, sample_profile):
        """Test integration with conversation history"""
        user_message = "How are you doing?"
        
        # No history
        response_no_history = tone_engine.generate_response_with_tone(
            user_message, sample_profile, []
        )
        
        # With work history
        work_history = [
            {"message": "I have a meeting tomorrow", "context": "work"},
            {"message": "Need to prepare the report", "context": "work"}
        ]
        response_with_history = tone_engine.generate_response_with_tone(
            user_message, sample_profile, work_history
        )
        
        # Both should generate responses
        assert len(response_no_history["response"]) > 0
        assert len(response_with_history["response"]) > 0 