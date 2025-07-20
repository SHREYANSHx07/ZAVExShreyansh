from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import sqlite3
import json
import time
import os

from core.memory_manager import MemoryManager

router = APIRouter(prefix="/api/memory", tags=["memory"])

# Initialize memory manager
memory_manager = MemoryManager()

class MemoryResponse(BaseModel):
    user_id: str
    short_term_count: int
    long_term_size_kb: float
    max_short_term: int
    max_long_term_kb: int
    short_term_memory: List[Dict[str, Any]]
    long_term_memory: Optional[Dict[str, Any]]

class MemoryClearResponse(BaseModel):
    message: str
    user_id: str
    cleared_at: str

@router.get("/{user_id}", response_model=MemoryResponse)
async def get_user_memory(user_id: str):
    """
    Get user's memory (short-term and long-term)
    """
    try:
        memory_summary = memory_manager.get_memory_summary(user_id)
        
        return MemoryResponse(
            user_id=user_id,
            short_term_count=memory_summary["short_term_count"],
            long_term_size_kb=memory_summary["long_term_size_kb"],
            max_short_term=memory_summary["max_short_term"],
            max_long_term_kb=memory_summary["max_long_term_kb"],
            short_term_memory=memory_summary["short_term_memory"],
            long_term_memory=memory_summary["long_term_memory"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory: {str(e)}")

@router.delete("/{user_id}", response_model=MemoryClearResponse)
async def clear_user_memory(user_id: str):
    """
    Clear user's memory
    """
    try:
        memory_manager.clear_user_memory(user_id)
        return MemoryClearResponse(
            message="Memory cleared successfully",
            user_id=user_id,
            cleared_at=time.strftime('%Y-%m-%d %H:%M:%S')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")

@router.get("/{user_id}/short-term")
async def get_short_term_memory(user_id: str):
    """
    Get only short-term memory for user
    """
    try:
        short_term_memory = memory_manager.get_short_term_memory(user_id)
        return {
            "user_id": user_id,
            "short_term_memory": short_term_memory,
            "count": len(short_term_memory)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving short-term memory: {str(e)}")

@router.get("/{user_id}/long-term")
async def get_long_term_memory(user_id: str):
    """
    Get only long-term memory for user
    """
    try:
        long_term_memory = memory_manager.get_long_term_memory(user_id)
        return {
            "user_id": user_id,
            "long_term_memory": long_term_memory,
            "size_kb": memory_manager._get_long_term_size(user_id) / 1024
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving long-term memory: {str(e)}")

@router.get("/{user_id}/analytics")
async def get_memory_analytics(user_id: str):
    """
    Get memory analytics and insights
    """
    try:
        memory_summary = memory_manager.get_memory_summary(user_id)
        
        # Calculate analytics
        short_term = memory_summary["short_term_memory"]
        long_term = memory_summary["long_term_memory"]
        
        analytics = {
            "user_id": user_id,
            "memory_usage": {
                "short_term_count": len(short_term),
                "long_term_size_kb": memory_summary["long_term_size_kb"],
                "utilization_percentage": (memory_summary["long_term_size_kb"] / memory_summary["max_long_term_kb"]) * 100
            },
            "conversation_patterns": {
                "total_exchanges": len(short_term),
                "context_distribution": {},
                "tone_distribution": {}
            },
            "learning_metrics": {
                "context_preferences": long_term.get("context_preferences", {}) if long_term else {},
                "tone_effectiveness": long_term.get("tone_effectiveness", {}) if long_term else {}
            }
        }
        
        # Analyze conversation patterns
        if short_term:
            contexts = [exchange.get("context", "unknown") for exchange in short_term]
            context_counts = {}
            for context in contexts:
                context_counts[context] = context_counts.get(context, 0) + 1
            analytics["conversation_patterns"]["context_distribution"] = context_counts
            
            # Analyze tone patterns
            tones = [exchange.get("applied_tone", {}) for exchange in short_term]
            tone_counts = {}
            for tone_data in tones:
                for tone_type, level in tone_data.items():
                    if tone_type not in tone_counts:
                        tone_counts[tone_type] = {}
                    tone_counts[tone_type][level] = tone_counts[tone_type].get(level, 0) + 1
            analytics["conversation_patterns"]["tone_distribution"] = tone_counts
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory analytics: {str(e)}") 