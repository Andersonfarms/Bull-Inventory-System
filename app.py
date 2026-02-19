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
    available_df = df[df['Qty_On_Hand'] > 0]
    st.dataframe(available_df[['ID', 'Category', 'Model', 'Status', 'Location', 'Qty_On_Hand']], use_container_width=True)

    st.divider()
    st.header("🏗️ Log Transaction")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        available_ids = df[df['Qty_On_Hand'] > 0]['ID'].tolist()
        selected_id = st.selectbox("Select Item ID (VIN)", options=available_ids)
    
    with col2:
        user_list = ["Captain", "Fredrik L", "Bailey S", "Alain L", "Michael A"]
        selected_user = st.selectbox("Logged By", options=user_list)
        
    with col3:
        action = st.selectbox("Action", ["Sale", "Repair Start", "Repair Complete"])
    
    with col4:
        st.write(" ") 
        if st.button("Update Inventory", use_container_width=True):
            # Find the machine data
            idx = df.index[df['ID'] == selected_id].tolist()[0]
            item_model = df.at[idx, 'Model'] # AUTO-LOOKUP MODEL
            
            # Update Status
            if action == "Sale":
                df.at[idx, 'Qty_On_Hand'] = 0
                df.at[idx, 'Status'] = "Sold"
            elif action == "Repair Start":
                df.at[idx, 'Status'] = "In Repair"
            elif action == "Repair Complete":
                df.at[idx, 'Status'] = "Available"
            
            df.to_csv(INV_FILE, index=False)
            
            # Log the activity with the exact Model
            log_entry = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ID": selected_id,
                "Model": item_model,
                "Action": action,
                "User": selected_user
            }])
            
            if not os.path.isfile(LOG_FILE):
                log_entry.to_csv(LOG_FILE, index=False)
            else:
                log_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)
            
            st.success(f"Success: {item_model} ({selected_id}) logged by {selected_user}")
            
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

with tab2:
    st.subheader("📊 Detailed Unit Counts")
    st.markdown("### 🏗️ Machines")
    
    with tab3:
        st.subheader("Recent Activity")
        log_file_path = LOG_FILE
        if os.path.exists(log_file_path):
            log_df = pd.read_csv(log_file_path)
            if not log_df.empty:
                display_cols = ["Timestamp", "ID", "Model", "Action", "User"]
                available_cols = [col for col in display_cols if col in log_df.columns]
                st.dataframe(log_df[available_cols])
            else:
                st.write("Activity log is empty.")
        else:
            st.write("Activity log file not found.")
    
    
    machines_df = df[(df['Category'] == 'Machine') & (df['Qty_On_Hand'] > 0)]
    if not machines_df.empty:
        m_counts = machines_df.groupby('Model')['Qty_On_Hand'].sum()
    with tab3:
        st.subheader("Recent Activity")
        log_file_path = LOG_FILE
        if os.path.exists(log_file_path):
            log_df = pd.read_csv(log_file_path)
            if not log_df.empty:
                display_cols = ["Timestamp", "ID", "Model", "Action", "User"]
                available_cols = [col for col in display_cols if col in log_df.columns]
                st.dataframe(log_df[available_cols])
            else:
                st.write("Activity log is empty.")
        else:
            st.write("Activity log file not found.")
    
    # The code below from line 102 was part of the original error and should be removed manually if it persists after this edit.
    # The corrected tab3 block is above.
    
    
        cols = st.columns(len(m_counts))
        for i, (model, count) in enumerate(m_counts.items()):
            cols[i].metric(label=model, value=int(count))
    st.divider()
    st.markdown("### 🛠️ Attachments")
    attach_df = df[(df['Category'] == 'Attachment') & (df['Qty_On_Hand'] > 0)]
    if not attach_df.empty:
        a_counts = attach_df.groupby('Model')['Qty_On_Hand'].sum()
        rows = [a_counts.iloc[i:i+4] for i in range(0, len(a_counts), 4)]
        for row in rows:
            cols = st.



