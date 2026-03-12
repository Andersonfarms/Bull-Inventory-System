# ==========================================
# Bull Inventory TERMINAL // DATA-LINK v2.6
# System Engineered by: NyssaFire Gaming & Michael Anderson
# Core Uplink Established: 2026-02-17 // 10:13 CST
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from supabase import create_client, Client

# --- 1. CONFIG & CONNECTION ---
st.set_page_config(page_title="Bull Inventory System", page_icon="🏗️", layout="wide")

# ==========================================================
# TACTICAL UI THEME INJECTION
# ==========================================================
tactical_css = """
<style>
:root {
    --bg-base: #0a0a0a;         
    --surface-level: #1c1c1c;   
    --accent-orange: #ff5500;   
    --text-main: #ffffff;       
    --text-muted: #888888;      
    --border-grid: #333333;     
}

.stApp {
    background-color: var(--bg-base);
    color: var(--text-main);
    font-family: 'Courier New', Courier, monospace;
}

div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
    background-color: transparent !important;
    color: var(--text-main) !important; 
    border: 2px solid var(--accent-orange) !important;
    padding: 8px 15px !important;
    font-size: 0.95rem !important;
    font-weight: bold !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    transition: all 0.2s ease-in-out !important;
}

div[data-testid="stButton"] > button:hover,
div[data-testid="stButton"] > button:active,
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:active {
    background-color: var(--accent-orange) !important;
    color: var(--bg-base) !important;
    border-color: var(--accent-orange) !important;
}

.sidebar-header {
    color: var(--text-muted);
    font-size: 0.85rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 25px;
    margin-bottom: 10px;
    border-bottom: 1px solid var(--border-grid);
    padding-bottom: 3px;
}

/* Custom Link Button for Tracking */
.tracking-btn {
    display: inline-block;
    background-color: transparent;
    color: var(--accent-orange) !important;
    border: 1px solid var(--accent-orange);
    padding: 5px 10px;
    text-decoration: none;
    font-weight: bold;
    font-size: 0.85rem;
    border-radius: 3px;
    text-transform: uppercase;
    transition: 0.2s;
}
.tracking-btn:hover {
    background-color: var(--accent-orange);
    color: var(--bg-base) !important;
}
</style>
"""

st.markdown(tactical_css, unsafe_allow_html=True)

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()
CENTRAL = pytz.timezone("US/Central")

# --- 2. DATA LOADERS ---
def load_inventory():
    response = supabase.table("bull_inventory").select("*").execute()
    return pd.DataFrame(response.data)

def load_activity():
    response = supabase.table("bull_activity_log").select("*").order("Timestamp", desc=True).execute()
    return pd.DataFrame(response.data)

def load_inbound():
    response = supabase.table("bull_inbound_tracking").select("*").execute()
    return pd.DataFrame(response.data)

# --- 3. THE TACTICAL SIDEBAR ROUTER ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def nav_to(page_name):
    st.session_state.current_page = page_name

try:
    st.sidebar.image("bull.png", width=200)
except:
    pass # Failsafe if image doesn't load

st.sidebar.markdown('<div class="sidebar-header">CORE OPERATIONS</div>', unsafe_allow_html=True)
st.sidebar.button("Sitrep / Dashboard", on_click=nav_to, args=("Dashboard",), use_container_width=True)
st.sidebar.button("Official Duty Log", on_click=nav_to, args=("Activity Log",), use_container_width=True)

st.sidebar.markdown('<div class="sidebar-header">S-2 INTEL (TRACKING)</div>', unsafe_allow_html=True)
st.sidebar.button("Inbound Freight", on_click=nav_to, args=("Inbound Freight",), use_container_width=True)

st.sidebar.markdown('<div class="sidebar-header">DIGITAL LEDGERS</div>', unsafe_allow_html=True)
st.sidebar.button("Equipment Ledger", on_click=nav_to, args=("Equipment Ledger",), use_container_width=True)
st.sidebar.button("Attachment Ledger", on_click=nav_to, args=("Attachment Ledger",), use_container_width=True)
st.sidebar.button("Parts Ledger", on_click=nav_to, args=("Parts Ledger",), use_container_width=True)
st.sidebar.button("Damaged Ledger", on_click=nav_to, args=("Damaged Ledger",), use_container_width=True)

