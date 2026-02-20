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
    df['Qty_On_Hand'] = pd.to_numeric(df['Qty_On_Hand'], errors='coerce').fillna(0).astype(int)
    if 'Size' not in df.columns:
        df['Size'] = ""
    df = df.fillna("")
else:
    st.error("Inventory file not found!")
    st.stop()

# --- DASHBOARD TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 Current Inventory", "📈 Analytics", "🕒 Recent Activity", "➕ Add New Stock"])

with tab1:
    st.subheader("Live Warehouse Stock (Manual Edit Mode)")
    st.info("💡 You can edit cells directly. Click 'Save Manual Edits' when finished.")
    
    try:
        edited_df = st.data_editor(
            df, 
            use_container_width=True, 
            num_rows="dynamic", 
            key="inventory_editor",
            column_config={"Qty_On_Hand": st.column_config.NumberColumn(format="%d")}
        )
        
        if st.button("💾 Save Manual Edits"):
            edited_df.to_csv(INV_FILE, index=False)
            st.success("Inventory updated successfully!")
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
                
    except AttributeError:
        st.warning("Manual Edit Mode is not supported in this version. Reverting to read-only view.")
        st.dataframe(df, use_container_width=True)

    st.divider()
    st.header("🏗️ Log Transaction")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    available_items = df[df['Qty_On_Hand'] > 0]
    
    with col1:
        # Improved label for the dropdown so you can see size/model while picking
        item_options = available_items.apply(lambda x: f"{x['ID']} - {x['Size']} {x['Model']}", axis=1).tolist()
        selected_option = st.selectbox("Select Item (VIN - Model)", options=item_options)
        selected_id = selected_option.split(" - ")[0] if selected_option else None
    
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
                item_size = df.at[idx, 'Size']
                current_qty = int(df.at[idx, 'Qty_On_Hand'])
                
                # Update Inventory Data
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
                
                # Save Inventory
                df.to_csv(INV_FILE, index=False)
                
                # NEW ROBUST LOGGING
                new_log = {
                    "Timestamp": datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S"),
                    "ID": selected_id,
                    "Model": item_model,
                    "Size": item_size,
                    "Action": action,
                    "User": selected_user
                }
                
                log_df_entry = pd.DataFrame([new_log])
                
                # Ensure log file exists and has headers
                if not os.path.exists(LOG_FILE):
                    log_df_entry.to_csv(LOG_FILE, index=False)
                else:
                    log_df_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)
                
                st.success(f"Success: {item_size} {item_model} updated.")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
            else:
                st.error("Error: Record lookup failed.")

# ... (Tab 2, 3, and 4 follow exactly as before) ...
