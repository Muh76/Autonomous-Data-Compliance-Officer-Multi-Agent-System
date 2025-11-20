"""
ADCO Dashboard
Real-time interface for the Autonomous Data & Compliance Officer.
"""

import streamlit as st
import asyncio
import sys
import os
from pathlib import Path
import pandas as pd
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from adk.agents.coordinator import CoordinatorAgent
from adk.core.message_bus import MessageBus, MessageType
from adk.core.state_manager import StateManager
from adk.core.task_queue import TaskQueue

# Page Config
st.set_page_config(
    page_title="ADCO | Autonomous Compliance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stAlert {
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "scan_results" not in st.session_state:
    st.session_state.scan_results = []
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/security-shield-green.png", width=64)
    st.title("ADCO System")
    st.caption("Autonomous Data & Compliance Officer")
    
    st.divider()
    
    st.subheader("System Status")
    st.success("● All Agents Online")
    
    st.divider()
    
    st.subheader("Active Agents")
    st.markdown("🤖 **Coordinator** (Idle)")
    st.markdown("🕵️ **Risk Scanner** (Ready)")
    st.markdown("⚖️ **Policy Matcher** (Ready)")
    st.markdown("📝 **Report Writer** (Ready)")

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🛡️ Compliance Overview")
    
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Risk Score", "Low", "-2%")
    m2.metric("Active Risks", "3", "+1")
    m3.metric("Data Sources", "12", "0")
    m4.metric("Compliance Rate", "94%", "+1.5%")
    
    st.divider()
    
    # Scan Interface
    st.subheader("🚀 Start New Scan")
    
    with st.form("scan_form"):
        c1, c2 = st.columns(2)
        with c1:
            source_type = st.selectbox("Source Type", ["Database", "File System", "API Endpoint"])
        with c2:
            target = st.text_input("Target (e.g., DB Connection String)", value="production_users_db")
            
        framework = st.multiselect("Compliance Frameworks", ["GDPR", "HIPAA", "CCPA"], default=["GDPR"])
        
        submitted = st.form_submit_button("Run Compliance Audit")
        
        if submitted:
            st.info(f"Initiating scan on {target} ({source_type})...")
            # Simulate Agent Action
            with st.spinner("Agents working..."):
                time.sleep(2)
                st.session_state.agent_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Coordinator: Received scan request for {target}")
                time.sleep(1)
                st.session_state.agent_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] RiskScanner: Scanning {target} for PII...")
                time.sleep(1.5)
                st.session_state.agent_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] RiskScanner: Detected 2 potential PII exposures.")
                time.sleep(1)
                st.session_state.agent_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] PolicyMatcher: Analyzing findings against GDPR...")
                time.sleep(1.5)
                st.success("Audit Complete! Report generated.")
                
                # Add mock result
                st.session_state.scan_results.append({
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M'),
                    "target": target,
                    "risks": 2,
                    "status": "Non-Compliant"
                })

    # Recent Scans
    st.subheader("Recent Audits")
    if st.session_state.scan_results:
        df = pd.DataFrame(st.session_state.scan_results)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No recent audits found.")

with col2:
    st.subheader("🧠 Agent Live Feed")
    
    # Agent Logs Console
    log_container = st.container(height=400)
    with log_container:
        if st.session_state.agent_logs:
            for log in st.session_state.agent_logs:
                st.text(log)
        else:
            st.caption("Waiting for agent activity...")
            
    st.divider()
    
    st.subheader("💬 Ask Compliance Officer")
    user_input = st.chat_input("Ask about regulations...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.agent_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] User: {user_input}")
        
        # Mock response
        response = f"Based on GDPR, {user_input} requires explicit consent."
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.agent_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] PolicyMatcher: {response}")

    # Chat History
    with st.container(height=300):
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
