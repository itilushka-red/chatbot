import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import random
import datetime
import io
from PIL import Image
import base64

# Import audio recorder component
from audio_recorder_streamlit import audio_recorder

# Set page configuration
st.set_page_config(
    page_title="Industrial QA System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #34495e;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    .report-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #3498db;
    }
    .bot-message {
        background-color: #eef2f7;
        padding: 12px;
        border-radius: 15px 15px 15px 0;
        margin: 10px 0;
        display: inline-block;
        max-width: 80%;
    }
    .user-message {
        background-color: #1565c0;
        color: white;
        padding: 12px;
        border-radius: 15px 15px 0 15px;
        margin: 10px 0;
        display: inline-block;
        max-width: 80%;
        margin-left: auto;
    }
    .category-tag {
        background-color: #3498db;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 5px;
    }
    .priority-high {
        background-color: #e74c3c;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .priority-medium {
        background-color: #f39c12;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .priority-low {
        background-color: #27ae60;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .thinking-animation {
        display: inline-block;
        margin-left: 5px;
    }
    .stButton>button {
        background-color: #1565c0;
        color: white;
        border-radius: 5px;
    }
    .voice-input-button>button {
        background-color: #e74c3c !important;
        color: white;
        border-radius: 25px;
    }
    .manager-view-button>button {
        background-color: #2c3e50 !important;
        color: white;
    }
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .recommendation-item {
        padding: 8px 0;
        border-bottom: 1px solid #eee;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .audio-recorder {
        margin-top: 10px;
    }
    .transcribing-message {
        color: #7f8c8d;
        font-style: italic;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'view' not in st.session_state:
    st.session_state.view = "engineer"  # Default view is engineer
if 'reports' not in st.session_state:
    # Initialize with some mock reports
    st.session_state.reports = [
        {
            "id": "QA-2023-0470",
            "description": "Multiple scratches on product surface",
            "timestamp": "2023-11-11 08:23:15",
            "category": "PRODUCT DEFECT - EXTERIOR COMPONENT",
            "priority": "Low",
            "machine": "Assembly line 3"
        },
        {
            "id": "QA-2023-0471",
            "description": "Bearing making unusual noise",
            "timestamp": "2023-11-11 09:45:22",
            "category": "EQUIPMENT MALFUNCTION - NOISE",
            "priority": "Medium",
            "machine": "Press 2211"
        }
    ]
if 'waiting_for_confirmation' not in st.session_state:
    st.session_state.waiting_for_confirmation = False
if 'current_report' not in st.session_state:
    st.session_state.current_report = None
if 'current_report_id' not in st.session_state:
    st.session_state.current_report_id = 473  # Start with this ID since we have mock reports already
if 'transcribing' not in st.session_state:
    st.session_state.transcribing = False
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None

# Mock data for historical oil leak issues
if 'oil_leak_history' not in st.session_state:
    # Generate dates for the last 4 weeks
    today = datetime.datetime.now()
    dates = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(28)]
    
    # Generate frequencies with an increasing trend for the most recent days
    frequencies = [0] * 28
    # Last week - increasing trend
    frequencies[0:7] = [2, 1, 1, 0, 1, 1, 0]
    # 2 weeks ago
    frequencies[7:14] = [0, 1, 0, 0, 0, 1, 0]
    # 3 weeks ago
    frequencies[14:21] = [0, 0, 1, 0, 0, 0, 0]
    # 4 weeks ago
    frequencies[21:28] = [0, 0, 0, 0, 1, 0, 0]
    
    # Reverse the lists so dates are in chronological order
    dates.reverse()
    frequencies.reverse()
    
    st.session_state.oil_leak_history = {
        "dates": dates,
        "frequencies": frequencies
    }

# Function to simulate speech to text conversion
def simulate_transcription(audio_data):
    """Simulate transcription of audio to text"""
    # In a real implementation, you would send the audio to a speech-to-text service
    # For the demo, we'll simulate the process with a fixed response
    time.sleep(2)  # Simulate processing time
    return "Item with number 12345 has a cover defect"

# Sidebar for application controls and information
with st.sidebar:
    st.image("https://via.placeholder.com/150x80?text=CompanyLogo", width=150)
    st.markdown("### Industrial QA System")
    st.markdown("AI-powered quality assurance reporting and analysis")
    
    st.divider()
    
    # View toggle
    if st.session_state.view == "engineer":
        st.markdown("### Engineer View")
        st.markdown("Current mode: Quality Reporting")
        st.markdown("---")
        st.button("Switch to Manager View", key="switch_to_manager", 
                 on_click=lambda: setattr(st.session_state, 'view', 'manager'),
                 type="primary")
    else:
        st.markdown("### Manager View")
        st.markdown("Current mode: Quality Analysis")
        st.markdown("---")
        st.button("Switch to Engineer View", key="switch_to_engineer", 
                 on_click=lambda: setattr(st.session_state, 'view', 'engineer'),
                 type="primary")
    
    st.divider()
    st.markdown("### Demo Controls")
    if st.button("Reset Demo"):
        st.session_state.messages = []
        st.session_state.waiting_for_confirmation = False
        st.session_state.current_report = None
        st.session_state.transcribing = False
        st.session_state.audio_data = None
    
    st.markdown("---")
    st.markdown("##### Demo Version 1.0")
    st.markdown("© 2023 Your Company")

