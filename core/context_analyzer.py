import re
from typing import Dict, List, Tuple, Optional
from enum import Enum

class ContextType(Enum):
    WORK = "work"
    PERSONAL = "personal"
    ACADEMIC = "academic"
    UNKNOWN = "unknown"

class ContextAnalyzer:
    def __init__(self):
        # Keywords and patterns for context classification
        self.work_keywords = [
            'meeting', 'project', 'deadline', 'client', 'business', 'work', 'office',
            'report', 'presentation', 'team', 'manager', 'boss', 'colleague',
            'schedule', 'agenda', 'strategy', 'budget', 'quarterly', 'annual',
            'performance', 'review', 'promotion', 'salary', 'benefits', 'hr',
            'conference', 'workshop', 'training', 'development', 'code', 'software',
            'database', 'server', 'api', 'deployment', 'testing', 'bug', 'feature',
            'tomorrow', 'appointment', 'call', 'email', 'document', 'proposal'
        ]
        
        self.personal_keywords = [
            'family', 'friend', 'home', 'weekend', 'vacation', 'party', 'birthday',
            'dinner', 'movie', 'music', 'hobby', 'sport', 'game', 'pet', 'dog',
            'cat', 'love', 'relationship', 'dating', 'marriage', 'kids', 'baby',
            'health', 'fitness', 'gym', 'diet', 'travel', 'trip', 'holiday',
            'celebration', 'anniversary', 'wedding', 'graduation', 'fun', 'enjoy',
            'relax', 'stress', 'emotion', 'feeling', 'happy', 'sad', 'excited'
        ]
        
        self.academic_keywords = [
            'study', 'research', 'paper', 'thesis', 'dissertation', 'assignment',
            'homework', 'exam', 'test', 'quiz', 'grade', 'professor', 'lecture',
            'seminar', 'course', 'class', 'university', 'college', 'school',
            'student', 'academic', 'scholarly', 'literature', 'citation', 'reference',
            'methodology', 'analysis', 'data', 'statistics', 'theory', 'hypothesis',
            'experiment', 'laboratory', 'lab', 'fieldwork', 'survey', 'interview',
            'publication', 'journal', 'conference', 'peer review', 'plagiarism'
        ]
        
        # Context-specific phrases and patterns
        self.work_phrases = [
            r'\b(team|department|company|organization)\s+(meeting|call|discussion)',
            r'\b(project|task|assignment)\s+(deadline|timeline|schedule)',
            r'\b(quarterly|annual|monthly)\s+(report|review|planning)',
            r'\b(client|customer|stakeholder)\s+(meeting|presentation|feedback)',
            r'\b(performance|evaluation|appraisal)\s+(review|meeting)',
            r'\b(budget|financial|cost)\s+(analysis|planning|review)',
            r'\b(development|engineering|programming)\s+(task|feature|bug)',
            r'\b(conference|workshop|training)\s+(session|event)'
        ]
        
        self.personal_phrases = [
            r'\b(family|friend)\s+(dinner|party|gathering)',
            r'\b(weekend|vacation|holiday)\s+(plan|trip|activity)',
            r'\b(birthday|anniversary|celebration)\s+(party|event)',
            r'\b(relationship|dating|marriage)\s+(discussion|planning)',
            r'\b(health|fitness|wellness)\s+(goal|plan|routine)',
            r'\b(hobby|interest|passion)\s+(activity|project)',
            r'\b(emotion|feeling)\s+(happy|sad|excited|worried)',
            r'\b(pet|dog|cat)\s+(care|training|activity)'
        ]
        
        self.academic_phrases = [
            r'\b(research|study)\s+(paper|thesis|dissertation)',
            r'\b(academic|scholarly)\s+(publication|journal|conference)',
            r'\b(course|class|lecture)\s+(assignment|homework|exam)',
            r'\b(methodology|analysis|data)\s+(collection|analysis|interpretation)',
            r'\b(literature|citation|reference)\s+(review|search)',
            r'\b(experiment|laboratory|lab)\s+(work|procedure|protocol)',
            r'\b(statistics|statistical)\s+(analysis|test|method)',
            r'\b(peer\s+review|academic\s+writing)\s+(process|submission)'
        ]
    
    def analyze_context(self, message: str, user_id: str = None, 
                       conversation_history: List[Dict] = None) -> ContextType:
        """
        Analyze message context using keyword matching, phrase patterns, and conversation history
        """
        message_lower = message.lower()
        
        # Calculate scores for each context type
        work_score = self._calculate_work_score(message_lower)
        personal_score = self._calculate_personal_score(message_lower)
        academic_score = self._calculate_academic_score(message_lower)
        
        # Consider conversation history if available
        if conversation_history:
            historical_context = self._analyze_conversation_history(conversation_history)
            work_score += historical_context.get('work', 0) * 0.3
            personal_score += historical_context.get('personal', 0) * 0.3
            academic_score += historical_context.get('academic', 0) * 0.3
        
        # Determine the dominant context
        scores = {
            ContextType.WORK: work_score,
            ContextType.PERSONAL: personal_score,
            ContextType.ACADEMIC: academic_score
        }
        
        max_score = max(scores.values())
        if max_score > 0.1:  # Lower threshold for better detection
            return max(scores, key=scores.get)
        else:
            return ContextType.UNKNOWN
    
    def _calculate_work_score(self, message: str) -> float:
        """Calculate work context score"""
        score = 0.0
        
        # Keyword matching
        work_keyword_count = sum(1 for keyword in self.work_keywords if keyword in message)
        score += work_keyword_count * 0.1
        
        # Phrase pattern matching
        for pattern in self.work_phrases:
            if re.search(pattern, message):
                score += 0.3
        
        # Time-related work indicators
        time_work_patterns = [
            r'\b(9|10|11|12|1|2|3|4|5|6|7|8)\s*(am|pm)\s*(meeting|call|appointment)',
            r'\b(monday|tuesday|wednesday|thursday|friday)\s+(morning|afternoon|evening)',
            r'\b(deadline|due\s+date)\s+(today|tomorrow|this\s+week)',
            r'\b(work|office)\s+(schedule|hours|time)'
        ]
        
        for pattern in time_work_patterns:
            if re.search(pattern, message):
                score += 0.2
        
        return min(1.0, score)
    
    def _calculate_personal_score(self, message: str) -> float:
        """Calculate personal context score"""
        score = 0.0
        
        # Keyword matching
        personal_keyword_count = sum(1 for keyword in self.personal_keywords if keyword in message)
        score += personal_keyword_count * 0.1
        
        # Phrase pattern matching
        for pattern in self.personal_phrases:
            if re.search(pattern, message):
                score += 0.3
        
        # Personal time indicators
        personal_time_patterns = [
            r'\b(weekend|saturday|sunday)\s+(plan|activity|event)',
            r'\b(vacation|holiday|break)\s+(plan|trip|activity)',
            r'\b(birthday|anniversary|celebration)\s+(party|event)',
            r'\b(family|friend)\s+(dinner|lunch|coffee)'
        ]
        
        for pattern in personal_time_patterns:
            if re.search(pattern, message):
                score += 0.2
        
        return min(1.0, score)
    
    def _calculate_academic_score(self, message: str) -> float:
        """Calculate academic context score"""
        score = 0.0
        
        # Keyword matching
        academic_keyword_count = sum(1 for keyword in self.academic_keywords if keyword in message)
        score += academic_keyword_count * 0.1
        
        # Phrase pattern matching
        for pattern in self.academic_phrases:
            if re.search(pattern, message):
                score += 0.3
        
        # Academic time indicators
        academic_time_patterns = [
            r'\b(semester|quarter|term)\s+(exam|assignment|deadline)',
            r'\b(lecture|class|course)\s+(schedule|time|room)',
            r'\b(research|study)\s+(session|period|time)',
            r'\b(thesis|dissertation)\s+(defense|submission|deadline)'
        ]
        
        for pattern in academic_time_patterns:
            if re.search(pattern, message):
                score += 0.2
        
        return min(1.0, score)
    
    def _analyze_conversation_history(self, history: List[Dict]) -> Dict[str, float]:
        """Analyze conversation history to determine context trends"""
        context_counts = {'work': 0, 'personal': 0, 'academic': 0}
        total_messages = len(history)
        
        if total_messages == 0:
            return context_counts
        
        for message_data in history[-10:]:  # Look at last 10 messages
            if 'message' in message_data:
                message = message_data['message']
                context = self.analyze_context(message)
                if context != ContextType.UNKNOWN:
                    context_counts[context.value] += 1
        
        # Normalize counts
        for context in context_counts:
            context_counts[context] = context_counts[context] / total_messages
        
        return context_counts
    
    def get_context_confidence(self, message: str) -> Dict[str, float]:
        """Get confidence scores for each context type"""
        message_lower = message.lower()
        
        work_score = self._calculate_work_score(message_lower)
        personal_score = self._calculate_personal_score(message_lower)
        academic_score = self._calculate_academic_score(message_lower)
        
        return {
            'work': work_score,
            'personal': personal_score,
            'academic': academic_score,
            'unknown': 1.0 - max(work_score, personal_score, academic_score)
        }
    
    def extract_context_indicators(self, message: str) -> Dict[str, List[str]]:
        """Extract specific indicators that led to context classification"""
        message_lower = message.lower()
        indicators = {
            'work': [],
            'personal': [],
            'academic': []
        }
        
        # Find work indicators
        for keyword in self.work_keywords:
            if keyword in message_lower:
                indicators['work'].append(keyword)
        
        for pattern in self.work_phrases:
            matches = re.findall(pattern, message_lower)
            # Convert tuples to strings
            for match in matches:
                if isinstance(match, tuple):
                    indicators['work'].extend([m for m in match if m])
                else:
                    indicators['work'].append(match)
        
        # Find personal indicators
        for keyword in self.personal_keywords:
            if keyword in message_lower:
                indicators['personal'].append(keyword)
        
        for pattern in self.personal_phrases:
            matches = re.findall(pattern, message_lower)
            # Convert tuples to strings
            for match in matches:
                if isinstance(match, tuple):
                    indicators['personal'].extend([m for m in match if m])
                else:
                    indicators['personal'].append(match)
        
        # Find academic indicators
        for keyword in self.academic_keywords:
            if keyword in message_lower:
                indicators['academic'].append(keyword)
        
        for pattern in self.academic_phrases:
            matches = re.findall(pattern, message_lower)
            # Convert tuples to strings
            for match in matches:
                if isinstance(match, tuple):
                    indicators['academic'].extend([m for m in match if m])
                else:
                    indicators['academic'].append(match)
        
        return indicators 