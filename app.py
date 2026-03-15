# ==========================================
# NyssaFire Gaming // CORE INVENTORY TERMINAL
# System Engineered by: NyssaFire Gaming & Michael Anderson
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from supabase import create_client, Client

# --- 0. WHITE-LABEL CONFIGURATION ---
# Change these variables for each new client deployment.
APP_CONFIG = {
    "company_name": "Bull", 
    "app_title": "Inventory System",
    "logo_path": "bull.png", 
    "timezone": "US/Central",
    
    # Database Tables
    "table_inventory": "bull_inventory",        
    "table_activity": "bull_activity_log",      
    "table_inbound": "bull_inbound_tracking",   
    
    # Client-Specific Dropdowns
    "sales_team": ["Fredrik L.", "Bailey A.", "Admin", "Other"],
    "machine_models": ["12X", "18X", "22X", "25X", "40X", "1100X", "Bucket", "Auger", "Ripper", "Rake", "Forks", "Wood Splitter", "Hedge Trimmers", "Hammer", "Other"],
    "machine_types": ["Excavator", "Skid Steer", "Other"],
    "categories": ["Machine", "Attachment", "Parts", "Other"],
    "carriers": ["Maersk", "CMA-CGM", "MSC", "Hapag-Lloyd", "Evergreen", "Other"]
}

# --- 1. CONFIG & CONNECTION ---
st.set_page_config(page_title=f"{APP_CONFIG['company_name']} {APP_CONFIG['app_title']}", page_icon="🏗️", layout="wide")

# ==========================================================
# TACTICAL UI THEME INJECTION
# ==========================================================
tactical_css = """
<style>
:root {
    --bg-base: #0a0a0a;         
    --surface-level: #1c1c1c;   
    --accent-orange: #ff5500;   
    --text-main: #ffffff;       
    --text-muted: #888888;      
    --border-grid: #333333;     
}

.stApp {
    background-color: var(--bg-base);
    color: var(--text-main);
    font-family: 'Courier New', Courier, monospace;
}

div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
    background-color: transparent !important;
    color: var(--text-main) !important; 
    border: 2px solid var(--accent-orange) !important;
    padding: 8px 15px !important;
    font-size: 0.95rem !important;
    font-weight: bold !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    transition: all 0.2s ease-in-out !important;
}

div[data-testid="stButton"] > button:hover,
div[data-testid="stButton"] > button:active,
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:active {
    background-color: var(--accent-orange) !important;
    color: var(--bg-base) !important;
    border-color: var(--accent-orange) !important;
}

.sidebar-header {
    color: var(--text-muted);
    font-size: 0.85rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 25px;
    margin-bottom: 10px;
    border-bottom: 1px solid var(--border-grid);
    padding-bottom: 3px;
}

.tracking-btn {
    display: inline-block;
    background-color: transparent;
    color: var(--accent-orange) !important;
    border: 1px solid var(--accent-orange);
    padding: 5px 10px;
    text-decoration: none;
    font-weight: bold;
    font-size: 0.85rem;
    border-radius: 3px;
    text-transform: uppercase;
    transition: 0.2s;
}
.tracking-btn:hover {
    background-color: var(--accent-orange);
    color: var(--bg-base) !important;
}
</style>
"""

st.markdown(tactical_css, unsafe_allow_html=True)

# Dynamic Header Block
st.markdown(f"""
```text
# ==========================================
# {APP_CONFIG['company_name'].upper()} INVENTORY TERMINAL // DATA-LINK v3.0
# System Engineered by: NyssaFire Gaming
# Core Uplink Established: {datetime.now(pytz.timezone(APP_CONFIG['timezone'])).strftime('%Y-%m-%d // %H:%M %Z')}
# ==========================================
