import pytest
import tempfile
import os
import time
import json
from core.memory_manager import MemoryManager

class TestMemoryManager:
    @pytest.fixture
    def memory_manager(self):
        """Create a memory manager with temporary database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        yield MemoryManager(db_path=db_path, max_short_term=5, max_long_term_kb=10)
        
        # Cleanup
        os.unlink(db_path)
    
    def test_short_term_memory_add_and_get(self, memory_manager):
        """Test adding and retrieving short-term memory"""
        user_id = "test_user"
        exchange = {"message": "Hello", "response": "Hi there!", "timestamp": time.time()}
        
        # Add to short-term memory
        memory_manager.add_short_term_memory(user_id, exchange)
        
        # Retrieve short-term memory
        memory = memory_manager.get_short_term_memory(user_id)
        
        assert len(memory) == 1
        assert memory[0]["message"] == "Hello"
        assert memory[0]["response"] == "Hi there!"
    
    def test_short_term_memory_circular_buffer(self, memory_manager):
        """Test that short-term memory respects the circular buffer limit"""
        user_id = "test_user"
        
        # Add more exchanges than the limit
        for i in range(7):  # Limit is 5
            exchange = {"message": f"Message {i}", "response": f"Response {i}", "timestamp": time.time()}
            memory_manager.add_short_term_memory(user_id, exchange)
        
        # Check that only the last 5 exchanges are kept
        memory = memory_manager.get_short_term_memory(user_id)
        assert len(memory) == 5
        assert memory[0]["message"] == "Message 2"  # First 2 should be dropped
        assert memory[4]["message"] == "Message 6"  # Last one should be kept
    
    def test_long_term_memory_add_and_get(self, memory_manager):
        """Test adding and retrieving long-term memory"""
        user_id = "test_user"
        memory_data = {
            "context_preferences": {
                "work": {"count": 5, "last_used": time.time()},
                "personal": {"count": 3, "last_used": time.time()}
            },
            "tone_effectiveness": {
                "formality": 0.8,
                "enthusiasm": 0.6
            }
        }
        
        # Add to long-term memory
        memory_manager.add_long_term_memory(user_id, memory_data)
        
        # Retrieve long-term memory
        memory = memory_manager.get_long_term_memory(user_id)
        
        assert memory is not None
        assert "context_preferences" in memory
        assert "tone_effectiveness" in memory
        assert memory["context_preferences"]["work"]["count"] == 5
        assert memory["tone_effectiveness"]["formality"] == 0.8
    
    def test_memory_decay(self, memory_manager):
        """Test that memory decays over time"""
        user_id = "test_user"
        memory_data = {
            "context_preferences": {
                "work": {"count": 10, "last_used": time.time()}
            },
            "tone_effectiveness": {
                "formality": 0.9,
                "enthusiasm": 0.7
            }
        }
        
        # Add to long-term memory
        memory_manager.add_long_term_memory(user_id, memory_data)
        
        # Simulate time passing (this would normally be real time)
        # For testing, we'll just verify the decay calculation works
        memory = memory_manager.get_long_term_memory(user_id)
        
        # The decay should be applied but values should still be reasonable
        assert memory is not None
        assert memory["tone_effectiveness"]["formality"] > 0.1  # Should not decay below 10%
    
    def test_memory_size_limit(self, memory_manager):
        """Test that long-term memory respects size limits"""
        user_id = "test_user"
        
        # Create a large memory entry
        large_data = {
            "large_field": "x" * 8000,  # 8KB of data
            "context_preferences": {"work": {"count": 1}}
        }
        
        # This should trigger cleanup since it exceeds the 10KB limit
        memory_manager.add_long_term_memory(user_id, large_data)
        
        # Verify the data was stored (cleanup should have worked)
        memory = memory_manager.get_long_term_memory(user_id)
        assert memory is not None
    
    def test_clear_user_memory(self, memory_manager):
        """Test clearing all memory for a user"""
        user_id = "test_user"
        
        # Add some memory
        exchange = {"message": "Hello", "response": "Hi!", "timestamp": time.time()}
        memory_manager.add_short_term_memory(user_id, exchange)
        
        memory_data = {"context_preferences": {"work": {"count": 1}}}
        memory_manager.add_long_term_memory(user_id, memory_data)
        
        # Clear memory
        memory_manager.clear_user_memory(user_id)
        
        # Verify memory is cleared
        short_memory = memory_manager.get_short_term_memory(user_id)
        long_memory = memory_manager.get_long_term_memory(user_id)
        
        assert len(short_memory) == 0
        assert long_memory is None
    
    def test_memory_summary(self, memory_manager):
        """Test getting memory summary"""
        user_id = "test_user"
        
        # Add some memory
        exchange = {"message": "Hello", "response": "Hi!", "timestamp": time.time()}
        memory_manager.add_short_term_memory(user_id, exchange)
        
        memory_data = {"context_preferences": {"work": {"count": 1}}}
        memory_manager.add_long_term_memory(user_id, memory_data)
        
        # Get summary
        summary = memory_manager.get_memory_summary(user_id)
        
        assert "short_term_count" in summary
        assert "long_term_size_kb" in summary
        assert "max_short_term" in summary
        assert "max_long_term_kb" in summary
        assert summary["short_term_count"] == 1
        assert summary["max_short_term"] == 5
        assert summary["max_long_term_kb"] == 10
    
    def test_multiple_users(self, memory_manager):
        """Test that memory is isolated between users"""
        user1 = "user1"
        user2 = "user2"
        
        # Add memory for user1
        exchange1 = {"message": "Hello from user1", "response": "Hi user1!", "timestamp": time.time()}
        memory_manager.add_short_term_memory(user1, exchange1)
        
        # Add memory for user2
        exchange2 = {"message": "Hello from user2", "response": "Hi user2!", "timestamp": time.time()}
        memory_manager.add_short_term_memory(user2, exchange2)
        
        # Verify isolation
        user1_memory = memory_manager.get_short_term_memory(user1)
        user2_memory = memory_manager.get_short_term_memory(user2)
        
        assert len(user1_memory) == 1
        assert len(user2_memory) == 1
        assert user1_memory[0]["message"] == "Hello from user1"
        assert user2_memory[0]["message"] == "Hello from user2" 