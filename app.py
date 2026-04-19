from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import plotly.express as px
from dash_agent.team import get_dash_team
from dash_agent.agents.utils import get_db_url
import os
import uuid

# Load environment variables
load_dotenv()

# Set Page Config
st.set_page_config(
    page_title="DASH V2 - Strategic Intel",
    page_icon="💎",
    layout="wide"
)

# Initialize Session ID for Persistence
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Sidebar
with st.sidebar:
    st.title("🛡️ DASH V2")
    st.markdown("---")
    st.write(f"**Session ID:** `{st.session_state.session_id}`")
    st.success("Persistent Memory: Active")
    st.success("Self-Learning: Enabled")
    
    if st.button("New Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

st.title("💎 DASH: Self-Learning E-commerce Team")
st.caption("Strategic Intelligence with Persistent Memory & Reasoning")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Analyze business performance..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Team is reasoning..."):
            try:
                # Instantiate Team with session persistence
                team = get_dash_team()
                
                # Run Team using the session_id with streaming enabled
                response_stream = team.run(prompt, session_id=st.session_state.session_id, stream=True)
                
                # Streamlit write_stream takes a generator of strings
                def stream_generator():
                    for chunk in response_stream:
                        # Prevent duplicate text by ignoring the internal Analyst/Engineer streams
                        if hasattr(chunk, "agent_id") and str(chunk.agent_id).lower() in ["analyst", "engineer"]:
                            continue
                        if chunk.content:
                            yield chunk.content
                
                content = st.write_stream(stream_generator())
                st.session_state.messages.append({"role": "assistant", "content": content})
                
                # Note: Tool call visualization is simplified when streaming

            except Exception as e:
                st.error(f"Traceback: {e}")

st.markdown("---")
st.info("💡 Try asking: 'Analyze high-value customers' or 'Identify revenue trends'. The agent will reason through the SQL and learn patterns for your next questions.")
