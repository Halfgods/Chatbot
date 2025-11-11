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

# Modern Premium Chat UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* === GLOBAL RESET === */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hide Streamlit elements */
#MainMenu, footer, header, .stDeployButton, .stDecoration, 
.stToolbar, [data-testid="stToolbar"], .stStatusWidget {
    visibility: hidden !important;
    height: 0 !important;
    display: none !important;
}

/* === ROOT BACKGROUND === */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

/* Main container */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* === HEADER === */
.chat-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 20px 32px;
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
}

.header-content {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 16px;
}

.header-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

.header-text h1 {
    font-size: 22px;
    font-weight: 700;
    color: #1a1a2e;
    margin: 0;
}

.header-text p {
    font-size: 13px;
    color: #6b7280;
    margin: 2px 0 0 0;
}

/* === MESSAGES CONTAINER === */
[data-testid="stChatMessageContainer"] {
    padding: 32px 16px 120px 16px !important;
    max-width: 900px;
    margin: 0 auto;
}

/* === MESSAGE BUBBLES === */
[data-testid="stChatMessage"] {
    background: transparent !important;
    margin-bottom: 16px !important;
}

[data-testid="stChatMessage"] > div {
    padding: 14px 18px !important;
    border-radius: 16px !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
    max-width: 75% !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
}

/* User messages (right - gradient) */
[data-testid="stChatMessage"][data-testid*="user"] {
    justify-content: flex-end !important;
}

[data-testid="stChatMessage"][data-testid*="user"] > div {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: #ffffff !important;
    margin-left: auto !important;
    border-bottom-right-radius: 4px !important;
}

/* Assistant messages (left - white) */
[data-testid="stChatMessage"]:not([data-testid*="user"]) {
    justify-content: flex-start !important;
}

[data-testid="stChatMessage"]:not([data-testid*="user"]) > div {
    background: rgba(255, 255, 255, 0.95) !important;
    color: #1a1a2e !important;
    margin-right: auto !important;
    border-bottom-left-radius: 4px !important;
}

/* Avatar styling */
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarContainer"] {
    display: none !important;
}

/* === PREMIUM INPUT AREA === */
.stChatInputContainer {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    padding: 20px !important;
    background: linear-gradient(to top, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.95) 100%) !important;
    backdrop-filter: blur(10px);
    border-top: 1px solid rgba(0, 0, 0, 0.06);
    z-index: 999 !important;
}

.stChatInputContainer > div {
    max-width: 900px !important;
    margin: 0 auto !important;
    background: #ffffff !important;
    border-radius: 24px !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.05) !important;
    padding: 4px 4px 4px 20px !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    transition: all 0.3s ease !important;
}

.stChatInputContainer > div:focus-within {
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25), 0 0 0 2px #667eea !important;
}

/* Input textarea */
.stChatInputContainer textarea {
    background: transparent !important;
    border: none !important;
    color: #1a1a2e !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
    padding: 12px 0 !important;
    resize: none !important;
    outline: none !important;
    min-height: 24px !important;
    max-height: 120px !important;
}

.stChatInputContainer textarea::placeholder {
    color: #9ca3af !important;
}

/* Premium send button */
[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    width: 48px !important;
    height: 48px !important;
    min-width: 48px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}

[data-testid="stChatInputSubmitButton"]:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
}

[data-testid="stChatInputSubmitButton"]:active {
    transform: scale(0.95) !important;
}

/* === SCROLLBAR === */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.3);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(102, 126, 234, 0.5);
}

/* === CODE BLOCKS === */
pre {
    background: rgba(0, 0, 0, 0.05) !important;
    border-radius: 8px !important;
    padding: 12px !important;
    border-left: 3px solid #667eea !important;
}

code {
    background: rgba(102, 126, 234, 0.1) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    color: #667eea !important;
    font-family: 'Fira Code', monospace !important;
}

/* === WELCOME SCREEN === */
.welcome-container {
    text-align: center;
    padding: 80px 20px;
    max-width: 600px;
    margin: 0 auto;
}

.welcome-icon {
    font-size: 72px;
    margin-bottom: 24px;
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.welcome-title {
    font-size: 32px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 12px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.welcome-subtitle {
    font-size: 16px;
    color: rgba(255, 255, 255, 0.9);
    line-height: 1.6;
    margin-bottom: 8px;
}

.welcome-status {
    display: inline-block;
    padding: 8px 16px;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    color: #ffffff;
    font-size: 14px;
    margin-top: 16px;
}

/* === MOBILE RESPONSIVE === */
@media (max-width: 768px) {
    .chat-header {
        padding: 16px 20px;
    }
    
    .header-icon {
        width: 40px;
        height: 40px;
        font-size: 20px;
    }
    
    .header-text h1 {
        font-size: 18px;
    }
    
    [data-testid="stChatMessage"] > div {
        max-width: 85% !important;
        font-size: 14px !important;
    }
    
    .welcome-title {
        font-size: 24px;
    }
    
    .stChatInputContainer {
        padding: 12px !important;
    }
}

/* Hide spinner overlay */
.stSpinner > div {
    border-top-color: #667eea !important;
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
    rag_data = load_rag_data(JSON_FILE) 
    
    # Header
    st.markdown("""
    <div class="chat-header">
        <div class="header-content">
            <div class="header-icon">🤖</div>
            <div class="header-text">
                <h1>AI Chat Assistant</h1>
                <p>Powered by Gemini AI + RAG Technology</p>
            </div>
        </div>
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
    
    # Welcome screen
    if not st.session_state.messages:
        rag_status = "✅ RAG Data Loaded" if rag_data else "⚠️ AI Mode Only"
        st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-icon">🤖</div>
            <div class="welcome-title">Welcome to AI Assistant</div>
            <div class="welcome-subtitle">
                I'm here to help you with intelligent responses<br>
                powered by advanced AI and RAG technology
            </div>
            <div class="welcome-status">{rag_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    try:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here...", key="chat_input"):
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            response = ""
            
            # RAG Logic
            if rag_data:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        enhanced_prompt = f"""
                        User question: {prompt}
                        
                        Available user data: {json.dumps(rag_data, indent=2)}
                        
                        Please answer the user's question using the provided data when relevant.
                        """
                        response = st.session_state.chatbot.generate_response(enhanced_prompt)
                    st.markdown(response)
            else:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = st.session_state.chatbot.generate_response(prompt)
                    st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
            
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        st.info("🔧 Please check your configuration and try again.")

if __name__ == "__main__":
    main()
