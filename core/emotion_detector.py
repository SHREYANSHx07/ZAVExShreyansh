import re
from typing import Dict, List, Tuple
from enum import Enum

class EmotionType(str, Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"

class EmotionIntensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EmotionDetector:
    def __init__(self):
        # Emotion keywords and patterns
        self.emotion_keywords = {
            EmotionType.JOY: [
                'happy', 'joy', 'excited', 'thrilled', 'delighted', 'pleased', 'great', 'wonderful',
                'amazing', 'fantastic', 'awesome', 'brilliant', 'excellent', 'perfect', 'love', 'adore',
                'enjoy', 'fun', 'laugh', 'smile', '😊', '😄', '😃', '😁', '🎉', '✨', '💯'
            ],
            EmotionType.SADNESS: [
                'sad', 'depressed', 'melancholy', 'gloomy', 'miserable', 'unhappy', 'disappointed',
                'heartbroken', 'lonely', 'hopeless', 'sorrow', 'grief', 'tears', 'cry', '😢', '😭',
                '😔', '💔', '😞', '😥'
            ],
            EmotionType.ANGER: [
                'angry', 'mad', 'furious', 'irritated', 'annoyed', 'frustrated', 'rage', 'hate',
                'disgusted', 'outraged', 'livid', 'fuming', 'irate', '😠', '😡', '🤬', '💢', '😤'
            ],
            EmotionType.FEAR: [
                'afraid', 'scared', 'frightened', 'terrified', 'anxious', 'worried', 'nervous',
                'panicked', 'horrified', 'dread', 'terror', 'fear', '😨', '😰', '😱', '😳', '😟'
            ],
            EmotionType.SURPRISE: [
                'surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'bewildered', 'wow',
                'incredible', 'unbelievable', '😲', '😯', '😳', '🤯', '😱'
            ],
            EmotionType.DISGUST: [
                'disgusted', 'revolted', 'repulsed', 'sickened', 'gross', 'nasty', 'vile',
                '🤢', '🤮', '😷', '🤧'
            ]
        }
        
        # Emotion intensity indicators
        self.intensity_indicators = {
            EmotionIntensity.LOW: ['slightly', 'a bit', 'somewhat', 'kind of', 'sort of'],
            EmotionIntensity.MEDIUM: ['really', 'quite', 'pretty', 'fairly', 'rather'],
            EmotionIntensity.HIGH: ['extremely', 'absolutely', 'completely', 'totally', 'utterly', 'incredibly']
        }
        
        # Emoji intensity mapping
        self.emoji_intensity = {
            '😊': EmotionIntensity.LOW,
            '😄': EmotionIntensity.MEDIUM,
            '😃': EmotionIntensity.MEDIUM,
            '😁': EmotionIntensity.HIGH,
            '😢': EmotionIntensity.LOW,
            '😭': EmotionIntensity.HIGH,
            '😔': EmotionIntensity.LOW,
            '😠': EmotionIntensity.MEDIUM,
            '😡': EmotionIntensity.HIGH,
            '🤬': EmotionIntensity.HIGH,
            '😨': EmotionIntensity.MEDIUM,
            '😰': EmotionIntensity.MEDIUM,
            '😱': EmotionIntensity.HIGH,
            '😲': EmotionIntensity.MEDIUM,
            '😯': EmotionIntensity.LOW,
            '🤯': EmotionIntensity.HIGH,
            '🤢': EmotionIntensity.MEDIUM,
            '🤮': EmotionIntensity.HIGH
        }
    
    def detect_emotion(self, text: str) -> Dict[str, any]:
        """
        Detect emotion and intensity from text
        Returns: {
            'primary_emotion': EmotionType,
            'intensity': EmotionIntensity,
            'confidence': float,
            'emotions': Dict[EmotionType, float]
        }
        """
        text_lower = text.lower()
        
        # Count emotion keywords
        emotion_scores = {}
        for emotion_type, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            emotion_scores[emotion_type] = score
        
        # Count emojis and their intensity
        emoji_emotions = {}
        emoji_intensities = []
        
        for emoji, intensity in self.emoji_intensity.items():
            if emoji in text:
                emoji_emotions[emoji] = intensity
                emoji_intensities.append(intensity)
        
        # Determine primary emotion
        primary_emotion = EmotionType.NEUTRAL
        max_score = 0
        
        for emotion_type, score in emotion_scores.items():
            if score > max_score:
                max_score = score
                primary_emotion = emotion_type
        
        # Determine intensity
        intensity = EmotionIntensity.LOW
        
        # Check for intensity indicators
        for intensity_level, indicators in self.intensity_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    intensity = intensity_level
                    break
        
        # Override with emoji intensity if higher
        if emoji_intensities:
            high_count = sum(1 for i in emoji_intensities if i == EmotionIntensity.HIGH)
            medium_count = sum(1 for i in emoji_intensities if i == EmotionIntensity.MEDIUM)
            
            if high_count > 0:
                intensity = EmotionIntensity.HIGH
            elif medium_count > 0 and intensity == EmotionIntensity.LOW:
                intensity = EmotionIntensity.MEDIUM
        
        # Calculate confidence
        total_keywords = sum(emotion_scores.values())
        confidence = min(1.0, total_keywords / 10.0)  # Normalize to 0-1
        
        # If no emotions detected, set confidence to 0
        if total_keywords == 0:
            confidence = 0.0
        
        return {
            'primary_emotion': primary_emotion,
            'intensity': intensity,
            'confidence': confidence,
            'emotions': emotion_scores,
            'emoji_emotions': emoji_emotions
        }
    
    def get_emotion_context(self, emotion_data: Dict[str, any]) -> str:
        """Get contextual description of detected emotion"""
        emotion = emotion_data['primary_emotion']
        intensity = emotion_data['intensity']
        
        context_map = {
            EmotionType.JOY: {
                EmotionIntensity.LOW: "slightly positive",
                EmotionIntensity.MEDIUM: "positive",
                EmotionIntensity.HIGH: "very positive"
            },
            EmotionType.SADNESS: {
                EmotionIntensity.LOW: "slightly negative",
                EmotionIntensity.MEDIUM: "negative",
                EmotionIntensity.HIGH: "very negative"
            },
            EmotionType.ANGER: {
                EmotionIntensity.LOW: "slightly frustrated",
                EmotionIntensity.MEDIUM: "frustrated",
                EmotionIntensity.HIGH: "very frustrated"
            },
            EmotionType.FEAR: {
                EmotionIntensity.LOW: "slightly anxious",
                EmotionIntensity.MEDIUM: "anxious",
                EmotionIntensity.HIGH: "very anxious"
            },
            EmotionType.SURPRISE: {
                EmotionIntensity.LOW: "slightly surprised",
                EmotionIntensity.MEDIUM: "surprised",
                EmotionIntensity.HIGH: "very surprised"
            },
            EmotionType.DISGUST: {
                EmotionIntensity.LOW: "slightly displeased",
                EmotionIntensity.MEDIUM: "displeased",
                EmotionIntensity.HIGH: "very displeased"
            },
            EmotionType.NEUTRAL: {
                EmotionIntensity.LOW: "neutral",
                EmotionIntensity.MEDIUM: "neutral",
                EmotionIntensity.HIGH: "neutral"
            }
        }
        
        return context_map.get(emotion, {}).get(intensity, "neutral")
    
    def should_adjust_tone_for_emotion(self, emotion_data: Dict[str, any]) -> Dict[str, str]:
        """Determine tone adjustments based on detected emotion"""
        emotion = emotion_data['primary_emotion']
        intensity = emotion_data['intensity']
        
        adjustments = {
            'empathy_level': 'medium',
            'enthusiasm': 'medium',
            'formality': 'professional'
        }
        
        # Adjust based on emotion type
        if emotion == EmotionType.JOY:
            adjustments['enthusiasm'] = 'high' if intensity == EmotionIntensity.HIGH else 'medium'
        elif emotion == EmotionType.SADNESS:
            adjustments['empathy_level'] = 'high'
            adjustments['enthusiasm'] = 'low'
        elif emotion == EmotionType.ANGER:
            adjustments['empathy_level'] = 'high'
            adjustments['formality'] = 'professional'
        elif emotion == EmotionType.FEAR:
            adjustments['empathy_level'] = 'high'
            adjustments['formality'] = 'professional'
        elif emotion == EmotionType.SURPRISE:
            adjustments['enthusiasm'] = 'high' if intensity == EmotionIntensity.HIGH else 'medium'
        elif emotion == EmotionType.DISGUST:
            adjustments['empathy_level'] = 'medium'
            adjustments['formality'] = 'professional'
        
        return adjustments 