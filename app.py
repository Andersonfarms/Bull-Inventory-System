# ==========================================
# Bull Inventory TERMINAL // DATA-LINK v2.0
# System Engineered by: NyssaFire Gaming & Michael Anderson
# Core Uplink Established: 2026-02-17 // 10:13 CST
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from supabase import create_client, Client

# --- 1. CONFIG & CONNECTION ---
st.set_page_config(page_title="Bull Inventory System", page_icon="🏗️", layout="wide")

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

/* ---------------------------------------------------------
   TACTICAL BUTTON OVERRIDE (EDI STYLE)
--------------------------------------------------------- */
div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
    background-color: transparent !important;
    color: var(--accent-orange) !important;
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

/* ---------------------------------------------------------
   SIDEBAR HEADERS
--------------------------------------------------------- */
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
</style>
"""

st.markdown(tactical_css, unsafe_allow_html=True)

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()
CENTRAL = pytz.timezone("US/Central")

# --- 2. DATA LOADERS ---
def load_inventory():
    response = supabase.table("bull_inventory").select("*").execute()
    return pd.DataFrame(response.data)

def load_activity():
    response = supabase.table("bull_activity_log").select("*").order("Timestamp", desc=True).execute()
    return pd.DataFrame(response.data)

# --- 3. THE TACTICAL SIDEBAR ROUTER ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def nav_to(page_name):
    st.session_state.current_page = page_name

try:
    st.sidebar.image("bull.png", width=200)
except:
    pass # Failsafe if image doesn't load

st.sidebar.markdown('<div class="sidebar-header">CORE OPERATIONS</div>', unsafe_allow_html=True)
st.sidebar.button("Sitrep / Dashboard", on_click=nav_to, args=("Dashboard",), use_container_width=True)
st.sidebar.button("Official Duty Log", on_click=nav_to, args=("Activity Log",), use_container_width=True)

st.sidebar.markdown('<div class="sidebar-header">DIGITAL LEDGERS</div>', unsafe_allow_html=True)
st.sidebar.button("Equipment Ledger", on_click=nav_to, args=("Equipment Ledger",), use_container_width=True)
st.sidebar.button("Attachment Ledger", on_click=nav_to, args=("Attachment Ledger",), use_container_width=True)
st.sidebar.button("Parts Ledger", on_click=nav_to, args=("Parts Ledger",), use_container_width=True)

st.sidebar.markdown('<div class="sidebar-header">LOGISTICS (S-4)</div>', unsafe_allow_html=True)
st.sidebar.button("Add New Stock", on_click=nav_to, args=("Add New Stock",), use_container_width=True)
st.sidebar.button("Sell / Dispatch", on_click=nav_to, args=("Sell Inventory",), use_container_width=True)
st.sidebar.button("Update Status", on_click=nav_to, args=("Update Inventory",), use_container_width=True)

page = st.session_state.current_page

# --- PAGE: DASHBOARD (SITREP) ---
if page == "Dashboard":
    st.title("📡 Sitrep: Master Overview")
    df = load_inventory()
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Line Items", len(df))
        
        target_qty_col = 'Qty_On_Hand'
        if target_qty_col in df.columns:
            total_units = pd.to_numeric(df[target_qty_col], errors='coerce').sum()
            col2.metric("Total Physical Units", int(total_units))
        else:
            col2.metric("Total Physical Units", 0)
            
        st.markdown("---")
        st.markdown("### 📊 Active Fleet Breakdown")
        breakdown_col1, breakdown_col2 = st.columns(2)
        
        with breakdown_col1:
            if 'Model' in df.columns and target_qty_col in df.columns:
                st.write("**By Specific Model:**")
                model_counts = df.groupby('Model')[target_qty_col].sum().reset_index()
                model_counts = model_counts.sort_values(by=target_qty_col, ascending=False)
                st.dataframe(model_counts, hide_index=True, use_container_width=True)
        
        with breakdown_col2:
            if 'Category' in df.columns and target_qty_col in df.columns:
                st.write("**By Category:**")
                cat_counts = df.groupby('Category')[target_qty_col].sum().reset_index()
                st.dataframe(cat_counts, hide_index=True, use_container_width=True)
    else:
        st.warning("No inventory found in Supabase.")

# --- PAGES: THE DIGITAL LEDGERS ---
elif page in ["Equipment Ledger", "Attachment Ledger", "Parts Ledger"]:
    st.title(f"📂 {page}")
    df = load_inventory()
    
    if not df.empty:
        # Filter logic based on the selected ledger
        if page == "Equipment Ledger":
            df = df[df['Category'] == 'Machine']
        elif page == "Attachment Ledger":
            df = df[df['Category'] == 'Attachment']
        elif page == "Parts Ledger":
            df = df[df['Category'] == 'Parts']
            
        search = st.text_input(f"🔍 Search {page}:")
        if search:
            mask = pd.Series(False, index=df.index)
            if 'Model' in df.columns:
                mask |= df['Model'].astype(str).str.contains(search, case=False, na=False)
            if 'ID' in df.columns:
                mask |= df['ID'].astype(str).str.contains(search, case=False, na=False)
            df = df[mask]
            
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning(f"No records found for {page}.")

# --- PAGE: ADD NEW STOCK ---
elif page == "Add New Stock":
    st.title("➕ Logistics: Register New Stock")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("Item ID (e.g., A-9PWW)")
            model_options = ["12X", "18X", "22X", "25X", "40X", "1100X", "Bucket", "Auger", "Ripper", "Rake", "Forks", "Wood Splitter", "Hedge Trimmers", "Hammer", "Other"]
            new_model = st.selectbox("Model Name", model_options)
            new_type = st.selectbox("Machine Type", ["Excavator", "Skid Steer", "Other"])
            new_qty = st.number_input("Quantity", min_value=1, step=1)
            
        with col2:
            new_cat = st.selectbox("Category", ["Machine", "Attachment", "Parts", "Other"])
            size_options = ["N/A", "8\"", "12\"", "18\"", "24\"", "36\"", "40\"", "48\"", "Small", "Medium", "Large"]
            new_size = st.selectbox("Size", size_options)
            new_loc = st.text_input("Location", value="Warehouse")
