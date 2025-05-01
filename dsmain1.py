import streamlit as st
import logging
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
import time
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== CONSTANTS ==========
LEVELS = ["Beginner", "Intermediate", "Advanced"]
DOMAINS = ["Aptitude", "Coding", "HR Interview"]

# ========== MODEL MANAGEMENT ==========
@st.cache_resource(show_spinner=False)
def initialize_model():
    """Initialize with automatic model fallback"""
    model_configs = [
        {
            "name": "phi3",
            "config": {
                "max_tokens": 1024,
                "temperature": 0.7,
                "num_ctx": 2048
            }
        },
        {
            "name": "llama3.2", 
            "config": {
                "max_tokens": 512,
                "temperature": 0.6,
                "num_ctx": 1024
            }
        }
    ]
    
    for model in model_configs:
        try:
            llm = Ollama(
                model=model["name"],
                request_timeout=60,
                **model["config"]
            )
            # Test connection
            test_response = llm.chat([ChatMessage(role="user", content="ping")])
            if test_response:
                logger.info(f"Model loaded: {model['name']}")
                return llm
        except Exception as e:
            logger.warning(f"Model {model['name']} failed: {str(e)}")
            continue
    
    return None

# ========== SESSION MANAGEMENT ==========
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "level" not in st.session_state:
        st.session_state.level = "Beginner"
    if "domain" not in st.session_state:
        st.session_state.domain = "Aptitude"

# ========== DOMAIN-SPECIFIC PROMPT ENGINEERING ==========
def get_system_prompt():
    level = st.session_state.level
    domain = st.session_state.domain
    
    prompts = {
        "Aptitude": {
            "Beginner": "Explain basic concepts with simple examples. Ask one practice question at a time.",
            "Intermediate": "Provide moderately challenging problems with step-by-step guidance.",
            "Advanced": "Pose complex problems requiring optimization. Focus on speed and accuracy."
        },
        "Coding": {
            "Beginner": "Teach fundamental concepts with code snippets. Focus on understanding.",
            "Intermediate": "Discuss algorithms with time complexity analysis. Provide coding challenges.",
            "Advanced": "Give real interview problems. Expect optimal solutions with clean code."
        },
        "HR Interview": {
            "Beginner": "Help structure basic answers using STAR method. Be encouraging.",
            "Intermediate": "Simulate mock interviews with constructive feedback.",
            "Advanced": "Challenge with tough behavioral questions. Critique rigorously."
        }
    }
    
    return f"""
    You are a {level}-level {domain} coach. {prompts[domain][level]}
    - Respond concisely (under 100 words)
    - Ask one focused question at a time
    - Provide actionable feedback
    - Adapt to student's progress
    """

# ========== OPTIMIZED RESPONSE GENERATION ==========
def generate_response(prompt: str):
    try:
        messages = [
            ChatMessage(role="system", content=get_system_prompt())
        ]
        messages.extend([
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in st.session_state.messages[-4:]  # Limited context
        ])
        
        # Start generation in background thread
        with ThreadPoolExecutor() as executor:
            future = executor.submit(
                st.session_state.llm.chat,
                messages=messages,
                max_tokens=256  # Faster responses
            )
            return future.result(timeout=30).message.content
            
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        return f"⚠️ Please rephrase your question. Error: {str(e)}"

# ========== STREAMLIT UI ==========
def main():
    st.set_page_config(
        page_title="Placement Pro+",
        page_icon="💼",
        layout="centered"
    )
    
    # Custom CSS for better UX
    st.markdown("""
    <style>
        .stChatInput {position: fixed; bottom: 2rem;}
        [data-testid="stSidebar"] {background: #f0f2f6;}
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize
    init_session()
    if "llm" not in st.session_state:
        with st.spinner("🚀 Loading AI Coach..."):
            st.session_state.llm = initialize_model()
            if not st.session_state.llm:
                st.error("Ollama service unavailable. Please run `ollama serve`")
                st.stop()
    
    # Sidebar Controls
    with st.sidebar:
        st.title("Coach Settings")
        st.session_state.level = st.selectbox(
            "Your Level", LEVELS, index=LEVELS.index(st.session_state.level)
        )
        st.session_state.domain = st.radio(
            "Focus Area", DOMAINS, index=DOMAINS.index(st.session_state.domain)
        )
        if st.button("🔄 New Session"):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        st.caption(f"Using: {st.session_state.llm.model}")
    
    # Main Chat Interface
    st.title(f"🧠 {st.session_state.level} {st.session_state.domain} Coach")
    
    # Display chat history
    for msg in st.session_state.messages:
        avatar = "👨‍💻" if msg["role"] == "user" else "🤖"
        st.chat_message(msg["role"], avatar=avatar).write(msg["content"])
    
    # User input
    if prompt := st.chat_input(f"Ask {st.session_state.domain} question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user", avatar="👨‍💻"):
            st.write(prompt)
        
        # Generate and stream response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analyzing..."):
                response = generate_response(prompt)
                if response:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                    st.write(response)
                else:
                    st.error("Response failed. Try simplifying your question.")

if __name__ == "__main__":
    main()