# Main content area
if st.session_state.view == "engineer":
    st.markdown('<h1 class="main-header">Quality Reporting System</h1>', unsafe_allow_html=True)
    
    # Display message history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Typing animation when processing
    if 'thinking' in st.session_state and st.session_state.thinking:
        with st.container():
            st.markdown('<div class="bot-message">Processing your report<span class="thinking-animation">...</span></div>', 
                       unsafe_allow_html=True)
    
    # Show transcribing message when processing audio
    if st.session_state.transcribing:
        with st.container():
            st.markdown('<div class="bot-message">Transcribing audio<span class="thinking-animation">...</span></div>', 
                       unsafe_allow_html=True)
    
    # Input area at the bottom
    st.markdown("---")
    
    # If we're waiting for confirmation
    if st.session_state.waiting_for_confirmation:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, that's correct", key="confirm_yes"):
                # Process confirmation and categorize the issue
                if "oil leak" in st.session_state.current_report.lower():
                    category = "EQUIPMENT MALFUNCTION - FLUID LEAK"
                    priority = "Medium"
                elif "cover defect" in st.session_state.current_report.lower():
                    category = "PRODUCT DEFECT - EXTERIOR COMPONENT"
                    priority = "High"
                else:
                    category = "GENERAL ISSUE"
                    priority = "Medium"
                
                report_id = f"QA-2023-0{st.session_state.current_report_id}"
                
                # Add the bot response
                confirmation_response = f"Report confirmed. I've categorized this as: {category}. Priority: {priority}. Report ID: {report_id} has been created."
                st.session_state.messages.append({"role": "assistant", "content": confirmation_response})
                
                # Add to reports database
                new_report = {
                    "id": report_id,
                    "description": st.session_state.current_report,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "category": category,
                    "priority": priority,
                    "machine": f"Machine {random.randint(1000, 9999)}" if "machine" in st.session_state.current_report.lower() else "Item #12345"
                }
                st.session_state.reports.append(new_report)
                
                # Reset states
                st.session_state.waiting_for_confirmation = False
                st.session_state.current_report = None
                st.session_state.current_report_id += 1
                
                # Force refresh
                st.experimental_rerun()
                
        with col2:
            if st.button("No, let me correct it", key="confirm_no"):
                # Reset the confirmation state
                st.session_state.waiting_for_confirmation = False
                st.session_state.current_report = None
                st.session_state.messages.append({"role": "assistant", "content": "Please provide a corrected report."})
                st.experimental_rerun()
    else:
        # Text input and voice recording
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input("Enter quality issue details:", key="text_input")
        
        with col2:
            st.markdown("#### Record Audio")
            audio_bytes = audio_recorder(
                text="",
                recording_color="#e74c3c",
                neutral_color="#2c3e50",
                icon_name="microphone",
                icon_size="2x"
            )
            
            if audio_bytes:
                # Store the audio data in session state
                st.session_state.audio_data = audio_bytes
                st.session_state.transcribing = True
                st.experimental_rerun()
        
        # Process text input
        if user_input:
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Simulate AI thinking
            st.session_state.thinking = True
            st.experimental_rerun()

# Process audio if there's data and we're transcribing
if st.session_state.view == "engineer" and st.session_state.transcribing and st.session_state.audio_data:
    # Simulate transcription process
    with st.spinner("Transcribing audio..."):
        transcribed_text = simulate_transcription(st.session_state.audio_data)
    
    # Add the transcribed text as a user message
    st.session_state.messages.append({
        "role": "user", 
        "content": f"[Voice Message]: {transcribed_text}"
    })
    
    # Clear audio data and transcribing flag
    st.session_state.audio_data = None
    st.session_state.transcribing = False
    
    # Set up for AI processing
    st.session_state.current_report = transcribed_text
    st.session_state.thinking = True
    
    # Refresh to show the transcribed message
    st.experimental_rerun()

# If thinking, simulate processing and then respond
if 'thinking' in st.session_state and st.session_state.thinking and st.session_state.view == "engineer":
    # Simulate processing delay
    time.sleep(1.5)
    st.session_state.thinking = False
    
    # Get the last user message
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_message = st.session_state.messages[-1]["content"]
        
        # If it was a voice message, extract the actual message
        if "[Voice Message]:" in last_message:
            last_message = last_message.split("[Voice Message]:")[1].strip()
        
        # Store the current report being processed
        st.session_state.current_report = last_message
        
        # Generate confirmation request
        if "oil" in last_message.lower() and "leak" in last_message.lower():
            confirmation_text = f"Did I understand correctly that there is an oil leak on industrial machine 1234? Please confirm."
        elif "cover defect" in last_message.lower():
            confirmation_text = f"Did I understand correctly that item #12345 has a defect in its cover/casing? Please confirm."
        else:
            confirmation_text = f"Did I understand correctly that: {last_message}? Please confirm."
        
        # Add the response to messages
        st.session_state.messages.append({"role": "assistant", "content": confirmation_text})
        
        # Set waiting for confirmation
        st.session_state.waiting_for_confirmation = True
    
    # Refresh the page to show the response
    st.experimental_rerun()

