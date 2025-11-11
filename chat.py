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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

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

/* Base Light Theme */
body, .stApp {
    background: #ffffff !important;
    color: #111 !important;
}

/* Chat wrapper */
.chat-wrapper {
    max-width: 800px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background: #fff;
}

/* Header */
.chat-header {
    background: #f9f9f9;
    border-bottom: 1px solid #e5e5e5;
    padding: 28px 24px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    border-radius: 20px;
    margin: 20px auto;
    max-width: 820px;
}
.chat-title {
    font-size: 30px;
    font-weight: 700;
    background: linear-gradient(135deg, #007aff, #00c6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.chat-subtitle {
    color: #777;
    font-size: 15px;
    margin-top: 6px;
}

/* Messages */
.messages-container {
    flex: 1;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow-y: auto;
    max-width: 800px;
    margin: 0 auto;
}

/* Message Bubbles */
[data-testid="stChatMessage"] > div {
    border-radius: 20px !important;
    padding: 14px 18px !important;
    font-size: 16px !important;
    line-height: 1.5 !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

/* User bubble (Right side - Blue) */
[data-testid="stChatMessage"][data-testid*="user"] {
    justify-content: flex-end !important;
}
[data-testid="stChatMessage"][data-testid*="user"] > div {
    background: #007aff !important;
    color: #fff !important;
    border-radius: 20px 20px 4px 20px !important;
    box-shadow: 0 2px 8px rgba(0,122,255,0.2);
}
[data-testid="stChatMessage"][data-testid*="user"] > div:hover {
    transform: scale(1.02);
}

/* Assistant bubble (Left side - Light Gray) */
[data-testid="stChatMessage"]:not([data-testid*="user"]) {
    justify-content: flex-start !important;
}
[data-testid="stChatMessage"]:not([data-testid*="user"]) > div {
    background: #f2f2f7 !important;
    color: #111 !important;
    border-radius: 20px 20px 20px 4px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}

/* Avatars */
[data-testid="stChatMessage"] img {
    width: 36px !important;
    height: 36px !important;
    border-radius: 50% !important;
    margin: 0 12px 4px 0 !important;
}

/* Input Box */
.stChatInputContainer {
    position: sticky !important;
    bottom: 20px !important;
    max-width: 800px !important;
    margin: 0 auto;
    width: calc(100% - 40px) !important;
    z-index: 10;
}
.stChatInputContainer > div {
    background: #f2f2f7 !important;
    border-radius: 28px !important;
    padding: 6px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.stChatInputContainer textarea {
    background: transparent !important;
    color: #111 !important;
    font-size: 16px !important;
    padding: 14px 22px !important;
    border-radius: 20px !important;
}
[data-testid="stChatInputSubmitButton"] {
    border-radius: 50% !important;
    width: 46px !important;
    height: 46px !important;
    background: linear-gradient(135deg, #007aff, #00b4ff) !important;
    box-shadow: 0 4px 12px rgba(0,122,255,0.25);
}
[data-testid="stChatInputSubmitButton"]:hover {
    transform: scale(1.05);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 8px;
}

/* Code block */
pre {
    background: #f7f7f7 !important;
    color: #111 !important;
    border-radius: 10px !important;
    padding: 12px !important;
    overflow-x: auto;
}

/* Welcome Container */
.welcome-container {
    text-align: center;
    padding: 60px 20px;
    color: #333;
}
.welcome-title {
    font-size: 28px;
    font-weight: 600;
    color: #007aff;
}
.welcome-subtitle {
    font-size: 16px;
    color: #666;
    margin-top: 8px;
}

/* Animations */
[data-testid="stChatMessage"] > div {
    animation: fadeIn 0.3s ease;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(6px);}
    to {opacity: 1; transform: translateY(0);}
}

/* Mobile Responsive */
@media (max-width: 768px){
    .chat-title {font-size: 24px;}
    [data-testid="stChatMessage"] > div {font-size: 15px;}
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
