import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# --- Load environment variables safely ---
try:
    load_dotenv()
except Exception as e:
    st.warning(f"⚠️ Could not load .env file: {e}")

# --- Streamlit page setup ---
st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖", layout="wide")

# --- Clean Minimal CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

* {
    font-family: 'Inter', sans-serif;
    box-sizing: border-box;
}

body, .stApp {
    background: #f9fafb;
    color: #111;
}

.main {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding-top: 40px;
    min-height: 100vh;
}

.chat-wrapper {
    width: 100%;
    max-width: 800px;
}

.chat-header {
    text-align: center;
    padding: 20px 0;
    margin-bottom: 20px;
}
.chat-title {
    font-size: 30px;
    font-weight: 700;
    background: linear-gradient(90deg, #007bff, #00c6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.chat-subtitle {
    color: #555;
    font-size: 14px;
}

[data-testid="stChatMessage"] > div {
    border-radius: 16px !important;
    padding: 16px 20px !important;
    font-size: 16px;
    max-width: 70%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

[data-testid="stChatMessage"][data-testid*='user'] {
    justify-content: flex-end;
}
[data-testid="stChatMessage"][data-testid*='user'] > div {
    background: #007bff !important;
    color: white !important;
    border-radius: 16px 16px 0 16px !important;
}

[data-testid="stChatMessage"]:not([data-testid*='user']) > div {
    background: white !important;
    border: 1px solid #e5e7eb;
    color: #111 !important;
    border-radius: 16px 16px 16px 0 !important;
}

.stChatInputContainer {
    bottom: 10px !important;
    margin-top: 20px !important;
}
.stChatInputContainer textarea {
    background: white !important;
    color: #111 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 16px !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
}
[data-testid="stChatInputSubmitButton"] {
    border-radius: 50%;
    background: #007bff !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(0,123,255,0.3);
}
[data-testid="stChatInputSubmitButton"]:hover {
    background: #0056d2 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Gemini Chatbot Class ---
class Chatbot:
    def __init__(self):
        """Initialize Gemini API with proper error handling."""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.chat = self.model.start_chat(history=[])

        except ValueError as e:
            st.error(f"❌ Configuration Error: {e}")
            st.stop()

        except Exception as e:
            st.error(f"❌ Failed to initialize Gemini API: {e}")
            st.info("💡 Try restarting the app or checking your internet/API key.")
            st.stop()

    def generate(self, prompt: str):
        """Generate a response with safe fallback."""
        if not prompt.strip():
            return "⚠️ Please type something to start the conversation."

        try:
            response = self.chat.send_message(prompt)
            return response.text if response and response.text else "🤔 Sorry, I didn’t understand that."
        
        except genai.types.generation_types.BlockedPromptException:
            return "⚠️ Your prompt was blocked by Gemini for safety reasons."

        except genai.types.generation_types.InvalidArgument:
            return "⚠️ Invalid input sent to the model."

        except TimeoutError:
            return "⏳ The request took too long. Please try again."

        except Exception as e:
            return f"⚠️ Unexpected Error: {str(e)}"

# --- Streamlit App ---
def main():
    st.markdown("""
    <div class="chat-header">
        <div class="chat-title">🤖 AI Chat Assistant</div>
        <div class="chat-subtitle">Powered by Gemini API</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        if "bot" not in st.session_state:
            st.session_state.bot = Chatbot()
        if "history" not in st.session_state:
            st.session_state.history = []

        # Display chat history
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["text"])

        # Handle new message
        prompt = st.chat_input("Ask something...")
        if prompt:
            st.session_state.history.append({"role": "user", "text": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = st.session_state.bot.generate(prompt)
                    st.markdown(reply)

            st.session_state.history.append({"role": "assistant", "text": reply})
            st.rerun()

    except Exception as e:
        st.error(f"💥 Critical Error: {e}")
        st.info("Try refreshing the app or rechecking your configuration.")

# --- Run ---
if __name__ == "__main__":
    main()
