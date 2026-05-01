# ==========================================
# BULL INVENTORY TERMINAL // DATA-LINK v2.7
# System Engineered by: NyssaFire Gaming/Michael Anderson
# ==========================================

import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from supabase import create_client

# --- 0. WHITE-LABEL CONFIGURATION ---
APP_CONFIG = {
    "company_name": "Bull",
    "app_title": "Inventory System",
    "logo_path": "bull.png",
    "timezone": "US/Central",
    "table_inventory": "bull_inventory",
    "table_activity": "bull_activity_log",
    "table_inbound": "bull_inbound_tracking",
    "machine_models": ["12X", "18X", "20X", "22X", "25X", "40X", "1100X", "Bucket", "Auger", "Ripper", "Rake", "Forks", "Wood Splitter", "Hedge Trimmers", "Hammer", "Grapple", "Other"],
    "machine_types": ["Excavator", "Skid Steer", "Other"],
    "categories": ["Machine", "Attachment", "Parts", "Other"],
    "carriers": ["Maersk", "CMA-CGM", "MSC", "Hapag-Lloyd", "Evergreen", "Other"]
}

# --- DEFINE ADMIN EMAILS HERE ---
ADMIN_EMAILS = [
    "service@bull-equipment.com", 
    "fredrik@bull-equipment.com",
    "admin@bull-equipment.com" 
]

# --- 1. CONFIG & CONNECTION ---
st.set_page_config(page_title=f"{APP_CONFIG['company_name']} {APP_CONFIG['app_title']}", page_icon="🏗️", layout="wide")

tactical_css = """
<style>
:root {--bg-base: #0a0a0a; --surface-level: #1c1c1c; --accent-orange: #ff5500; --text-main: #ffffff; --text-muted: #888888; --border-grid: #333333; }
.stApp {background-color: var(--bg-base); color: var(--text-main); font-family: 'Courier New', Courier, monospace;}
div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {background-color: transparent !important; color: var(--text-main) !important; border: 2px solid var(--accent-orange) !important; padding: 8px 15px !important; font-size: 0.95rem !important; font-weight: bold !important; text-transform: uppercase !important; border-radius: 3px !important; transition: all 0.2s ease-in-out !important;}
div[data-testid="stButton"] > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {background-color: var(--accent-orange) !important; color: var(--bg-base) !important; border-color: var(--accent-orange) !important;}
.sidebar-header {color: var(--text-muted); font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; margin-top: 25px; margin-bottom: 10px; border-bottom: 1px solid var(--border-grid); padding-bottom: 3px;}
</style>
"""
st.markdown(tactical_css, unsafe_allow_html=True)

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()
CLIENT_TZ = pytz.timezone(APP_CONFIG['timezone'])

