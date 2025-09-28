import streamlit as st
import google.generativeai as genai
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

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
    margin: 0 !important;
    padding: 0 !important;
    display: none !important;
}

/* Root styling - Dark elegance */
.stApp {
    background: #0a0a0f !important;
}

.main {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a1625 50%, #0a0a0f 100%) !important;
    min-height: 100vh;
    padding: 0 !important;
    margin: 0 !important;
    display: flex;
    flex-direction: column;
}

.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: none !important;
    width: 100% !important;
}

/* Centered Container for all content */
.chat-wrapper {
    max-width: 800px;
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    position: relative;
}

/* Premium Header - Perfectly centered */
.chat-header {
    background: linear-gradient(135deg, #1a1625, #2d1b35, #1a1625);
    border-bottom: 1px solid rgba(255, 107, 107, 0.1);
    padding: 32px 24px;
    text-align: center;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.chat-title {
    font-size: 32px;
    font-weight: 700;
    background: linear-gradient(135deg, #ff6b6b, #feca57, #48cae4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 8px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
}

.chat-subtitle {
    color: rgba(255, 255, 255, 0.7);
    font-size: 15px;
    font-weight: 400;
    margin: 0;
}

/* Messages container - Perfectly centered */
.messages-container {
    flex: 1;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    overflow-y: auto;
    max-width: 800px;
    margin: 0 auto;
    width: 100%;
}

/* Override Streamlit's chat container */
.stChatFloatingInputContainer {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    margin: 0 auto !important;
    padding: 0 !important;
    max-width: 800px !important;
    width: 100% !important;
}

/* Message styling - Clean and centered */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
    max-width: 800px !important;
    width: 100% !important;
    display: flex !important;
    align-items: flex-end !important;
}

/* User messages - Right aligned */
[data-testid="stChatMessage"][data-testid*="user"] {
    justify-content: flex-end !important;
    margin-bottom: 20px !important;
}

[data-testid="stChatMessage"][data-testid*="user"] > div {
    background: linear-gradient(135deg, #ff6b6b, #ee5a52) !important;
    color: #ffffff !important;
    border-radius: 28px 28px 8px 28px !important;
    padding: 18px 24px !important;
    max-width: 70% !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    line-height: 1.5 !important;
    box-shadow: 
        0 8px 24px rgba(255, 107, 107, 0.25),
        0 4px 12px rgba(0, 0, 0, 0.3) !important;
    border: none !important;
    animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    margin: 0 !important;
}

/* Assistant messages - Left aligned */
[data-testid="stChatMessage"]:not([data-testid*="user"]) {
    justify-content: flex-start !important;
    margin-bottom: 20px !important;
}

[data-testid="stChatMessage"]:not([data-testid*="user"]) > div {
    background: linear-gradient(135deg, #2d1b35, #1a1625) !important;
    color: #f8f9fa !important;
    border-radius: 28px 28px 28px 8px !important;
    padding: 18px 24px !important;
    max-width: 70% !important;
    font-size: 16px !important;
    font-weight: 400 !important;
    line-height: 1.6 !important;
    box-shadow: 
        0 8px 24px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    backdrop-filter: blur(10px) !important;
    margin: 0 !important;
}

/* Avatar styling */
[data-testid="stChatMessage"] img {
    width: 36px !important;
    height: 36px !important;
    border-radius: 50% !important;
    margin: 0 16px 6px 0 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    border: 2px solid rgba(255, 107, 107, 0.3) !important;
    background: linear-gradient(135deg, #2d1b35, #ff6b6b) !important;
}

/* Input container - Floating and centered */
.stChatInputContainer {
    position: sticky !important;
    bottom: 24px !important;
    margin: 0 auto 24px auto !important;
    z-index: 100 !important;
    max-width: 800px !important;
    width: calc(100% - 48px) !important;
}

.stChatInputContainer > div {
    background: linear-gradient(135deg, #1a1625, #2d1b35) !important;
    border: 2px solid rgba(255, 107, 107, 0.2) !important;
    border-radius: 32px !important;
    padding: 6px !important;
    box-shadow: 
        0 12px 40px rgba(0, 0, 0, 0.5),
        0 8px 24px rgba(255, 107, 107, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(20px) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.stChatInputContainer > div:focus-within {
    border-color: rgba(255, 107, 107, 0.6) !important;
    box-shadow: 
        0 16px 48px rgba(0, 0, 0, 0.6),
        0 8px 32px rgba(255, 107, 107, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    transform: translateY(-3px) !important;
}

/* Input text */
.stChatInputContainer textarea {
    background: transparent !important;
    color: #ffffff !important;
    border: none !important;
    font-size: 16px !important;
    font-weight: 400 !important;
    padding: 18px 28px !important;
    border-radius: 28px !important;
    resize: none !important;
    min-height: 28px !important;
    max-height: 120px !important;
    line-height: 1.5 !important;
}

.stChatInputContainer textarea::placeholder {
    color: rgba(255, 255, 255, 0.5) !important;
    font-weight: 300 !important;
}

.stChatInputContainer textarea:focus {
    outline: none !important;
    color: #ffffff !important;
}

/* Send button - Perfect circle */
[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #ff6b6b, #feca57) !important;
    border: none !important;
    border-radius: 50% !important;
    width: 52px !important;
    height: 52px !important;
    margin: 6px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
}

[data-testid="stChatInputSubmitButton"]:hover {
    transform: scale(1.08) translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(255, 107, 107, 0.6) !important;
}

[data-testid="stChatInputSubmitButton"]:active {
    transform: scale(0.95) !important;
}

[data-testid="stChatInputSubmitButton"] svg {
    color: #ffffff !important;
    width: 22px !important;
    height: 22px !important;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2)) !important;
}

/* Animations */
@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px) scale(0.98);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes fadeInScale {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

/* Welcome screen */
.welcome-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 60px 40px;
    animation: fadeInScale 0.6s ease-out;
}

.welcome-title {
    font-size: 36px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 20px;
    background: linear-gradient(135deg, #ff6b6b, #feca57, #48cae4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.welcome-subtitle {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.7);
    line-height: 1.7;
    max-width: 500px;
    margin: 0 auto;
    font-weight: 300;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ff6b6b, #feca57);
    border-radius: 8px;
    border: 2px solid transparent;
    background-clip: content-box;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #ee5a52, #feb636);
    background-clip: content-box;
}

/* Loading spinner */
.stSpinner > div {
    border-top-color: #ff6b6b !important;
    border-right-color: #feca57 !important;
}

/* Alert styling */
.stAlert {
    background: linear-gradient(135deg, #1a1625, #2d1b35) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 107, 107, 0.3) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
    backdrop-filter: blur(10px) !important;
    margin: 20px 24px !important;
}

/* Code blocks */
pre {
    background: rgba(0, 0, 0, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
    overflow-x: auto !important;
    margin: 16px 0 !important;
}

code {
    background: rgba(255, 107, 107, 0.15) !important;
    color: #ff6b6b !important;
    padding: 3px 8px !important;
    border-radius: 6px !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .chat-wrapper {
        max-width: 100%;
    }
    
    .chat-header {
        padding: 24px 16px;
    }
    
    .chat-title {
        font-size: 28px;
    }
    
    .messages-container {
        padding: 16px;
    }
    
    .stChatInputContainer {
        margin: 0 16px 16px 16px !important;
    }
    
    [data-testid="stChatMessage"] > div {
        max-width: 85% !important;
        font-size: 15px !important;
    }
    
    .welcome-title {
        font-size: 30px;
    }
    
    .welcome-subtitle {
        font-size: 16px;
        padding: 0 20px;
    }
}

/* Selection styling */
::selection {
    background: rgba(255, 107, 107, 0.3);
    color: #ffffff;
}

/* Focus states */
button:focus-visible,
textarea:focus-visible {
    outline: 2px solid #ff6b6b;
    outline-offset: 2px;
}

/* Container wrapper to center everything */
.stChatFloatingInputContainer {
    max-width: 800px;
    margin: 0 auto !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

class Chatbot:
    def __init__(self):
        """Initialize the chatbot with Gemini API."""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise Exception("GEMINI_API_KEY environment variable not found. Check your .env file and installation.")
                
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
    # Center everything in a wrapper
    st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
    
    # Premium Header
    st.markdown("""
    <div class="chat-header">
        <div class="chat-title">
            <span>🤖</span> AI Chat Assistant
        </div>
        <div class="chat-subtitle">Powered by advanced AI • Chat with intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = Chatbot()
        except Exception as e:
            st.error(f"🚫 Failed to initialize chatbot: {str(e)}")
            st.info("💡 Please check your API key configuration and try again.")
            st.stop()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Welcome screen for empty chat
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-title">👋 Welcome!</div>
            <div class="welcome-subtitle">
                I'm your AI assistant, ready to help with questions, creative tasks, coding, and more.<br>
                Start a conversation by typing your message below.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    try:
        # Display chat messages in container
        st.markdown('<div class="messages-container">', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message["content"])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Type your message here...", key="chat_input"):
            # Display user message
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Generate and display assistant response
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
    
    # Close wrapper
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
