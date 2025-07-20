from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import re
from enum import Enum

class FormalityLevel(str, Enum):
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    FORMAL = "formal"

class EnthusiasmLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class VerbosityLevel(str, Enum):
    CONCISE = "concise"
    BALANCED = "balanced"
    DETAILED = "detailed"

class EmpathyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class HumorLevel(str, Enum):
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"

class TechnicalLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class AgeGroup(str, Enum):
    TEEN = "teen"
    YOUNG_ADULT = "young_adult"
    ADULT = "adult"
    SENIOR = "senior"

class TonePreferences(BaseModel):
    formality: FormalityLevel = Field(default=FormalityLevel.PROFESSIONAL, description="Formality level")
    enthusiasm: EnthusiasmLevel = Field(default=EnthusiasmLevel.MEDIUM, description="Enthusiasm level")
    verbosity: VerbosityLevel = Field(default=VerbosityLevel.BALANCED, description="Verbosity level")
    empathy_level: EmpathyLevel = Field(default=EmpathyLevel.MEDIUM, description="Empathy level")
    humor: HumorLevel = Field(default=HumorLevel.LIGHT, description="Humor level")

class CommunicationStyle(BaseModel):
    preferred_greeting: str = Field(default="Hello", description="User's preferred greeting")
    technical_level: TechnicalLevel = Field(default=TechnicalLevel.INTERMEDIATE, description="Technical expertise level")
    cultural_context: str = Field(default="", description="Cultural context or background")
    age_group: AgeGroup = Field(default=AgeGroup.ADULT, description="User's age group")

class InteractionHistory(BaseModel):
    total_interactions: int = Field(default=0, description="Total number of interactions")
    successful_tone_matches: int = Field(default=0, description="Number of successful tone matches")
    feedback_score: float = Field(default=0.0, ge=0.0, le=5.0, description="Average feedback score")
    last_interaction: Optional[str] = Field(default=None, description="Timestamp of last interaction")

class ContextPreferences(BaseModel):
    work: Optional[TonePreferences] = None
    personal: Optional[TonePreferences] = None
    academic: Optional[TonePreferences] = None

