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

# WhatsApp-Inspired Clean CSS
st.markdown("""
<style>
/* === GLOBAL RESET === */
* {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    box-sizing: border-box;
}

/* Hide Streamlit branding */
#MainMenu, footer, header, .stDeployButton, .stDecoration, 
.stToolbar, [data-testid="stToolbar"] {
    visibility: hidden !important;
    height: 0 !important;
    display: none !important;
}

/* === PAGE BACKGROUND === */
.stApp {
    background: #0b141a;
}

div.block-container{
    padding: 15px !important; 
}

/* === HEADER SECTION === */
.app-header {
    background: #202c33;
    padding: 16px 24px;
    text-align: center;
    border-bottom: 1px solid #2a3942;
    margin-bottom: 0;
}

.app-title {
    font-size: 20px;
    font-weight: 500;
    color: #e9edef;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.app-subtitle {
    color: #8696a0;
    font-size: 13px;
    margin-top: 4px;
}

/* === MESSAGES AREA === */
.messages-container {
    flex: 1;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    overflow-y: auto;
    max-width: 100%;
    background: #0b141a;
}

/* === MESSAGE BUBBLES === */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 2px 0 !important;
}

[data-testid="stChatMessage"] > div {
    border-radius: 7.5px !important;
    padding: 8px 12px !important;
    max-width: 65% !important;
    font-size: 14.2px !important;
    line-height: 19px !important;
    box-shadow: 0 1px 0.5px rgba(0,0,0,0.13) !important;
    word-wrap: break-word;
}

/* User message bubble (right side - green) */
[data-testid="stChatMessage"][data-testid*="user"] {
    justify-content: flex-end !important;
}

[data-testid="stChatMessage"][data-testid*="user"] > div {
    background: #005c4b !important;
    color: #e9edef !important;
    border-radius: 7.5px 7.5px 0 7.5px !important;
    margin-left: auto;
}

/* Assistant message bubble (left side - dark gray) */
[data-testid="stChatMessage"]:not([data-testid*="user"]) {
    justify-content: flex-start !important;
}

[data-testid="stChatMessage"]:not([data-testid*="user"]) > div {
    background: #202c33 !important;
    color: #e9edef !important;
    border-radius: 7.5px 7.5px 7.5px 0 !important;
    margin-right: auto;
}

/* === AVATAR STYLING === */
[data-testid="stChatMessage"] img {
    width: 32px !important;
    height: 32px !important;
    border-radius: 50% !important;
    margin: 0 8px 0 0 !important;
}

/* === INPUT AREA === */
.stChatInputContainer {
    position: sticky !important;
    bottom: 0 !important;
    padding: 10px 16px !important;
    background: #202c33 !important;
    border-top: 1px solid #2a3942;
    z-index: 100 !important;
}

.stChatInputContainer > div {
    background: #2a3942 !important;
    border-radius: 21px !important;
    padding: 0 !important;
    box-shadow: none !important;
    border: none !important;
}

/* Input text field */
.stChatInputContainer textarea {
    background: transparent !important;
    color: #e9edef !important;
    font-size: 15px !important;
    padding: 10px 16px !important;
    border: none !important;
    border-radius: 21px !important;
}

.stChatInputContainer textarea::placeholder {
    color: #8696a0 !important;
}

/* Send button */
[data-testid="stChatInputSubmitButton"] {
    background: #00a884 !important;
    border-radius: 50% !important;
    width: 42px !important;
    height: 42px !important;
    min-width: 42px !important;
    box-shadow: none !important;
    border: none !important;
}

[data-testid="stChatInputSubmitButton"]:hover {
    background: #06cf9c !important;
}

/* === SCROLLBAR === */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: #374248;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: #445258;
}

/* === CODE BLOCKS === */
pre {
    background: #182229 !important;
    border-radius: 5px !important;
    padding: 12px !important;
    border-left: 3px solid #00a884 !important;
}

code {
    background: #182229 !important;
    padding: 2px 6px !important;
    border-radius: 3px !important;
    color: #06cf9c !important;
}

/* === WELCOME SCREEN === */
.welcome-container {
    text-align: center;
    padding: 60px 20px;
    color: #8696a0;
}

.welcome-title {
    font-size: 24px;
    color: #e9edef;
    margin-bottom: 12px;
}

.welcome-subtitle {
    font-size: 14px;
    line-height: 1.6;
}

/* === MOBILE RESPONSIVE === */
@media (max-width: 768px) {
    [data-testid="stChatMessage"] > div {
        max-width: 80% !important;
        font-size: 13.5px !important;
    }
    
    .app-title {
        font-size: 18px;
    }
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
    <div class="app-header">
        <div class="app-title">
            🤖 AI Chat Assistant
        </div>
        <div class="app-subtitle">Powered by Gemini AI + RAG</div>
    </div>
    """, unsafe_allow_html=True)
    
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
                I'm your AI assistant with RAG capabilities.<br>
                Status: {rag_status}<br>
                Start chatting by typing below.
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
        if prompt := st.chat_input("Type a message", key="chat_input"):
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

if __name__ == "__main__":
    main()