st.sidebar.markdown('<div class="sidebar-header">LOGISTICS (S-4)</div>', unsafe_allow_html=True)
st.sidebar.button("Add New Stock", on_click=nav_to, args=("Add New Stock",), use_container_width=True)
st.sidebar.button("Sell / Dispatch", on_click=nav_to, args=("Sell Inventory",), use_container_width=True)
st.sidebar.button("Update Status", on_click=nav_to, args=("Update Inventory",), use_container_width=True)

page = st.session_state.current_page

# --- PAGE: DASHBOARD (SITREP) ---
if page == "Dashboard":
    st.title("📡 Sitrep: Master Overview")
    df = load_inventory()
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Line Items", len(df))
        
        target_qty_col = 'Qty_On_Hand'
        if target_qty_col in df.columns:
            total_units = pd.to_numeric(df[target_qty_col], errors='coerce').sum()
            col2.metric("Total Physical Units", int(total_units))
        else:
            col2.metric("Total Physical Units", 0)
            
        st.markdown("---")
        st.markdown("### 📊 Active Fleet Breakdown")
        breakdown_col1, breakdown_col2 = st.columns(2)
        
        with breakdown_col1:
            if 'Model' in df.columns and target_qty_col in df.columns:
                st.write("**By Specific Model:**")
                model_counts = df.groupby('Model')[target_qty_col].sum().reset_index()
                model_counts = model_counts.sort_values(by=target_qty_col, ascending=False)
                st.dataframe(model_counts, hide_index=True, use_container_width=True)
        
        with breakdown_col2:
            if 'Category' in df.columns and target_qty_col in df.columns:
                st.write("**By Category:**")
                cat_counts = df.groupby('Category')[target_qty_col].sum().reset_index()
                st.dataframe(cat_counts, hide_index=True, use_container_width=True)
    else:
        st.warning("No inventory found in Supabase.")

