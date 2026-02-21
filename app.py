import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time
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
    st.subheader("Live Warehouse Stock")
    st.dataframe(
        df.assign(ID=df['ID'].astype(str)), 
        use_container_width=True,
        column_config={
            "Qty_On_Hand": st.column_config.NumberColumn(format="%d")
        }
    )
                
    st.divider()
    st.header("🏗️ Log Transaction")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    available_items = df[df['Qty_On_Hand'] > 0]
    
    with col1:
        item_options = available_items.apply(lambda x: f"{x['ID']} - {x['Size']} {x['Model']}", axis=1).tolist()
        selected_option = st.selectbox("Select Item (VIN - Model)", options=item_options)
        selected_id = selected_option.split(" - ")[0] if selected_option else None
    
    with col2:
        user_list = ["Fredrik L", "Bailey S", "Alain L", "Michael A"]
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
                
                # Save Inventory
                df.to_csv(INV_FILE, index=False)
                
                # --- UPDATED ROBUST LOGGING ---
                new_log_data = {
                    "Timestamp": datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S"),
                    "ID": str(selected_id).strip(), # Ensure ID is clean string
                    "Model": item_model,
                    "Size": item_size,
                    "Action": action,
                    "User": selected_user
                }
                
                # Load existing log or create new one if it doesn't exist
                if os.path.exists(LOG_FILE):
                    try:
                        current_log_df = pd.read_csv(LOG_FILE)
                    except:
                        current_log_df = pd.DataFrame(columns=["Timestamp", "ID", "Model", "Size", "Action", "User"])
                else:
                    current_log_df = pd.DataFrame(columns=["Timestamp", "ID", "Model", "Size", "Action", "User"])

                # Add the new entry and save
                new_entry_df = pd.DataFrame([new_log_data])
                updated_log_df = pd.concat([current_log_df, new_entry_df], ignore_index=True)
                updated_log_df.to_csv(LOG_FILE, index=False)
                # ------------------------------

                st.success(f"Success: {item_size} {item_model} updated and logged.")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()


with tab2:
    st.subheader("📊 Detailed Unit Counts")
    st.markdown("### 🏗️ Machines")
    machines_df = df[(df['Category'] == 'Machine') & (df['Qty_On_Hand'] > 0)]
    if not machines_df.empty:
        m_counts = machines_df.groupby('Model')['Qty_On_Hand'].sum()
        cols = st.columns(len(m_counts) if len(m_counts) > 0 else 1)
        for i, (model, count) in enumerate(m_counts.items()):
            cols[i].metric(label=model, value=int(count))

    st.divider()
    st.markdown("### 🛠️ Attachments & Implements")
    attach_df = df[(df['Category'].isin(['Attachment', 'Implement'])) & (df['Qty_On_Hand'] > 0)]
    if not attach_df.empty:
        a_counts = attach_df.groupby(['Model', 'Size'])['Qty_On_Hand'].sum()
        for (model, size), count in a_counts.items():
            label = f"{size} {model}" if size and size != "N/A" else model
            st.metric(label=label, value=int(count))

with tab3:
    st.subheader("🕒 Recent Activity")
    if os.path.exists(LOG_FILE):
        try:
            log_df = pd.read_csv(LOG_FILE, on_bad_lines='skip')
            if not log_df.empty:
                st.dataframe(log_df.sort_values(by=log_df.columns[0], ascending=False), use_container_width=True)
            else:
                st.info("No activity recorded yet.")
        except Exception as e:
            st.error(f"Log Error: {e}")
    else:
        st.info("No transactions logged yet.")

with tab4:
    st.subheader("➕ Add New Inventory")
    with st.form("new_item_form", clear_on_submit=True):
        f_id = st.text_input("Item ID (e.g., 1208003)")
        f_cat = st.selectbox("Category", ["Machine", "Attachment", "Implement"])
        f_type = st.selectbox("Type", ["Excavator", "Skid Steer"])
        f_model = st.selectbox("Model Name", ["12X", "18X", "22X", "25X", "40X", "1100X", "1200X", "Bucket", "Ripper", "Auger", "Rake", "Wood Splitter", "Flail Mower", "Forks", "Hedge Trimmers"])
        f_serial = st.text_input("Serial Number (VIN e.g., 2025-**-*****)")
        f_size_choice = st.selectbox("Select Size", ["N/A", "12\"", "18\"", "24\"", "36\"", "40\"", "48\"", "Small", "Large", "Custom", "N/A"])
        f_custom_size = st.text_input("If Custom, enter size here:")
        f_size = f_custom_size if f_size_choice == "Custom" else f_size_choice
        f_loc = st.text_input("Location", value="Warehouse")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            f_qty = st.number_input("Qty On Hand", min_value=1, value=1, step=1)
        with col2:
            f_qty_order = st.number_input("Qty On Order", min_value=0, value=0, step=1)
        with col3:
            f_reorder = st.number_input("Reorder Level", min_value=0, value=0, step=1)
            
        submitted = st.form_submit_button("Add to Inventory")
        
        if submitted:
            if not f_id or not f_model:
                st.error("Missing info.")
            else:
                # 1 & 2: Match the exact columns of the live warehouse stock and save properly
                new_row = pd.DataFrame([{
                    "ID": f_id,
                    "Category": f_cat,
                    "Type": f_type,
                    "Model": f_model,
                    "Serial_Number": f_serial,
                    "Status": "Available",
                    "Location": f_loc,
                    "Qty_On_Hand": f_qty,
                    "Qty_On_Order": f_qty_order,
                    "Reorder_Level": f_reorder,
                    "Size": f_size
                }])
                
                # Append and Save to CSV
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(INV_FILE, index=False)
                
                # Log the addition
                log_add = pd.DataFrame([{
                    "Timestamp": datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S"),
                    "ID": f_id,
                    "Model": f_model,
                    "Size": f_size,
                    "Action": "Added New Stock",
                    "User": "Employee" 
                }])
                log_add.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)
                
                # 3: Flash the ACCEPTED message and balloons
                st.markdown("<h1 style='text-align: center; color: green;'>ACCEPTED</h1>", unsafe_allow_html=True)
                st.balloons()
                
                # Pause for 1.5 seconds so you can actually see the message flash before it clears!
                time.sleep(1.5) 
                
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
