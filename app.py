import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
INV_FILE = "bull_inventory.csv"
LOG_FILE = "activity_log.csv"

st.set_page_config(page_title="Bull Inventory System", layout="wide")
st.title("🏗️ Anderson Farms Bull Inventory")

# --- DATA LOAD ---
if os.path.exists(INV_FILE):
    df = pd.read_csv(INV_FILE)
else:
    st.error("Inventory file not found!")
    st.stop()

# --- DASHBOARD TABS ---
tab1, tab2, tab3 = st.tabs(["📋 Current Inventory", "📈 Analytics", "🕒 Recent Activity"])

with tab1:
    st.subheader("Live Warehouse Stock")
    st.divider()
    # Display the inventory table
    st.dataframe(df[['ID', 'Category', 'Model', 'Status', 'Location', 'Qty_On_Hand']], use_container_width=True)

    st.divider()
    st.header("🏗️ Log Transaction")
    
    # Horizontal Layout for Transactions
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Show only items that are currently in stock (Qty > 0)
        available_ids = df[df['Qty_On_Hand'] > 0]['ID'].tolist()
        selected_id = st.selectbox("Select Item ID (VIN)", options=available_ids)
    
    with col2:
        action = st.selectbox("Action", ["Sale", "Repair Start", "Repair Complete"])
    
    with col3:
        if st.button("Update Inventory", use_container_width=True):
            # 1. Update the DataFrame
            idx = df.index[df['ID'] == selected_id].tolist()[0]
            
            if action == "Sale":
                df.at[idx, 'Qty_On_Hand'] = 0
                df.at[idx, 'Status'] = "Sold"
            elif action == "Repair Start":
                df.at[idx, 'Status'] = "In Repair"
            elif action == "Repair Complete":
                df.at[idx, 'Status'] = "Available"
            
            # 2. Save to CSV
            df.to_csv(INV_FILE, index=False)
            
            # 3. Log the activity
            log_entry = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ID": selected_id,
                "Action": action,
                "User": "Captain"
            }])