# Manager view
if st.session_state.view == "manager":
    st.markdown('<h1 class="main-header">Quality Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Tabs for different manager views
    tab1, tab2, tab3 = st.tabs(["Quality Reports", "Analysis", "Recommendations"])
    
    with tab1:
        st.markdown('<p class="sub-header">Recent Quality Issues</p>', unsafe_allow_html=True)
        
        # Convert reports to dataframe for display
        if st.session_state.reports:
            df = pd.DataFrame(st.session_state.reports)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No quality reports found in the system.")
    
    with tab2:
        st.markdown('<p class="sub-header">Quality Trends Analysis</p>', unsafe_allow_html=True)
        
        # Analysis query options
        analysis_query = st.selectbox(
            "What would you like to analyze?",
            ["Select an option", "Oil leakage problems", "Product defects", "Equipment malfunctions"]
        )
        
        if analysis_query == "Oil leakage problems":
            st.markdown("### Oil Leakage Analysis")
            
            # Text analysis
            st.markdown("""
            <div class="bot-message">
            Yes, there were 7 oil leakage reports in the last two weeks. This appears to be an increasing trend, 
            with 4 reports occurring in just the last 3 days.
            </div>
            """, unsafe_allow_html=True)
            
            # Chart of oil leakage over time
            if st.button("Show me a chart of oil leakage reports over time"):
                with st.spinner("Generating visualization..."):
                    time.sleep(1)  # Simulate processing
                    
                    # Create the chart
                    fig, ax = plt.subplots(figsize=(10, 5))
                    
                    # Get data from session state
                    dates = st.session_state.oil_leak_history["dates"]
                    frequencies = st.session_state.oil_leak_history["frequencies"]
                    
                    # Plot the data
                    ax.bar(dates, frequencies, color='#3498db')
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Number of Oil Leak Reports')
                    ax.set_title('Oil Leak Reports Over Time (Last 4 Weeks)')
                    
                    # Format x-axis to show fewer dates (weekly)
                    ax.set_xticks([dates[i] for i in range(0, len(dates), 7)])
                    ax.tick_params(axis='x', rotation=45)
                    
                    # Add grid lines
                    ax.grid(axis='y', linestyle='--', alpha=0.7)
                    
                    # Tight layout
                    plt.tight_layout()
                    
                    # Display the chart
                    st.pyplot(fig)
        
        elif analysis_query == "Product defects":
            st.info("This analysis option is part of the extended demo. Please select 'Oil leakage problems' for the main demo flow.")
        
        elif analysis_query == "Equipment malfunctions":
            st.info("This analysis option is part of the extended demo. Please select 'Oil leakage problems' for the main demo flow.")
    
    with tab3:
        st.markdown('<p class="sub-header">Recommended Actions</p>', unsafe_allow_html=True)
        
        # Recommendation query options
        rec_query = st.text_input("Ask for recommendations:", value="What actions should we take?")
        
        if rec_query and "action" in rec_query.lower():
            # Simulate thinking
            with st.spinner("Analyzing quality data and generating recommendations..."):
                time.sleep(1.5)  # Simulate processing time
            
            # Display recommendations
            st.markdown("""
            <div class="bot-message">
            Based on the pattern of reports, I recommend:
            <ol>
                <li class="recommendation-item">Immediate inspection of machine 1234</li>
                <li class="recommendation-item">Review of the last 3 maintenance records for similar machines</li>
                <li class="recommendation-item">Scheduling preventive maintenance for all hydraulic systems</li>
            </ol>
            <br>
            This could prevent potential production stoppage estimated at 4-8 hours.
            </div>
            """, unsafe_allow_html=True)
            
            # Additional insight
            st.markdown("### Impact Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                # Simple impact visualization
                fig, ax = plt.subplots(figsize=(5, 4))
                
                # Sample data
                categories = ['Production Loss', 'Repair Costs', 'Quality Impact']
                no_action = [8, 12, 7]
                with_action = [2, 5, 1]
                
                x = np.arange(len(categories))
                width = 0.35
                
                ax.bar(x - width/2, no_action, width, label='Without Action', color='#e74c3c')
                ax.bar(x + width/2, with_action, width, label='With Recommended Action', color='#2ecc71')
                
                ax.set_ylabel('Severity (1-10)')
                ax.set_title('Estimated Impact Analysis')
                ax.set_xticks(x)
                ax.set_xticklabels(categories)
                ax.legend()
                
                plt.tight_layout()
                st.pyplot(fig)
            
            with col2:
                st.markdown("### Estimated Savings")
                st.markdown("""
                * **Production time saved**: 4-8 hours
                * **Labor cost reduction**: ~$1,200
                * **Parts/material savings**: ~$3,500
                * **Total estimated benefit**: $5,000 - $7,000
                """)

# Footer
st.markdown("---")
st.markdown("This is a demonstration system showcasing LLM-based quality assurance capabilities.")