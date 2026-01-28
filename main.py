# app.py
import streamlit as st
from groq import Groq
import time

st.set_page_config(
    page_title="Blah",
    page_icon="🐒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("AI")

client = Groq(api_key=st.secrets["Groq"])

MODELS = [
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",  
    "meta-llama/llama-4-8b",
]

MAX_TOKENS = 1024

def stream_response(messages):
    last_error = None

    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=MAX_TOKENS,
                stream=True
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
            return
        except Exception as e:
            last_error = e
            continue

    yield f"Error: {last_error}"

if "chat" not in st.session_state:
    st.session_state.chat = []

# Render chat history
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("Ask a question"):
    # 🔔 PHRASE-TRIGGERED DIALOG
    if prompt.lower().strip() == "open dialog":
        @st.dialog("Dialog")
        def show_dialog():
            st.write("aryan")
        show_dialog()
        st.stop()

    # Show user message immediately
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # System rules
    system_message = {
        "role": "system",
        "content": (
            "Give  answers with enthusiasm and explanation like you're their friend/mentor."
            "Do not show chain-of-thought, derivations, or internal reasoning. "
            "Avoid unnecessary formatting."
        )
    }

    # Only last 3 messages
    messages = [system_message] + st.session_state.chat
    # Assistant response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        for chunk in stream_response(messages):
            full_response += chunk
            placeholder.markdown(full_response)
            time.sleep(0.01)

    st.session_state.chat.append(
        {"role": "assistant", "content": full_response}
    )
