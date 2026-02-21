import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

# --- CONFIGURATION ---
INV_FILE = "bull_inventory.csv"
LOG_FILE = "activity_log.csv"
CENTRAL = pytz.timezone('US/Central')

st.set_page_config(page_title="Bull Inventory System", layout="wide")
st.title("🏗️ Bull Inventory")

# --- DATA LOAD ---
if os.path.exists(INV_FILE):
    df = pd.read_csv(INV_FILE)
    # Safety checks for missing columns
    if 'Size' not in df.columns:
        df['Size'] = ""
    if 'Model' not in df.columns:
        df['Model'] = ""
    df['Qty_On_Hand'] = pd.to_numeric(df['Qty_On_Hand'], errors='coerce').fillna(0).astype(int)
    df = df.fillna("")
else:
    st.error("Inventory file not found!")
    st.stop()

# --- DASHBOARD TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 Current Inventory", "📈 Analytics", "🕒 Recent Activity", "➕ Add New Stock"])

with tab1:
    # Refresh data for the live view
    df = pd.read_csv(INV_FILE)
    
    # Re-apply safety checks after refreshing the live view
    if 'Size' not in df.columns:
        df['Size'] = ""
    if 'Model' not in df.columns:
        df['Model'] = ""
    df = df.fillna("")

    st.subheader("Live Warehouse Stock")
    # Display ID as string to remove commas
    st.dataframe(df.assign(ID=df['ID'].astype(str)), use_container_width=True)

    st.divider()
    st.header("🏗️ Log Transaction")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    if not df.empty:
        available_items = df[df['Status'] == 'Available']
        # Safely format the options using .get() to prevent KeyErrors
        item_options = available_items.apply(
            lambda x: f"{x.get('ID', 'N/A')} - {x.get('Size', '')} {x.get('Model', '')}", axis=1
        ).tolist()
    else:
        item_options = []

    with col1:
        selected_option = st.selectbox("Select Item (VIN - Model)", options=item_options, key="transaction_select")
        selected_id = str(selected_option.split(" - ")[0]) if selected_option else None

    with col2:
        user_list = ["Fredrik L", "Bailey S"]
        selected_user = st.selectbox("Logged By", options=user_list)

    with col3:
        action = st.selectbox("Action", ["Check Out", "Return", "Sold"])

    with col4:
        if st.button("Submit Transaction"):
            if selected_id:
                # Update Status
                new_status = "Out" if action == "Check Out" or action == "Sold" else "Available"
                df
