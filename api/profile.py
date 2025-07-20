from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import sqlite3
import json
import time
import os

from core.profile_parser import ProfileParser, UserProfile, TonePreferences, ContextPreferences

router = APIRouter(prefix="/api/profile", tags=["profile"])

# Database setup
DB_PATH = "data/users.db"

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with user profiles table"""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                tone_preferences TEXT,
                communication_style TEXT,
                interaction_history TEXT,
                context_preferences TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.commit()

# Initialize database on startup
init_database()

class ProfileCreateRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    tone_preferences: Dict[str, str] = Field(..., description="Tone preferences")
    communication_style: Optional[Dict[str, Any]] = Field(None, description="Communication style preferences")
    interaction_history: Optional[Dict[str, Any]] = Field(None, description="Interaction history")
    context_preferences: Optional[Dict[str, Dict[str, str]]] = Field(None, description="Context-specific preferences")

class ProfileResponse(BaseModel):
    user_id: str
    tone_preferences: Dict[str, str]
    communication_style: Dict[str, Any]
    interaction_history: Dict[str, Any]
    context_preferences: Optional[Dict[str, Optional[Dict[str, str]]]]
    created_at: Optional[str]
    updated_at: Optional[str]

@router.post("/", response_model=ProfileResponse)
async def create_or_update_profile(request: ProfileCreateRequest):
    """
    Create or update a user profile with tone preferences
    """
    parser = ProfileParser()
    
    # Validate profile data
    if not parser.validate_profile(request.dict()):
        raise HTTPException(status_code=400, detail="Invalid profile data")
    
    # Parse profile
    profile = parser.parse_profile(request.dict())
    
    # Store in database
    with get_db_connection() as conn:
        # Check if user already exists
        cursor = conn.execute("SELECT user_id FROM user_profiles WHERE user_id = ?", (request.user_id,))
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
                request.user_id
            ))
        else:
            # Create new profile
            conn.execute("""
                INSERT INTO user_profiles 
                (user_id, tone_preferences, communication_style, interaction_history, context_preferences, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                request.user_id,
                json.dumps(profile.tone_preferences.dict()),
                json.dumps(profile.communication_style.dict()),
                json.dumps(profile.interaction_history.dict()),
                json.dumps(profile.context_preferences.dict() if profile.context_preferences else {}),
                time.strftime('%Y-%m-%d %H:%M:%S'),
                time.strftime('%Y-%m-%d %H:%M:%S')
            ))
        
        conn.commit()
    
    # Convert context preferences to dict, handling None values
    context_prefs_dict = None
    if profile.context_preferences:
        context_prefs_dict = {}
        for context in ['work', 'personal', 'academic']:
            context_pref = getattr(profile.context_preferences, context, None)
            if context_pref:
                context_prefs_dict[context] = context_pref.dict()
            else:
                context_prefs_dict[context] = None
    
    return ProfileResponse(
        user_id=profile.user_id,
        tone_preferences=profile.tone_preferences.dict(),
        communication_style=profile.communication_style.dict(),
        interaction_history=profile.interaction_history.dict(),
        context_preferences=context_prefs_dict,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str):
    """
    Retrieve a user profile by user ID
    """
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT user_id, tone_preferences, communication_style, interaction_history, context_preferences, created_at, updated_at
            FROM user_profiles WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Parse stored JSON data
        tone_preferences = json.loads(row['tone_preferences'])
        communication_style = json.loads(row['communication_style'])
        interaction_history = json.loads(row['interaction_history'])
        context_preferences = json.loads(row['context_preferences']) if row['context_preferences'] else None
        
        return ProfileResponse(
            user_id=row['user_id'],
            tone_preferences=tone_preferences,
            communication_style=communication_style,
            interaction_history=interaction_history,
            context_preferences=context_preferences,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

@router.delete("/{user_id}")
async def delete_profile(user_id: str):
    """
    Delete a user profile
    """
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return {"message": "Profile deleted successfully"}

@router.get("/{user_id}/validate")
async def validate_profile(user_id: str):
    """
    Validate a user profile and return analysis
    """
    try:
        # Get profile
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT tone_preferences, context_preferences FROM user_profiles WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="User profile not found")
            
            tone_preferences = json.loads(row['tone_preferences'])
            context_preferences = json.loads(row['context_preferences']) if row['context_preferences'] else {}
        
        # Analyze profile
        parser = ProfileParser()
        profile_data = {
            'user_id': user_id,
            'tone_preferences': tone_preferences,
            'context_preferences': context_preferences
        }
        
        profile = parser.parse_profile(profile_data)
        
        # Generate analysis
        analysis = {
            'profile_valid': True,
            'tone_analysis': {
                'formality_level': _get_tone_description(profile.tone_preferences.formality, 'formality'),
                'enthusiasm_level': _get_tone_description(profile.tone_preferences.enthusiasm, 'enthusiasm'),
                'verbosity_level': _get_tone_description(profile.tone_preferences.verbosity, 'verbosity'),
                'empathy_level': _get_tone_description(profile.tone_preferences.empathy_level, 'empathy'),
                'humor_level': _get_tone_description(profile.tone_preferences.humor, 'humor')
            },
            'context_preferences': {},
            'recommendations': []
        }
        
        # Analyze context preferences
        if profile.context_preferences:
            for context in ['work', 'personal', 'academic']:
                context_pref = getattr(profile.context_preferences, context, None)
                if context_pref:
                    analysis['context_preferences'][context] = {
                        'formality': _get_tone_description(context_pref.formality, 'formality'),
                        'enthusiasm': _get_tone_description(context_pref.enthusiasm, 'enthusiasm'),
                        'verbosity': _get_tone_description(context_pref.verbosity, 'verbosity'),
                        'empathy': _get_tone_description(context_pref.empathy_level, 'empathy'),
                        'humor': _get_tone_description(context_pref.humor, 'humor')
                    }
        
        # Generate recommendations
        if profile.tone_preferences.formality.value == 'formal':
            analysis['recommendations'].append("Consider adding casual context for more relaxed conversations")
        
        if profile.tone_preferences.enthusiasm.value == 'low':
            analysis['recommendations'].append("Consider increasing enthusiasm for more engaging interactions")
        
        if profile.tone_preferences.verbosity.value == 'detailed':
            analysis['recommendations'].append("Consider adding concise context for quick responses")
        
        if profile.tone_preferences.humor.value == 'heavy':
            analysis['recommendations'].append("Consider adding professional context for formal situations")
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating profile: {str(e)}")

def _get_tone_description(value: str, tone_type: str) -> str:
    """Convert tone value to human-readable description"""
    if tone_type == 'formality':
        if value == 'casual':
            return "Very casual and informal"
        elif value == 'professional':
            return "Professional and balanced"
        else:
            return "Very formal and structured"
    elif tone_type == 'enthusiasm':
        if value == 'low':
            return "Calm and reserved"
        elif value == 'medium':
            return "Moderately enthusiastic"
        else:
            return "Very enthusiastic and energetic"
    elif tone_type == 'verbosity':
        if value == 'concise':
            return "Brief and to the point"
        elif value == 'balanced':
            return "Moderately detailed"
        else:
            return "Very detailed and comprehensive"
    elif tone_type == 'empathy':
        if value == 'low':
            return "Direct and factual"
        elif value == 'medium':
            return "Moderately empathetic"
        else:
            return "Very empathetic and understanding"
    elif tone_type == 'humor':
        if value == 'none':
            return "Serious and straightforward"
        elif value == 'light':
            return "Occasionally lighthearted"
        elif value == 'moderate':
            return "Moderately humorous"
        else:
            return "Very humorous and playful"
    else:
        return "Standard" 