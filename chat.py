import streamlit as st
import google.generativeai as genai
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# load_dotenv()

# --- Configuration and Data Loading ---

# JSON file ka naam define karein
JSON_FILE = 'response.json'

@st.cache_data
def load_rag_data(file_path):
    """
    Load RAG data from response.json file - keeps your existing data as-is
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
            
    except FileNotFoundError:
        st.warning(f"Warning: RAG file '{file_path}' not found. Chatbot will use only Gemini API.")
        return {}
    except json.JSONDecodeError:
        st.error(f"Error: The file '{file_path}' is not a valid JSON file. Please check its format.")
        return {}
    except Exception as e:
        st.error(f"An unexpected error occurred during RAG data loading: {str(e)}")
        return {}

# Load environment variables from .env file
load_dotenv()

# Configure page with a custom theme
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Centered Chatbot CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

/* Global Reset */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    box-sizing: border-box;
}

/* Hide all Streamlit elements */
#MainMenu, footer, header, .stDeployButton, .stDecoration, 
.stToolbar, [data-testid="stToolbar"] {
    visibility: hidden !important;
    height: 0 !important;
    display: none !important;
}

/* Root styling - Dark elegance */
.stApp {
    background: #0a0a0f !important;
}

/* Main wrapper */
.main {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a1625 50%, #0a0a0f 100%) !important;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    padding: 0;
}

/* Chat container */
.chat-wrapper {
    max-width: 800px;
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    position: relative;
}

/* Premium Header */
.chat-header {
    background: linear-gradient(135deg, #1a1625, #2d1b35, #1a1625);
    border-bottom: 1px solid rgba(255, 107, 107, 0.1);
    padding: 32px 24px;
    text-align: center;
    backdrop-filter: blur(20px);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);
    border-radius: 0 0 24px 24px;
    margin-bottom: 16px;
}

.chat-title {
    font-size: 34px;
    font-weight: 700;
    background: linear-gradient(135deg, #ff6b6b, #feca57, #48cae4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
}

.chat-subtitle {
    color: rgba(255, 255, 255, 0.7);
    font-size: 15px;
    font-weight: 400;
}

/* Messages container */
.messages-container {
    flex: 1;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    overflow-y: auto;
    max-width: 800px;
    margin: 0 auto;
    width: 100%;
}

/* Chat bubbles */
[data-testid="stChatMessage"] > div {
    border-radius: 28px !important;
    padding: 20px 28px !important;
    max-width: 70% !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.5) !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

/* User message - right */
[data-testid="stChatMessage"][data-testid*="user"] {
    justify-content: flex-end !important;
}
[data-testid="stChatMessage"][data-testid*="user"] > div {
    background: linear-gradient(135deg, #ff6b6b, #ee5a52) !important;
    color: #fff !important;
    border-radius: 28px 28px 8px 28px !important;
}
[data-testid="stChatMessage"][data-testid*="user"] > div:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(255,107,107,0.35);
}

/* Assistant message - left */
[data-testid="stChatMessage"]:not([data-testid*="user"]) {
    justify-content: flex-start !important;
}
[data-testid="stChatMessage"]:not([data-testid*="user"]) > div {
    background: linear-gradient(135deg, #2d1b35, #1a1625) !important;
    color: #f8f9fa !important;
    border-radius: 28px 28px 28px 8px !important;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* Avatar styling */
[data-testid="stChatMessage"] img {
    width: 38px !important;
    height: 38px !important;
    border-radius: 50% !important;
    margin: 0 16px 6px 0 !important;
    box-shadow: 0 6px 16px rgba(0,0,0,0.4) !important;
    border: 2px solid rgba(255,107,107,0.3) !important;
}

/* Input container */
.stChatInputContainer {
    position: sticky !important;
    bottom: 24px !important;
    margin: 0 auto 24px auto !important;
    z-index: 100 !important;
    max-width: 800px !important;
    width: calc(100% - 48px) !important;
    display: flex;
    gap: 12px;
}
.stChatInputContainer > div {
    background: linear-gradient(135deg, #1a1625, #2d1b35) !important;
    border-radius: 32px !important;
    padding: 8px !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1);
    transition: all 0.3s ease;
}
.stChatInputContainer > div:focus-within {
    transform: translateY(-2px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.15);
}

/* Input text */
.stChatInputContainer textarea {
    background: transparent !important;
    color: #fff !important;
    font-size: 16px !important;
    padding: 18px 28px !important;
    border-radius: 28px !important;
}

/* Send button */
[data-testid="stChatInputSubmitButton"] {
    border-radius: 50% !important;
    width: 54px !important;
    height: 54px !important;
    box-shadow: 0 8px 28px rgba(255,107,107,0.45) !important;
    transition: all 0.3s ease;
}
[data-testid="stChatInputSubmitButton"]:hover {
    transform: scale(1.1) translateY(-2px);
}
[data-testid="stChatInputSubmitButton"]:active {
    transform: scale(0.95);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.05);
    border-radius: 8px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ff6b6b, #feca57);
    border-radius: 8px;
}

/* Code block */
pre {
    background: rgba(0,0,0,0.5) !important;
    border-radius: 20px !important;
    padding: 20px !important;
}
code {
    background: rgba(255,107,107,0.15) !important;
    padding: 4px 8px !important;
    border-radius: 6px !important;
}

/* Animations */
@keyframes slideUp {
    from { opacity:0; transform: translateY(20px) scale(0.98); }
    to { opacity:1; transform: translateY(0) scale(1);}
}

/* Mobile tweaks */
@media (max-width: 768px){
    .messages-container {padding: 16px;}
    .chat-title {font-size: 28px;}
    [data-testid="stChatMessage"] > div {max-width: 85% !important;}
}
</style>

""", unsafe_allow_html=True)

