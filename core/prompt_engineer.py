"""
Custom Prompt Engineering System
Built from scratch without external frameworks as per implementation constraints
"""

import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

class PromptType(Enum):
    """Types of prompts for different use cases"""
    CONVERSATION = "conversation"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"

class PromptStyle(Enum):
    """Different prompt styles"""
    DIRECT = "direct"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    FORMAL = "formal"

@dataclass
class PromptTemplate:
    """Template for prompt generation"""
    template: str
    variables: List[str]
    style: PromptStyle
    context_requirements: List[str]
    output_format: str
    max_length: int = 1000

class CustomPromptEngineer:
    """
    Custom prompt engineering system built from scratch
    - No external prompt libraries
    - Custom template system
    - Context-aware prompt generation
    - Dynamic prompt adaptation
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.context_patterns = self._initialize_context_patterns()
        self.style_adapters = self._initialize_style_adapters()
        self.prompt_history = defaultdict(list)
        
    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize prompt templates"""
        return {
            "conversation_start": PromptTemplate(
                template="You are an AI assistant with tone adaptation capabilities. The user prefers {formality} communication with {enthusiasm} enthusiasm. Context: {context}. User message: {message}",
                variables=["formality", "enthusiasm", "context", "message"],
                style=PromptStyle.CONVERSATIONAL,
                context_requirements=["user_preferences", "context"],
                output_format="natural_response"
            ),
            
            "tone_analysis": PromptTemplate(
                template="Analyze the tone of this message: '{message}'. Consider formality, enthusiasm, verbosity, empathy, and humor levels. Context: {context}",
                variables=["message", "context"],
                style=PromptStyle.DIRECT,
                context_requirements=["message_content"],
                output_format="tone_analysis"
            ),
            
            "context_detection": PromptTemplate(
                template="Detect the context of this message: '{message}'. Classify as work, personal, academic, or unknown. Provide confidence score.",
                variables=["message"],
                style=PromptStyle.DIRECT,
                context_requirements=["message_content"],
                output_format="context_classification"
            ),
            
            "response_generation": PromptTemplate(
                template="Generate a response to: '{message}'. Style: {formality} formality, {enthusiasm} enthusiasm, {verbosity} detail, {empathy} empathy, {humor} humor. Context: {context}",
                variables=["message", "formality", "enthusiasm", "verbosity", "empathy", "humor", "context"],
                style=PromptStyle.CONVERSATIONAL,
                context_requirements=["user_message", "tone_preferences", "context"],
                output_format="adapted_response"
            ),
            
            "feedback_processing": PromptTemplate(
                template="Process feedback: {feedback}. Current tone preferences: {current_prefs}. Adjust preferences based on feedback.",
                variables=["feedback", "current_prefs"],
                style=PromptStyle.DIRECT,
                context_requirements=["feedback_data", "current_preferences"],
                output_format="updated_preferences"
            ),
            
            "memory_retrieval": PromptTemplate(
                template="Find relevant memories for query: '{query}'. User context: {context}. Previous interactions: {history}",
                variables=["query", "context", "history"],
                style=PromptStyle.DIRECT,
                context_requirements=["query", "user_context", "conversation_history"],
                output_format="relevant_memories"
            ),
            
            "emotion_detection": PromptTemplate(
                template="Detect emotions in: '{message}'. Identify primary emotion, intensity, and emotional indicators.",
                variables=["message"],
                style=PromptStyle.DIRECT,
                context_requirements=["message_content"],
                output_format="emotion_analysis"
            ),
            
            "conversation_summary": PromptTemplate(
                template="Summarize this conversation: {conversation}. Focus on key topics, tone patterns, and user preferences.",
                variables=["conversation"],
                style=PromptStyle.DIRECT,
                context_requirements=["conversation_history"],
                output_format="conversation_summary"
            )
        }
    
    def _initialize_context_patterns(self) -> Dict[str, List[str]]:
        """Initialize context detection patterns"""
        return {
            "work": [
                r"\b(meeting|project|deadline|client|business|work|office|report|presentation|team|manager|boss|colleague)\b",
                r"\b(schedule|agenda|strategy|budget|quarterly|annual|performance|review|promotion|salary|benefits|hr)\b",
                r"\b(conference|workshop|training|development|code|software|database|server|api|deployment|testing|bug|feature)\b"
            ],
            "personal": [
                r"\b(family|friend|home|weekend|vacation|party|birthday|dinner|movie|music|hobby|sport|game|pet|dog|cat)\b",
                r"\b(love|relationship|dating|marriage|kids|baby|health|fitness|gym|diet|travel|trip|holiday|celebration)\b",
                r"\b(anniversary|wedding|graduation|fun|enjoy|relax|stress|emotion|feeling|happy|sad|excited)\b"
            ],
            "academic": [
                r"\b(study|research|paper|thesis|dissertation|assignment|homework|exam|test|quiz|grade|professor|lecture|seminar)\b",
                r"\b(course|class|university|college|school|student|academic|scholarly|literature|citation|reference)\b",
                r"\b(methodology|analysis|data|statistics|theory|hypothesis|experiment|laboratory|lab|fieldwork|survey|interview)\b"
            ]
        }
    
    def _initialize_style_adapters(self) -> Dict[PromptStyle, Dict[str, str]]:
        """Initialize style adaptation patterns"""
        return {
            PromptStyle.DIRECT: {
                "prefix": "",
                "suffix": "",
                "separator": "\n",
                "variable_format": "{variable}"
            },
            PromptStyle.CONVERSATIONAL: {
                "prefix": "Hey! ",
                "suffix": " What do you think?",
                "separator": "\n\n",
                "variable_format": "{variable}"
            },
            PromptStyle.TECHNICAL: {
                "prefix": "Technical Analysis: ",
                "suffix": " End Analysis",
                "separator": "\n---\n",
                "variable_format": "[{variable}]"
            },
            PromptStyle.CREATIVE: {
                "prefix": "✨ ",
                "suffix": " ✨",
                "separator": "\n💭\n",
                "variable_format": "🎯{variable}🎯"
            },
            PromptStyle.FORMAL: {
                "prefix": "Respectfully, ",
                "suffix": " Thank you for your attention.",
                "separator": "\n\n",
                "variable_format": "{{variable}}"
            }
        }
    
    def generate_prompt(self, prompt_type: str, variables: Dict[str, Any], 
                       style: PromptStyle = PromptStyle.DIRECT,
                       context: Dict[str, Any] = None) -> str:
        """Generate a prompt based on type and variables"""
        if prompt_type not in self.templates:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        template = self.templates[prompt_type]
        
        # Validate required variables
        missing_vars = [var for var in template.variables if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        # Apply style adaptation
        adapted_template = self._apply_style(template.template, style)
        
        # Fill template with variables
        prompt = adapted_template.format(**variables)
        
        # Add context if provided
        if context:
            prompt = self._add_context(prompt, context)
        
        # Store prompt in history
        self._store_prompt(prompt_type, prompt, variables, style)
        
        return prompt
    
    def _apply_style(self, template: str, style: PromptStyle) -> str:
        """Apply style adaptation to template"""
        if style not in self.style_adapters:
            return template
        
        adapter = self.style_adapters[style]
        
        # Apply prefix and suffix
        styled_template = f"{adapter['prefix']}{template}{adapter['suffix']}"
        
        # Apply variable formatting
        for var in re.findall(r'\{(\w+)\}', template):
            styled_template = styled_template.replace(
                f"{{{var}}}", 
                adapter['variable_format'].replace('{variable}', var)
            )
        
        return styled_template
    
    def _add_context(self, prompt: str, context: Dict[str, Any]) -> str:
        """Add context information to prompt"""
        context_str = "\nContext Information:\n"
        for key, value in context.items():
            if isinstance(value, dict):
                context_str += f"- {key}: {json.dumps(value, indent=2)}\n"
            else:
                context_str += f"- {key}: {value}\n"
        
        return prompt + context_str
    
    def _store_prompt(self, prompt_type: str, prompt: str, variables: Dict[str, Any], style: PromptStyle):
        """Store prompt in history for analysis"""
        self.prompt_history[prompt_type].append({
            'prompt': prompt,
            'variables': variables,
            'style': style.value if hasattr(style, 'value') else str(style),
            'timestamp': time.time()
        })
        
        # Keep only last 100 prompts per type
        if len(self.prompt_history[prompt_type]) > 100:
            self.prompt_history[prompt_type] = self.prompt_history[prompt_type][-100:]
    
    def analyze_prompt_effectiveness(self, prompt_type: str) -> Dict[str, Any]:
        """Analyze effectiveness of prompts by type"""
        if prompt_type not in self.prompt_history:
            return {}
        
        prompts = self.prompt_history[prompt_type]
        if not prompts:
            return {}
        
        # Analyze prompt patterns
        analysis = {
            'total_prompts': len(prompts),
            'average_length': sum(len(p['prompt']) for p in prompts) / len(prompts),
            'style_distribution': defaultdict(int),
            'variable_usage': defaultdict(int),
            'recent_usage': len([p for p in prompts if time.time() - p['timestamp'] < 3600])
        }
        
        for prompt in prompts:
            analysis['style_distribution'][prompt['style']] += 1
            for var in prompt['variables']:
                analysis['variable_usage'][var] += 1
        
        return analysis
    
    def optimize_prompt(self, prompt_type: str, target_style: PromptStyle = None) -> str:
        """Optimize prompt based on historical effectiveness"""
        if prompt_type not in self.templates:
            return ""
        
        template = self.templates[prompt_type]
        
        # Get most effective style if not specified
        if not target_style:
            analysis = self.analyze_prompt_effectiveness(prompt_type)
            if analysis.get('style_distribution'):
                most_used_style = max(analysis['style_distribution'].items(), key=lambda x: x[1])[0]
                target_style = PromptStyle(most_used_style)
            else:
                target_style = PromptStyle.DIRECT
        
        # Create optimized template
        optimized_template = self._apply_style(template.template, target_style)
        
        return optimized_template
    
    def create_dynamic_prompt(self, base_type: str, user_profile: Dict[str, Any],
                            conversation_context: Dict[str, Any] = None) -> str:
        """Create a dynamic prompt based on user profile and context"""
        # Determine appropriate style based on user profile
        formality = user_profile.get('tone_preferences', {}).get('formality', 'professional')
        
        if formality == 'formal':
            style = PromptStyle.FORMAL
        elif formality == 'casual':
            style = PromptStyle.CONVERSATIONAL
        elif formality == 'technical':
            style = PromptStyle.TECHNICAL
        else:
            style = PromptStyle.DIRECT
        
        # Prepare variables
        variables = {
            'formality': formality,
            'enthusiasm': user_profile.get('tone_preferences', {}).get('enthusiasm', 'medium'),
            'verbosity': user_profile.get('tone_preferences', {}).get('verbosity', 'balanced'),
            'empathy': user_profile.get('tone_preferences', {}).get('empathy_level', 'medium'),
            'humor': user_profile.get('tone_preferences', {}).get('humor', 'light'),
            'context': conversation_context.get('context', 'general') if conversation_context else 'general',
            'message': conversation_context.get('message', '') if conversation_context else ''
        }
        
        return self.generate_prompt(base_type, variables, style, conversation_context)
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """Get overall prompt statistics"""
        stats = {
            'total_prompts': sum(len(prompts) for prompts in self.prompt_history.values()),
            'prompt_types': list(self.prompt_history.keys()),
            'most_used_type': None,
            'style_distribution': defaultdict(int),
            'recent_activity': 0
        }
        
        if self.prompt_history:
            # Find most used type
            type_counts = {ptype: len(prompts) for ptype, prompts in self.prompt_history.items()}
            stats['most_used_type'] = max(type_counts.items(), key=lambda x: x[1])[0]
            
            # Overall style distribution
            for prompts in self.prompt_history.values():
                for prompt in prompts:
                    stats['style_distribution'][prompt['style']] += 1
                    if time.time() - prompt['timestamp'] < 3600:
                        stats['recent_activity'] += 1
        
        return stats 