import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Configuration
SERVER_URL = "https://dadusecurity-2.onrender.com"  # Replace with your actual server URL

st.set_page_config(page_title="Police Monitor", page_icon="👮", layout="wide")
st.title("👮 Police Connection Monitor")
st.write("Real-time monitoring of user connections to the server")

# Initialize session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# Function to fetch connection data
def fetch_connection_data():
    try:
        # Get active connections
        active_response = requests.get(f"{SERVER_URL}/active-connections")
        active_data = active_response.json().get('active_connections', []) if active_response.status_code == 200 else []
        
        # Get connection history
        history_response = requests.get(f"{SERVER_URL}/connection-history?limit=50")
        history_data = history_response.json().get('connection_history', []) if history_response.status_code == 200 else []
        
        return active_data, history_data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return [], []

# Create layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Active Connections")
    refresh_btn = st.button("🔄 Refresh Data")
    
    # Fetch data
    active_connections, connection_history = fetch_connection_data()
    
    # Display active connections
    if active_connections:
        active_df = pd.DataFrame(active_connections)
        # Format timestamp
        if 'timestamp' in active_df.columns:
            active_df['timestamp'] = pd.to_datetime(active_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(active_df[['user_name', 'timestamp']], use_container_width=True)
        st.metric("Active Users", len(active_connections))
    else:
        st.info("No active connections")
        st.metric("Active Users", 0)

with col2:
    st.subheader("Recent Connection History")
    
    if connection_history:
        history_df = pd.DataFrame(connection_history)
        # Format timestamp
        if 'timestamp' in history_df.columns:
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Color code actions
        def color_action(action):
            return "color: green;" if action == "connect" else "color: red;"
        
        styled_df = history_df[['user_name', 'action', 'timestamp']].style.applymap(
            color_action, subset=['action']
        )
        
        st.dataframe(styled_df, use_container_width=True, height=400)
    else:
        st.info("No connection history available")

# Notifications section
st.divider()
st.subheader("Live Notifications")

# Simulate receiving notifications (in a real app, this would use websockets or polling)
if refresh_btn:
    # Check for new events since last update
    new_events = [event for event in connection_history 
                 if datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')) > st.session_state.last_update]
    
    for event in new_events:
        emoji = "✅" if event['action'] == 'connect' else "❌"
        st.session_state.notifications.append(
            f"{emoji} {event['user_name']} {event['action']}ed at {event['timestamp']}"
        )
    
    st.session_state.last_update = datetime.now()

# Display notifications
if st.session_state.notifications:
    for notification in reversed(st.session_state.notifications[-10:]):  # Show last 10
        st.write(notification)
else:
    st.info("No notifications yet. Connections will appear here in real-time.")

# Auto-refresh
if st.checkbox("Auto-refresh every 10 seconds"):
    st.write("Auto-refresh enabled")
    time.sleep(10)
    st.rerun()

# Instructions
with st.expander("Monitoring Instructions"):
    st.markdown("""
    This police monitor shows:
    - **Active Connections**: Users currently connected to the server
    - **Connection History**: Recent connection and disconnection events
    - **Live Notifications**: Real-time alerts when users connect or disconnect
    
    Use the Refresh button to update the data manually, or enable auto-refresh
    for continuous monitoring.
    """)
