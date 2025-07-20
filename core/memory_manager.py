import sqlite3
import json
import time
from typing import Dict, List, Optional, Any
from collections import deque
import threading
import os

class MemoryManager:
    def __init__(self, db_path: str = "data/users.db", max_short_term: int = 10, max_long_term_kb: int = 50):
        self.db_path = db_path
        self.max_short_term = max_short_term
        self.max_long_term_kb = max_long_term_kb
        self.short_term_memory: Dict[str, deque] = {}
        self.lock = threading.Lock()
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with memory table"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    user_id TEXT PRIMARY KEY,
                    memory_data TEXT,
                    last_updated REAL,
                    size_bytes INTEGER
                )
            """)
            conn.commit()
    
    def add_short_term_memory(self, user_id: str, exchange: Dict[str, Any]):
        """Add exchange to short-term memory (circular buffer)"""
        with self.lock:
            if user_id not in self.short_term_memory:
                self.short_term_memory[user_id] = deque(maxlen=self.max_short_term)
            
            # Add timestamp to exchange
            exchange['timestamp'] = time.time()
            self.short_term_memory[user_id].append(exchange)
    
    def get_short_term_memory(self, user_id: str) -> List[Dict[str, Any]]:
        """Get short-term memory for user"""
        with self.lock:
            return list(self.short_term_memory.get(user_id, []))
    
    def add_long_term_memory(self, user_id: str, memory_data: Dict[str, Any]):
        """Add data to long-term memory with size tracking and decay"""
        memory_json = json.dumps(memory_data)
        size_bytes = len(memory_json.encode('utf-8'))
        
        # Check if adding this would exceed limit
        current_size = self._get_long_term_size(user_id)
        if current_size + size_bytes > self.max_long_term_kb * 1024:
            self._cleanup_long_term_memory(user_id, size_bytes)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO long_term_memory 
                (user_id, memory_data, last_updated, size_bytes)
                VALUES (?, ?, ?, ?)
            """, (user_id, memory_json, time.time(), size_bytes))
            conn.commit()
    
    def get_long_term_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get long-term memory for user with decay applied"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT memory_data, last_updated FROM long_term_memory 
                WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            
            if result:
                memory_data = json.loads(result[0])
                last_updated = result[1]
                
                # Apply decay based on time
                decay_factor = self._calculate_decay_factor(last_updated)
                return self._apply_decay(memory_data, decay_factor)
            
            return None
    
    def _calculate_decay_factor(self, last_updated: float) -> float:
        """Calculate decay factor based on time elapsed"""
        days_elapsed = (time.time() - last_updated) / (24 * 3600)
        # Exponential decay: half-life of 30 days
        decay_factor = 2 ** (-days_elapsed / 30)
        return max(0.1, decay_factor)  # Minimum 10% retention
    
    def _apply_decay(self, memory_data: Dict[str, Any], decay_factor: float) -> Dict[str, Any]:
        """Apply decay to memory data"""
        decayed_data = {}
        for key, value in memory_data.items():
            if isinstance(value, (int, float)):
                decayed_data[key] = value * decay_factor
            elif isinstance(value, dict):
                decayed_data[key] = self._apply_decay(value, decay_factor)
            else:
                decayed_data[key] = value
        return decayed_data
    
    def _get_long_term_size(self, user_id: str) -> int:
        """Get current size of long-term memory for user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT size_bytes FROM long_term_memory WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
    
    def _cleanup_long_term_memory(self, user_id: str, new_size: int):
        """Clean up old memory entries to make room"""
        with sqlite3.connect(self.db_path) as conn:
            # Get all entries sorted by age (oldest first)
            cursor = conn.execute("""
                SELECT memory_data, last_updated FROM long_term_memory 
                WHERE user_id = ? ORDER BY last_updated ASC
            """, (user_id,))
            entries = cursor.fetchall()
            
            # Remove oldest entries until we have enough space
            total_size = sum(len(entry[0].encode('utf-8')) for entry in entries)
            target_size = self.max_long_term_kb * 1024 - new_size
            
            for entry in entries:
                if total_size <= target_size:
                    break
                entry_size = len(entry[0].encode('utf-8'))
                total_size -= entry_size
                # Remove this entry
                conn.execute("""
                    DELETE FROM long_term_memory 
                    WHERE user_id = ? AND last_updated = ?
                """, (user_id, entry[1]))
            
            conn.commit()
    
    def clear_user_memory(self, user_id: str):
        """Clear all memory for a user"""
        with self.lock:
            if user_id in self.short_term_memory:
                self.short_term_memory[user_id].clear()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM long_term_memory WHERE user_id = ?", (user_id,))
            conn.commit()
    
    def get_memory_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's memory usage"""
        short_term = self.get_short_term_memory(user_id)
        long_term = self.get_long_term_memory(user_id)
        
        return {
            "short_term_count": len(short_term),
            "long_term_size_kb": self._get_long_term_size(user_id) / 1024,
            "max_short_term": self.max_short_term,
            "max_long_term_kb": self.max_long_term_kb,
            "short_term_memory": short_term,
            "long_term_memory": long_term
        } 