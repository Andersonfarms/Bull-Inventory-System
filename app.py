# ==========================================
# Bull Inventory TERMINAL // DATA-LINK 
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

# --- 3. SIDEBAR & LOGO ---
st.sidebar.image("bull.png", width=200)
st.sidebar.title("Navigation")
# ONLY ONE RADIO BUTTON FOR THE ENTIRE APP
page = st.sidebar.radio("Go to", ["Dashboard", "Add New Stock", "Update Inventory", "Activity Log"])

# --- PAGE: DASHBOARD ---
if page == "Dashboard":
    st.title("🏗️ Bull Inventory Dashboard")
    df = load_inventory()
    
    if not df.empty:
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Models", len(df))
        
        target_qty_col = 'Qty_On_Hand'
        if target_qty_col in df.columns:
            total_units = pd.to_numeric(df[target_qty_col], errors='coerce').sum()
            col2.metric("Total Units", int(total_units))
        else:
            col2.metric("Total Units", 0)
            
        col3.metric("Categories", len(df['Category'].unique()) if 'Category' in df.columns else 0)

        # --- FLEET BREAKDOWN ---
        st.markdown("### 📊 Fleet Breakdown")
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

        st.markdown("---")
        
        # Search and Table (Bulletproofed against empty cells)