class Chatbot:
    def __init__(self):
        """Initialize the chatbot with Gemini API."""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise Exception("GEMINI_API_KEY environment variable not found. Check your .env file.")
                
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.chat = self.model.start_chat(history=[])
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini API: {str(e)}")
    
    def generate_response(self, user_input: str) -> str:
        """Generate response from the model."""
        try:
            response = self.chat.send_message(user_input)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

def main():
    # --- RAG Data Loading ---
    # Load and cache RAG data
    rag_data = load_rag_data(JSON_FILE) 
    
    # Header
    st.markdown("""
    <div class="chat-header">
        <div class="chat-title">
            🤖 AI Chat Assistant
        </div>
        <div class="chat-subtitle">Powered by Gemini AI + RAG • Ask me anything</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Initialize session state
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = Chatbot()
        except Exception as e:
            st.error(f"❌ Failed to initialize chatbot: {str(e)}")
            st.info("💡 Please check your API key configuration.")
            st.stop()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Welcome screen for empty chat
    if not st.session_state.messages:
        rag_status = "✅ RAG Data Loaded" if rag_data else "⚠️ Only AI Mode"
        st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-title">👋 Welcome!</div>
            <div class="welcome-subtitle">
                I'm your AI assistant with RAG capabilities. I can answer from my knowledge base or use AI.<br>
                Status: {rag_status} | Start a conversation by typing below.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    try:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here...", key="chat_input"):
            # Display user message
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            response = ""
            user_query_clean = prompt.strip().lower()

            # --- Simple RAG Logic - No smart matching ---
            response = ""
            
            # RAG: Just load your data and let Gemini handle everything
            if rag_data:
                # Pass RAG data to Gemini for context
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Thinking..."):
                        # Include RAG data as context for Gemini
                        enhanced_prompt = f"""
                        User question: {prompt}
                        
                        Available user data: {json.dumps(rag_data, indent=2)}
                        
                        Please answer the user's question using the provided data when relevant.
                        """
                        response = st.session_state.chatbot.generate_response(enhanced_prompt)
                    st.markdown(response)
            else:
                # No RAG data - just use Gemini
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Thinking..."):
                        response = st.session_state.chatbot.generate_response(prompt)
                    st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Auto-scroll to bottom
            st.rerun()
            
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        st.info("🔧 Please check your configuration and try again.")
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
