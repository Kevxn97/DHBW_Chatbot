import os
import streamlit as st
from PIL import Image
import random
import json
import time
import requests

# Backend API URL
BACKEND_URL = "http://localhost:3001/api/ask"

# Function to get response from backend
def get_assistant_response(user_input):
    try:
        response = requests.post(
            BACKEND_URL,
            json={"question": user_input},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raise an exception for bad responses
        return response.json()["answer"]
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return "Entschuldigung, ich konnte keine Verbindung zum Backend herstellen. Bitte versuche es später noch einmal."

# Page configuration
st.set_page_config(
    page_title="DHBW Chatbot",
    page_icon="🗨️",
    layout="wide"
)

# CSS Styles
st.markdown("""
<style>
/* Page background */
.stApp {
    background-color: #f8f9fa;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
}

/* Button styling */
.stButton>button {
    background-color: #007bff;
    color: white;
    border-radius: 8px;
}

.stButton>button:hover {
    background-color: #0056b3; /* Darker shade of the primary button color #007bff */
}

/* Text-input frame */
.stTextInput>div>div>input {
    border: 2px solid #007bff;
    border-radius: 5px;
}

/* Chat header */
.stChatHeader {
    background-color: #5A6268 !important;
    color: white !important;
    padding: 8px;
    border-radius: 5px;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    font-family: inherit; /* Inherit font from .stApp */
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6 {
    color: #007bff; /* Primary accent color */
}

/* Small example question buttons */
.small-btn {
    font-size: 0.8em !important;
    padding: 0.2rem 0.5rem !important;
    height: auto !important;
    margin: 0.2rem !important;
    border-radius: 8px;
    background-color: #007bff;
    color: white;
}

.small-btn:hover {
    background-color: #0056b3; /* Darker shade */
}

/* Message bubbles styling */
.message-container {
    display: flex;
    margin-bottom: 10px;
    width: 100%;
}

.user-container {
    justify-content: flex-end;
}

.bot-container {
    justify-content: flex-start;
}

.message-bubble {
    max-width: 70%;
    padding: 10px 15px;
    border-radius: 20px;
    position: relative;
    font-size: 16px;
    line-height: 1.4;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.user-bubble {
    background-color: #e9ecef;
    color: #000;
    margin-left: auto;
}

.bot-bubble {
    background-color: #007bff;
    color: white;
    margin-right: auto;
}

.avatar {
    display: inline-block;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: #5A6268;
    color: white;
    text-align: center;
    line-height: 30px;
    margin: 0 8px;
    align-self: flex-end;
}

/* Loading indicator styles */
.chat-input-container {
    display: flex;
    align-items: center;
    position: relative;
    width: 100%;
}
.loading-symbol {
    position: absolute;
    right: 10px;
    bottom: 10px;
    font-size: 24px;
    color: #007bff;
    animation: loading-spin 1s linear infinite;
    z-index: 1000;
    pointer-events: none;
}
@keyframes loading-spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Adjust streamlit's chat input container */
.stChatInput {
    padding-right: 40px !important;
}

/* Generation message styling */
.generating-text {
    font-style: italic;
    opacity: 0.8;
}

/* Animated text generation effect */
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

@keyframes fade {
    0%, 100% { opacity: 0.7; }
    50% { opacity: 1; }
}

.generating-char {
    display: inline-block;
    animation-duration: 1s;
    animation-iteration-count: infinite;
    animation-name: bounce, fade;
    animation-timing-function: ease-in-out;
}

.char-1 { animation-delay: 0.0s; }
.char-2 { animation-delay: 0.1s; }
.char-3 { animation-delay: 0.2s; }
.char-4 { animation-delay: 0.3s; }
.char-5 { animation-delay: 0.4s; }
.char-6 { animation-delay: 0.5s; }
.char-7 { animation-delay: 0.6s; }
.char-8 { animation-delay: 0.7s; }
.char-9 { animation-delay: 0.8s; }
.char-10 { animation-delay: 0.9s; }
.char-11 { animation-delay: 1.0s; }
.char-12 { animation-delay: 1.1s; }
.char-13 { animation-delay: 1.2s; }
.char-14 { animation-delay: 1.3s; }
.char-15 { animation-delay: 1.4s; }
.char-16 { animation-delay: 1.5s; }
.char-17 { animation-delay: 1.6s; }

/* Gray hover effect */
.hover-effect {
    position: relative;
}

.hover-effect::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, rgba(128,128,128,0.2) 0%, rgba(128,128,128,0) 50%, rgba(128,128,128,0.2) 100%);
    background-size: 200% 100%;
    animation: gradient-move 2s ease infinite;
    pointer-events: none;
}

@keyframes gradient-move {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
""", unsafe_allow_html=True)

# Function to save chat history
def save_chat_history():
    # Create chats directory if it doesn't exist
    chat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats')
    os.makedirs(chat_dir, exist_ok=True)
    
    # Save each chat to a separate file
    for chat_name in st.session_state['chat_list']:
        # Create a filename-safe version of chat name
        safe_name = chat_name.replace(" ", "_").lower()
        file_path = os.path.join(chat_dir, f"{safe_name}.json")
        
        # Get messages for this chat
        if chat_name == st.session_state['current_chat']:
            messages = st.session_state['messages']
        else:
            messages = st.session_state.get(f'messages_{chat_name}', [])
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'chat_name': chat_name,
                'messages': messages,
                'timestamp': time.time()
            }, f, ensure_ascii=False, indent=2)

