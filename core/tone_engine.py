from typing import Dict, Any, List, Optional
from .profile_parser import TonePreferences, UserProfile
from .context_analyzer import ContextType, ContextAnalyzer
import re
import random
import time
from collections import deque

class ToneEngine:
    def __init__(self):
        self.context_analyzer = ContextAnalyzer()
        
        # Conversation flow tracking for dynamic adjustment
        self.conversation_flows = {}  # user_id -> deque of recent exchanges
        self.context_transitions = {}  # user_id -> list of context changes
        self.tone_effectiveness = {}  # user_id -> dict of tone effectiveness scores
        
        # Learning integration data
        self.feedback_learning = {}  # user_id -> list of feedback data
        self.adaptive_preferences = {}  # user_id -> dynamically adjusted preferences
        
        # Context switching tracking
        self.context_history = {}  # user_id -> list of context changes
        self.topic_transitions = {}  # user_id -> list of topic transitions
        
        # Tone adaptation templates and patterns
        self.formality_patterns = {
            'formal': {
                'greetings': ['Good morning', 'Good afternoon', 'Good evening', 'Greetings'],
                'farewells': ['Best regards', 'Sincerely', 'Yours truly', 'Respectfully'],
                'transitions': ['Furthermore', 'Moreover', 'Additionally', 'Consequently'],
                'acknowledgments': ['I understand', 'I comprehend', 'I acknowledge', 'I recognize']
            },
            'professional': {
                'greetings': ['Hello', 'Hi there', 'Good day', 'Greetings'],
                'farewells': ['Regards', 'Best wishes', 'Take care', 'See you'],
                'transitions': ['Also', 'Additionally', 'Furthermore', 'Moreover'],
                'acknowledgments': ['I see', 'I understand', 'Got it', 'I know']
            },
            'casual': {
                'greetings': ['Hey', 'Hi', 'Yo', 'What\'s up'],
                'farewells': ['Bye', 'See ya', 'Take care', 'Later'],
                'transitions': ['Also', 'Plus', 'And', 'Besides'],
                'acknowledgments': ['Got it', 'I see', 'Cool', 'Sure']
            }
        }
        
        self.enthusiasm_patterns = {
            'high': {
                'exclamations': ['!', '!!', '!!!'],
                'intensifiers': ['absolutely', 'definitely', 'certainly', 'without a doubt'],
                'positive_words': ['amazing', 'fantastic', 'incredible', 'wonderful', 'excellent'],
                'emojis': ['😊', '🎉', '✨', '👍', '💯']
            },
            'medium': {
                'exclamations': ['!'],
                'intensifiers': ['really', 'quite', 'pretty', 'fairly'],
                'positive_words': ['good', 'nice', 'great', 'fine', 'okay'],
                'emojis': ['😊', '👍']
            },
            'low': {
                'exclamations': [],
                'intensifiers': ['somewhat', 'kind of', 'sort of', 'maybe'],
                'positive_words': ['okay', 'fine', 'alright', 'sure'],
                'emojis': []
            }
        }
        
        self.verbosity_patterns = {
            'detailed': {
                'explanations': ['Let me explain in detail', 'I want to make sure you understand', 'To be more specific'],
                'examples': ['For example', 'To illustrate this point', 'As an example'],
                'clarifications': ['What I mean is', 'To clarify', 'In other words']
            },
            'balanced': {
                'explanations': ['Let me explain', 'I want to clarify', 'To be specific'],
                'examples': ['For example', 'For instance', 'Like'],
                'clarifications': ['I mean', 'That is', 'In other words']
            },
            'concise': {
                'explanations': ['Here\'s why', 'Because', 'Since'],
                'examples': ['Like', 'Such as', 'For example'],
                'clarifications': ['I mean', 'That is', 'So']
            }
        }
        
        self.empathy_patterns = {
            'high': {
                'acknowledgments': ['I understand how you feel', 'That must be difficult', 'I can see why you\'d think that'],
                'support': ['I\'m here for you', 'That sounds challenging', 'I appreciate you sharing that'],
                'questions': ['How does that make you feel?', 'What do you think about that?', 'How are you handling this?']
            },
            'medium': {
                'acknowledgments': ['I understand', 'That makes sense', 'I see your point'],
                'support': ['That sounds tough', 'I get it', 'That\'s understandable'],
                'questions': ['What do you think?', 'How do you feel about that?', 'What\'s your take on this?']
            },
            'low': {
                'acknowledgments': ['I see', 'Got it', 'Understood'],
                'support': ['Okay', 'Sure', 'Right'],
                'questions': ['What do you think?', 'Any thoughts?', 'Your opinion?']
            }
        }
        
        self.humor_patterns = {
            'heavy': {
                'jokes': ['😄', '😂', 'LOL', 'That\'s funny!', 'Good one!'],
                'playful': ['Just kidding!', 'Haha', '😊', 'That\'s a good point!'],
                'lighthearted': ['Well, well, well...', 'Oh boy!', 'Here we go!']
            },
            'moderate': {
                'jokes': ['😊', 'Haha', 'That\'s funny', 'Good point!'],
                'playful': ['Just kidding', 'Haha', '😊'],
                'lighthearted': ['Well...', 'Oh!', 'Interesting!']
            },
            'light': {
                'jokes': ['😊', 'Haha'],
                'playful': ['Just kidding', '😊'],
                'lighthearted': ['Well...', 'Oh!']
            },
            'none': {
                'jokes': [],
                'playful': [],
                'lighthearted': []
            }
        }
    
    def baseline_matching(self, user_profile: UserProfile, context: ContextType) -> TonePreferences:
        """
        Strategy 1: Baseline Matching - Start with profile preferences
        """
        from .profile_parser import ProfileParser
        parser = ProfileParser()
        # Use .value if context is Enum, else use as is
        context_val = context.value if hasattr(context, 'value') else str(context)
        return parser.get_tone_for_context(user_profile, context_val)
    
    def dynamic_adjustment(self, user_id: str, baseline_prefs: TonePreferences, 
                          conversation_history: List[Dict] = None) -> TonePreferences:
        """
        Strategy 2: Dynamic Adjustment - Modify based on conversation flow
        """
        if user_id not in self.conversation_flows:
            self.conversation_flows[user_id] = deque(maxlen=10)
        
        # Analyze recent conversation flow
        recent_flow = self._analyze_conversation_flow(user_id, conversation_history)
        
        # Adjust based on flow patterns
        adjusted_prefs = self._create_adjusted_preferences(baseline_prefs, recent_flow)
        
        return adjusted_prefs
    
    def learning_integration(self, user_id: str, adjusted_prefs: TonePreferences,
                           feedback_data: Dict[str, Any] = None) -> TonePreferences:
        """
        Strategy 3: Learning Integration - Incorporate feedback to improve future responses
        """
        if user_id not in self.feedback_learning:
            self.feedback_learning[user_id] = []
        
        # Store feedback for learning
        if feedback_data:
            self.feedback_learning[user_id].append({
                'timestamp': time.time(),
                'feedback': feedback_data,
                'preferences_used': adjusted_prefs.model_dump()
            })
        
        # Learn from feedback history
        learned_prefs = self._learn_from_feedback(user_id, adjusted_prefs)
        
        return learned_prefs
    
    def context_switching(self, user_id: str, learned_prefs: TonePreferences,
                         current_context: ContextType, conversation_history: List[Dict] = None) -> TonePreferences:
        """
        Strategy 4: Context Switching - Adapt to topic changes
        """
        # Track context changes
        if user_id not in self.context_history:
            self.context_history[user_id] = []
        
        # Detect context transitions
        context_transition = self._detect_context_transition(user_id, current_context, conversation_history)
        
        # Adjust preferences based on context transition
        final_prefs = self._adapt_to_context_transition(learned_prefs, context_transition)
        
        return final_prefs
    
    def adapt_response(self, base_response: str, user_profile: UserProfile, 
                      context: ContextType, conversation_history: List[Dict] = None,
                      user_id: str = None, feedback_data: Dict[str, Any] = None) -> str:
        """
        Enhanced adapt_response with all four adaptation strategies
        """
        # Strategy 1: Baseline Matching
        baseline_prefs = self.baseline_matching(user_profile, context)
        
        # Strategy 2: Dynamic Adjustment
        adjusted_prefs = self.dynamic_adjustment(user_id, baseline_prefs, conversation_history)
        
        # Strategy 3: Learning Integration
        learned_prefs = self.learning_integration(user_id, adjusted_prefs, feedback_data)
        
        # Strategy 4: Context Switching
        final_prefs = self.context_switching(user_id, learned_prefs, context, conversation_history)
        
        # Apply tone adaptations with final preferences
        adapted_response = base_response
        
        # Apply formality adaptation
        adapted_response = self._apply_formality(adapted_response, str(final_prefs.formality))
        
        # Apply enthusiasm adaptation
        adapted_response = self._apply_enthusiasm(adapted_response, str(final_prefs.enthusiasm))
        
        # Apply verbosity adaptation
        adapted_response = self._apply_verbosity(adapted_response, str(final_prefs.verbosity))
        
        # Apply empathy adaptation
        adapted_response = self._apply_empathy(adapted_response, str(final_prefs.empathy_level))
        
        # Apply humor adaptation
        adapted_response = self._apply_humor(adapted_response, str(final_prefs.humor))
        
        return adapted_response
    
    def _analyze_conversation_flow(self, user_id: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Analyze conversation flow patterns"""
        flow_analysis = {
            'message_length_trend': 'stable',
            'response_speed': 'normal',
            'topic_consistency': 'high',
            'user_engagement': 'medium',
            'context_stability': 'stable'
        }
        
        if not conversation_history:
            return flow_analysis
        
        # Analyze message length trends
        recent_messages = conversation_history[-5:] if len(conversation_history) >= 5 else conversation_history
        message_lengths = [len(msg.get('message', '')) for msg in recent_messages]
        
        if len(message_lengths) >= 2:
            if message_lengths[-1] > message_lengths[-2] * 1.5:
                flow_analysis['message_length_trend'] = 'increasing'
            elif message_lengths[-1] < message_lengths[-2] * 0.7:
                flow_analysis['message_length_trend'] = 'decreasing'
        
        # Analyze topic consistency
        topics = [msg.get('context', 'unknown') for msg in recent_messages]
        unique_topics = len(set(topics))
        if unique_topics <= 2:
            flow_analysis['topic_consistency'] = 'high'
        elif unique_topics <= 3:
            flow_analysis['topic_consistency'] = 'medium'
        else:
            flow_analysis['topic_consistency'] = 'low'
        
        # Analyze user engagement (based on message complexity)
        avg_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
        if avg_length > 100:
            flow_analysis['user_engagement'] = 'high'
        elif avg_length > 50:
            flow_analysis['user_engagement'] = 'medium'
        else:
            flow_analysis['user_engagement'] = 'low'
        
        return flow_analysis
    
    def _create_adjusted_preferences(self, baseline_prefs: TonePreferences, 
                                   flow_analysis: Dict[str, Any]) -> TonePreferences:
        """Create adjusted preferences based on conversation flow"""
        # Import enum classes
        from .profile_parser import (
            FormalityLevel, EnthusiasmLevel, VerbosityLevel, 
            EmpathyLevel, HumorLevel
        )
        
        # Start with baseline preferences
        adjusted_prefs = baseline_prefs
        
        # Adjust based on message length trend
        if flow_analysis['message_length_trend'] == 'increasing':
            # User is becoming more detailed, increase verbosity
            if adjusted_prefs.verbosity == VerbosityLevel.CONCISE:
                adjusted_prefs.verbosity = VerbosityLevel.BALANCED
            elif adjusted_prefs.verbosity == VerbosityLevel.BALANCED:
                adjusted_prefs.verbosity = VerbosityLevel.DETAILED
        
        elif flow_analysis['message_length_trend'] == 'decreasing':
            # User is becoming more concise, decrease verbosity
            if adjusted_prefs.verbosity == VerbosityLevel.DETAILED:
                adjusted_prefs.verbosity = VerbosityLevel.BALANCED
            elif adjusted_prefs.verbosity == VerbosityLevel.BALANCED:
                adjusted_prefs.verbosity = VerbosityLevel.CONCISE
        
        # Adjust based on user engagement
        if flow_analysis['user_engagement'] == 'high':
            # User is highly engaged, increase enthusiasm
            if adjusted_prefs.enthusiasm == EnthusiasmLevel.LOW:
                adjusted_prefs.enthusiasm = EnthusiasmLevel.MEDIUM
            elif adjusted_prefs.enthusiasm == EnthusiasmLevel.MEDIUM:
                adjusted_prefs.enthusiasm = EnthusiasmLevel.HIGH
        
        elif flow_analysis['user_engagement'] == 'low':
            # User is less engaged, increase empathy
            if adjusted_prefs.empathy_level == EmpathyLevel.LOW:
                adjusted_prefs.empathy_level = EmpathyLevel.MEDIUM
            elif adjusted_prefs.empathy_level == EmpathyLevel.MEDIUM:
                adjusted_prefs.empathy_level = EmpathyLevel.HIGH
        
        # Adjust based on topic consistency
        if flow_analysis['topic_consistency'] == 'low':
            # Topics are changing rapidly, increase formality for clarity
            if adjusted_prefs.formality == FormalityLevel.CASUAL:
                adjusted_prefs.formality = FormalityLevel.PROFESSIONAL
        
        return adjusted_prefs
    
    def _learn_from_feedback(self, user_id: str, current_prefs: TonePreferences) -> TonePreferences:
        """Learn from feedback history to improve preferences"""
        if user_id not in self.feedback_learning or not self.feedback_learning[user_id]:
            return current_prefs
        
        # Import enum classes
        from .profile_parser import (
            FormalityLevel, EnthusiasmLevel, VerbosityLevel, 
            EmpathyLevel, HumorLevel
        )
        
        learned_prefs = current_prefs
        
        # Analyze recent feedback (last 10 feedback entries)
        recent_feedback = self.feedback_learning[user_id][-10:]
        
        # Calculate average feedback scores by tone aspect
        feedback_scores = {
            'formality': [],
            'enthusiasm': [],
            'verbosity': [],
            'empathy': [],
            'humor': []
        }
        
        for feedback_entry in recent_feedback:
            feedback = feedback_entry.get('feedback', {})
            if 'rating' in feedback:
                rating = feedback['rating']
                # Map feedback to tone aspects based on context
                context = feedback.get('context', 'general')
                if context == 'work':
                    feedback_scores['formality'].append(rating)
                elif context == 'personal':
                    feedback_scores['enthusiasm'].append(rating)
                    feedback_scores['empathy'].append(rating)
                else:
                    # General feedback affects all aspects
                    for aspect in feedback_scores:
                        feedback_scores[aspect].append(rating)
        
        # Adjust preferences based on feedback scores
        for aspect, scores in feedback_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                
                # If average score is low (< 3.0), adjust the corresponding preference
                if avg_score < 3.0:
                    if aspect == 'formality':
                        if learned_prefs.formality == FormalityLevel.FORMAL:
                            learned_prefs.formality = FormalityLevel.PROFESSIONAL
                        elif learned_prefs.formality == FormalityLevel.PROFESSIONAL:
                            learned_prefs.formality = FormalityLevel.CASUAL
                    elif aspect == 'enthusiasm':
                        if learned_prefs.enthusiasm == EnthusiasmLevel.HIGH:
                            learned_prefs.enthusiasm = EnthusiasmLevel.MEDIUM
                        elif learned_prefs.enthusiasm == EnthusiasmLevel.MEDIUM:
                            learned_prefs.enthusiasm = EnthusiasmLevel.LOW
                    elif aspect == 'verbosity':
                        if learned_prefs.verbosity == VerbosityLevel.DETAILED:
                            learned_prefs.verbosity = VerbosityLevel.BALANCED
                        elif learned_prefs.verbosity == VerbosityLevel.BALANCED:
                            learned_prefs.verbosity = VerbosityLevel.CONCISE
                    elif aspect == 'empathy':
                        if learned_prefs.empathy_level == EmpathyLevel.HIGH:
                            learned_prefs.empathy_level = EmpathyLevel.MEDIUM
                        elif learned_prefs.empathy_level == EmpathyLevel.MEDIUM:
                            learned_prefs.empathy_level = EmpathyLevel.LOW
                    elif aspect == 'humor':
                        if learned_prefs.humor == HumorLevel.HEAVY:
                            learned_prefs.humor = HumorLevel.MODERATE
                        elif learned_prefs.humor == HumorLevel.MODERATE:
                            learned_prefs.humor = HumorLevel.LIGHT
                        elif learned_prefs.humor == HumorLevel.LIGHT:
                            learned_prefs.humor = HumorLevel.NONE
        
        return learned_prefs
    
    def _detect_context_transition(self, user_id: str, current_context: ContextType,
                                 conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Detect context transitions in conversation"""
        transition_info = {
            'has_transition': False,
            'from_context': None,
            'to_context': current_context.value if hasattr(current_context, 'value') else str(current_context),
            'transition_type': 'none',
            'confidence': 0.0
        }
        
        if not conversation_history or len(conversation_history) < 2:
            return transition_info
        
        # Get previous context
        previous_context = self.context_history[user_id][-1]['context'] if self.context_history[user_id] else None
        
        if previous_context != (current_context.value if hasattr(current_context, 'value') else str(current_context)):
            transition_info['has_transition'] = True
            transition_info['from_context'] = previous_context
            transition_info['confidence'] = 0.8
            
            # Determine transition type
            if previous_context == 'work' and (current_context.value if hasattr(current_context, 'value') else str(current_context)) == 'personal':
                transition_info['transition_type'] = 'work_to_personal'
            elif previous_context == 'personal' and (current_context.value if hasattr(current_context, 'value') else str(current_context)) == 'work':
                transition_info['transition_type'] = 'personal_to_work'
            elif previous_context == 'academic' and (current_context.value if hasattr(current_context, 'value') else str(current_context)) in ['work', 'personal']:
                transition_info['transition_type'] = 'academic_to_other'
            elif (current_context.value if hasattr(current_context, 'value') else str(current_context)) == 'academic':
                transition_info['transition_type'] = 'other_to_academic'
            else:
                transition_info['transition_type'] = 'general_transition'
        
        # Store context history
        if user_id not in self.context_history:
            self.context_history[user_id] = []
        
        self.context_history[user_id].append({
            'timestamp': time.time(),
            'context': current_context.value if hasattr(current_context, 'value') else str(current_context),
            'transition': transition_info
        })
        
        return transition_info
    
    def _adapt_to_context_transition(self, current_prefs: TonePreferences,
                                   context_transition: Dict[str, Any]) -> TonePreferences:
        """Adapt preferences based on context transition"""
        # Import enum classes
        from .profile_parser import (
            FormalityLevel, EnthusiasmLevel, VerbosityLevel, 
            EmpathyLevel, HumorLevel
        )
        
        adapted_prefs = current_prefs
        
        if not context_transition['has_transition']:
            return adapted_prefs
        
        transition_type = context_transition['transition_type']
        
        # Adapt based on transition type
        if transition_type == 'work_to_personal':
            # Transition from work to personal - become more casual and enthusiastic
            if adapted_prefs.formality == FormalityLevel.FORMAL:
                adapted_prefs.formality = FormalityLevel.PROFESSIONAL
            elif adapted_prefs.formality == FormalityLevel.PROFESSIONAL:
                adapted_prefs.formality = FormalityLevel.CASUAL
            
            if adapted_prefs.enthusiasm == EnthusiasmLevel.LOW:
                adapted_prefs.enthusiasm = EnthusiasmLevel.MEDIUM
            elif adapted_prefs.enthusiasm == EnthusiasmLevel.MEDIUM:
                adapted_prefs.enthusiasm = EnthusiasmLevel.HIGH
        
        elif transition_type == 'personal_to_work':
            # Transition from personal to work - become more formal and professional
            if adapted_prefs.formality == FormalityLevel.CASUAL:
                adapted_prefs.formality = FormalityLevel.PROFESSIONAL
            elif adapted_prefs.formality == FormalityLevel.PROFESSIONAL:
                adapted_prefs.formality = FormalityLevel.FORMAL
            
            if adapted_prefs.enthusiasm == EnthusiasmLevel.HIGH:
                adapted_prefs.enthusiasm = EnthusiasmLevel.MEDIUM
            elif adapted_prefs.enthusiasm == EnthusiasmLevel.MEDIUM:
                adapted_prefs.enthusiasm = EnthusiasmLevel.LOW
        
        elif transition_type == 'academic_to_other':
            # Transition from academic to other contexts - become more engaging
            if adapted_prefs.verbosity == VerbosityLevel.DETAILED:
                adapted_prefs.verbosity = VerbosityLevel.BALANCED
            
            if adapted_prefs.empathy_level == EmpathyLevel.LOW:
                adapted_prefs.empathy_level = EmpathyLevel.MEDIUM
        
        elif transition_type == 'other_to_academic':
            # Transition to academic context - become more detailed and formal
            if adapted_prefs.verbosity == VerbosityLevel.CONCISE:
                adapted_prefs.verbosity = VerbosityLevel.BALANCED
            elif adapted_prefs.verbosity == VerbosityLevel.BALANCED:
                adapted_prefs.verbosity = VerbosityLevel.DETAILED
            
            if adapted_prefs.formality == FormalityLevel.CASUAL:
                adapted_prefs.formality = FormalityLevel.PROFESSIONAL
        
        return adapted_prefs
    
    def _apply_formality(self, response: str, formality_level: str) -> str:
        """Apply formality adaptations to the response"""
        formality_type = formality_level.lower()
        
        if formality_type not in self.formality_patterns:
            return response
        
        patterns = self.formality_patterns[formality_type]
        
        # Replace casual greetings with formal ones
        if formality_type == 'formal':
            response = re.sub(r'\b(hi|hello|hey)\b', random.choice(patterns['greetings']), response, flags=re.IGNORECASE)
            # Add formal language patterns
            if random.random() < 0.3:
                response = response.replace('I\'m', 'I am').replace('I\'d', 'I would').replace('I\'ll', 'I will')
        elif formality_type == 'casual':
            response = re.sub(r'\b(good morning|good afternoon|greetings)\b', random.choice(patterns['greetings']), response, flags=re.IGNORECASE)
            # Add casual contractions
            if random.random() < 0.3:
                response = response.replace('I am', 'I\'m').replace('I would', 'I\'d').replace('I will', 'I\'ll')
        
        # Add formal transitions
        if formality_type == 'formal' and 'also' in response.lower():
            response = response.replace('also', random.choice(patterns['transitions']))
        
        # Add formal prefixes for high formality
        if formality_type == 'formal' and not any(greeting.lower() in response.lower() for greeting in patterns['greetings']):
            if random.random() < 0.4:
                response = f"{random.choice(patterns['greetings'])}! {response}"
        
        # Add formal closings for high formality
        if formality_type == 'formal' and random.random() < 0.2:
            response += f" {random.choice(patterns['farewells'])}."
        
        return response
    
    def _apply_enthusiasm(self, response: str, enthusiasm_level: str) -> str:
        """Apply enthusiasm adaptations to the response"""
        enthusiasm_type = enthusiasm_level.lower()
        
        if enthusiasm_type not in self.enthusiasm_patterns:
            return response
        
        patterns = self.enthusiasm_patterns[enthusiasm_type]
        
        # Add exclamations
        if patterns['exclamations'] and not response.endswith('!'):
            if enthusiasm_type == 'high' and random.random() < 0.4:
                response += random.choice(patterns['exclamations'])
            elif enthusiasm_type == 'medium' and random.random() < 0.2:
                response += random.choice(patterns['exclamations'])
        
        # Add positive intensifiers
        if patterns['intensifiers'] and random.random() < 0.3:
            intensifier = random.choice(patterns['intensifiers'])
            if enthusiasm_type == 'high':
                response = f"{intensifier}, {response.lower()}"
            elif enthusiasm_type == 'medium':
                response = f"{intensifier} {response}"
        
        # Add emojis
        if patterns['emojis'] and random.random() < 0.2:
            response += f" {random.choice(patterns['emojis'])}"
        
        # Add enthusiasm for high enthusiasm
        if enthusiasm_type == 'high' and random.random() < 0.5:
            if 'great' in response.lower() or 'good' in response.lower():
                response += "!!!"
            elif not response.endswith('!'):
                response += "!"
        
        # Add enthusiasm words
        if enthusiasm_type == 'high' and random.random() < 0.3:
            if 'help' in response.lower():
                response = response.replace('help', 'absolutely help')
            elif 'assist' in response.lower():
                response = response.replace('assist', 'definitely assist')
        
        return response
    
    def _apply_verbosity(self, response: str, verbosity_level: str) -> str:
        """Apply verbosity adaptations to the response"""
        verbosity_type = verbosity_level.lower()
        
        if verbosity_type not in self.verbosity_patterns:
            return response
        
        patterns = self.verbosity_patterns[verbosity_type]
        
        # Add explanations for complex responses
        if verbosity_type == 'detailed' and len(response.split()) > 10:
            if random.random() < 0.3:
                explanation = random.choice(patterns['explanations'])
                response = f"{explanation}: {response}"
        
        # Add examples for longer responses
        if verbosity_type == 'detailed' and len(response.split()) > 15:
            if random.random() < 0.2:
                example_intro = random.choice(patterns['examples'])
                response += f" {example_intro}, this approach has worked well in similar situations."
        
        return response
    
    def _apply_empathy(self, response: str, empathy_level: str) -> str:
        """Apply empathy adaptations to the response"""
        empathy_type = empathy_level.lower()
        
        if empathy_type not in self.empathy_patterns:
            return response
        
        patterns = self.empathy_patterns[empathy_type]
        
        # Add empathetic acknowledgments
        if empathy_type == 'high' and random.random() < 0.2:
            acknowledgment = random.choice(patterns['acknowledgments'])
            response = f"{acknowledgment}. {response}"
        
        # Add supportive phrases
        if empathy_type == 'medium' and random.random() < 0.15:
            support = random.choice(patterns['support'])
            response = f"{response} {support}."
        
        # Add empathetic questions
        if empathy_type == 'high' and random.random() < 0.1:
            question = random.choice(patterns['questions'])
            response += f" {question}"
        
        return response
    
    def _apply_humor(self, response: str, humor_level: str) -> str:
        """Apply humor adaptations to the response"""
        humor_type = humor_level.lower()
        
        if humor_type not in self.humor_patterns:
            return response
        
        patterns = self.humor_patterns[humor_type]
        
        # Add lighthearted elements
        if humor_type == 'heavy' and random.random() < 0.15:
            playful = random.choice(patterns['playful'])
            response += f" {playful}"
        
        # Add emojis for humor
        if patterns['jokes'] and random.random() < 0.1:
            joke_emoji = random.choice(patterns['jokes'])
            response += f" {joke_emoji}"
        
        return response
    
    def generate_response_with_tone(self, user_message: str, user_profile: UserProfile,
                                  conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate a complete response with tone analysis and adaptation
        """
        # Analyze context
        context = self.context_analyzer.analyze_context(user_message, 
                                                      conversation_history=conversation_history)
        
        # Generate base response (this would typically come from an AI model)
        base_response = self._generate_base_response(user_message, context)
        
        # Adapt response to user's tone preferences
        adapted_response = self.adapt_response(base_response, user_profile, context, conversation_history)
        
        # Get context confidence scores
        confidence_scores = self.context_analyzer.get_context_confidence(user_message)
        
        # Get context indicators
        indicators = self.context_analyzer.extract_context_indicators(user_message)
        
        return {
            'response': adapted_response,
            'context': context.value if hasattr(context, 'value') else str(context),
            'context_confidence': confidence_scores,
            'context_indicators': indicators,
            'applied_tone': {
                'formality': str(user_profile.tone_preferences.formality),
                'enthusiasm': str(user_profile.tone_preferences.enthusiasm),
                'verbosity': str(user_profile.tone_preferences.verbosity),
                'empathy': str(user_profile.tone_preferences.empathy_level),
                'humor': str(user_profile.tone_preferences.humor)
            },
            'base_response': base_response
        }
    
    def _generate_base_response(self, user_message: str, context: ContextType) -> str:
        """
        Generate a base response based on the user message and context
        This is a simplified version - in a real implementation, this would use an AI model
        """
        message_lower = user_message.lower()
        
        # Greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            if context == ContextType.WORK:
                return "Hello! I'm ready to assist you with your work tasks. What would you like to work on today?"
            elif context == ContextType.PERSONAL:
                return "Hi there! How are you doing today? I'm here to chat and help with whatever you need."
            elif context == ContextType.ACADEMIC:
                return "Hello! I'm here to help with your studies. What subject or topic would you like to explore?"
            else:
                return "Hello! I'm here to help you. What can I assist you with today?"
        
        # Help requests
        elif any(word in message_lower for word in ['help', 'assist', 'support', 'aid']):
            if context == ContextType.WORK:
                return "I'm here to help with your work tasks. Whether it's project management, analysis, or problem-solving, I'm ready to assist. What specific area do you need help with?"
            elif context == ContextType.PERSONAL:
                return "I'd be happy to help with whatever you need! Whether it's advice, information, or just someone to talk to, I'm here for you."
            elif context == ContextType.ACADEMIC:
                return "I can help you with your academic work. From research to writing to problem-solving, I'm here to support your learning. What subject or topic do you need help with?"
            else:
                return "I'm here to help! I can assist with information, problem-solving, analysis, or just general conversation. What would you like to work on?"
        
        # Questions about the AI
        elif any(phrase in message_lower for phrase in ['what can you do', 'your capabilities', 'what do you do', 'your features']):
            return "I'm an AI assistant with tone adaptation capabilities. I can help with information, analysis, problem-solving, writing, and more. I adapt my communication style based on your preferences and the context of our conversation."
        
        # Questions about tone adaptation
        elif any(phrase in message_lower for phrase in ['tone', 'style', 'adaptation', 'preferences']):
            return "I adapt my communication style based on your preferences for formality, enthusiasm, verbosity, empathy, and humor. I analyze the context of our conversation and adjust my tone accordingly to provide the most helpful and comfortable experience for you."
        
        # Gratitude
        elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome! I'm glad I could help. Is there anything else you'd like to work on or discuss?"
        
        # Well-being questions
        elif any(phrase in message_lower for phrase in ['how are you', 'how do you do', 'are you ok']):
            return "I'm functioning well and ready to help! I'm designed to assist with various tasks and adapt my communication style to your preferences. How about you - how are you doing?"
        
        # Specific questions (improved responses)
        elif '?' in user_message:
            if context == ContextType.WORK:
                return "That's a great question! Let me help you find the information or solution you need. Could you provide a bit more context so I can give you the most relevant and helpful response?"
            elif context == ContextType.PERSONAL:
                return "I'd be happy to help answer your question! What specific information or advice are you looking for?"
            elif context == ContextType.ACADEMIC:
                return "That's an interesting question! I can help you research this topic or break it down for better understanding. What aspect would you like to explore further?"
            else:
                return "That's a good question! I'm here to help you find the answer. Could you give me a bit more context so I can provide the most helpful response?"
        
        # Statements or general messages
        else:
            if context == ContextType.WORK:
                return "I understand your message. This sounds like a work-related topic. Let me help you with that - what specific aspect would you like to focus on or develop further?"
            elif context == ContextType.PERSONAL:
                return "Thanks for sharing that with me. I'm here to listen and help however I can. What would you like to explore or discuss further?"
            elif context == ContextType.ACADEMIC:
                return "I see you're working on something academic. This sounds interesting! How can I help you develop this further or explore related topics?"
            else:
                return "I understand what you're saying. This sounds like something I can help you with. What specific aspect would you like to work on or explore further?"
    
    def _get_tone_level(self, value: float) -> str:
        """Convert numeric tone value to descriptive level"""
        if value < 0.3:
            return 'low'
        elif value < 0.7:
            return 'medium'
        else:
            return 'high' 