import requests
import streamlit as st
from dotenv import load_dotenv
import os
import shelve
import time

load_dotenv()

st.title("TheraBot")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"
API_URL = "https://rwoohdfg50dehvj3.us-east-1.aws.endpoints.huggingface.cloud"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Define the system prompt
SYSTEM_PROMPT = "You are an expert mental health assistant. Answer the following question clearly and concisely. You give advice to a user who is seeking help for their mental health."

# Load chat history from shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

# Save chat history to shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        save_chat_history([])

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("How can I help?"):
    st.session_state.messages.append({"role": "user", "content": f"Question: {prompt}\nPlease provide a detailed and clear response to the question above. If you do not know the answer, kindly state that and provide suggestions for further inquiries."})
    print(st.session_state.messages)
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""
        
        # Make a request to the Hugging Face API
        payload = {
            "inputs": f"{SYSTEM_PROMPT}\n\nUser: {prompt}\nAssistant:",
            "parameters": {
                "max_length": 5000  # Adjust this value as needed
            }
        }
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Check for HTTP errors
            response_json = response.json()
            
            # Extract the response text
            if response_json and 'generated_text' in response_json[0]:
                full_response = response_json[0]['generated_text'].split("Assistant:")[1].strip()
                print(full_response)
            else:
                full_response = "I'm sorry, I don't have an answer to that question. Can you please ask me another question?"
        
        except requests.exceptions.RequestException as e:
            # Handle request errors
            full_response = f"An error occurred: {e}"
        except (IndexError, KeyError):
            # Handle parsing errors
            full_response = "I'm sorry, I don't have an answer to that question. Can you please ask me another question?"

        # Stream the response word by word
        words = full_response.split()
        displayed_response = ""
        for word in words:
            displayed_response += word + " "
            message_placeholder.markdown(displayed_response.strip())
            time.sleep(0.05)  # Adjust the delay as needed

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)