class UserProfile(BaseModel):
    user_id: str
    tone_preferences: TonePreferences
    communication_style: CommunicationStyle
    interaction_history: InteractionHistory
    context_preferences: Optional[ContextPreferences] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ProfileParser:
    def __init__(self):
        self.default_tone_preferences = TonePreferences()
        self.default_communication_style = CommunicationStyle()
        self.default_interaction_history = InteractionHistory()
    
    def parse_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """Parse raw profile data into structured UserProfile"""
        # Extract tone preferences
        tone_prefs_data = profile_data.get('tone_preferences', {})
        
        # Handle both string and enum values
        def get_enum_value(enum_class, value, default):
            if isinstance(value, enum_class):
                return value
            elif isinstance(value, str):
                try:
                    return enum_class(value)
                except ValueError:
                    return default
            return default
        
        tone_prefs = TonePreferences(
            formality=get_enum_value(FormalityLevel, tone_prefs_data.get('formality'), FormalityLevel.PROFESSIONAL),
            enthusiasm=get_enum_value(EnthusiasmLevel, tone_prefs_data.get('enthusiasm'), EnthusiasmLevel.MEDIUM),
            verbosity=get_enum_value(VerbosityLevel, tone_prefs_data.get('verbosity'), VerbosityLevel.BALANCED),
            empathy_level=get_enum_value(EmpathyLevel, tone_prefs_data.get('empathy_level'), EmpathyLevel.MEDIUM),
            humor=get_enum_value(HumorLevel, tone_prefs_data.get('humor'), HumorLevel.LIGHT)
        )
        
        # Extract communication style
        comm_style_data = profile_data.get('communication_style', {})
        comm_style = CommunicationStyle(
            preferred_greeting=comm_style_data.get('preferred_greeting', 'Hello'),
            technical_level=get_enum_value(TechnicalLevel, comm_style_data.get('technical_level'), TechnicalLevel.INTERMEDIATE),
            cultural_context=comm_style_data.get('cultural_context', ''),
            age_group=get_enum_value(AgeGroup, comm_style_data.get('age_group'), AgeGroup.ADULT)
        )
        
        # Extract interaction history
        history_data = profile_data.get('interaction_history', {})
        interaction_history = InteractionHistory(
            total_interactions=history_data.get('total_interactions', 0),
            successful_tone_matches=history_data.get('successful_tone_matches', 0),
            feedback_score=history_data.get('feedback_score', 0.0),
            last_interaction=history_data.get('last_interaction')
        )
        
        # Extract context-specific preferences
        context_prefs = profile_data.get('context_preferences', {})
        context_preferences = ContextPreferences()
        
        if context_prefs is not None:
            for context in ['work', 'personal', 'academic']:
                if context in context_prefs and context_prefs[context] is not None:
                    context_data = context_prefs[context]
                    context_preferences.__setattr__(context, TonePreferences(
                        formality=get_enum_value(FormalityLevel, context_data.get('formality'), tone_prefs.formality),
                        enthusiasm=get_enum_value(EnthusiasmLevel, context_data.get('enthusiasm'), tone_prefs.enthusiasm),
                        verbosity=get_enum_value(VerbosityLevel, context_data.get('verbosity'), tone_prefs.verbosity),
                        empathy_level=get_enum_value(EmpathyLevel, context_data.get('empathy_level'), tone_prefs.empathy_level),
                        humor=get_enum_value(HumorLevel, context_data.get('humor'), tone_prefs.humor)
                    ))
        
        return UserProfile(
            user_id=profile_data['user_id'],
            tone_preferences=tone_prefs,
            communication_style=comm_style,
            interaction_history=interaction_history,
            context_preferences=context_preferences,
            created_at=profile_data.get('created_at'),
            updated_at=profile_data.get('updated_at')
        )
    
    def get_tone_for_context(self, profile: UserProfile, context: str) -> TonePreferences:
        """Get tone preferences for specific context, falling back to general preferences"""
        if not profile.context_preferences:
            return profile.tone_preferences
        
        context_prefs = getattr(profile.context_preferences, context, None)
        if context_prefs:
            return context_prefs
        
        return profile.tone_preferences
    
    def analyze_text_tone(self, text: str) -> Dict[str, Any]:
        """Analyze the tone of input text to understand user's communication style"""
        text_lower = text.lower()
        
        # Formality indicators
        formal_words = ['therefore', 'consequently', 'furthermore', 'moreover', 'thus', 'hence']
        informal_words = ['hey', 'cool', 'awesome', 'gonna', 'wanna', 'gotta']
        
        formal_count = sum(1 for word in formal_words if word in text_lower)
        informal_count = sum(1 for word in informal_words if word in text_lower)
        
        if formal_count > informal_count:
            formality = FormalityLevel.FORMAL
        elif informal_count > formal_count:
            formality = FormalityLevel.CASUAL
        else:
            formality = FormalityLevel.PROFESSIONAL
        
        # Enthusiasm indicators
        enthusiastic_words = ['amazing', 'fantastic', 'incredible', 'wonderful', 'excellent', 'great']
        neutral_words = ['okay', 'fine', 'alright', 'sure']
        
        enthusiastic_count = sum(1 for word in enthusiastic_words if word in text_lower)
        neutral_count = sum(1 for word in neutral_words if word in text_lower)
        
        if enthusiastic_count > neutral_count:
            enthusiasm = EnthusiasmLevel.HIGH
        elif neutral_count > enthusiastic_count:
            enthusiasm = EnthusiasmLevel.LOW
        else:
            enthusiasm = EnthusiasmLevel.MEDIUM
        
        # Verbosity indicators
        word_count = len(text.split())
        if word_count < 10:
            verbosity = VerbosityLevel.CONCISE
        elif word_count > 50:
            verbosity = VerbosityLevel.DETAILED
        else:
            verbosity = VerbosityLevel.BALANCED
        
        # Empathy indicators
        empathetic_words = ['feel', 'understand', 'sorry', 'hope', 'care', 'concerned']
        empathetic_count = sum(1 for word in empathetic_words if word in text_lower)
        
        if empathetic_count > 2:
            empathy_level = EmpathyLevel.HIGH
        elif empathetic_count > 0:
            empathy_level = EmpathyLevel.MEDIUM
        else:
            empathy_level = EmpathyLevel.LOW
        
        # Humor indicators
        humor_words = ['haha', 'lol', 'funny', 'joke', 'hilarious', '😂', '😄']
        humor_count = sum(1 for word in humor_words if word in text_lower)
        
        if humor_count > 2:
            humor = HumorLevel.HEAVY
        elif humor_count > 0:
            humor = HumorLevel.MODERATE
        else:
            humor = HumorLevel.NONE
        
        return {
            'formality': formality,
            'enthusiasm': enthusiasm,
            'verbosity': verbosity,
            'empathy_level': empathy_level,
            'humor': humor
        }
    
    def update_profile_from_text(self, profile: UserProfile, text: str, context: str = None) -> UserProfile:
        """Update profile based on analyzed text tone"""
        analyzed_tone = self.analyze_text_tone(text)
        
        # Get current preferences for the context
        current_prefs = self.get_tone_for_context(profile, context) if context else profile.tone_preferences
        
        # Update preferences (simple replacement for enum-based system)
        updated_tone_prefs = TonePreferences(
            formality=analyzed_tone['formality'],
            enthusiasm=analyzed_tone['enthusiasm'],
            verbosity=analyzed_tone['verbosity'],
            empathy_level=analyzed_tone['empathy_level'],
            humor=analyzed_tone['humor']
        )
        
        # Update interaction history
        updated_history = InteractionHistory(
            total_interactions=profile.interaction_history.total_interactions + 1,
            successful_tone_matches=profile.interaction_history.successful_tone_matches,
            feedback_score=profile.interaction_history.feedback_score,
            last_interaction=profile.interaction_history.last_interaction
        )
        
        # Create updated profile
        updated_profile = UserProfile(
            user_id=profile.user_id,
            tone_preferences=updated_tone_prefs,
            communication_style=profile.communication_style,
            interaction_history=updated_history,
            context_preferences=profile.context_preferences,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        
        return updated_profile
    
    def validate_profile(self, profile_data: Dict[str, Any]) -> bool:
        """Validate profile data structure and values"""
        try:
            # Check required fields
            if 'user_id' not in profile_data:
                return False
            
            if 'tone_preferences' not in profile_data:
                return False
            
            # Validate tone preferences
            tone_prefs = profile_data['tone_preferences']
            valid_formality = ['casual', 'professional', 'formal']
            valid_enthusiasm = ['low', 'medium', 'high']
            valid_verbosity = ['concise', 'balanced', 'detailed']
            valid_empathy = ['low', 'medium', 'high']
            valid_humor = ['none', 'light', 'moderate', 'heavy']
            
            if 'formality' in tone_prefs and tone_prefs['formality'] not in valid_formality:
                return False
            if 'enthusiasm' in tone_prefs and tone_prefs['enthusiasm'] not in valid_enthusiasm:
                return False
            if 'verbosity' in tone_prefs and tone_prefs['verbosity'] not in valid_verbosity:
                return False
            if 'empathy_level' in tone_prefs and tone_prefs['empathy_level'] not in valid_empathy:
                return False
            if 'humor' in tone_prefs and tone_prefs['humor'] not in valid_humor:
                return False
            
            # Validate communication style if present
            if 'communication_style' in profile_data:
                comm_style = profile_data['communication_style']
                valid_technical = ['beginner', 'intermediate', 'advanced']
                valid_age_groups = ['teen', 'young_adult', 'adult', 'senior']
                
                if 'technical_level' in comm_style and comm_style['technical_level'] not in valid_technical:
                    return False
                if 'age_group' in comm_style and comm_style['age_group'] not in valid_age_groups:
                    return False
            
            # Validate interaction history if present
            if 'interaction_history' in profile_data:
                history = profile_data['interaction_history']
                if 'feedback_score' in history:
                    score = history['feedback_score']
                    if not isinstance(score, (int, float)) or score < 0 or score > 5:
                        return False
            
            return True
            
        except Exception:
            return False 