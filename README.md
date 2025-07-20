# AI Tone Adaptation System - Comprehensive Implementation

A complete FastAPI-based AI system that adapts its communication tone based on user profiles, context, and feedback. Built from scratch without framework dependencies, featuring advanced memory management and learning capabilities.

## 🎯 **Core Features**

### **Enhanced User Profile System**
- **Comprehensive Tone Preferences**: Formality, enthusiasm, verbosity, empathy, and humor levels
- **Communication Style**: Preferred greetings, technical level, cultural context, age group
- **Interaction History**: Track total interactions, successful matches, feedback scores
- **Context-Specific Preferences**: Different tone settings for work, personal, and academic contexts

### **Advanced Memory Architecture**
- **Short-term Memory**: Circular buffer storing last 10 exchanges per session
- **Long-term Memory**: SQLite database with timestamp-based decay and learning
- **Memory Analytics**: Context distribution, tone patterns, learning metrics
- **Memory Management**: Automatic cleanup, size limits (50KB per user)

### **Intelligent Tone Adaptation Engine**
- **Profile Parser**: Extract tone indicators from user profiles
- **Context Analyzer**: Understand conversation context and topic
- **Tone Generator**: Modify response style based on preferences
- **Feedback Processor**: Learn from user reactions and explicit feedback

### **Bonus Features**
- **Emotion Detection**: Detect user emotional state from messages
- **Memory Analytics**: Detailed insights into conversation patterns
- **Performance Optimization**: < 2s response time, < 100ms memory lookup
- **Concurrent Support**: 50+ simultaneous conversations

## 🏗️ **Architecture**

```
User Memory Store
├── Profile Data (Enhanced JSON Schema)
├── Conversation History (Circular Buffer)
├── Tone Patterns (Key-Value Store)
├── Feedback Metrics (Time Series)
└── Context Embeddings (Vector Store)
```

## 📋 **API Endpoints**

### **Core Endpoints**
- `POST /api/chat` - Main conversation endpoint with tone adaptation
- `POST /api/profile` - Create/update user profile with enhanced schema
- `GET /api/profile/{user_id}` - Retrieve user profile
- `DELETE /api/profile/{user_id}` - Delete user profile

### **Memory Management**
- `GET /api/memory/{user_id}` - Get user's memory (short-term and long-term)
- `DELETE /api/memory/{user_id}` - Clear user's memory
- `GET /api/memory/{user_id}/short-term` - Get only short-term memory
- `GET /api/memory/{user_id}/long-term` - Get only long-term memory
- `GET /api/memory/{user_id}/analytics` - Get memory analytics and insights

### **Feedback & Learning**
- `POST /api/chat/feedback` - Submit feedback for tone adaptation learning
- `GET /api/chat/{user_id}/feedback` - Get feedback summary and recommendations

## 🗂️ **Project Structure**

```
├── api/
│   ├── chat.py         # POST /api/chat with tone adaptation
│   ├── profile.py      # Profile management with enhanced schema
│   └── memory.py       # Memory management endpoints
├── core/
│   ├── memory_manager.py   # Advanced memory system
│   ├── tone_engine.py      # Tone adaptation logic
│   ├── profile_parser.py   # Enhanced profile parsing
│   ├── context_analyzer.py # Context understanding
│   ├── feedback_processor.py # Learning from feedback
│   └── emotion_detector.py # Emotion detection (bonus)
├── tests/
│   ├── test_comprehensive.py # Complete test suite
│   ├── test_memory_manager.py
│   ├── test_tone_engine.py
│   └── test_performance.py
├── data/
│   └── users.db        # SQLite database
├── main.py             # FastAPI application
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## Project Structure

```
├── api/
│   ├── chat.py         # POST /api/chat
│   └── profile.py      # POST & GET /api/profile, GET /api/memory, DELETE /api/memory
├── core/
│   ├── memory_manager.py   # Handles memory (short & long term)
│   ├── tone_engine.py      # Tone adaptation logic
│   ├── profile_parser.py   # Parses user profile to tone indicators
│   ├── context_analyzer.py # Understands message context
│   └── feedback_processor.py # Learns from feedback
├── data/
│   ├── users.db         # SQLite database
│   └── redis_memory.py  # Redis or in-memory store setup
├── main.py              # FastAPI initialization with endpoints
├── requirements.txt      # Dependencies
└── README.md           # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Redis (optional, falls back to in-memory storage)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd personalized-tone-adaptation-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

### Interactive Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

#### User Profile Management
- `POST /api/profile` - Create or update user profile
- `GET /api/profile/{user_id}` - Retrieve user profile

#### Memory Management
- `GET /api/memory/{user_id}` - Get user's memory (short and long term)
- `DELETE /api/memory/{user_id}` - Clear user's memory

#### Chat Interface
- `POST /api/chat` - Send message and receive tone-adapted response

## Usage Examples

### Creating a User Profile
```bash
curl -X POST "http://localhost:8000/api/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "preferences": {
      "formality": 0.7,
      "enthusiasm": 0.8,
      "verbosity": 0.6,
      "empathy": 0.9,
      "humor": 0.4
    },
    "context_preferences": {
      "work": {"formality": 0.9, "enthusiasm": 0.5},
      "personal": {"formality": 0.3, "enthusiasm": 0.9},
      "academic": {"formality": 0.8, "enthusiasm": 0.6}
    }
  }'
```

### Sending a Chat Message
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hello, how are you today?",
    "context": "personal",
    "feedback": null
  }'
```

## Architecture

### Memory System
- **Short-term Memory**: Circular buffer storing last 10 exchanges per session
- **Long-term Memory**: SQLite database with timestamp-based decay
- **Memory Limits**: 50KB max per user with automatic cleanup

### Tone Adaptation Engine
- **Profile Parser**: Extracts tone preferences from user profiles
- **Context Analyzer**: Categorizes messages (work/personal/academic)
- **Tone Generator**: Applies tone adjustments based on profile + context
- **Feedback Processor**: Learns from user feedback to improve future responses

### Performance
- Supports 50+ concurrent users
- Response time < 200ms for typical requests
- Memory usage optimized with decay and cleanup

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run performance tests:
```bash
pytest tests/test_performance.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details 