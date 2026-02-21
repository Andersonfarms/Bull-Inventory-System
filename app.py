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
    # Refresh data for the live view
    df = pd.read_csv(INV_FILE)
    st.subheader("Live Warehouse Stock")
    # Display ID as string to remove commas
    st.dataframe(df.assign(ID=df['ID'].astype(str)), use_container_width=True)

    st.divider()
    st.header("🏗️ Log Transaction")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    if not df.empty:
        available_items = df[df['Status'] == 'Available']
        item_options = available_items.apply(lambda x: f"{x['ID']} - {x['Size']} {x['Model']}", axis=1).tolist()
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
                df.loc[df['ID'].astype(str) == selected_id, 'Status'] = new_status
                df.to_csv(INV_FILE, index=False)

                # Log Activity
                new_log = pd.DataFrame([{
                    "Timestamp": datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S"),
                    "ID": selected_id,
                    "Action": action,
                    "User": selected_user
                }])
                if os.path.exists(LOG_FILE):
                    log_df = pd.read_csv(LOG_FILE)
                    log_df = pd.concat([log_df, new_log], ignore_index=True)
                else:
                    log_df = new_log
                log_df.to_csv(LOG_FILE, index=False)

                st.markdown("<h1 style='text-align: center; color: green;'>ACCEPTED</h1>", unsafe_allow_html=True)
                st.balloons()
                st.rerun()

with tab2:
    st.subheader("Inventory Metrics")
    if not df.empty:
        col1, col2 = st.columns(2)
        col1.metric("Total Units", len(df))
        col2.metric("Available", len(df[df['Status'] == 'Available']))
    else:
        st.write("No data available.")

with tab3:
    st.subheader("Recent Activity Log")
    if os.path.exists(LOG_FILE):
        log_display = pd.read_csv(LOG_FILE)
        st.table(log_display.tail(10))
    else:
        st.write("No activity recorded yet.")

with tab4:
    st.subheader("Add New Equipment")
    with st.form("new_item_form"):
        new_id = st.text_input("VIN / Serial Number (e.g., 2025-XX-XXXX)")
        new_cat = st.selectbox("Category", ["Skid Steer", "Excavator", "Attachment", "Other"])
        new_model = st.text_input("Model")
        new_size = st.text_input("Size (e.g., 12x, 18x)")
        new_loc = st.text_input("Location", value="Warehouse")
        new_qty = st.number_input("Quantity", min_value=1, value=1)
        
        submitted = st.form_submit_button("Add to Inventory")
        
        if submitted:
            if new_id and new_model:
                new_row = pd.DataFrame([{
                    "ID": str(new_id),
                    "Category": new_cat,
                    "Model": new_model,
                    "Size": new_size,
                    "Status": "Available",
                    "Location": new_loc,
                    "Qty_On_Hand": int(new_qty)
                }])
                
                # Append and Save
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(INV_FILE, index=False)
                
                st.markdown("<h1 style='text-align: center; color: green;'>ACCEPTED</h1>", unsafe_allow_html=True)
                st.balloons()
                st.rerun()
            else:
                st.error("Please provide both a VIN and a Model.")
