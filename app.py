import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page Config for Mobile
st.set_page_config(page_title="Bull Inventory", layout="centered")

INV_FILE = "bull_inventory.csv"
LOG_FILE = "inventory_log.csv"

def log_event(asset_id, action, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if os.path.exists(LOG_FILE):
        df_log = pd.read_csv(LOG_FILE)
        new_log = pd.DataFrame([[timestamp, asset_id, action, details]], columns=df_log.columns)
        df_log = pd.concat([df_log, new_log], ignore_index=True)
        df_log.to_csv(LOG_FILE, index=False)

st.title("🏗️ Bull Equipment Inventory")

if os.path.exists(INV_FILE):
    df = pd.read_csv(INV_FILE)

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Fleet Status", "📥 Receive Shipment", "📜 Activity"])

    with tab1:
        st.subheader("Fleet Overview")
        
        # This part now automatically finds ALL your models (12X, 18X, 22X, etc.)
        machines_df = df[df['Category'] == 'Machine']
        
        if not machines_df.empty:
            # Group by Model and sum the quantities
            fleet_summary = machines_df.groupby('Model')['Qty_On_Hand'].sum()
            
            # Display them in nice columns
            cols = st.columns(3)
            for i, (model, count) in enumerate(fleet_summary.items()):
                cols[i % 3].metric(f"Bull {model}", f"{int(count)} Units")
        else:
            st.info("No machines registered yet.")
        
        st.divider()
        st.
    st.divider()
    st.subheader("Log a Sale or Repair")
    selected_id = st.selectbox("Select Item ID", df['ID'].unique(), key="main_select_id")
    action = st.radio("Action", ["Sale", "Maintenance/Repair"], key="main_action")
    quantity = st.number_input("Quantity", min_value=1, value=1, key="main_quantity")

    if st.button("Update Inventory", key="main_update"):
        idx = df.index[df['ID'] == selected_id].tolist()[0]
        if df.at[idx, 'Qty_On_Hand'] >= quantity:
            df.at[idx, 'Qty_On_Hand'] -= quantity
            df.to_csv(INV_FILE, index=False)
            st.success(f"Updated {selected_id}! Remaining: {df.at[idx, 'Qty_On_Hand']}")
            st_autorefresh(interval=1000, limit=2, key="refresh_after_update_main") 
        else:
            st.error("Not enough quantity on hand.")
# --- End of moved section
subheader("All Inventory Items")
        st.dataframe(df[['Category', 'Model', 'Qty_On_Hand', 'Qty_On_Order']], use_container_width=True)

    with tab2:
        st.subheader("Receive New Units")
        asset_to_update = st.selectbox("Select Asset to Receive", df['ID'] + " - " + df['Model'])
        id_only = asset_to_update.split(" - ")[0]
        
        qty_received = st.number_input("How many units arrived?", min_value=1, step=1)
        
        if st.button("Confirm Receipt", type="primary"):
            idx = df[df['ID'] == id_only].index[0]
            df.at[idx, 'Qty_On_Hand'] = int(df.at[idx, 'Qty_On_Hand']) + qty_received
            df.at[idx, 'Qty_On_Order'] = max(0, int(df.at[idx, 'Qty_On_Order']) - qty_received)
            df.to_csv(INV_FILE, index=False)
            log_event(id_only, "WEB_RECEIVE", f"Received {qty_received} units via Mobile UI")
            st.success(f"Updated {id_only}! New Qty: {df.at[idx, 'Qty_On_Hand']}")
            st.rerun()

    with tab3:
        st.subheader("Recent Activity")
        if os.path.exists(LOG_FILE):
            logs = pd.read_csv(LOG_FILE)
            st.table(logs.tail(10))

else:

    st.error("No inventory file found. Please run inventory.py first to create the data.")