# --- PAGE: INBOUND FREIGHT (DYNAMIC TRACKING) ---
elif page == "Inbound Freight":
    st.title("🚢 S-2 Intel: Inbound Freight")
    
    def get_tracking_url(carrier, tracking_number):
        if carrier == "Maersk":
            return f"https://www.maersk.com/tracking/{tracking_number}"
        elif carrier == "CMA-CGM":
            return f"https://www.cma-cgm.com/ebusiness/tracking/search?reference={tracking_number}"
        elif carrier == "MSC":
            return f"https://www.msc.com/en/track-a-shipment?trackingNumber={tracking_number}"
        elif carrier == "Hapag-Lloyd":
            return f"https://www.hapag-lloyd.com/en/online-business/track/track-by-container-solution.html?blno={tracking_number}"
        else:
            # Universal fallback for "Other" or unknown
            return f"https://www.searates.com/container/tracking/?number={tracking_number}"

    # 1. Display Current Inbound Shipments
    inbound_df = load_inbound()
    if not inbound_df.empty:
        active_shipments = inbound_df[inbound_df['Status'] != 'Arrived']
        if not active_shipments.empty:
            st.markdown("### 📡 Active Inbound Containers")
            for index, row in active_shipments.iterrows():
                tracking_url = get_tracking_url(row['Carrier'], row['Tracking_Number'])
                with st.container():
                    st.markdown(f"""
                    <div style="border-left: 3px solid var(--accent-orange); padding-left: 10px; margin-bottom: 15px; background-color: var(--surface-level); padding: 15px; border-radius: 4px;">
                        <h4 style="margin: 0; color: var(--text-main);">CONTAINER: {row['Tracking_Number']}</h4>
                        <p style="margin: 5px 0; color: var(--text-muted); font-size: 0.9rem;">
                            <strong>Carrier:</strong> {row['Carrier']} &nbsp;|&nbsp; 
                            <strong>ETA:</strong> {row['ETA']} &nbsp;|&nbsp; 
                            <strong>Contents:</strong> {row['Contents']}
                        </p>
                        <a href="{tracking_url}" target="_blank" class="tracking-btn">
                            [>> LIVE {row['Carrier'].upper()} UPLINK <<]
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No active containers currently in transit.")
            
        # Optional: Mark as Arrived
        st.markdown("---")
        st.markdown("**Update Shipment Status**")
        update_id = st.selectbox("Select Container to mark as 'Arrived'", inbound_df[inbound_df['Status'] != 'Arrived']['Tracking_Number'].tolist() if not active_shipments.empty else ["None"])
        if update_id != "None":
            if st.button("Mark as Arrived"):
                try:
                    supabase.table("bull_inbound_tracking").update({"Status": "Arrived"}).eq("Tracking_Number", update_id).execute()
                    st.success(f"✅ Container {update_id} marked as Arrived. Please move contents to Add New Stock.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Database Error: {e}")
    else:
        st.info("No tracking data on file.")

    st.markdown("---")
    # 2. Add New Inbound Shipment
    st.markdown("### ➕ Log New Inbound Container")
    with st.form("inbound_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tracking_num = st.text_input("Container / Tracking Number (e.g., MSKU1234567)")
            carrier = st.selectbox("Carrier", ["Maersk", "CMA-CGM", "MSC", "Hapag-Lloyd", "Evergreen", "Other"])
        with col2:
            contents = st.text_input("Primary Contents (e.g., 5x 18X Excavators, Parts)")
            eta = st.text_input("Expected Time of Arrival (ETA)")
            
        submit_tracker = st.form_submit_button("Start Tracking")
        
        if submit_tracker and tracking_num:
            new_shipment = {
                "Tracking_Number": tracking_num,
                "Carrier": carrier,
                "Contents": contents,
                "ETA": eta,
                "Status": "In Transit"
            }
            try:
                supabase.table("bull_inbound_tracking").insert(new_shipment).execute()
                st.success(f"✅ Container {tracking_num} logged into tracking network!")
                st.rerun()
            except Exception as e:
                st.error(f"Database Error: {e}")

# --- PAGES: THE DIGITAL LEDGERS ---
elif page in ["Equipment Ledger", "Attachment Ledger", "Parts Ledger", "Damaged Ledger"]:
    st.title(f"📂 {page}")
    df = load_inventory()
    
    if not df.empty:
        # Filter logic based on the selected ledger
        if page == "Equipment Ledger":
            df = df[df['Category'] == 'Machine']
        elif page == "Attachment Ledger":
            df = df[df['Category'] == 'Attachment']
        elif page == "Parts Ledger":
            df = df[df['Category'] == 'Parts']
        elif page == "Damaged Ledger":
            df = df[df['Status'] == 'Damaged']
            
        search = st.text_input(f"🔍 Search {page}:")
        if search:
            mask = pd.Series(False, index=df.index)
            if 'Model' in df.columns:
                mask |= df['Model'].astype(str).str.contains(search, case=False, na=False)
            if 'ID' in df.columns:
                mask |= df['ID'].astype(str).str.contains(search, case=False, na=False)
            if 'Description' in df.columns:
                mask |= df['Description'].astype(str).str.contains(search, case=False, na=False)
            df = df[mask]
            
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning(f"No records found for {page}.")

# --- PAGE: ADD NEW STOCK ---
elif page == "Add New Stock":
    st.title("➕ Logistics: Register New Stock")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("Item ID (e.g., A-9PWW)")
            model_options = ["12X", "18X", "22X", "25X", "40X", "1100X", "Bucket", "Auger", "Ripper", "Rake", "Forks", "Wood Splitter", "Hedge Trimmers", "Hammer", "Other"]
            new_model = st.selectbox("Model Name", model_options)
            new_type = st.selectbox("Machine Type", ["Excavator", "Skid Steer", "Other"])
            new_qty = st.number_input("Quantity", min_value=1, step=1)
            
        with col2:
            new_cat = st.selectbox("Category", ["Machine", "Attachment", "Parts", "Other"])
            size_options = ["N/A", "8\"", "12\"", "18\"", "24\"", "36\"", "40\"", "48\"", "Small", "Medium", "Large"]
            new_size = st.selectbox("Size", size_options)
            
            # --- NEW DESCRIPTION FIELD FOR PARTS ---
            desc_options = [
                "N/A", "Air Filter", "Oil Filter", "Hydraulic Filter", "Fuel Filter", 
                "Hydraulic Hose", "O-Rings / Seals", "Track Assembly", "Sprocket / Idler", 
                "Teeth / Cutting Edge", "Pins & Bushings", "Electrical Relay / Fuse", 
                "Sensors", "Hardware / Fasteners", "Fluids / Grease", "Other"
            ]
            new_desc = st.selectbox("Part Description", desc_options)
            
            new_loc = st.text_input("Location", value="Warehouse")
            
        submit = st.form_submit_button("Commit to Database")
        
        if submit and new_id:
            now = datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S")
            trx_id = f"TRX-{datetime.now().strftime('%f')}" 
            
            # Pack the description into the database payload
            new_item = {
                "ID": new_id, "Model": new_model, "Type": new_type, "Qty_On_Hand": int(new_qty), 
                "Location": new_loc, "Category": new_cat, "Size": new_size, "Description": new_desc, 
                "Status": "Available"
            }
            try:
                supabase.table("bull_inventory").insert(new_item).execute()
                
                # Format the log entry to show the description if it's not N/A
                desc_log = f" - {new_desc}" if new_desc != "N/A" else ""
                log_entry = {
                    "Transaction #": trx_id, "Timestamp": now, "ID": new_id, "Model": new_model, 
                    "Change": f"Added {new_qty} units ({new_size}{desc_log})", "User": "Admin"
                }
                supabase.table("bull_activity_log").insert(log_entry).execute()
                st.success(f"✅ {new_model} successfully stored!")
            except Exception as e:
                st.error(f"Database Error: {e}")

# --- PAGE: SELL INVENTORY ---
elif page == "Sell Inventory":
    st.title("🛒 Logistics: Dispatch / Sell")
    df = load_inventory()
    if not df.empty and 'ID' in df.columns:
        df['Qty_On_Hand'] = pd.to_numeric(df['Qty_On_Hand'], errors='coerce').fillna(0)
        available_items = df[df['Qty_On_Hand'] > 0]
        if not available_items.empty:
            
            selected_id = st.selectbox("Select Primary Item to Dispatch", available_items['ID'].dropna().tolist())
            
            if selected_id:
                current_item = available_items[available_items['ID'] == selected_id].iloc[0]
                current_qty = int(current_item['Qty_On_Hand'])
                st.info(f"Target: **{current_item.get('Model', 'Unknown')}** | Current Stock: **{current_qty}**")
                
                # Pre-gather attachment options for bundling
                attachments_df = available_items[available_items['Category'] == 'Attachment']
                # Exclude the primary item from the attachment list if it happens to be an attachment itself
                attachments_df = attachments_df[attachments_df['ID'] != selected_id]
                attachment_options = ["None"] + attachments_df['ID'].dropna().tolist()
                
                with st.form("sell_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        sell_qty = st.number_input("Quantity Dispatched", min_value=1, max_value=current_qty, step=1)
                        salesperson = st.selectbox("Salesperson", ["Fredrik L.", "Bailey A.", "Admin", "Other"])
                        buyer_notes = st.text_input("Dispatch Notes / Buyer Name")
                        
                    with col2:
                        transport_co = st.text_input("Transport Company", help="Browser autofill will remember previous entries.")
                        st.markdown("**Bundle an Attachment?**")
                        addon_id = st.selectbox("Select Add-on Attachment", attachment_options)
                        addon_qty = st.number_input("Add-on Quantity", min_value=1, step=1)
                        
                    sell_btn = st.form_submit_button("Execute Dispatch")
                    
                    if sell_btn:
                        now = datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S")
                        new_qty = current_qty - sell_qty
                        new_status = "Sold" if new_qty == 0 else current_item.get('Status', 'Available')
                        
                        addon_success = True
                        addon_log = ""
                        
                        # Process Add-on Attachment First
                        if addon_id != "None":
                            addon_item = available_items[available_items['ID'] == addon_id].iloc[0]
                            addon_current_qty = int(addon_item['Qty_On_Hand'])
                            
                            if addon_qty > addon_current_qty:
                                st.error(f"🚫 Cannot bundle {addon_qty}x of {addon_id}. Only {addon_current_qty} in stock!")
                                addon_success = False
                            else:
                                addon_new_qty = addon_current_qty - addon_qty
                                addon_new_status = "Sold" if addon_new_qty == 0 else addon_item.get('Status', 'Available')
                                try:
                                    supabase.table("bull_inventory").update({"Qty_On_Hand": addon_new_qty, "Status": addon_new_status}).eq("ID", addon_id).execute()
                                    addon_log = f" | Bundled {addon_qty}x {addon_id}"
                                    
                                    # Log the attachment sale
                                    log_entry_addon = {
                                        "Transaction #": f"TRX-{datetime.now().strftime('%f')}-A", 
                                        "Timestamp": now, 
                                        "ID": addon_id, 
                                        "Model": addon_item.get('Model', 'Unknown'), 
                                        "Change": f"DISPATCHED {addon_qty} units (Bundled). Remaining: {addon_new_qty}", 
                                        "User": salesperson
                                    }
                                    supabase.table("bull_activity_log").insert(log_entry_addon).execute()
                                except Exception as e:
                                    st.error(f"Database Error on Add-on: {e}")
                                    addon_success = False

                        # Process Primary Item if addon didn't fail
                        if addon_success:
                            try:
                                supabase.table("bull_inventory").update({"Qty_On_Hand": new_qty, "Status": new_status}).eq("ID", selected_id).execute()
                                
                                notes_str = f" | Buyer: {buyer_notes}" if buyer_notes else ""
                                trans_str = f" | Trans: {transport_co}" if transport_co else ""
                                full_change_log = f"DISPATCHED {sell_qty} units. Remaining: {new_qty}{addon_log}{notes_str}{trans_str}"
                                
                                log_entry = {
                                    "Transaction #": f"TRX-{datetime.now().strftime('%f')}", 
                                    "Timestamp": now, 
                                    "ID": selected_id, 
                                    "Model": current_item.get('Model', 'Unknown'), 
                                    "Change": full_change_log, 
                                    "User": salesperson
                                }
                                supabase.table("bull_activity_log").insert(log_entry).execute()
                                st.success(f"✅ Dispatch executed for {sell_qty}x {current_item.get('Model', 'Unknown')}!")
                            except Exception as e:
                                st.error(f"Database Error: {e}")
        else:
            st.warning("No items currently available to dispatch.")

# --- PAGE: UPDATE INVENTORY ---
elif page == "Update Inventory":
    st.title("🔄 Logistics: Update Status")
    df = load_inventory()
    if not df.empty and 'ID' in df.columns:
        selected_id = st.selectbox("Select Item ID", df['ID'].dropna().tolist())
        if selected_id:
            current_item = df[df['ID'] == selected_id].iloc[0]
            with st.form("update_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_qty = st.number_input("New Quantity", value=int(current_item.get('Qty_On_Hand', 0)), min_value=0)
                    new_loc = st.text_input("New Location", value=str(current_item.get('Location', 'Warehouse')))
                with col2:
                    status_options = ["Available", "Sold", "On Rent", "Maintenance", "Damaged"]
                    current_status = str(current_item.get('Status', 'Available'))
                    if current_status not in status_options: status_options.append(current_status)
                    new_status = st.selectbox("Update Status", status_options, index=status_options.index(current_status))
                
                if st.form_submit_button("Update Database"):
                    try:
                        supabase.table("bull_inventory").update({"Qty_On_Hand": int(new_qty), "Location": new_loc, "Status": new_status}).eq("ID", selected_id).execute()
                        now = datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S")
                        log_entry = {"Transaction #": f"TRX-{datetime.now().strftime('%f')}", "Timestamp": now, "ID": selected_id, "Model": current_item.get('Model', 'Unknown'), "Change": f"Updated Status: {new_status}. Qty: {new_qty}", "User": "Admin"}
                        supabase.table("bull_activity_log").insert(log_entry).execute()
                        st.success(f"✅ Record updated successfully!")
                    except Exception as e:
                        st.error(f"Database Error: {e}")

# --- PAGE: ACTIVITY LOG ---
elif page == "Activity Log":
    st.title("📖 Official Duty Log")
    log_df = load_activity()
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity recorded yet.")
