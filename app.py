import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz # Added for timezone support

# --- CONFIGURATION ---
INV_FILE = "bull_inventory.csv"
LOG_FILE = "activity_log.csv"
CENTRAL = pytz.timezone('US/Central') # Define Central Time

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
                item_size = df.at[idx, 'Size']
                current_qty = int(df.at[idx, 'Qty_On_Hand'])
                
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
                
                # Log entry with CENTRAL TIME
                log_entry = pd.DataFrame([{
                    "Timestamp": datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S"),
                    "ID": selected_id,
                    "Model": item_model,
                    "Size": item_size,
                    "Action": action,
                    "User": selected_user
                }])
                
                if not os.path.isfile(LOG_FILE):
                    log_entry.to_csv(LOG_FILE, index=False)
                else:
                    log_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)
                
                st.success(f"Success: {item_size} {item_model} ({selected_id}) logged by {selected_user}")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
            else:
                st.error("Error: Could not locate record.")

# ... (Tab 2 and 3 logic) ...

with tab4:
    st.subheader("➕ Add New Inventory")
    with st.form("new_item_form", clear_on_submit=True):
        f_id = st.text_input("Item ID (VIN)")
        f_cat = st.selectbox("Category", ["Machine", "Attachment", "Implement"])
        f_model = st.text_input("Model Name")
        f_size_choice = st.selectbox("Select Size", ["N/A", "12\"", "18\"", "24\"", "36\"", "40\"", "48\"", "Small", "Large", "Custom"])
        f_custom_size = st.text_input("If Custom, enter size here:")
        f_size = f_custom_size if f_size_choice == "Custom" else f_size_choice
        f_loc = st.text_input("Location")
        f_qty = st.number_input("Starting Quantity", min_value=1, value=1, step=1)
        
        submitted = st.form_submit_button("Add to Inventory")
        if submitted:
            if not f_id or not f_model:
                st.error("Missing info.")
            else:
                new_row = pd.DataFrame([{
                    "ID": f_id, "Category": f_cat, "Model": f_model, "Size": f_size,
                    "Status": "Available", "Location": f_loc, "Qty_On_Hand": f_qty
                }])
                pd.concat([df, new_row], ignore_index=True).to_csv(INV_FILE, index=False)
                
                # Log addition with CENTRAL TIME
                log_add = pd.DataFrame([{
                    "Timestamp": datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S"),
                    "ID": f_id, "Model": f_model, "Size": f_size,
                    "Action": "Added New Stock", "User": "Captain"
                }])
                log_add.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)
                
                st.success("Added to stock.")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
