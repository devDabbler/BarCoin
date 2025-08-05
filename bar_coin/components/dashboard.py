"""
Main dashboard component for BAR-COIN Streamlit application.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd

from bar_coin.hardware.coin_counter import coin_counter
from bar_coin.utils.database import db
from bar_coin.utils.helpers import (
    calculate_total_value, calculate_total_coins, format_coin_counts,
    get_coin_statistics, format_duration, format_timestamp
)
from bar_coin.config.settings import PHILIPPINE_COINS, COLORS, UI_CONFIG

def render_dashboard(user: Dict[str, Any]):
    """Render the main dashboard."""
    
    # Initialize session state
    if 'coin_counts' not in st.session_state:
        st.session_state.coin_counts = {denom: 0 for denom in PHILIPPINE_COINS.keys()}
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = None
    
    # Page header
    st.title("🪙 BAR-COIN Dashboard")
    st.markdown("---")
    
    # Hardware status and controls
    render_hardware_controls()
    
    # Main dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_real_time_counter()
        render_coin_breakdown()
    
    with col2:
        render_control_panel()
        render_hardware_status()
    
    # Statistics and charts
    st.markdown("---")
    render_statistics_section(user)
    
    # Session management
    render_session_management(user)

def render_hardware_controls():
    """Render hardware connection controls."""
    st.markdown("### 🔧 Hardware Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔌 Connect Hardware", use_container_width=True):
            if coin_counter.connect():
                st.success("Hardware connected successfully!")
                st.session_state.hardware_connected = True
            else:
                st.error("Failed to connect to hardware")
    
    with col2:
        if st.button("🔌 Disconnect", use_container_width=True):
            coin_counter.disconnect()
            st.session_state.hardware_connected = False
            st.success("Hardware disconnected")
    
    with col3:
        if st.button("🔄 Test Connection", use_container_width=True):
            if coin_counter.test_connection():
                st.success("Connection test successful!")
            else:
                st.error("Connection test failed")

def render_real_time_counter():
    """Render real-time coin counter display."""
    st.markdown("### 📊 Real-time Counter")
    
    # Get current statistics
    stats = get_coin_statistics(st.session_state.coin_counts)
    
    # Main counter display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Coins",
            value=f"{stats['total_coins']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Value",
            value=stats['formatted_total_value'],
            delta=None
        )
    
    with col3:
        if st.session_state.session_start_time:
            elapsed = datetime.now() - st.session_state.session_start_time
            speed = calculate_processing_speed(st.session_state.session_start_time, stats['total_coins'])
            st.metric(
                label="Speed (coins/min)",
                value=f"{speed:.1f}",
                delta=None
            )
        else:
            st.metric(
                label="Speed (coins/min)",
                value="0.0",
                delta=None
            )
    
    # Processing speed indicator
    if st.session_state.session_start_time:
        elapsed = datetime.now() - st.session_state.session_start_time
        speed = calculate_processing_speed(st.session_state.session_start_time, stats['total_coins'])
        
        if speed > 10:
            status = "🟢 High Speed"
            color = COLORS["SUCCESS_GREEN"]
        elif speed > 5:
            status = "🟡 Medium Speed"
            color = COLORS["WARNING_ORANGE"]
        else:
            status = "🔴 Low Speed"
            color = COLORS["ERROR_RED"]
        
        st.markdown(f"**Processing Speed:** {status} ({speed:.1f} coins/min)")

def render_coin_breakdown():
    """Render coin breakdown by denomination."""
    st.markdown("### 🪙 Coin Breakdown")
    
    formatted_counts = format_coin_counts(st.session_state.coin_counts)
    
    # Create a DataFrame for display
    df = pd.DataFrame(formatted_counts)
    
    if not df.empty:
        # Display as a table
        st.dataframe(
            df[['name', 'count', 'formatted_value']].rename(columns={
                'name': 'Denomination',
                'count': 'Count',
                'formatted_value': 'Value'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Create pie chart
        fig = px.pie(
            df, 
            values='value', 
            names='name',
            title="Coin Distribution by Value",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_control_panel():
    """Render control panel for hardware operations."""
    st.markdown("### 🎮 Control Panel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Start", use_container_width=True, type="primary"):
            if not st.session_state.current_session_id:
                # Create new session
                session_id = db.create_session(st.session_state.user['id'])
                st.session_state.current_session_id = session_id
                st.session_state.session_start_time = datetime.now()
                
                if coin_counter.start_session(str(session_id)):
                    st.success("Session started!")
                else:
                    st.error("Failed to start session")
            else:
                st.warning("Session already in progress")
    
    with col2:
        if st.button("⏸️ Pause", use_container_width=True):
            st.info("Pause functionality - coming soon")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("⏹️ Stop", use_container_width=True):
            if st.session_state.current_session_id:
                # End session
                stats = get_coin_statistics(st.session_state.coin_counts)
                db.end_session(
                    st.session_state.current_session_id,
                    stats['total_value'],
                    stats['total_coins']
                )
                
                coin_counter.end_session()
                st.session_state.current_session_id = None
                st.session_state.session_start_time = None
                st.success("Session ended!")
            else:
                st.warning("No active session")
    
    with col4:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.coin_counts = {denom: 0 for denom in PHILIPPINE_COINS.keys()}
            coin_counter.reset_counters()
            st.success("Counters reset!")
    
    # Emergency stop
    st.markdown("---")
    if st.button("🚨 EMERGENCY STOP", use_container_width=True, type="secondary"):
        coin_counter.emergency_stop()
        st.session_state.current_session_id = None
        st.session_state.session_start_time = None
        st.error("EMERGENCY STOP ACTIVATED!")

def render_hardware_status():
    """Render hardware status information."""
    st.markdown("### 📡 Hardware Status")
    
    status = coin_counter.get_status()
    
    # Connection status
    if status['connected']:
        st.success("🟢 Connected")
    else:
        st.error("🔴 Disconnected")
    
    # Mode indicator
    if status['mock_mode']:
        st.info("🧪 Mock Mode")
    else:
        st.info("🔧 Hardware Mode")
    
    # Session status
    if st.session_state.current_session_id:
        st.success(f"📊 Session Active: {st.session_state.current_session_id}")
    else:
        st.info("📊 No Active Session")
    
    # Hardware statistics
    if 'stats' in status:
        stats = status['stats']
        st.markdown("**Hardware Stats:**")
        st.write(f"- Coins Processed: {stats.get('total_coins_processed', 0)}")
        st.write(f"- Errors: {stats.get('errors', 0)}")
        st.write(f"- Warnings: {stats.get('warnings', 0)}")
    
    # Hardware info
    info = coin_counter.get_hardware_info()
    st.markdown("**Hardware Info:**")
    st.write(f"- Type: {info['type']}")
    st.write(f"- Port: {info['port']}")
    st.write(f"- Baud Rate: {info['baud_rate']}")

def render_statistics_section(user: Dict[str, Any]):
    """Render statistics and charts section."""
    st.markdown("### 📈 Statistics & Analytics")
    
    # Get user sessions
    sessions = db.get_user_sessions(user['id'], limit=10)
    
    if sessions:
        # Create sessions DataFrame
        sessions_df = pd.DataFrame(sessions)
        sessions_df['start_time'] = pd.to_datetime(sessions_df['start_time'])
        sessions_df['end_time'] = pd.to_datetime(sessions_df['end_time'])
        sessions_df['duration'] = (sessions_df['end_time'] - sessions_df['start_time']).dt.total_seconds() / 60
        
        # Recent sessions chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                sessions_df.head(10),
                x='start_time',
                y='calculated_value',
                title="Recent Sessions - Total Value",
                labels={'calculated_value': 'Value (₱)', 'start_time': 'Session Start'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                sessions_df.head(10),
                x='start_time',
                y='calculated_coins',
                title="Recent Sessions - Coin Count",
                labels={'calculated_coins': 'Coins', 'start_time': 'Session Start'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Daily statistics
        daily_stats = db.get_daily_stats(user['id'], days=30)
        if daily_stats:
            daily_df = pd.DataFrame(daily_stats)
            daily_df['date'] = pd.to_datetime(daily_df['date'])
            
            fig = px.area(
                daily_df,
                x='date',
                y='total_value',
                title="Daily Total Value (Last 30 Days)",
                labels={'total_value': 'Value (₱)', 'date': 'Date'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No session data available. Start counting coins to see statistics!")

def render_session_management(user: Dict[str, Any]):
    """Render session management section."""
    st.markdown("### 📋 Session Management")
    
    # Current session info
    if st.session_state.current_session_id:
        st.markdown("**Current Session:**")
        st.write(f"- Session ID: {st.session_state.current_session_id}")
        if st.session_state.session_start_time:
            elapsed = datetime.now() - st.session_state.session_start_time
            st.write(f"- Duration: {format_duration(int(elapsed.total_seconds()))}")
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Export Session Data", use_container_width=True):
                export_session_data(st.session_state.current_session_id)
        
        with col2:
            if st.button("📄 Generate Report", use_container_width=True):
                generate_session_report(st.session_state.current_session_id)
    
    # Recent sessions
    sessions = db.get_user_sessions(user['id'], limit=5)
    if sessions:
        st.markdown("**Recent Sessions:**")
        for session in sessions:
            with st.expander(f"Session {session['id']} - {session['start_time']}"):
                st.write(f"**Duration:** {format_duration(int(session.get('duration', 0)))}")
                st.write(f"**Total Value:** {format_peso(session.get('calculated_value', 0))}")
                st.write(f"**Total Coins:** {session.get('calculated_coins', 0)}")
                st.write(f"**Status:** {session.get('status', 'Unknown')}")

def export_session_data(session_id: int):
    """Export session data to CSV."""
    try:
        data = db.export_session_data(session_id)
        
        # Create CSV data
        csv_data = []
        for denomination, count in data['coin_counts'].items():
            csv_data.append({
                'Denomination': get_coin_name(denomination),
                'Count': count,
                'Value': denomination * count
            })
        
        df = pd.DataFrame(csv_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Export failed: {str(e)}")

def generate_session_report(session_id: int):
    """Generate session report."""
    try:
        data = db.export_session_data(session_id)
        
        # Create report content
        report = f"""
