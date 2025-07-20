from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import sqlite3
import json
import time
import os

from core.tone_engine import ToneEngine
from core.memory_manager import MemoryManager
from core.profile_parser import ProfileParser, UserProfile
from core.feedback_processor import FeedbackProcessor

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize core components
tone_engine = ToneEngine()
memory_manager = MemoryManager()
profile_parser = ProfileParser()
feedback_processor = FeedbackProcessor()

# Database setup
DB_PATH = "data/users.db"

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="User message")
    context: Optional[str] = Field(None, description="Message context (work, personal, academic)")
    feedback: Optional[Dict[str, Any]] = Field(None, description="User feedback on previous response")

class ChatResponse(BaseModel):
    response: str
    context: str
    context_confidence: Dict[str, float]
    context_indicators: Dict[str, List[str]]
    applied_tone: Dict[str, str]
    base_response: str
    memory_summary: Optional[Dict[str, Any]] = None

class FeedbackRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    message_id: Optional[str] = Field(None, description="Message ID for feedback")
    type: str = Field(..., description="Feedback type: rating, correction, preference")
    value: Optional[float] = Field(None, description="Feedback value (for rating)")
    corrections: Optional[Dict[str, float]] = Field(None, description="Specific tone corrections")
    preferences: Optional[Dict[str, float]] = Field(None, description="Direct preference updates")
    context: Optional[str] = Field(None, description="Context for feedback")

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message with tone adaptation
    """
    try:
        # Get user profile
        user_profile = await get_user_profile(request.user_id)
        if not user_profile:
            # Create a default profile for new users
            default_profile_data = {
                'user_id': request.user_id,
                'tone_preferences': {
                    'formality': 'professional',
                    'enthusiasm': 'medium',
                    'verbosity': 'balanced',
                    'empathy_level': 'medium',
                    'humor': 'light'
                },
                'communication_style': {
                    'preferred_greeting': 'Hello',
                    'technical_level': 'intermediate',
                    'cultural_context': '',
                    'age_group': 'adult'
                },
                'interaction_history': {
                    'total_interactions': 0,
                    'successful_tone_matches': 0,
                    'feedback_score': 0.0,
                    'last_interaction': None
                },
                'context_preferences': None
            }
            
            # Create the profile
            from core.profile_parser import ProfileParser
            parser = ProfileParser()
            user_profile = parser.parse_profile(default_profile_data)
            
            # Store the profile in database
            await update_user_profile(user_profile)
        
        # Get conversation history from memory
        conversation_history = memory_manager.get_short_term_memory(request.user_id)
        
        # Process feedback if provided
        if request.feedback:
            user_profile = feedback_processor.process_feedback(
                request.user_id, request.feedback, user_profile
            )
            # Update profile in database
            await update_user_profile(user_profile)
        
        # Generate response with enhanced tone adaptation using all four strategies
        response_data = tone_engine.generate_response_with_tone(
            request.message, user_profile, conversation_history
        )
        
        # Apply enhanced adaptation strategies
        adapted_response = tone_engine.adapt_response(
            response_data['response'], 
            user_profile, 
            response_data['context'], 
            conversation_history,
            user_id=request.user_id,
            feedback_data=request.feedback
        )
        
        # Update response data with enhanced adaptation
        response_data['response'] = adapted_response
        
        # Store exchange in memory
        exchange = {
            'user_message': request.message,
            'ai_response': response_data['response'],
            'context': response_data['context'],
            'applied_tone': response_data['applied_tone'],
            'timestamp': time.time()
        }
        
        memory_manager.add_short_term_memory(request.user_id, exchange)
        
        # Update long-term memory with learning data
        learning_data = {
            'context_preferences': {
                response_data['context']: {
                    'count': 1,
                    'last_used': time.time()
                }
            },
            'tone_effectiveness': {
                'formality': 1.0,
                'enthusiasm': 1.0,
                'verbosity': 1.0,
                'empathy': 1.0,
                'humor': 1.0
            }
        }
        
        # Merge with existing long-term memory
        existing_memory = memory_manager.get_long_term_memory(request.user_id)
        if existing_memory:
            # Update context preferences
            if 'context_preferences' in existing_memory:
                for context, data in learning_data['context_preferences'].items():
                    if context in existing_memory['context_preferences']:
                        existing_memory['context_preferences'][context]['count'] += 1
                        existing_memory['context_preferences'][context]['last_used'] = data['last_used']
                    else:
                        existing_memory['context_preferences'][context] = data
            else:
                existing_memory['context_preferences'] = learning_data['context_preferences']
            
            # Update tone effectiveness
            if 'tone_effectiveness' in existing_memory:
                for tone, effectiveness in learning_data['tone_effectiveness'].items():
                    if tone in existing_memory['tone_effectiveness']:
                        # Average with existing effectiveness
                        existing_memory['tone_effectiveness'][tone] = (
                            existing_memory['tone_effectiveness'][tone] + effectiveness
                        ) / 2
                    else:
                        existing_memory['tone_effectiveness'][tone] = effectiveness
            else:
                existing_memory['tone_effectiveness'] = learning_data['tone_effectiveness']
        else:
            existing_memory = learning_data
        
        memory_manager.add_long_term_memory(request.user_id, existing_memory)
        
        # Get memory summary
        memory_summary = memory_manager.get_memory_summary(request.user_id)
        
        return ChatResponse(
            response=response_data['response'],
            context=response_data['context'],
            context_confidence=response_data['context_confidence'],
            context_indicators=response_data['context_indicators'],
            applied_tone=response_data['applied_tone'],
            base_response=response_data['base_response'],
            memory_summary=memory_summary
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        error_details = f"Error processing chat: {str(e)}"
        if str(e) == "":
            error_details = f"Error processing chat: Unknown error occurred"
        raise HTTPException(status_code=500, detail=error_details)

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for tone adaptation learning
    """
    try:
        # Get user profile
        user_profile = await get_user_profile(request.user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Process feedback
        feedback_data = {
            'type': request.type,
            'value': request.value,
            'corrections': request.corrections,
            'preferences': request.preferences,
            'context': request.context
        }
        
        updated_profile = feedback_processor.process_feedback(
            request.user_id, feedback_data, user_profile
        )
        
        # Update profile in database
        await update_user_profile(updated_profile)
        
        return {
            "message": "Feedback processed successfully",
            "updated_profile": {
                "user_id": updated_profile.user_id,
                "tone_preferences": updated_profile.tone_preferences.dict(),
                "interaction_history": updated_profile.interaction_history.dict()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")

@router.get("/{user_id}/memory")
async def get_user_memory(user_id: str):
    """
    Get user's memory summary
    """
    try:
        memory_summary = memory_manager.get_memory_summary(user_id)
        return memory_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory: {str(e)}")

@router.delete("/{user_id}/memory")
async def clear_user_memory(user_id: str):
    """
    Clear all memory for a user
    """
    try:
        memory_manager.clear_user_memory(user_id)
        return {"message": "Memory cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")

@router.get("/{user_id}/feedback")
async def get_feedback_summary(user_id: str):
    """
    Get feedback summary for a user
    """
    try:
        feedback_summary = feedback_processor.get_feedback_summary(user_id)
        return feedback_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feedback: {str(e)}")

# Helper functions
async def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """
    Get user profile from database
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT user_id, tone_preferences, communication_style, interaction_history, context_preferences, created_at, updated_at
                FROM user_profiles WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Parse stored JSON data
            tone_preferences = json.loads(row['tone_preferences'])
            communication_style = json.loads(row['communication_style'])
            interaction_history = json.loads(row['interaction_history'])
            context_preferences = json.loads(row['context_preferences']) if row['context_preferences'] else None
            
            # Create UserProfile object
            profile_data = {
                'user_id': row['user_id'],
                'tone_preferences': tone_preferences,
                'communication_style': communication_style,
                'interaction_history': interaction_history,
                'context_preferences': context_preferences,
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            
            try:
                return profile_parser.parse_profile(profile_data)
            except Exception as e:
                print(f"Error parsing profile: {e}")
                # Return None if parsing fails
                return None
            
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None

async def update_user_profile(profile: UserProfile):
    """
    Update user profile in database
    """
    try:
        with get_db_connection() as conn:
            # Check if user exists
            cursor = conn.execute("SELECT user_id FROM user_profiles WHERE user_id = ?", (profile.user_id,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing profile
                conn.execute("""
                    UPDATE user_profiles 
                    SET tone_preferences = ?, communication_style = ?, interaction_history = ?, context_preferences = ?, updated_at = ?
                    WHERE user_id = ?
                """, (
                    json.dumps(profile.tone_preferences.dict()),
                    json.dumps(profile.communication_style.dict()),
                    json.dumps(profile.interaction_history.dict()),
                    json.dumps(profile.context_preferences.dict() if profile.context_preferences else {}),
                    time.strftime('%Y-%m-%d %H:%M:%S'),
                    profile.user_id
                ))
            else:
                # Create new profile
                conn.execute("""
                    INSERT INTO user_profiles 
                    (user_id, tone_preferences, communication_style, interaction_history, context_preferences, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    json.dumps(profile.tone_preferences.dict()),
                    json.dumps(profile.communication_style.dict()),
                    json.dumps(profile.interaction_history.dict()),
                    json.dumps(profile.context_preferences.dict() if profile.context_preferences else {}),
                    time.strftime('%Y-%m-%d %H:%M:%S'),
                    time.strftime('%Y-%m-%d %H:%M:%S')
                ))
            
            conn.commit()
            
    except Exception as e:
        print(f"Error updating user profile: {e}")
        raise 