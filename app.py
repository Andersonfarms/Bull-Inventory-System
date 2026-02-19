import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
INV_FILE = "bull_inventory.csv"
LOG_FILE = "activity_log.csv"

st.set_page_config(page_title="Bull Inventory System", layout="wide")
st.title("🏗️ Bull Inventory")

# --- DATA LOAD ---
if os.path.exists(INV_FILE):
    df = pd.read_csv(INV_FILE)
    df['Qty_On_Hand'] = pd.to_numeric(df['Qty_On_Hand'], errors='coerce')
else:
    st.error("Inventory file not found!")
    st.stop()

# --- DASHBOARD TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 Current Inventory", "📈 Analytics", "🕒 Recent Activity", "➕ Add New Stock"])

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
            idx_list = df.index[df['ID'] == selected_id].tolist()
            
            if len(idx_list) == 1:
                idx = idx_list[0]
                item_model = df.at[idx, 'Model']
                current_qty = df.at[idx, 'Qty_On_Hand']
                
                if action == "Sale":
                    if current_qty > 1:
                        df.at[idx, 'Qty_On_Hand'] = current_qty - 1
                    else:
                        df.at[idx, 'Qty_On_Hand'] = 0
                        df.at[idx, 'Status'] = "Sold"
                elif action == "Repair Start":
                    df.at[idx, 'Status'] = "In Repair"
                elif action == "Repair Complete":
                    df.at[idx, 'Status'] = "Available"
                
                df.to_csv(INV_FILE, index=False)
                
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
            else:
                st.error("Error: Could not locate a unique record for this ID.")

with tab2:
    st.subheader("📊 Detailed Unit Counts")
    st.markdown("### 🏗️ Machines")
    machines_df = df[(df['Category'] == 'Machine') & (df['Qty_On_Hand'] > 0)]
    if not machines_df.empty:
        m_counts = machines_df.groupby('Model')['Qty_On_Hand'].sum()
        cols = st.columns(len(m_counts))
        for i, (model, count) in enumerate(m_counts.items()):
            cols[i].metric(label=model, value=int(count))
    st.divider()
    st.markdown("### 🛠️ Attachments & Implements")
    attach_df = df[(df['Category'].isin(['Attachment', 'Implement'])) & (df['Qty_On_Hand'] > 0)]
    if not attach_df.empty:
        a_counts = attach_df.groupby('Model')['Qty_On_Hand'].sum()
        rows = [a_counts.iloc[i:i+4] for i in range(0, len(a_counts), 4)]
        for row in rows:
            cols = st.columns(4)
            for i, (model, count) in enumerate(row.items()):
                cols[i].metric(label=model, value=int(count))

with tab3:
    st.subheader("🕒 Recent Activity")
    if os.path.exists(LOG_FILE):
        try:
            log_df = pd.read_csv(LOG_FILE, on_bad_lines='skip')
            display_columns = ['Timestamp', 'ID', 'Model', 'Action', 'User']
            existing_cols = [c for c in display_columns if c in log_df.columns]
            if not log_df.empty:
                st.table(log_df[existing_cols].sort_values(by="Timestamp", ascending=False).head(20))
            else:
                st.info("No valid history found yet.")
        except Exception as e:
            st.error("The activity log file is corrupted.")
            if st.button("Reset Activity Log"):
                os.remove(LOG_FILE)
                st.rerun()
    else:
        st.info("No transactions logged yet.")

with tab4:
    st.subheader("➕ Add New Inventory")
    with st.form("new_item_form", clear_on_submit=True):
        f_id = st.text_input("Item ID (VIN)")
        f_cat = st.selectbox("Category", ["Machine", "Attachment", "Implement"])
        f_model = st.text_input("Model Name (e.g., 25X, Ripper, etc.)")
        f_loc = st.text_input("Location (Warehouse/Yard)")
        f_qty = st.number_input("Starting Quantity", min_value=1, value=1, step=1)
        
        submitted = st.form_submit_button("Add to Inventory")
        
        if submitted:
            if not f_id or not f_model:
                st.error("Please provide both a VIN and a Model name.")
            elif f_id in df['ID'].values:
                st.error(f"Error: VIN {f_id} already exists in the system!")
            else:
                new_row = pd.DataFrame([{
                    "ID": f_id,
                    "Category": f_cat,
                    "Model": f_model,
                    "Status": "Available",
                    "Location": f_loc,
                    "Qty_On_Hand": f_qty
                }])
                
                # Update Inventory File
                updated_df = pd.concat([df, new_row], ignore_index=True)
                updated_df.to_csv(INV_FILE, index=False)
                
                # Log the addition
                log_add = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ID": f_id,
                    "Model": f_model,
                    "Action": "Added New Stock",
                    "User": "Captain"
                }])
                log_add.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)
                
                st.success(f"Successfully added {f_model} ({f_id}) to stock.")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
