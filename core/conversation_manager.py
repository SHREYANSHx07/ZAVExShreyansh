"""
Custom Conversation State Management System
Built from scratch without external frameworks as per implementation constraints
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Tuple
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3

class ConversationState(Enum):
    """States of a conversation"""
    INITIAL = "initial"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

class TopicType(Enum):
    """Types of conversation topics"""
    WORK = "work"
    PERSONAL = "personal"
    ACADEMIC = "academic"
    TECHNICAL = "technical"
    CASUAL = "casual"
    UNKNOWN = "unknown"

@dataclass
class ConversationTurn:
    """Represents a single turn in conversation"""
    user_id: str
    message: str
    response: str
    timestamp: float
    context: str
    tone_applied: Dict[str, Any]
    topic: str
    state: ConversationState
    metadata: Dict[str, Any] = None

@dataclass
class ConversationSession:
    """Represents a conversation session"""
    session_id: str
    user_id: str
    start_time: float
    end_time: Optional[float] = None
    state: ConversationState = ConversationState.INITIAL
    topic_history: List[str] = None
    tone_preferences: Dict[str, Any] = None
    context_transitions: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.topic_history is None:
            self.topic_history = []
        if self.tone_preferences is None:
            self.tone_preferences = {}
        if self.context_transitions is None:
            self.context_transitions = []
        if self.metadata is None:
            self.metadata = {}

class CustomConversationManager:
    """
    Custom conversation state management system built from scratch
    - No external state management libraries
    - Custom session tracking
    - Topic and context management
    - Thread-safe operations
    """
    
    def __init__(self, db_path: str = "conversation_manager.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.active_sessions = {}  # session_id -> ConversationSession
        self.session_turns = defaultdict(deque)  # session_id -> deque of turns
        self.user_sessions = defaultdict(list)  # user_id -> list of session_ids
        self._init_database()
    
    def _init_database(self):
        """Initialize the conversation management database"""
        with sqlite3.connect(self.db_path) as conn:
            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    state TEXT NOT NULL,
                    topic_history TEXT,
                    tone_preferences TEXT,
                    context_transitions TEXT,
                    metadata TEXT
                )
            """)
            
            # Conversation turns table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS turns (
                    turn_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    context TEXT,
                    tone_applied TEXT,
                    topic TEXT,
                    state TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            
            # Topic tracking table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    topic_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    confidence REAL,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_user ON sessions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_state ON sessions(state)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_turn_session ON turns(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_turn_timestamp ON turns(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_topic_session ON topics(session_id)")
    
    def create_session(self, user_id: str, initial_context: str = "general",
                      tone_preferences: Dict[str, Any] = None) -> str:
        """Create a new conversation session"""
        with self.lock:
            session_id = f"{user_id}_{int(time.time() * 1000)}"
            
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id,
                start_time=time.time(),
                state=ConversationState.ACTIVE,
                tone_preferences=tone_preferences or {}
            )
            
            # Store in memory
            self.active_sessions[session_id] = session
            self.user_sessions[user_id].append(session_id)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO sessions 
                    (session_id, user_id, start_time, state, topic_history, tone_preferences, context_transitions, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    user_id,
                    session.start_time,
                    session.state.value,
                    json.dumps(session.topic_history),
                    json.dumps(session.tone_preferences),
                    json.dumps(session.context_transitions),
                    json.dumps(session.metadata)
                ))
            
            return session_id
    
    def add_turn(self, session_id: str, user_id: str, message: str, response: str,
                 context: str, tone_applied: Dict[str, Any], topic: str = None,
                 metadata: Dict[str, Any] = None) -> str:
        """Add a conversation turn"""
        with self.lock:
            turn_id = f"{session_id}_{int(time.time() * 1000)}"
            
            turn = ConversationTurn(
                user_id=user_id,
                message=message,
                response=response,
                timestamp=time.time(),
                context=context,
                tone_applied=tone_applied,
                topic=topic or "unknown",
                state=ConversationState.ACTIVE,
                metadata=metadata or {}
            )
            
            # Store in memory
            if session_id not in self.session_turns:
                self.session_turns[session_id] = deque(maxlen=100)
            self.session_turns[session_id].append(turn)
            
            # Update session topic history
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                if topic and topic not in session.topic_history:
                    session.topic_history.append(topic)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO turns 
                    (turn_id, session_id, user_id, message, response, timestamp, context, tone_applied, topic, state, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    turn_id,
                    session_id,
                    user_id,
                    message,
                    response,
                    turn.timestamp,
                    context,
                    json.dumps(tone_applied),
                    topic or "unknown",
                    turn.state.value if hasattr(turn.state, 'value') else str(turn.state),
                    json.dumps(metadata) if metadata else None
                ))
            
            return turn_id
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get a conversation session"""
        # Check memory first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Load from database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT session_id, user_id, start_time, end_time, state, topic_history, 
                       tone_preferences, context_transitions, metadata
                FROM sessions WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                session = ConversationSession(
                    session_id=row[0],
                    user_id=row[1],
                    start_time=row[2],
                    end_time=row[3],
                    state=ConversationState(row[4]),
                    topic_history=json.loads(row[5]) if row[5] else [],
                    tone_preferences=json.loads(row[6]) if row[6] else {},
                    context_transitions=json.loads(row[7]) if row[7] else [],
                    metadata=json.loads(row[8]) if row[8] else {}
                )
                
                # Cache in memory
                self.active_sessions[session_id] = session
                return session
        
        return None
    
    def get_session_turns(self, session_id: str, limit: int = 50) -> List[ConversationTurn]:
        """Get turns for a session"""
        # Check memory first
        if session_id in self.session_turns:
            return list(self.session_turns[session_id])[-limit:]
        
        # Load from database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT turn_id, user_id, message, response, timestamp, context, 
                       tone_applied, topic, state, metadata
                FROM turns WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            turns = []
            for row in cursor.fetchall():
                turn = ConversationTurn(
                    user_id=row[1],
                    message=row[2],
                    response=row[3],
                    timestamp=row[4],
                    context=row[5],
                    tone_applied=json.loads(row[6]) if row[6] else {},
                    topic=row[7],
                    state=ConversationState(row[8]),
                    metadata=json.loads(row[9]) if row[9] else {}
                )
                turns.append(turn)
            
            return turns[::-1]  # Reverse to get chronological order
    
    def update_session_state(self, session_id: str, new_state: ConversationState,
                           metadata: Dict[str, Any] = None):
        """Update session state"""
        with self.lock:
            # Update memory
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.state = new_state
                if metadata:
                    session.metadata.update(metadata)
                
                if new_state == ConversationState.COMPLETED:
                    session.end_time = time.time()
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE sessions SET state = ?, end_time = ?, metadata = ?
                    WHERE session_id = ?
                """, (
                    new_state.value,
                    time.time() if new_state == ConversationState.COMPLETED else None,
                    json.dumps(metadata) if metadata else None,
                    session_id
                ))
    
    def get_user_sessions(self, user_id: str, limit: int = 20) -> List[ConversationSession]:
        """Get all sessions for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT session_id, user_id, start_time, end_time, state, topic_history, 
                       tone_preferences, context_transitions, metadata
                FROM sessions WHERE user_id = ?
                ORDER BY start_time DESC
                LIMIT ?
            """, (user_id, limit))
            
            sessions = []
            for row in cursor.fetchall():
                session = ConversationSession(
                    session_id=row[0],
                    user_id=row[1],
                    start_time=row[2],
                    end_time=row[3],
                    state=ConversationState(row[4]),
                    topic_history=json.loads(row[5]) if row[5] else [],
                    tone_preferences=json.loads(row[6]) if row[6] else {},
                    context_transitions=json.loads(row[7]) if row[7] else [],
                    metadata=json.loads(row[8]) if row[8] else {}
                )
                sessions.append(session)
            
            return sessions
    
    def track_topic_change(self, session_id: str, new_topic: str, confidence: float = 1.0,
                          metadata: Dict[str, Any] = None):
        """Track topic changes in conversation"""
        with self.lock:
            topic_id = f"{session_id}_{int(time.time())}"
            
            # Update session topic history
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                if new_topic not in session.topic_history:
                    session.topic_history.append(new_topic)
            
            # Store topic in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO topics 
                    (topic_id, session_id, topic_name, start_time, confidence, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    topic_id,
                    session_id,
                    new_topic,
                    time.time(),
                    confidence,
                    json.dumps(metadata) if metadata else None
                ))
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        turns = self.get_session_turns(session_id)
        
        summary = {
            'session_id': session_id,
            'user_id': session.user_id,
            'duration': (session.end_time or time.time()) - session.start_time,
            'total_turns': len(turns),
            'topics_discussed': session.topic_history,
            'state': session.state.value,
            'context_transitions': len(session.context_transitions),
            'tone_preferences': session.tone_preferences,
            'metadata': session.metadata
        }
        
        # Analyze tone patterns
        if turns:
            tone_patterns = defaultdict(int)
            for turn in turns:
                for tone_key, tone_value in turn.tone_applied.items():
                    tone_patterns[tone_key] += 1
            
            summary['tone_patterns'] = dict(tone_patterns)
            
            # Calculate average message length
            avg_message_length = sum(len(turn.message) for turn in turns) / len(turns)
            summary['average_message_length'] = avg_message_length
        
        return summary
    
    def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """Clean up old sessions"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                # Delete old turns
                cursor = conn.execute("DELETE FROM turns WHERE timestamp < ?", (cutoff_time,))
                turns_deleted = cursor.rowcount
                
                # Delete old topics
                cursor = conn.execute("DELETE FROM topics WHERE start_time < ?", (cutoff_time,))
                topics_deleted = cursor.rowcount
                
                # Delete old sessions
                cursor = conn.execute("DELETE FROM sessions WHERE start_time < ?", (cutoff_time,))
                sessions_deleted = cursor.rowcount
                
                return sessions_deleted + turns_deleted + topics_deleted
    
    def get_conversation_statistics(self, user_id: str = None) -> Dict[str, Any]:
        """Get conversation statistics"""
        with sqlite3.connect(self.db_path) as conn:
            if user_id:
                cursor = conn.execute("""
                    SELECT COUNT(*) as total_sessions,
                           COUNT(CASE WHEN state = 'completed' THEN 1 END) as completed_sessions,
                           AVG(end_time - start_time) as avg_duration,
                           COUNT(DISTINCT topic_name) as unique_topics
                    FROM sessions s
                    LEFT JOIN topics t ON s.session_id = t.session_id
                    WHERE user_id = ?
                """, (user_id,))
            else:
                cursor = conn.execute("""
                    SELECT COUNT(*) as total_sessions,
                           COUNT(CASE WHEN state = 'completed' THEN 1 END) as completed_sessions,
                           AVG(end_time - start_time) as avg_duration,
                           COUNT(DISTINCT user_id) as unique_users,
                           COUNT(DISTINCT topic_name) as unique_topics
                    FROM sessions s
                    LEFT JOIN topics t ON s.session_id = t.session_id
                """)
            
            row = cursor.fetchone()
            if row:
                return {
                    'total_sessions': row[0],
                    'completed_sessions': row[1],
                    'avg_duration': row[2] or 0,
                    'unique_users': row[3] if len(row) > 4 else None,
                    'unique_topics': row[3] if len(row) <= 4 else row[4]
                }
        
        return {} 