# Function to load chat history
def load_chat_history():
    chat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats')
    
    # If directory doesn't exist, create it and return default values
    if not os.path.exists(chat_dir):
        os.makedirs(chat_dir, exist_ok=True)
        return ["Chat 1"], "Chat 1", []
    
    # Load all chat files
    chat_list = []
    messages_dict = {}
    
    for filename in os.listdir(chat_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(chat_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chat_name = data['chat_name']
                    chat_list.append(chat_name)
                    messages_dict[chat_name] = data['messages']
            except (json.JSONDecodeError, KeyError) as e:
                st.warning(f"Error loading chat file {filename}: {e}")
    
    # If no chats were loaded, return default values
    if not chat_list:
        return ["Chat 1"], "Chat 1", []
    
    # Sort chat list by name (you could also sort by timestamp if available)
    chat_list.sort()
    current_chat = chat_list[0]
    
    # Return the messages for the current chat
    return chat_list, current_chat, messages_dict.get(current_chat, [])

# Function to delete current chat
def delete_chat(chat_name):
    # Remove chat file if it exists
    chat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats')
    safe_name = chat_name.replace(" ", "_").lower()
    file_path = os.path.join(chat_dir, f"{safe_name}.json")
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove chat from session state
    st.session_state['chat_list'].remove(chat_name)
    if f'messages_{chat_name}' in st.session_state:
        del st.session_state[f'messages_{chat_name}']
    
    # If there are no more chats, create a new one
    if not st.session_state['chat_list']:
        st.session_state['chat_list'] = ["Chat 1"]
        st.session_state['current_chat'] = "Chat 1"
        st.session_state['messages'] = []
    else:
        # Switch to the first available chat
        st.session_state['current_chat'] = st.session_state['chat_list'][0]
        if f'messages_{st.session_state["current_chat"]}' in st.session_state:
            st.session_state['messages'] = st.session_state[f'messages_{st.session_state["current_chat"]}']
        else:
            st.session_state['messages'] = []

# Initialize session state with loaded chat history
if 'chat_list' not in st.session_state:
    chat_list, current_chat, messages = load_chat_history()
    st.session_state['chat_list'] = chat_list
    st.session_state['current_chat'] = current_chat
    st.session_state['messages'] = messages
    
    # Also store messages for each chat
    for chat_name in chat_list:
        if chat_name != current_chat:
            chat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chats')
            safe_name = chat_name.replace(" ", "_").lower()
            file_path = os.path.join(chat_dir, f"{safe_name}.json")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    st.session_state[f'messages_{chat_name}'] = data['messages']
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                st.session_state[f'messages_{chat_name}'] = []

# Load DHBW logo
testpath = os.path.dirname(os.path.abspath(__file__))
print(testpath)
logo = Image.open(os.path.join(testpath, 'resources', "DHBW Logo.png"))

# Sidebar
with st.sidebar:
    st.image(logo, width=100)  # Logo top-left
    st.header("Chats")
    with st.expander("Verlauf"):
        choice = st.radio("", st.session_state['chat_list'],
                          index=st.session_state['chat_list'].index(st.session_state['current_chat']))
        st.session_state['current_chat'] = choice
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Neuer Chat", use_container_width=True):
            # Save current chat messages before creating a new one
            if st.session_state['messages']:
                st.session_state[f'messages_{st.session_state["current_chat"]}'] = st.session_state['messages']
            
            new_chat = f"Chat {len(st.session_state['chat_list']) + 1}"
            st.session_state['chat_list'].append(new_chat)
            st.session_state['current_chat'] = new_chat
            st.session_state['messages'] = []
            save_chat_history()  # Save after creating a new chat
    
    with col2:
        if st.button("Chat löschen", use_container_width=True):
            if len(st.session_state['chat_list']) > 0:
                current_chat = st.session_state['current_chat']
                delete_chat(current_chat)
                save_chat_history()  # Update chat history after deletion
                st.rerun()

# When switching chats, update session state
if 'previous_chat' not in st.session_state:
    st.session_state['previous_chat'] = st.session_state['current_chat']
elif st.session_state['previous_chat'] != st.session_state['current_chat']:
    # Save messages from the previous chat
    st.session_state[f'messages_{st.session_state["previous_chat"]}'] = st.session_state['messages']
    
    # Load messages for the new current chat
    if f'messages_{st.session_state["current_chat"]}' in st.session_state:
        st.session_state['messages'] = st.session_state[f'messages_{st.session_state["current_chat"]}']
    else:
        st.session_state['messages'] = []
    
    st.session_state['previous_chat'] = st.session_state['current_chat']

# Main layout
col1, col2 = st.columns([9, 1])

with col2:
    st.image(logo, width=60)  # Logo on right

with col1:
    st.markdown(f"### {st.session_state['current_chat']}")
    
    # Chat message display - unified logic
    if 'temp_messages' in st.session_state and 'loading' in st.session_state and st.session_state['loading']:
        # Display chat messages including the temporary "Generating Answer" message
        messages_to_show = st.session_state['temp_messages']
    else:
        # Display normal messages
        messages_to_show = st.session_state['messages']
    
    # Display the appropriate set of messages
    for msg in messages_to_show:
        if msg['role'] == "user":
            # User messages: right-aligned with green bubbles
            st.markdown(f"""
            <div class="message-container user-container">
                <div class="message-bubble user-bubble">
                    {msg['content']}
                </div>
                <div class="avatar">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Bot messages: left-aligned with red bubbles
            st.markdown(f"""
            <div class="message-container bot-container">
                <div class="avatar">🤖</div>
                <div class="message-bubble bot-bubble">
                    {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Define example questions
example_questions = [
    "Wie kann ich mich für eine Klausur anmelden?",
    "Wo finde ich den Stundenplan?",
    "Wann sind die Vorlesungszeiten?",
    "Wie kontaktiere ich die Studiengangsleitung?"
]

# Display example questions as buttons above the input field
cols = st.columns(len(example_questions))
for i, (col, q) in enumerate(zip(cols, example_questions)):
    with col:
        if st.button(q, key=f"example_{i}", use_container_width=True):
            st.session_state['messages'].append({"role": "user", "content": q})
            
            # Set loading state
            st.session_state['loading'] = True
            
            # Show temporary "Generating Answer" message from bot
            temp_messages = st.session_state['messages'].copy()
            
            # Create an animated "Generating Answer" text with individual bouncing characters
            generating_text = "Generating Answer"
            animated_text = '<span class="hover-effect">'
            for i, char in enumerate(generating_text):
                if char == ' ':
                    animated_text += ' '
                else:
                    animated_text += f'<span class="generating-char char-{i+1}">{char}</span>'
            animated_text += '</span>'
            
            temp_messages.append({"role": "assistant", "content": animated_text})
            
            # Rerun to display user message and "Generating Answer" immediately
            st.session_state['temp_messages'] = temp_messages
            st.rerun()

# Add some spacing before the input area
st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

# Place input field with loading symbol
input_container = st.container()
with input_container:
    # Use a container with relative positioning for the chat input
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    # Add chat input field
    user_input = st.chat_input("Schreibe eine Nachricht…")
    
    # Always show the loading symbol container, but only animate when loading
    if 'loading' in st.session_state and st.session_state['loading']:
        st.markdown('<div class="loading-symbol">⟳</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Check if we're in the generation state
if 'temp_messages' in st.session_state and 'loading' in st.session_state and st.session_state['loading']:
    # Get response from backend API
    user_message = st.session_state['messages'][-1]["content"]
    bot_response = get_assistant_response(user_message)
    
    # Clear temporary state
    st.session_state.pop('temp_messages', None)
    st.session_state['loading'] = False
    
    # Add the real response
    st.session_state['messages'].append({"role": "assistant", "content": bot_response})
    save_chat_history()
    st.rerun()

# Handle user input
if user_input:
    # Handle message input and show it immediately
    st.session_state['messages'].append({"role": "user", "content": user_input})
    
    # Set loading state
    st.session_state['loading'] = True
    
    # Show temporary "Generating Answer" message from bot
    temp_messages = st.session_state['messages'].copy()
    
    # Create an animated "Generating Answer" text with individual bouncing characters
    generating_text = "Generating Answer"
    animated_text = '<span class="hover-effect">'
    for i, char in enumerate(generating_text):
        if char == ' ':
            animated_text += ' '
        else:
            animated_text += f'<span class="generating-char char-{i+1}">{char}</span>'
    animated_text += '</span>'
    
    temp_messages.append({"role": "assistant", "content": animated_text})
    
    # Rerun to display user message and "Generating Answer" immediately
    st.session_state['temp_messages'] = temp_messages
    st.rerun()
