"""
Custom Vector Storage System
Built from scratch without external frameworks as per implementation constraints
"""

import math
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import hashlib
import sqlite3
import threading

class CustomVectorStore:
    """
    Custom vector storage system built from scratch
    - No external vector libraries
    - Custom similarity calculations
    - In-memory and persistent storage
    - Thread-safe operations
    """
    
    def __init__(self, db_path: str = "vector_store.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the vector storage database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    vector_data TEXT NOT NULL,
                    metadata TEXT,
                    timestamp REAL NOT NULL,
                    context TEXT,
                    embedding_type TEXT DEFAULT 'text'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS similarity_cache (
                    vector_id1 TEXT,
                    vector_id2 TEXT,
                    similarity REAL,
                    timestamp REAL,
                    PRIMARY KEY (vector_id1, vector_id2)
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON vectors(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON vectors(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_context ON vectors(context)")
    
    def _text_to_vector(self, text: str) -> List[float]:
        """
        Convert text to a simple vector representation
        Uses character frequency and basic text features
        """
        # Simple character frequency-based vector
        char_freq = defaultdict(int)
        word_freq = defaultdict(int)
        
        # Count character frequencies
        for char in text.lower():
            if char.isalnum():
                char_freq[char] += 1
        
        # Count word frequencies
        words = text.lower().split()
        for word in words:
            if len(word) > 2:  # Skip very short words
                word_freq[word] += 1
        
        # Create feature vector
        vector = []
        
        # Character frequency features (26 letters + numbers)
        for char in 'abcdefghijklmnopqrstuvwxyz0123456789':
            vector.append(char_freq.get(char, 0))
        
        # Text length features
        vector.append(len(text))
        vector.append(len(words))
        vector.append(len(set(words)))  # unique words
        
        # Word length features
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        vector.append(avg_word_length)
        
        # Punctuation features
        punctuation_count = sum(1 for char in text if char in '.,!?;:')
        vector.append(punctuation_count)
        
        # Case features
        upper_count = sum(1 for char in text if char.isupper())
        vector.append(upper_count)
        
        # Normalize vector
        magnitude = math.sqrt(sum(x * x for x in vector))
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        
        return vector
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _generate_id(self, content: str, user_id: str) -> str:
        """Generate unique ID for vector"""
        combined = f"{user_id}:{content}:{time.time()}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def add_vector(self, user_id: str, content: str, metadata: Dict[str, Any] = None,
                   context: str = None, embedding_type: str = "text") -> str:
        """Add a vector to the store"""
        with self.lock:
            vector_data = self._text_to_vector(content)
            vector_id = self._generate_id(content, user_id)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO vectors 
                    (id, user_id, content, vector_data, metadata, timestamp, context, embedding_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vector_id,
                    user_id,
                    content,
                    json.dumps(vector_data),
                    json.dumps(metadata) if metadata else None,
                    time.time(),
                    context,
                    embedding_type
                ))
            
            return vector_id
    
    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a vector by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, user_id, content, vector_data, metadata, timestamp, context, embedding_type
                FROM vectors WHERE id = ?
            """, (vector_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'user_id': row[1],
                    'content': row[2],
                    'vector_data': json.loads(row[3]),
                    'metadata': json.loads(row[4]) if row[4] else None,
                    'timestamp': row[5],
                    'context': row[6],
                    'embedding_type': row[7]
                }
        return None
    
    def find_similar(self, query_content: str, user_id: str = None, 
                    limit: int = 10, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Find similar vectors"""
        query_vector = self._text_to_vector(query_content)
        
        with sqlite3.connect(self.db_path) as conn:
            if user_id:
                cursor = conn.execute("""
                    SELECT id, user_id, content, vector_data, metadata, timestamp, context, embedding_type
                    FROM vectors WHERE user_id = ?
                    ORDER BY timestamp DESC
                """, (user_id,))
            else:
                cursor = conn.execute("""
                    SELECT id, user_id, content, vector_data, metadata, timestamp, context, embedding_type
                    FROM vectors ORDER BY timestamp DESC
                """)
            
            similarities = []
            for row in cursor.fetchall():
                stored_vector = json.loads(row[3])
                similarity = self._cosine_similarity(query_vector, stored_vector)
                
                if similarity >= threshold:
                    similarities.append({
                        'id': row[0],
                        'user_id': row[1],
                        'content': row[2],
                        'similarity': similarity,
                        'metadata': json.loads(row[4]) if row[4] else None,
                        'timestamp': row[5],
                        'context': row[6],
                        'embedding_type': row[7]
                    })
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:limit]
    
    def get_user_vectors(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all vectors for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, user_id, content, vector_data, metadata, timestamp, context, embedding_type
                FROM vectors WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            
            vectors = []
            for row in cursor.fetchall():
                vectors.append({
                    'id': row[0],
                    'user_id': row[1],
                    'content': row[2],
                    'vector_data': json.loads(row[3]),
                    'metadata': json.loads(row[4]) if row[4] else None,
                    'timestamp': row[5],
                    'context': row[6],
                    'embedding_type': row[7]
                })
            
            return vectors
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM vectors WHERE id = ?", (vector_id,))
                return cursor.rowcount > 0
    
    def delete_user_vectors(self, user_id: str) -> int:
        """Delete all vectors for a user"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM vectors WHERE user_id = ?", (user_id,))
                return cursor.rowcount
    
    def get_vector_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get statistics about stored vectors"""
        with sqlite3.connect(self.db_path) as conn:
            if user_id:
                cursor = conn.execute("""
                    SELECT COUNT(*) as total, 
                           COUNT(DISTINCT context) as contexts,
                           MIN(timestamp) as oldest,
                           MAX(timestamp) as newest
                    FROM vectors WHERE user_id = ?
                """, (user_id,))
            else:
                cursor = conn.execute("""
                    SELECT COUNT(*) as total,
                           COUNT(DISTINCT user_id) as users,
                           COUNT(DISTINCT context) as contexts,
                           MIN(timestamp) as oldest,
                           MAX(timestamp) as newest
                    FROM vectors
                """)
            
            row = cursor.fetchone()
            if row:
                return {
                    'total_vectors': row[0],
                    'unique_users': row[1] if len(row) > 4 else None,
                    'unique_contexts': row[2] if len(row) > 4 else row[1],
                    'oldest_timestamp': row[3] if len(row) > 4 else row[2],
                    'newest_timestamp': row[4] if len(row) > 4 else row[3]
                }
        return {}
    
    def cleanup_old_vectors(self, max_age_days: int = 30) -> int:
        """Clean up old vectors"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM vectors WHERE timestamp < ?", (cutoff_time,))
                return cursor.rowcount
    
    def search_by_context(self, context: str, user_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search vectors by context"""
        with sqlite3.connect(self.db_path) as conn:
            if user_id:
                cursor = conn.execute("""
                    SELECT id, user_id, content, vector_data, metadata, timestamp, context, embedding_type
                    FROM vectors WHERE context = ? AND user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (context, user_id, limit))
            else:
                cursor = conn.execute("""
                    SELECT id, user_id, content, vector_data, metadata, timestamp, context, embedding_type
                    FROM vectors WHERE context = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (context, limit))
            
            vectors = []
            for row in cursor.fetchall():
                vectors.append({
                    'id': row[0],
                    'user_id': row[1],
                    'content': row[2],
                    'vector_data': json.loads(row[3]),
                    'metadata': json.loads(row[4]) if row[4] else None,
                    'timestamp': row[5],
                    'context': row[6],
                    'embedding_type': row[7]
                })
            
            return vectors 