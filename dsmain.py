'''import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
WEAKNESS_THRESHOLD = 0.3
MIN_ATTEMPTS_FOR_ANALYSIS = 5
LEVEL_OPTIONS = ["Beginner", "Intermediate", "Advanced"]
TOPICS = {
    "aptitude": ["quantitative", "logical"],
    "coding": ["arrays", "trees", "dynamic_programming"],
    "hr": ["behavioral"]
}

# Model Initialization
@st.cache_resource(show_spinner=False)
def load_model():
    try:
        logger.info("Connecting to Ollama...")
        return Ollama(
            model="phi3",
            base_url="http://localhost:11434",
            request_timeout=120,
            temperature=0.7
        )
    except Exception as e:
        error_msg = f"""
        ⚠️ AI Connection Failed ⚠️
        1. Please ensure Ollama is running
        2. Verify Phi-3 is installed
        
        Try these commands:
        ```
        ollama pull phi3
        ollama serve
        ```
        Error details: {str(e)}
        """
        st.error(error_msg)
        logger.error(f"Model init error: {str(e)}")
        return None

def initialize_session_state():
    """Initialize session state with defaults"""
    if "model" not in st.session_state:
        st.session_state.model = load_model()
    
    if "weakness_data" not in st.session_state:
        st.session_state.weakness_data = {
            topic: {subtopic: {"attempts": 0, "correct": 0, "last_attempt": None}
            for subtopic in subtopics}
            for topic, subtopics in TOPICS.items()
        }
    
    if "level" not in st.session_state:
        st.session_state.level = "Beginner"
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def get_model_response(prompt: str) -> str:
    """Get response with connection checks"""
    if not st.session_state.model:
        return "🔴 AI service unavailable. Please check Ollama is running."
    
    try:
        messages = [
            ChatMessage(role="system", content=f"""
            You are a placement coach helping a {st.session_state.level} student.
            Respond in 2-3 concise sentences.
            """),
            ChatMessage(role="user", content=prompt)
        ]
        
        response = st.session_state.model.chat(messages)
        return response.message.content
    except Exception as e:
        logger.error(f"Response error: {str(e)}")
        return "🔄 Please try again or check your Ollama connection"

def main():
    st.set_page_config(page_title="Placement Pro", layout="wide")
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Menu", ["Chat Coach", "Performance Analysis"])
        
        st.divider()
        st.subheader("User Profile")
        st.session_state.level = st.selectbox(
            "Your Level",
            LEVEL_OPTIONS,
            index=LEVEL_OPTIONS.index(st.session_state.level)
        )
        
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
    
    # Main Content
    if page == "Performance Analysis":
        st.title("Performance Dashboard")
        # Add your analysis components here
    else:
        st.title("Placement Coach")
        
        # Display chat
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # Input
        if prompt := st.chat_input(f"Ask your {st.session_state.level} question..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                response = get_model_response(prompt)
                st.write(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()'''

import streamlit as st
import logging
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== MODEL MANAGEMENT ==========
@st.cache_resource(show_spinner=False)
def initialize_model():
    """Initialize with automatic model fallback"""
    model_configs = [
        {
            "name": "phi3",
            "max_tokens": 1024,
            "temperature": 0.7,
            "system_prompt": "You are an expert placement coach for computer science students."
        },
        {
            "name": "llama3.2", 
            "max_tokens": 512,
            "temperature": 0.6,
            "system_prompt": "You help students prepare for technical interviews."
        },
        {
            "name": "llama3.1",
            "max_tokens": 256,
            "temperature": 0.5,
            "system_prompt": "Provide short answers to interview questions."
        }
    ]
    
    for config in model_configs:
        try:
            llm = Ollama(
                model=config["name"],
                request_timeout=120,
                temperature=config["temperature"]
            )
            # Test connection
            test_response = llm.chat([ChatMessage(role="user", content="ping")])
            if test_response:
                logger.info(f"Model loaded: {config['name']}")
                return llm, config
        except Exception as e:
            logger.warning(f"Model {config['name']} failed: {str(e)}")
            continue
    
    return None, None

# ========== SESSION MANAGEMENT ==========
def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model_info" not in st.session_state:
        st.session_state.model_info = None

# ========== CHAT INTERFACE ==========
def display_chat():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

def handle_user_input():
    if prompt := st.chat_input("Ask about placements..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            try:
                messages = [
                    ChatMessage(role="system", content=st.session_state.model_info["system_prompt"])
                ]
                messages.extend([
                    ChatMessage(role=msg["role"], content=msg["content"])
                    for msg in st.session_state.messages[-6:]  # Keep last 3 exchanges
                ])
                
                with st.spinner("Thinking..."):
                    response = st.session_state.llm.chat(
                        messages=messages,
                        max_tokens=st.session_state.model_info["max_tokens"]
                    )
                    st.write(response.message.content)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response.message.content}
                    )
            except Exception as e:
                logger.error(f"Chat error: {str(e)}")
                st.error("Failed to generate response. Please try again.")

# ========== MAIN APP ==========
def main():
    st.set_page_config(
        page_title="Placement Pro",
        page_icon="💼",
        layout="wide"
    )
    st.title("AI Placement Coach")
    
    # Initialize
    initialize_session()
    
    if not st.session_state.get("llm"):
        with st.spinner("Loading AI model..."):
            llm, model_info = initialize_model()
            if not llm:
                st.error("""
                ❌ No working models found. Please:
                1. Ensure Ollama is running (`ollama serve`)
                2. Check models (`ollama list`)
                3. Restart this app
                """)
                return
            st.session_state.llm = llm
            st.session_state.model_info = model_info
    
    # Display model info
    with st.sidebar:
        st.subheader("Current Model")
        if st.session_state.model_info:
            st.write(f"**Model**: {st.session_state.model_info['name']}")
            st.write(f"**Max Tokens**: {st.session_state.model_info['max_tokens']}")
        
        if st.button("🔄 Restart Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    # Chat interface
    display_chat()
    handle_user_input()

if __name__ == "__main__":
    main()