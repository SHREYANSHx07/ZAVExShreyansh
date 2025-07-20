from typing import Dict, Any, Optional
from core.profile_parser import UserProfile, TonePreferences
import time

class FeedbackProcessor:
    def __init__(self):
        self.feedback_history = {}
    
    def process_feedback(self, user_id: str, feedback_data: Dict[str, Any], profile: UserProfile) -> UserProfile:
        """
        Process user feedback and update profile accordingly
        """
        feedback_type = feedback_data.get('type', 'rating')
        
        if feedback_type == 'rating':
            return self._process_rating_feedback(user_id, feedback_data, profile)
        elif feedback_type == 'correction':
            return self._process_correction_feedback(user_id, feedback_data, profile)
        elif feedback_type == 'preference':
            return self._process_preference_feedback(user_id, feedback_data, profile)
        else:
            return profile
    
    def _process_rating_feedback(self, user_id: str, feedback_data: Dict[str, Any], profile: UserProfile) -> UserProfile:
        """
        Process rating-based feedback (1-5 scale)
        """
        rating = feedback_data.get('value', 3.0)
        context = feedback_data.get('context', 'general')
        
        # Update interaction history
        profile.interaction_history.total_interactions += 1
        profile.interaction_history.last_interaction = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # If rating is high (4-5), consider it a successful tone match
        if rating >= 4.0:
            profile.interaction_history.successful_tone_matches += 1
        
        # Update average feedback score
        current_score = profile.interaction_history.feedback_score
        total_interactions = profile.interaction_history.total_interactions
        new_score = ((current_score * (total_interactions - 1)) + rating) / total_interactions
        profile.interaction_history.feedback_score = new_score
        
        # Store feedback in history
        if user_id not in self.feedback_history:
            self.feedback_history[user_id] = []
        
        self.feedback_history[user_id].append({
            'type': 'rating',
            'value': rating,
            'context': context,
            'timestamp': time.time()
        })
        
        return profile
    
    def _process_correction_feedback(self, user_id: str, feedback_data: Dict[str, Any], profile: UserProfile) -> UserProfile:
        """
        Process correction-based feedback (specific tone adjustments)
        """
        corrections = feedback_data.get('corrections', {})
        context = feedback_data.get('context', 'general')
        
        # Update interaction history
        profile.interaction_history.total_interactions += 1
        profile.interaction_history.last_interaction = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Apply corrections to tone preferences
        for tone_aspect, adjustment in corrections.items():
            if hasattr(profile.tone_preferences, tone_aspect):
                current_value = getattr(profile.tone_preferences, tone_aspect)
                # Convert enum to numeric for adjustment, then back to enum
                if tone_aspect == 'formality':
                    current_numeric = self._enum_to_numeric(current_value, 'formality')
                    new_numeric = max(0.0, min(1.0, current_numeric + adjustment))
                    setattr(profile.tone_preferences, tone_aspect, self._numeric_to_enum(new_numeric, 'formality'))
                elif tone_aspect == 'enthusiasm':
                    current_numeric = self._enum_to_numeric(current_value, 'enthusiasm')
                    new_numeric = max(0.0, min(1.0, current_numeric + adjustment))
                    setattr(profile.tone_preferences, tone_aspect, self._numeric_to_enum(new_numeric, 'enthusiasm'))
                elif tone_aspect == 'verbosity':
                    current_numeric = self._enum_to_numeric(current_value, 'verbosity')
                    new_numeric = max(0.0, min(1.0, current_numeric + adjustment))
                    setattr(profile.tone_preferences, tone_aspect, self._numeric_to_enum(new_numeric, 'verbosity'))
                elif tone_aspect == 'empathy_level':
                    current_numeric = self._enum_to_numeric(current_value, 'empathy')
                    new_numeric = max(0.0, min(1.0, current_numeric + adjustment))
                    setattr(profile.tone_preferences, tone_aspect, self._numeric_to_enum(new_numeric, 'empathy'))
                elif tone_aspect == 'humor':
                    current_numeric = self._enum_to_numeric(current_value, 'humor')
                    new_numeric = max(0.0, min(1.0, current_numeric + adjustment))
                    setattr(profile.tone_preferences, tone_aspect, self._numeric_to_enum(new_numeric, 'humor'))
        
        # Store feedback in history
        if user_id not in self.feedback_history:
            self.feedback_history[user_id] = []
        
        self.feedback_history[user_id].append({
            'type': 'correction',
            'corrections': corrections,
            'context': context,
            'timestamp': time.time()
        })
        
        return profile
    
    def _process_preference_feedback(self, user_id: str, feedback_data: Dict[str, Any], profile: UserProfile) -> UserProfile:
        """
        Process direct preference updates
        """
        preferences = feedback_data.get('preferences', {})
        context = feedback_data.get('context', 'general')
        
        # Update interaction history
        profile.interaction_history.total_interactions += 1
        profile.interaction_history.last_interaction = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Apply direct preference updates
        for tone_aspect, value in preferences.items():
            if hasattr(profile.tone_preferences, tone_aspect):
                if tone_aspect == 'formality':
                    setattr(profile.tone_preferences, tone_aspect, self._numeric_to_enum(value, 'formality'))
                elif tone_aspect == 'enthusiasm':
                    setattr(profile.tone_preferences, tone_aspect, self._numeric_to_enum(value, 'enthusiasm'))
                elif tone_aspect == 'verbosity':
                    setattr(profile.tone_preferences, tone_aspect, self._numeric_to_enum(value, 'verbosity'))
                elif tone_aspect == 'empathy_level':
                    setattr(profile.tone_preferences, tone_aspect, self._numeric_to_enum(value, 'empathy'))
                elif tone_aspect == 'humor':
                    setattr(profile.tone_preferences, tone_aspect, self._numeric_to_enum(value, 'humor'))
        
        # Store feedback in history
        if user_id not in self.feedback_history:
            self.feedback_history[user_id] = []
        
        self.feedback_history[user_id].append({
            'type': 'preference',
            'preferences': preferences,
            'context': context,
            'timestamp': time.time()
        })
        
        return profile
    
    def _enum_to_numeric(self, enum_value, tone_type):
        """Convert enum value to numeric (0.0-1.0)"""
        if tone_type == 'formality':
            mapping = {'casual': 0.0, 'professional': 0.5, 'formal': 1.0}
        elif tone_type == 'enthusiasm':
            mapping = {'low': 0.0, 'medium': 0.5, 'high': 1.0}
        elif tone_type == 'verbosity':
            mapping = {'concise': 0.0, 'balanced': 0.5, 'detailed': 1.0}
        elif tone_type == 'empathy':
            mapping = {'low': 0.0, 'medium': 0.5, 'high': 1.0}
        elif tone_type == 'humor':
            mapping = {'none': 0.0, 'light': 0.33, 'moderate': 0.66, 'heavy': 1.0}
        else:
            return 0.5
        
        return mapping.get(str(enum_value), 0.5)
    
    def _numeric_to_enum(self, numeric_value, tone_type):
        """Convert numeric value (0.0-1.0) to enum"""
        if tone_type == 'formality':
            if numeric_value < 0.33:
                return 'casual'
            elif numeric_value < 0.66:
                return 'professional'
            else:
                return 'formal'
        elif tone_type == 'enthusiasm':
            if numeric_value < 0.33:
                return 'low'
            elif numeric_value < 0.66:
                return 'medium'
            else:
                return 'high'
        elif tone_type == 'verbosity':
            if numeric_value < 0.33:
                return 'concise'
            elif numeric_value < 0.66:
                return 'balanced'
            else:
                return 'detailed'
        elif tone_type == 'empathy':
            if numeric_value < 0.33:
                return 'low'
            elif numeric_value < 0.66:
                return 'medium'
            else:
                return 'high'
        elif tone_type == 'humor':
            if numeric_value < 0.25:
                return 'none'
            elif numeric_value < 0.5:
                return 'light'
            elif numeric_value < 0.75:
                return 'moderate'
            else:
                return 'heavy'
        else:
            return 'medium'
    
    def get_feedback_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get feedback summary for a user
        """
        if user_id not in self.feedback_history:
            return {
                'total_feedback': 0,
                'feedback_types': {},
                'recent_feedback': []
            }
        
        feedback_list = self.feedback_history[user_id]
        
        # Count feedback types
        feedback_types = {}
        for feedback in feedback_list:
            feedback_type = feedback['type']
            feedback_types[feedback_type] = feedback_types.get(feedback_type, 0) + 1
        
        # Get recent feedback (last 10)
        recent_feedback = sorted(feedback_list, key=lambda x: x['timestamp'], reverse=True)[:10]
        
        return {
            'total_feedback': len(feedback_list),
            'feedback_types': feedback_types,
            'recent_feedback': recent_feedback
        } 