# Session Report - {session_id}

## Summary
- **Session ID:** {session_id}
- **Start Time:** {data['session'].get('start_time', 'N/A')}
- **End Time:** {data['session'].get('end_time', 'N/A')}
- **Total Value:** {format_peso(data['session'].get('calculated_value', 0))}
- **Total Coins:** {data['session'].get('calculated_coins', 0)}

## Coin Breakdown
"""
        
        for denomination, count in data['coin_counts'].items():
            report += f"- {get_coin_name(denomination)}: {count} coins ({format_peso(denomination * count)})\n"
        
        st.text_area("Session Report", report, height=300)
        
    except Exception as e:
        st.error(f"Report generation failed: {str(e)}")

def update_coin_counts():
    """Update coin counts from hardware data."""
    try:
        data_queue = coin_counter.get_data_queue()
        
        while not data_queue.empty():
            try:
                data = data_queue.get_nowait()
                if data and 'denomination' in data:
                    denomination = float(data['denomination'])
                    if denomination in PHILIPPINE_COINS:
                        st.session_state.coin_counts[denomination] += 1
                        
                        # Update database if session is active
                        if st.session_state.current_session_id:
                            db.add_coin_count(st.session_state.current_session_id, denomination)
            except:
                continue
                
    except Exception as e:
        st.error(f"Error updating coin counts: {str(e)}") 