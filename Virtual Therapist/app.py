import streamlit as st
import torch
import datetime
import os
import sys

# Import functions from the therapist.py script
# Assuming the pasted code is saved as therapist.py in the same directory
from therapist import (
    MODEL_NAME, 
    tokenizer, 
    model,
    sentiment_analyzer,
    toxicity_classifier,
    analyze_sentiment,
    detect_toxicity,
    generate_emotional_prompt
)

# Page configuration
st.set_page_config(
    page_title="Serenity AI",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'conversation_memory' not in st.session_state:
    st.session_state.conversation_memory = []
if 'session_log' not in st.session_state:
    st.session_state.session_log = []
if 'user_details' not in st.session_state:
    st.session_state.user_details = {}
if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False

# Custom CSS
st.markdown("""
<style>
.user-bubble {
    background-color: #E9F5FE;
    color: #1E1E1E;
    padding: 10px 15px;
    border-radius: 20px 20px 0px 20px;
    margin: 5px 0;
    max-width: 80%;
    align-self: flex-end;
    float: right;
    clear: both;
}
.therapist-bubble {
    background-color: #F0F2F6;
    color: #1E1E1E;
    padding: 10px 15px;
    border-radius: 20px 20px 20px 0px;
    margin: 5px 0;
    max-width: 80%;
    align-self: flex-start;
    float: left;
    clear: both;
}
.chat-container {
    height: 400px;
    overflow-y: auto;
    padding: 10px;
    border-radius: 10px;
    background-color: #FFFFFF;
    border: 1px solid #EEEEEE;
}
.bubble-container {
    overflow: auto;
    margin-bottom: 10px;
}
.therapist-emoji {
    font-size: 1.5em;
    margin-right: 5px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("🧠 Serenity AI")
st.markdown("A safe space to talk about your feelings and get support.")

# Function to start session
def start_session():
    st.session_state.user_details = {
        "name": name or "Friend",
        "age": age or "Unknown",
        "location": location or "Somewhere",
        "reason": reason or "To talk"
    }
    st.session_state.onboarding_complete = True
    # Add welcome message to conversation
    welcome_msg = f"👋 Hello {st.session_state.user_details['name']} from {st.session_state.user_details['location']}! I'm here to support you. Let's talk about {st.session_state.user_details['reason']}."
    st.session_state.conversation_memory.append(f"Therapist: {welcome_msg}")
    st.session_state.session_log.append(f"Therapist: {welcome_msg}")

# Function to reset session
def reset_session():
    st.session_state.conversation_memory = []
    st.session_state.session_log = []
    st.session_state.onboarding_complete = False

# Function to handle user message
def process_user_message():
    # Check for toxicity
    is_toxic, toxicity_score = detect_toxicity(user_input)
    
    if is_toxic:
        st.warning("⚠️ I detected potentially harmful language. Let's focus on positive healing. 💙")
        st.session_state.session_log.append(f"You: [REDACTED TOXIC CONTENT]")
    else:
        # Add user message to conversation
        st.session_state.conversation_memory.append(f"You: {user_input}")
        st.session_state.session_log.append(f"You: {user_input}")
        
        # Generate emotional prompt based on sentiment
        emotional_prompt = generate_emotional_prompt(user_input)
        
        # Prepare input for model
        input_text = " ".join(st.session_state.conversation_memory[-6:]) + f" {emotional_prompt} {user_input}"
        input_ids = tokenizer(input_text, return_tensors="pt")
        
        # Generate response
        with torch.no_grad():
            response_ids = model.generate(
                input_ids["input_ids"],
                max_length=150,
                temperature=0.7,
                top_p=0.92,
                do_sample=True
            )
        
        # Decode response
        response = tokenizer.decode(response_ids[0], skip_special_tokens=True)
        
        # Check response for toxicity
        is_toxic, _ = detect_toxicity(response)
        if is_toxic:
            response = "I'm here to help in a supportive and respectful way. Let's focus on healing. 💙"
        
        # Make response more empathetic
        response = response.replace("I am", "I'm").replace("do not", "don't").replace("you are", "you're")
        
        # Add therapist response to conversation
        st.session_state.conversation_memory.append(f"Therapist: {response}")
        st.session_state.session_log.append(f"Therapist: {response}")
        
        # Keep only last 6 messages
        st.session_state.conversation_memory = st.session_state.conversation_memory[-6:]

# Function to save conversation
def save_conversation():
    # Create directory if it doesn't exist
    if not os.path.exists("therapy_sessions"):
        os.makedirs("therapy_sessions")
    
    # Save conversation to file
    filename = f"therapy_sessions/therapy_session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        for line in st.session_state.session_log:
            file.write(line + "\n")
    
    st.success(f"💾 Your session has been saved as `{filename}`")

# User onboarding form
if not st.session_state.onboarding_complete:
    with st.container():
        st.subheader("👤 Let's personalize your therapy session")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("What's your name?", placeholder="Enter your name")
        with col2:
            age = st.text_input("How old are you?", placeholder="Enter your age")
        
        location = st.text_input("Where are you from?", placeholder="Enter your location")
        reason = st.text_area("What brings you here today?", 
                             placeholder="E.g., stress, anxiety, personal growth", 
                             height=100)
        
        if st.button("Start My Session", type="primary", on_click=start_session):
            pass

# Chat interface
if st.session_state.onboarding_complete:
    # Display conversation history
    st.subheader("Your Session")
    
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.conversation_memory:
            parts = message.split(": ", 1)
            if len(parts) == 2:
                speaker, content = parts
                if speaker == "You":
                    st.markdown(f'<div class="bubble-container"><div class="user-bubble">{content}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bubble-container"><div class="therapist-bubble"><span class="therapist-emoji">🧑‍⚕️</span> {content}</div></div>', unsafe_allow_html=True)
    
    # User input
    with st.container():
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            process_user_message()
            st.rerun()

    # Sidebar options
    with st.sidebar:
        st.subheader("Session Options")
        
        if st.button("Save Conversation", on_click=save_conversation):
            pass
        
        if st.button("Start New Session", on_click=reset_session):
            pass
        
        # Display user details
        if st.session_state.user_details:
            st.subheader("Your Profile")
            st.write(f"**Name:** {st.session_state.user_details['name']}")
            st.write(f"**Age:** {st.session_state.user_details['age']}")
            st.write(f"**Location:** {st.session_state.user_details['location']}")
            st.write(f"**Reason for visit:** {st.session_state.user_details['reason']}")