# --- 2. AUTHENTICATION GATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login_screen():
    st.title("🏗️ BULL TERMINAL ACCESS")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("LOG IN"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.rerun()
            except Exception as e:
                st.error("Authentication Failed: Invalid Credentials")

if not st.session_state.authenticated:
    login_screen()
    st.stop()

# --- 3. ROLE-BASED ACCESS CONTROL ---
is_admin = st.session_state.user_email in ADMIN_EMAILS
is_sales = not is_admin # Anyone not an Admin is treated as Sales

# --- 4. DATA LOADERS ---
def load_inventory():
    return pd.DataFrame(supabase.table(APP_CONFIG["table_inventory"]).select("*").execute().data)

def load_activity():
    return pd.DataFrame(supabase.table(APP_CONFIG["table_activity"]).select("*").order("Timestamp", desc=True).execute().data)

def load_inbound():
    return pd.DataFrame(supabase.table(APP_CONFIG["table_inbound"]).select("*").execute().data)

# --- 5. SIDEBAR ROUTER ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def nav_to(page_name):
    st.session_state.current_page = page_name

with st.sidebar:
    try:
        st.image(APP_CONFIG["logo_path"], width=200)
    except:
        st.markdown(f"### {APP_CONFIG['company_name']}")

    st.markdown('<div class="sidebar-header">CORE OPERATIONS</div>', unsafe_allow_html=True)
    st.button("Sitrep / Dashboard", on_click=nav_to, args=("Dashboard",), use_container_width=True)
    st.button("Official Duty Log", on_click=nav_to, args=("Activity Log",), use_container_width=True)

    st.markdown('<div class="sidebar-header">TRACKING</div>', unsafe_allow_html=True)
    st.button("Inbound Freight", on_click=nav_to, args=("Inbound Freight",), use_container_width=True)

    st.markdown('<div class="sidebar-header">DIGITAL LEDGERS</div>', unsafe_allow_html=True)
    
    if is_admin:
        st.button("Equipment Ledger", on_click=nav_to, args=("Equipment Ledger",), use_container_width=True)
        st.button("Attachment Ledger", on_click=nav_to, args=("Attachment Ledger",), use_container_width=True)
        st.button("Parts Ledger", on_click=nav_to, args=("Parts Ledger",), use_container_width=True)
        
    st.button("Damaged Ledger", on_click=nav_to, args=("Damaged Ledger",), use_container_width=True)
    st.button("🛠️ Troubleshooting", on_click=nav_to, args=("Troubleshooting",), use_container_width=True)

    st.markdown('<div class="sidebar-header">LOGISTICS (S-4)</div>', unsafe_allow_html=True)
    
    if is_admin:
        st.button("Add New Stock", on_click=nav_to, args=("Add New Stock",), use_container_width=True)
        st.button("Update Status", on_click=nav_to, args=("Update Inventory",), use_container_width=True)

    st.button("Sell / Dispatch", on_click=nav_to, args=("Sell Inventory",), use_container_width=True)
    
    st.markdown("---")
    st.write(f"User: `{st.session_state.user_email}`")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- TRACKING LINK GENERATOR ---
def get_tracking_link(carrier, tracking_number):
    t_num = str(tracking_number).strip()
    c_name = str(carrier).upper()
    if "MAERSK" in c_name: return f"https://www.maersk.com/tracking/{t_num}"
    elif "CMA" in c_name or "CGM" in c_name: return f"https://www.cma-cgm.com/ebusiness/tracking/search?reference={t_num}"
    elif "MSC" in c_name: return f"https://www.msc.com/en/track-a-shipment?trackingNumber={t_num}"
    elif "HAPAG" in c_name: return f"https://www.hapag-lloyd.com/en/online-business/track/track-by-booking.html?blno={t_num}"
    elif "EVERGREEN" in c_name: return f"https://ct.shipmentlink.com/servlet/TDB1_CargoTracking.do"
    return f"https://www.google.com/search?q={c_name}+tracking+{t_num}" # Fallback

# --- 6. PAGE LOGIC ---
page = st.session_state.current_page

if page == "Dashboard":
    st.title(f"📡 {APP_CONFIG['company_name']} Sitrep: Master Overview")
    df = load_inventory()
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Line Items", len(df))
        if 'Qty_On_Hand' in df.columns:
            total_units = pd.to_numeric(df['Qty_On_Hand'], errors='coerce').sum()
            col2.metric("Total Physical Units", int(total_units))
        
        st.markdown("---")
        st.markdown("### 📊 Active Fleet Breakdown")
        bc1, bc2 = st.columns(2)
        with bc1:
            st.write("**By Specific Model:**")
            model_counts = df.groupby('Model')['Qty_On_Hand'].sum().reset_index().sort_values(by='Qty_On_Hand', ascending=False)
            st.dataframe(model_counts, hide_index=True, use_container_width=True)
        with bc2:
            st.write("**By Category:**")
            cat_counts = df.groupby('Category')['Qty_On_Hand'].sum().reset_index()
            st.dataframe(cat_counts, hide_index=True, use_container_width=True)
    else:
        st.warning("No inventory found.")

# --- PAGE LOGIC ---
elif page == "Inbound Freight":
    st.title("🚢 Inbound Freight Tracking")
   
    # 1. ADD NEW FREIGHT FORM (Admin Only)
    if is_admin:
        with st.expander("➕ Register New Inbound Shipment", expanded=False):
            with st.form("inbound_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    new_tracking = st.text_input("Container / Tracking Number")
                    new_carrier = st.selectbox("Carrier", APP_CONFIG["carriers"])
                with col2:
                    new_contents = st.text_input("Contents (e.g., 20x 12X models)")
                    new_eta = st.date_input("Estimated Time of Arrival (ETA)")
                    new_status = st.selectbox("Status", ["In Transit", "Customs", "Arrived", "Delayed"])
                
                if st.form_submit_button("Register Shipment") and new_tracking:
                    try:
                        # Save to Supabase
                        supabase.table(APP_CONFIG["table_inbound"]).insert({
                            "Tracking_Number": new_tracking,
                            "Carrier": new_carrier,
                            "Contents": new_contents,
                            "ETA": str(new_eta),
                            "Status": new_status
                        }).execute()
                        st.success(f"✅ Container {new_tracking} registered successfully!")
                        st.rerun() # Refresh the page to show the new data
                    except Exception as e:
                        st.error(f"Database Error: {e}")

    # 2. LIVE TRACKING BOARD
    inbound_df = load_inbound()
    if not inbound_df.empty:
        # Generate the live links for the dataframe
        inbound_df['Live_Tracking'] = inbound_df.apply(lambda row: get_tracking_link(row['Carrier'], row['Tracking_Number']), axis=1)
        
        # Display the interactive dataframe
        st.dataframe(
            inbound_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Live_Tracking": st.column_config.LinkColumn("Live Tracker", display_text="Track Shipment 🔗"),
                "Tracking_Number": st.column_config.TextColumn("Container #")
            }
        )
    else:
        st.info("No inbound shipments currently active.")

elif page in ["Equipment Ledger", "Attachment Ledger", "Parts Ledger", "Damaged Ledger"]:
    if is_sales and page != "Damaged Ledger":
        st.error("🚫 RESTRICTED: Admin Clearance Required.")
        st.stop()
        
    st.title(f"📂 {page}")
    df = load_inventory()
    if not df.empty:
        if page == "Equipment Ledger": df = df[df['Category'] == 'Machine']
        elif page == "Attachment Ledger": df = df[df['Category'] == 'Attachment']
        elif page == "Parts Ledger": df = df[df['Category'] == 'Parts']
        elif page == "Damaged Ledger": df = df[df['Status'] == 'Damaged']
        
        search = st.text_input(f"🔍 Search {page}:")
        if search:
            mask = pd.Series(False, index=df.index)
            for col in ['Model', 'ID', 'Description']:
                if col in df.columns: mask |= df[col].astype(str).str.contains(search, case=False, na=False)
            df = df[mask]
        st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Troubleshooting":
    st.title("🛠️ Tactical Field Diagnostics")
    st.info("Select a system from the menu above to begin diagnostics.")
    # (Your troubleshooting text can be re-expanded here as needed)

elif page == "Add New Stock":
    if is_sales:
        st.error("🚫 RESTRICTED: High-Level Logistics Clearance Required to Add Stock.")
        st.stop()
        
    st.title("➕ Logistics: Register New Stock")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("Item ID (e.g., A-9PWW)")
            new_model = st.selectbox("Model Name", APP_CONFIG["machine_models"])
            new_type = st.selectbox("Machine Type", APP_CONFIG["machine_types"])
            new_qty = st.number_input("Quantity", min_value=1, step=1)
        with col2:
            new_cat = st.selectbox("Category", APP_CONFIG["categories"])
            new_size = st.selectbox("Size", ["N/A", "8\"", "12\"", "18\"", "24\"", "Small", "Large"])
            new_desc = st.text_input("Part Description (Optional)", "N/A")
            new_loc = st.text_input("Location", value="Warehouse")
            
        if st.form_submit_button("Commit to Database") and new_id:
            now = datetime.now(CLIENT_TZ).strftime("%Y-%m-%d %H:%M:%S")
            try:
                supabase.table(APP_CONFIG["table_inventory"]).insert({
                    "ID": new_id, "Model": new_model, "Type": new_type, 
                    "Qty_On_Hand": int(new_qty), "Location": new_loc, 
                    "Category": new_cat, "Size": new_size, 
                    "Description": new_desc, "Status": "Available"
                }).execute()
                
                supabase.table(APP_CONFIG["table_activity"]).insert({
                    "Transaction #": f"TRX-{datetime.now().strftime('%f')}", 
                    "Timestamp": now, "ID": new_id, "Model": new_model, 
                    "Change": f"Added {new_qty} units", 
                    "User": st.session_state.user_email
                }).execute()
                st.success(f"✅ {new_model} successfully stored!")
            except Exception as e:
                st.error(f"Database Error: {e}")

elif page == "Sell Inventory":
    st.title("🛒 Logistics: Dispatch / Sell")
    df = load_inventory()
    if not df.empty:
        available = df[pd.to_numeric(df['Qty_On_Hand'], errors='coerce') > 0]
        selected_id = st.selectbox("Select Primary Item", available['ID'].dropna().tolist())
        if selected_id:
            item = available[available['ID'] == selected_id].iloc[0]
            with st.form("sell_form"):
                sell_qty = st.number_input("Quantity Dispatched", min_value=1, max_value=int(item['Qty_On_Hand']))
                buyer_notes = st.text_input("Dispatch Notes / Buyer Name")
                
                if st.form_submit_button("Execute Dispatch"):
                    new_qty = int(item['Qty_On_Hand']) - sell_qty
                    new_status = "Sold" if new_qty == 0 else item.get('Status', 'Available')
                    try:
                        supabase.table(APP_CONFIG["table_inventory"]).update({"Qty_On_Hand": new_qty, "Status": new_status}).eq("ID", selected_id).execute()
                        supabase.table(APP_CONFIG["table_activity"]).insert({
                            "Transaction #": f"TRX-{datetime.now().strftime('%f')}", 
                            "Timestamp": datetime.now(CLIENT_TZ).strftime("%Y-%m-%d %H:%M:%S"), 
                            "ID": selected_id, "Model": item['Model'], 
                            "Change": f"DISPATCHED {sell_qty}. Notes: {buyer_notes}", 
                            "User": st.session_state.user_email
                        }).execute()
                        st.success("✅ Dispatch executed!")
                    except Exception as e:
                        st.error(f"Error: {e}")

elif page == "Update Inventory":
    if is_sales:
        st.error("🚫 RESTRICTED: Admin Clearance Required.")
        st.stop()
        
    st.title("🔄 Logistics: Update Status")
    df = load_inventory()
    if not df.empty:
        selected_id = st.selectbox("Select Item ID", df['ID'].dropna().tolist())
        if selected_id:
            item = df[df['ID'] == selected_id].iloc[0]
            with st.form("update_form"):
                new_qty = st.number_input("New Quantity", value=int(item.get('Qty_On_Hand', 0)))
                new_status = st.selectbox("Update Status", ["Available", "Sold", "On Rent", "Maintenance", "Damaged"])
                if st.form_submit_button("Update Database"):
                    try:
                        supabase.table(APP_CONFIG["table_inventory"]).update({"Qty_On_Hand": new_qty, "Status": new_status}).eq("ID", selected_id).execute()
                        supabase.table(APP_CONFIG["table_activity"]).insert({
                            "Transaction #": f"TRX-{datetime.now().strftime('%f')}",
                            "Timestamp": datetime.now(CLIENT_TZ).strftime("%Y-%m-%d %H:%M:%S"),
                            "ID": selected_id, "Model": item['Model'],
                            "Change": f"Updated Status to {new_status}. New Qty: {new_qty}",
                            "User": st.session_state.user_email
                        }).execute()
                        st.success("✅ Record updated!")
                    except Exception as e:
                        st.error(f"Error: {e}")

elif page == "Activity Log":
    st.title("📖 Official Duty Log")
    log_df = load_activity()
    
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity recorded yet.")
