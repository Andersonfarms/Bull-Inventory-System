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
    # Show only Available items in the main table
    available_df = df[df['Qty_On_Hand'] > 0]
    st.dataframe(available_df[['ID', 'Category', 'Model', 'Status', 'Location', 'Qty_On_Hand']], use_container_width=True)

    st.divider()
    st.header("🏗️ Log Transaction")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Select from IDs that are currently in stock
        available_ids = df[df['Qty_On_Hand'] > 0]['ID'].tolist()
        selected_id = st.selectbox("Select Item ID (VIN)", options=available_ids)
    
    with col2:
        action = st.selectbox("Action", ["Sale", "Repair Start", "Repair Complete"])
    
    with col3:
        if st.button("Update Inventory", use_container_width=True):
            idx = df.index[df['ID'] == selected_id].tolist()[0]
            
            if action == "Sale":
                df.at[idx, 'Qty_On_Hand'] = 0
                df.at[idx, 'Status'] = "Sold"
            elif action == "Repair Start":
                df.at[idx, 'Status'] = "In Repair"
            elif action == "Repair Complete":
                df.at[idx, 'Status'] = "Available"
            
            df.to_csv(INV_FILE, index=False)
            
            # Log the activity
            log_entry = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ID": selected_id,
                "Action": action,
                "User": "Captain"
            }])
            
            if not os.path.isfile(LOG_FILE):
                log_entry.to_csv(LOG_FILE, index=False)
            else:
                log_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)
            
            st.success(f"Transaction Complete: {selected_id} updated to {action}")
            st.rerun()

with tab2:
    st.subheader("📈 Inventory Metrics")
    total_units = df['Qty_On_Hand'].sum()
    st.metric("Total Units in Stock", int(total_units))
    
    # Show stock levels by model
    model_counts = df[df['Qty_On_Hand'] > 0].groupby('Model')['Qty_On_Hand'].sum()
    if not model_counts.empty:
        st.bar_chart(model_counts)
    else:
        st.info("No stock currently available to graph.")

with tab3:
    st.subheader("🕒 Recent Activity")
    if os.path.exists(LOG_FILE):
        log_df = pd.read_csv(LOG_FILE)
        # Display the log, newest first
        st.table(log_df.sort_values(by="Timestamp", ascending=False).head(20))
    else:
        st.info("No transactions have been logged yet. Use the 'Log Transaction' tool in the first tab to start.")
