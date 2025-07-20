import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_user_profile(user_id, tone_preferences, communication_style, interaction_history, context_preferences):
    """Create a new user profile (new schema)"""
    try:
        payload = {
            "user_id": user_id,
            "tone_preferences": tone_preferences,
            "communication_style": communication_style,
            "interaction_history": interaction_history,
            "context_preferences": context_preferences
        }
        response = requests.post(
            f"{API_BASE_URL}/api/profile/",
            json=payload
        )
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def send_chat_message(user_id, message, context=None):
    """Send a chat message and get response"""
    try:
        payload = {
            "user_id": user_id,
            "message": message
        }
        if context:
            payload["context"] = context
        
        response = requests.post(
            f"{API_BASE_URL}/api/chat/",
            json=payload,
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            try:
                error_data = response.json()
                return False, error_data
            except:
                return False, response.text
    except requests.exceptions.ConnectionError:
        return False, "Connection error: API server is not responding"
    except requests.exceptions.Timeout:
        return False, "Timeout: Request took too long"
    except Exception as e:
        return False, f"Error: {str(e)}"

def submit_feedback(user_id, feedback_type, value=None, corrections=None, preferences=None, context=None):
    """Submit feedback for learning"""
    try:
        payload = {
            "user_id": user_id,
            "type": feedback_type,
            "value": value,
            "corrections": corrections,
            "preferences": preferences,
            "context": context
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/chat/feedback",
            json=payload
        )
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def get_user_memory(user_id):
    """Get user's memory data"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/chat/{user_id}/memory")
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def get_user_profile(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/api/profile/{user_id}")
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def clear_user_memory(user_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/api/memory/{user_id}")
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def export_user_profile(user_id):
    success, profile = get_user_profile(user_id)
    if success:
        return json.dumps(profile, indent=2)
    return None

def export_user_memory(user_id):
    success, memory = get_user_memory(user_id)
    if success:
        return json.dumps(memory, indent=2)
    return None

def import_user_profile(user_id, profile_json):
    try:
        profile = json.loads(profile_json)
        # Overwrite user_id to ensure correct assignment
        profile['user_id'] = user_id
        response = requests.post(f"{API_BASE_URL}/api/profile/", json=profile)
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def import_user_memory(user_id, memory_json):
    # Placeholder: implement if backend supports memory import
    return False, "Not supported by backend."

def main():
    st.set_page_config(
        page_title="AI Tone Adaptation System",
        page_icon="🎭",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .response-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .feedback-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .sidebar-section {
        margin-bottom: 2rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
    }
    .metric-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎭 AI Tone Adaptation System</h1>', unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("❌ API server is not running. Please start the FastAPI server first.")
        st.info("Run: `uvicorn main:app --reload` in your terminal")
        return
    
    st.success("✅ API server is running and healthy!")
    
    # Enum options
    FORMALITY_OPTIONS = ["casual", "professional", "formal"]
    ENTHUSIASM_OPTIONS = ["low", "medium", "high"]
    VERBOSITY_OPTIONS = ["concise", "balanced", "detailed"]
    EMPATHY_OPTIONS = ["low", "medium", "high"]
    HUMOR_OPTIONS = ["none", "light", "moderate", "heavy"]
    TECHNICAL_OPTIONS = ["beginner", "intermediate", "advanced"]
    AGE_GROUP_OPTIONS = ["teen", "young_adult", "adult", "senior"]
    
    # Sidebar for user management
    with st.sidebar:
        st.markdown('<h3 class="sub-header">👤 User Management</h3>', unsafe_allow_html=True)
        
        # User ID input
        user_id = st.text_input("User ID", value="demo_user", help="Enter a unique user identifier")
        
        # Profile creation section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📝 Create Profile")
        st.markdown("**General Tone Preferences**")
        col1, col2 = st.columns(2)
        with col1:
            formality = st.selectbox("Formality", FORMALITY_OPTIONS, index=1)
            enthusiasm = st.selectbox("Enthusiasm", ENTHUSIASM_OPTIONS, index=1)
            verbosity = st.selectbox("Verbosity", VERBOSITY_OPTIONS, index=1)
        with col2:
            empathy = st.selectbox("Empathy", EMPATHY_OPTIONS, index=1)
            humor = st.selectbox("Humor", HUMOR_OPTIONS, index=1)
        tone_preferences = {
            "formality": formality,
            "enthusiasm": enthusiasm,
            "verbosity": verbosity,
            "empathy_level": empathy,
            "humor": humor
        }
        st.markdown("**Communication Style**")
        col3, col4 = st.columns(2)
        with col3:
            preferred_greeting = st.text_input("Preferred Greeting", value="Hello")
            technical_level = st.selectbox("Technical Level", TECHNICAL_OPTIONS, index=1)
        with col4:
            cultural_context = st.text_input("Cultural Context", value="")
            age_group = st.selectbox("Age Group", AGE_GROUP_OPTIONS, index=2)
        communication_style = {
            "preferred_greeting": preferred_greeting,
            "technical_level": technical_level,
            "cultural_context": cultural_context,
            "age_group": age_group
        }
        st.markdown("**Context-Specific Preferences (Optional)**")
        context_preferences = {}
        for context in ["work", "personal", "academic"]:
            with st.expander(f"{context.capitalize()} Context Preferences"):
                enable_context = st.checkbox(f"Enable {context} context preferences", key=f"enable_{context}")
                if enable_context:
                    c1, c2 = st.columns(2)
                    with c1:
                        c_formality = st.selectbox(f"Formality ({context})", FORMALITY_OPTIONS, index=1, key=f"{context}_formality")
                        c_enthusiasm = st.selectbox(f"Enthusiasm ({context})", ENTHUSIASM_OPTIONS, index=1, key=f"{context}_enthusiasm")
                        c_verbosity = st.selectbox(f"Verbosity ({context})", VERBOSITY_OPTIONS, index=1, key=f"{context}_verbosity")
                    with c2:
                        c_empathy = st.selectbox(f"Empathy ({context})", EMPATHY_OPTIONS, index=1, key=f"{context}_empathy")
                        c_humor = st.selectbox(f"Humor ({context})", HUMOR_OPTIONS, index=1, key=f"{context}_humor")
                    context_preferences[context] = {
                        "formality": c_formality,
                        "enthusiasm": c_enthusiasm,
                        "verbosity": c_verbosity,
                        "empathy_level": c_empathy,
                        "humor": c_humor
                    }
        st.markdown("**Interaction History (Optional)**")
        col5, col6 = st.columns(2)
        with col5:
            total_interactions = st.number_input("Total Interactions", min_value=0, value=0)
            successful_tone_matches = st.number_input("Successful Tone Matches", min_value=0, value=0)
        with col6:
            feedback_score = st.slider("Feedback Score", 0.0, 5.0, 0.0, 0.1)
            last_interaction = st.text_input("Last Interaction (timestamp)", value="")
        interaction_history = {
            "total_interactions": total_interactions,
            "successful_tone_matches": successful_tone_matches,
            "feedback_score": feedback_score,
            "last_interaction": last_interaction if last_interaction else None
        }
        if st.button("Create/Update Profile", type="primary"):
            success, result = create_user_profile(
                user_id,
                tone_preferences,
                communication_style,
                interaction_history,
                context_preferences if context_preferences else None
            )
            if success:
                st.success("✅ Profile created successfully!")
            else:
                st.error(f"❌ Failed to create profile: {result}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Memory section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🧠 Memory Management")
        if st.button("Get Memory"):
            success, memory = get_user_memory(user_id)
            if success:
                st.json(memory)
            else:
                st.error(f"Failed to get memory: {memory}")
        if st.button("Clear Memory", type="secondary"):
            success, result = clear_user_memory(user_id)
            if success:
                st.success("✅ Memory cleared successfully!")
            else:
                st.error(f"❌ Failed to clear memory: {result}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Export/Import section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📤 Export/Import")
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("Export Profile"):
                profile_json = export_user_profile(user_id)
                if profile_json:
                    st.download_button("Download Profile JSON", profile_json, file_name=f"{user_id}_profile.json")
                else:
                    st.error("Failed to export profile.")
            if st.button("Export Memory"):
                memory_json = export_user_memory(user_id)
                if memory_json:
                    st.download_button("Download Memory JSON", memory_json, file_name=f"{user_id}_memory.json")
                else:
                    st.error("Failed to export memory.")
        with col_exp2:
            profile_file = st.file_uploader("Import Profile JSON", type=["json"], key="import_profile")
            if profile_file:
                profile_json = StringIO(profile_file.getvalue().decode("utf-8")).read()
                if st.button("Import Profile"):
                    success, result = import_user_profile(user_id, profile_json)
                    if success:
                        st.success("✅ Profile imported successfully!")
                    else:
                        st.error(f"❌ Failed to import profile: {result}")
            memory_file = st.file_uploader("Import Memory JSON", type=["json"], key="import_memory")
            if memory_file:
                memory_json = StringIO(memory_file.getvalue().decode("utf-8")).read()
                if st.button("Import Memory"):
                    success, result = import_user_memory(user_id, memory_json)
                    if success:
                        st.success("✅ Memory imported successfully!")
                    else:
                        st.error(f"❌ Failed to import memory: {result}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Profile view section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 👁️ View Current Profile")
        if st.button("Get Profile"):
            success, profile = get_user_profile(user_id)
            if success:
                st.json(profile)
            else:
                st.error(f"Failed to get profile: {profile}")
        st.markdown("</div>", unsafe_allow_html=True)
    # Main content area
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Interface", "📊 Analytics", "🎯 Feedback Learning", "🔧 System Info"])
    
    # Chat Interface Tab
    with tab1:
        st.markdown('<h2 class="sub-header">💬 Interactive Chat</h2>', unsafe_allow_html=True)
        
        # Context selection
        context = st.selectbox(
            "Message Context",
            ["", "work", "personal", "academic"],
            help="Select the context for your message (optional)"
        )
        
        # Message input
        message = st.text_area("Your Message", height=100, placeholder="Type your message here...")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            send_button = st.button("Send Message", type="primary", disabled=not message.strip())
        
        with col2:
            if st.button("Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Send message
        if send_button and message.strip():
            with st.spinner("Processing message..."):
                success, response = send_chat_message(user_id, message, context if context else None)
                
                if success:
                    # Check if this is the first message (profile might have been auto-created)
                    if len(st.session_state.chat_history) == 0:
                        st.info("ℹ️ A default profile was automatically created for you. You can customize your preferences in the sidebar.")
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now(),
                        "user_message": message,
                        "context": context if context else "unknown",
                        "response": response
                    })
                    
                    # Display response
                    st.markdown('<div class="response-box">', unsafe_allow_html=True)
                    st.markdown(f"**AI Response:** {response.get('response', 'No response received')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Display analysis
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Detected Context", response.get('context', 'Unknown'))
                        confidence_values = response.get('context_confidence', {}).values()
                        if confidence_values:
                            st.metric("Confidence", f"{max(confidence_values):.2f}")
                        else:
                            st.metric("Confidence", "N/A")
                    
                    with col2:
                        applied_tone = response.get('applied_tone', {})
                        st.metric("Formality", applied_tone.get('formality', 'N/A'))
                        st.metric("Enthusiasm", applied_tone.get('enthusiasm', 'N/A'))
                    
                    with col3:
                        st.metric("Verbosity", applied_tone.get('verbosity', 'N/A'))
                        st.metric("Empathy", applied_tone.get('empathy_level', applied_tone.get('empathy', 'N/A')))
                    
                    # Context indicators
                    context_indicators = response.get('context_indicators', {})
                    if context_indicators:
                        st.markdown("**Context Indicators:**")
                        for context_type, indicators in context_indicators.items():
                            if indicators:
                                st.write(f"- {context_type}: {', '.join(indicators)}")
                    
                    st.rerun()
                else:
                    if isinstance(response, str):
                        st.error(f"❌ Failed to send message: {response}")
                    else:
                        st.error(f"❌ Failed to send message: {response.get('detail', 'Unknown error')}")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### Chat History")
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"Message {len(st.session_state.chat_history) - i} - {chat['timestamp'].strftime('%H:%M:%S')}"):
                    st.write(f"**You:** {chat['user_message']}")
                    st.write(f"**Context:** {chat['context']}")
                    st.write(f"**AI:** {chat['response']['response']}")
                    
                    # Show tone analysis
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Applied Tone:**")
                        applied_tone = chat['response'].get('applied_tone', {})
                        for tone, level in applied_tone.items():
                            # Handle empathy_level vs empathy field name
                            display_name = tone.replace('_', ' ').title()
                            st.write(f"- {display_name}: {level}")
                    
                    with col2:
                        st.write("**Context Confidence:**")
                        context_confidence = chat['response'].get('context_confidence', {})
                        for context, confidence in context_confidence.items():
                            st.write(f"- {context}: {confidence:.2f}")
    
    # Analytics Tab
    with tab2:
        st.markdown('<h2 class="sub-header">📊 System Analytics</h2>', unsafe_allow_html=True)
        
        if st.session_state.chat_history:
            # Create analytics from chat history
            df = pd.DataFrame(st.session_state.chat_history)
            
            # Tone analysis over time
            st.markdown("### Tone Adaptation Over Time")
            
            tone_data = []
            for chat in st.session_state.chat_history:
                applied_tone = chat['response'].get('applied_tone', {})
                # Convert string tone values to numeric for plotting
                def tone_to_numeric(value):
                    if isinstance(value, (int, float)):
                        return float(value)
                    elif isinstance(value, str):
                        # Map string values to numeric
                        tone_mapping = {
                            'low': 0.2, 'medium': 0.5, 'high': 0.8,
                            'casual': 0.2, 'professional': 0.7, 'formal': 0.9,
                            'concise': 0.3, 'balanced': 0.5, 'detailed': 0.8,
                            'none': 0.0, 'light': 0.3, 'moderate': 0.6, 'heavy': 0.9
                        }
                        return tone_mapping.get(value.lower(), 0.5)
                    return 0.5
                
                tone_data.append({
                    'timestamp': chat['timestamp'],
                    'formality': tone_to_numeric(applied_tone.get('formality', 0.5)),
                    'enthusiasm': tone_to_numeric(applied_tone.get('enthusiasm', 0.5)),
                    'verbosity': tone_to_numeric(applied_tone.get('verbosity', 0.5)),
                    'empathy': tone_to_numeric(applied_tone.get('empathy_level', applied_tone.get('empathy', 0.5))),
                    'humor': tone_to_numeric(applied_tone.get('humor', 0.5))
                })
            
            if tone_data:
                tone_df = pd.DataFrame(tone_data)
                
                # Tone trends
                fig = go.Figure()
                for tone in ['formality', 'enthusiasm', 'verbosity', 'empathy', 'humor']:
                    if tone in tone_df.columns:
                        fig.add_trace(go.Scatter(
                            x=tone_df['timestamp'],
                            y=tone_df[tone],
                            mode='lines+markers',
                            name=tone.capitalize()
                        ))
                
                fig.update_layout(
                    title="Tone Adaptation Trends",
                    xaxis_title="Time",
                    yaxis_title="Tone Level",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Context distribution
                context_counts = df['context'].value_counts()
                fig_pie = px.pie(
                    values=context_counts.values,
                    names=context_counts.index,
                    title="Message Context Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Response length analysis
            response_lengths = [len(chat['response']['response']) for chat in st.session_state.chat_history]
            fig_hist = px.histogram(
                x=response_lengths,
                title="Response Length Distribution",
                labels={'x': 'Response Length (characters)', 'y': 'Frequency'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)

            # Show interaction history metrics
            st.markdown("### Interaction History Metrics")
            success, profile = get_user_profile(user_id)
            if success and profile:
                ih = profile.get("interaction_history", {})
                total_interactions = ih.get("total_interactions", 0)
                successful_matches = ih.get("successful_tone_matches", 0)
                feedback_score = ih.get("feedback_score", 0.0)
                last_interaction = ih.get("last_interaction", "N/A")
                
                st.metric("Total Interactions", total_interactions)
                st.metric("Successful Tone Matches", successful_matches)
                if isinstance(feedback_score, (int, float)):
                    st.metric("Feedback Score", f"{feedback_score:.2f}")
                else:
                    st.metric("Feedback Score", str(feedback_score))
                st.metric("Last Interaction", str(last_interaction))
        else:
            st.info("Start chatting to see analytics!")
    
    # Feedback Learning Tab
    with tab3:
        st.markdown('<h2 class="sub-header">🎯 Feedback Learning</h2>', unsafe_allow_html=True)
        
        if st.session_state.chat_history:
            # Select message to provide feedback on
            message_options = [f"Message {i+1}: {chat['user_message'][:50]}..." 
                             for i, chat in enumerate(st.session_state.chat_history)]
            
            selected_message = st.selectbox("Select message to provide feedback on:", message_options)
            
            if selected_message:
                message_index = int(selected_message.split(":")[0].split()[-1]) - 1
                selected_chat = st.session_state.chat_history[message_index]
                
                st.markdown("### Selected Message")
                st.write(f"**Your message:** {selected_chat['user_message']}")
                st.write(f"**AI response:** {selected_chat['response']['response']}")
                
                # Feedback form
                st.markdown("### Provide Feedback")
                
                feedback_type = st.selectbox("Feedback Type", ["rating", "correction", "preference"])
                
                if feedback_type == "rating":
                    rating = st.slider("Rate the response (1-5)", 1, 5, 3)
                    feedback_value = rating
                elif feedback_type == "correction":
                    st.write("Provide tone corrections:")
                    corrections = {}
                    for tone in ["formality", "enthusiasm", "verbosity", "empathy", "humor"]:
                        correction = st.slider(f"{tone.capitalize()} correction", -0.5, 0.5, 0.0, 0.1)
                        if correction != 0:
                            corrections[tone] = correction
                    feedback_value = corrections
                else:  # preference
                    st.write("Provide new preferences:")
                    preferences = {}
                    for tone in ["formality", "enthusiasm", "verbosity", "empathy", "humor"]:
                        pref = st.slider(f"Preferred {tone}", 0.0, 1.0, 0.5, 0.1)
                        preferences[tone] = pref
                    feedback_value = preferences
                
                if st.button("Submit Feedback", type="primary"):
                    with st.spinner("Processing feedback..."):
                        success, result = submit_feedback(
                            user_id=user_id,
                            feedback_type=feedback_type,
                            value=feedback_value if feedback_type == "rating" else None,
                            corrections=feedback_value if feedback_type == "correction" else None,
                            preferences=feedback_value if feedback_type == "preference" else None,
                            context=selected_chat['context']
                        )
                        
                        if success:
                            st.success("✅ Feedback submitted successfully!")
                            st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
                            st.json(result)
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.error(f"❌ Failed to submit feedback: {result}")
        else:
            st.info("Start chatting to provide feedback!")
    
    # System Info Tab
    with tab4:
        st.markdown('<h2 class="sub-header">🔧 System Information</h2>', unsafe_allow_html=True)
        
        # API Status
        st.markdown("### API Status")
        api_healthy = check_api_health()
        if api_healthy:
            st.success("✅ API Server: Running")
        else:
            st.error("❌ API Server: Not responding")
        
        # System Metrics
        st.markdown("### System Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Messages", len(st.session_state.chat_history))
            st.metric("Active User", user_id)
        
        with col2:
            if st.session_state.chat_history:
                avg_response_length = sum(len(chat['response']['response']) for chat in st.session_state.chat_history) / len(st.session_state.chat_history)
                st.metric("Avg Response Length", f"{avg_response_length:.0f} chars")
            else:
                st.metric("Avg Response Length", "N/A")
        
        with col3:
            # Show current profile info
            success, profile = get_user_profile(user_id)
            if success and profile:
                st.metric("Profile Status", "✅ Active")
            else:
                st.metric("Profile Status", "❌ Not Found")
            
            if st.session_state.chat_history:
                contexts = [chat['context'] for chat in st.session_state.chat_history]
                most_common_context = max(set(contexts), key=contexts.count)
                st.metric("Most Common Context", most_common_context)
            else:
                st.metric("Most Common Context", "N/A")
        
        # API Endpoints
        st.markdown("### Available API Endpoints")
        endpoints = [
            ("Health Check", "GET /health"),
            ("API Documentation", "GET /docs"),
            ("Create Profile", "POST /api/profile/"),
            ("Chat", "POST /api/chat/"),
            ("Submit Feedback", "POST /api/chat/feedback"),
            ("Get Memory", "GET /api/chat/{user_id}/memory"),
        ]
        
        for name, endpoint in endpoints:
            st.code(f"{name}: {endpoint}")
        
        # Current User Profile
        st.markdown("### Current User Profile")
        
        # Get current profile data
        success, profile = get_user_profile(user_id)
        if success and profile:
            profile_data = {
                "User ID": user_id,
                "Formality": profile.get("tone_preferences", {}).get("formality", "N/A"),
                "Enthusiasm": profile.get("tone_preferences", {}).get("enthusiasm", "N/A"),
                "Verbosity": profile.get("tone_preferences", {}).get("verbosity", "N/A"),
                "Empathy": profile.get("tone_preferences", {}).get("empathy_level", "N/A"),
                "Humor": profile.get("tone_preferences", {}).get("humor", "N/A"),
                "Preferred Greeting": profile.get("communication_style", {}).get("preferred_greeting", "N/A"),
                "Technical Level": profile.get("communication_style", {}).get("technical_level", "N/A"),
                "Cultural Context": profile.get("communication_style", {}).get("cultural_context", "N/A"),
                "Age Group": profile.get("communication_style", {}).get("age_group", "N/A"),
                "Total Interactions": profile.get("interaction_history", {}).get("total_interactions", "N/A"),
                "Successful Tone Matches": profile.get("interaction_history", {}).get("successful_tone_matches", "N/A"),
                "Feedback Score": profile.get("interaction_history", {}).get("feedback_score", "N/A"),
                "Last Interaction": profile.get("interaction_history", {}).get("last_interaction", "N/A")
            }
            
            for key, value in profile_data.items():
                if isinstance(value, (int, float)) and value != "N/A":
                    try:
                        st.metric(key, f"{value:.2f}")
                    except (ValueError, TypeError):
                        st.metric(key, str(value))
                else:
                    st.metric(key, str(value))
        else:
            st.info("No profile found for this user. Create a profile in the sidebar first.")

if __name__ == "__main__":
    main() 