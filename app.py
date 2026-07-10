# ==========================================
# CORE INVENTORY TERMINAL // DATA-LINK v4.0
# System Engineered by: NyssaFire Gaming & Michael Anderson
# Date Created: 27 Feb 2026
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import streamlit.components.v1 as components
from supabase import create_client, Client

# --- 0. WHITE-LABEL CONFIGURATION ---
APP_CONFIG = {
    "company_name": "Bull", 
    "app_title": "Inventory System",
    "logo_path": "bull.png", 
    "timezone": "US/Central",
    
    # Database Tables
    "table_inventory": "bull_inventory",        
    "table_activity": "bull_activity_log",      
    "table_inbound": "bull_inbound_tracking",
    "table_pdi": "bull_pdi_records",
    
    # Dropdowns
    "sales_team": ["Fredrik L.", "Bailey A.", "Admin", "Other"],
    "machine_models": ["12X", "18X", "20X", "22X", "25X", "40X", "1100X", "Bucket", "Auger", "Ripper", "Rake", "Forks", "Wood Splitter", "Hedge Trimmers", "Hammer", "Other"],
    "machine_types": ["Excavator", "Skid Steer", "Other"],
    "categories": ["Machine", "Attachment", "Parts", "Other"],
    "carriers": ["Maersk", "CMA-CGM", "MSC", "Hapag-Lloyd", "Evergreen", "Other"]
}

# --- 1. CONFIG & CONNECTION ---
st.set_page_config(page_title=f"{APP_CONFIG['company_name']} {APP_CONFIG['app_title']}", page_icon="🏗️", layout="wide")

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
CLIENT_TZ = pytz.timezone(APP_CONFIG['timezone'])

# --- 2. DATA LOADERS ---
def load_inventory():
    response = supabase.table(APP_CONFIG["table_inventory"]).select("*").execute()
    return pd.DataFrame(response.data)

def load_activity():
    response = supabase.table(APP_CONFIG["table_activity"]).select("*").order("Timestamp", desc=True).execute()
    return pd.DataFrame(response.data)

def load_inbound():
    response = supabase.table(APP_CONFIG["table_inbound"]).select("*").execute()
    return pd.DataFrame(response.data)

def load_pdi():
    response = supabase.table(APP_CONFIG["table_pdi"]).select("*").execute()
    return pd.DataFrame(response.data)

# --- 2.5 SECURITY GATEWAY (SUPABASE AUTH) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_email'] = None

if not st.session_state['authenticated']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"### 🔒 {APP_CONFIG['company_name'].upper()} TERMINAL ACCESS")
        st.info("Authorized Personnel Only. Please sign in via Supabase.")
        
        with st.form("login_form"):
            auth_email = st.text_input("Email Address")
            auth_password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("UPLINK / LOGIN")
            
            if submit_login:
                if auth_email and auth_password:
                    try:
                        # Ping Supabase to verify credentials
                        auth_response = supabase.auth.sign_in_with_password({
                            "email": auth_email,
                            "password": auth_password
                        })
                        
                        # If successful, lock in the session
                        if auth_response.user:
                            st.session_state['authenticated'] = True
                            st.session_state['user_email'] = auth_response.user.email
                            st.success("Authentication Confirmed. Initializing systems...")
                            st.rerun()
                    except Exception as e:
                        # Supabase throws an exception if the password or email is wrong
                        st.error("❌ Access Denied. Invalid Email or Password.")
                else:
                    st.warning("Please enter both email and password.")
    
    # Halt app execution until authenticated
    st.stop()

# --- 3. THE TACTICAL SIDEBAR ROUTER ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def nav_to(page_name):
    st.session_state.current_page = page_name

try:
    st.sidebar.image(APP_CONFIG["logo_path"], width=200)
except:
    st.sidebar.markdown(f"### {APP_CONFIG['company_name']}")

st.sidebar.markdown('<div class="sidebar-header">CORE OPERATIONS</div>', unsafe_allow_html=True)
st.sidebar.button("Sitrep / Dashboard", on_click=nav_to, args=("Dashboard",), use_container_width=True)
st.sidebar.button("Service Master Sheet", on_click=nav_to, args=("Service Master Sheet",), use_container_width=True)
st.sidebar.button("Official Duty Log", on_click=nav_to, args=("Activity Log",), use_container_width=True)

st.sidebar.markdown('<div class="sidebar-header">TRACKING</div>', unsafe_allow_html=True)
st.sidebar.button("Inbound Freight", on_click=nav_to, args=("Inbound Freight",), use_container_width=True)

st.sidebar.markdown('<div class="sidebar-header">DIGITAL LEDGERS</div>', unsafe_allow_html=True)
st.sidebar.button("Equipment Ledger", on_click=nav_to, args=("Equipment Ledger",), use_container_width=True)
st.sidebar.button("Attachment Ledger", on_click=nav_to, args=("Attachment Ledger",), use_container_width=True)
st.sidebar.button("Parts Ledger", on_click=nav_to, args=("Parts Ledger",), use_container_width=True)
st.sidebar.button("Sold Ledger", on_click=nav_to, args=("Sold Ledger",), use_container_width=True)
st.sidebar.button("PDI Records", on_click=nav_to, args=("PDI Records",), use_container_width=True)
st.sidebar.button("Damaged Ledger", on_click=nav_to, args=("Damaged Ledger",), use_container_width=True)
st.sidebar.button("🛠️ Troubleshooting", on_click=nav_to, args=("Troubleshooting",), use_container_width=True)

st.sidebar.markdown('<div class="sidebar-header">LOGISTICS (S-4)</div>', unsafe_allow_html=True)
st.sidebar.button("Add New Stock", on_click=nav_to, args=("Add New Stock",), use_container_width=True)
st.sidebar.button("Sell / Dispatch", on_click=nav_to, args=("Sell Inventory",), use_container_width=True)
st.sidebar.button("Update Status", on_click=nav_to, args=("Update Inventory",), use_container_width=True)

page = st.session_state.current_page

# --- PAGE: DASHBOARD (SITREP) ---
if page == "Dashboard":
    st.title(f"📡 {APP_CONFIG['company_name']} Sitrep: Master Overview")
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
        st.markdown("### 📊 Active Fleet Breakdown (Excluding Sold)")
        breakdown_col1, breakdown_col2 = st.columns(2)
        
        active_df = df[df['Status'] != 'Sold']
        
        with breakdown_col1:
            if 'Model' in active_df.columns and target_qty_col in active_df.columns:
                st.write("**By Specific Model:**")
                model_counts = active_df.groupby('Model')[target_qty_col].sum().reset_index()
                model_counts = model_counts.sort_values(by=target_qty_col, ascending=False)
                st.dataframe(model_counts, hide_index=True, use_container_width=True)
        
        with breakdown_col2:
            if 'Category' in active_df.columns and target_qty_col in active_df.columns:
                st.write("**By Category:**")
                cat_counts = active_df.groupby('Category')[target_qty_col].sum().reset_index()
                st.dataframe(cat_counts, hide_index=True, use_container_width=True)
    else:
        st.warning("No inventory found in database.")

# --- PAGE: SERVICE MASTER SHEET ---
elif page == "Service Master Sheet":
    st.title("📋 Live Service Master Sheet")
    st.markdown("Google Workspace Integration active. Tactical Dark Mode applied. Edit directly below.")
    sheet_url = "https://docs.google.com/spreadsheets/d/110U282cubI4SIL6UL5mN3l3DiQFzulMCnkrFMgJ1VBo/edit?embedded=true"
    
    dark_sheet_html = f"""
    <style>
        .dark-iframe-container iframe {{
            filter: invert(100%) hue-rotate(180deg) brightness(85%) contrast(95%);
            border: 2px solid #333333;
            border-radius: 5px;
            background-color: white; 
        }}
    </style>
    <div class="dark-iframe-container">
        <iframe src="{sheet_url}" width="100%" height="800px"></iframe>
    </div>
    """
    st.components.v1.html(dark_sheet_html, height=805)

# --- PAGE: INBOUND FREIGHT (DYNAMIC TRACKING) ---
elif page == "Inbound Freight":
    st.title("🚢 Inbound Freight")
    
    def get_tracking_url(carrier, tracking_number):
        urls = {
            "Maersk": f"https://www.maersk.com/tracking/{tracking_number}",
            "CMA-CGM": f"https://www.cma-cgm.com/ebusiness/tracking/search?reference={tracking_number}",
            "MSC": f"https://www.msc.com/en/track-a-shipment?trackingNumber={tracking_number}",
            "Hapag-Lloyd": f"https://www.hapag-lloyd.com/en/online-business/track/track-by-container-solution.html?blno={tracking_number}"
        }
        return urls.get(carrier, f"https://www.searates.com/container/tracking/?number={tracking_number}")

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
            
        st.markdown("---")
        st.markdown("**Update Shipment Status**")
        update_id = st.selectbox("Select Container to mark as 'Arrived'", inbound_df[inbound_df['Status'] != 'Arrived']['Tracking_Number'].tolist() if not active_shipments.empty else ["None"])
        if update_id != "None":
            if st.button("Mark as Arrived"):
                try:
                    supabase.table(APP_CONFIG["table_inbound"]).update({"Status": "Arrived"}).eq("Tracking_Number", update_id).execute()
                    st.success(f"✅ Container {update_id} marked as Arrived. Please move contents to Add New Stock.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Database Error: {e}")
    else:
        st.info("No tracking data on file.")

    st.markdown("---")
    st.markdown("### ➕ Log New Inbound Container")
    with st.form("inbound_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tracking_num = st.text_input("Container / Tracking Number")
            carrier = st.selectbox("Carrier", APP_CONFIG["carriers"])
        with col2:
            contents = st.text_input("Primary Contents")
            eta = st.text_input("Expected Time of Arrival (ETA)")
            
        if st.form_submit_button("Start Tracking") and tracking_num:
            new_shipment = {"Tracking_Number": tracking_num, "Carrier": carrier, "Contents": contents, "ETA": eta, "Status": "In Transit"}
            try:
                supabase.table(APP_CONFIG["table_inbound"]).insert(new_shipment).execute()
                st.success(f"✅ Container {tracking_num} logged!")
                st.rerun()
            except Exception as e:
                st.error(f"Database Error: {e}")

# --- PAGES: THE DIGITAL LEDGERS ---
elif page in ["Equipment Ledger", "Attachment Ledger", "Parts Ledger", "Sold Ledger", "Damaged Ledger"]:
    st.title(f"📂 {page}")
    df = load_inventory()
    
    if not df.empty:
        if page == "Equipment Ledger": 
            df = df[(df['Category'] == 'Machine') & (df['Status'] != 'Sold')]
        elif page == "Attachment Ledger": 
            df = df[(df['Category'] == 'Attachment') & (df['Status'] != 'Sold')]
        elif page == "Parts Ledger": 
            df = df[(df['Category'] == 'Parts') & (df['Status'] != 'Sold')]
        elif page == "Sold Ledger": 
            df = df[df['Status'] == 'Sold']
        elif page == "Damaged Ledger": 
            df = df[df['Status'] == 'Damaged']
            
        search = st.text_input(f"🔍 Search {page}:")
        if search:
            mask = pd.Series(False, index=df.index)
            for col in ['Model', 'ID', 'Description']:
                if col in df.columns:
                    mask |= df[col].astype(str).str.contains(search, case=False, na=False)
            df = df[mask]
            
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning(f"No records found for {page}.")

# --- PAGE: PDI RECORDS ---
elif page == "PDI Records":
    st.title("📋 Pre-Delivery Inspections (PDI)")
    
    st.subheader("Active PDI Ledger")
    pdi_df = load_pdi()
    if not pdi_df.empty:
        st.dataframe(pdi_df, use_container_width=True, hide_index=True)
    else:
        st.info("No PDI records found in database.")
        
    st.markdown("---")
    st.subheader("➕ Log New PDI")
    
    with st.form("pdi_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            pdi_vin = st.text_input("VIN / Serial Number")
            pdi_model = st.selectbox("Machine Model", APP_CONFIG["machine_models"])
            pdi_inspector = st.text_input("Inspector Email", value="service@bull-equipment.com")
            
        with col2:
            pdi_hours = st.number_input("Meter Hours", min_value=0.0, step=0.1)
            pdi_volts = st.number_input("Battery Volts (DC)", min_value=0.0, step=0.1)
            pdi_date = st.date_input("Inspection Date", datetime.now(CLIENT_TZ).date())
            
        if st.form_submit_button("Submit PDI Record"):
            if pdi_vin:
                new_pdi = {
                    "VIN": pdi_vin,
                    "Model": pdi_model,
                    "Hours": float(pdi_hours),
                    "Date": pdi_date.strftime("%Y-%m-%d"),
                    "Inspector": pdi_inspector,
                    "Volts": float(pdi_volts)
                }
                try:
                    supabase.table(APP_CONFIG["table_pdi"]).insert(new_pdi).execute()
                    
                    # Log activity
                    now = datetime.now(CLIENT_TZ).strftime("%Y-%m-%d %H:%M:%S")
                    trx_id = f"PDI-{datetime.now().strftime('%f')}" 
                    log_entry = {"Transaction #": trx_id, "Timestamp": now, "ID": pdi_vin, "Model": pdi_model, "Change": f"Completed PDI: {pdi_hours} hrs | {pdi_volts}V", "User": pdi_inspector}
                    supabase.table(APP_CONFIG["table_activity"]).insert(log_entry).execute()
                    
                    st.success(f"✅ PDI Logged for VIN: {pdi_vin}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.warning("⚠️ Please enter a valid VIN.")

# --- PAGE: TROUBLESHOOTING GUIDE ---
elif page == "Troubleshooting":
    st.title("🛠️ Tactical Field Diagnostics")
    st.markdown("Interactive repair sequences for mechanical and electrical units.")

    issue_cat = st.selectbox("Identify the System Failure:", 
                             ["Select system...", 
                              "No Lights on LCD / Won't Start", 
                              "Battery Not Charging (Electrical System)",
                              "Engine Won't Start (Starter/Battery Issues)",
                              "Track Issues (Slipping / No Movement)"])

    # --- ISSUE 1: LCD / IGNITION ---
    if issue_cat == "No Lights on LCD / Won't Start":
        st.header("🖥️ LCD & Ignition Diagnostic")
        st.subheader("STEP 1: Initial Safety Checks")
        st.info("1. Verify E-Stop is physically UP.\n2. Check fuses inside engine door.\n3. Check 30A/60A Main Fuses near battery.")
        
        if st.checkbox("Fuses and E-Stop button are physically OK"):
            st.subheader("STEP 2: The E-Stop Bypass Test")
            st.write("Unplug the E-Stop harness. Use a jumper wire to bridge the connection.")
            
            col1, col2 = st.columns(2)
            if col1.button("MACHINE FIRES UP"):
                st.success("✅ **FIXED: Bad E-Stop Switch.**")
                st.warning("The internal contact in the switch has failed. Replace the E-Stop assembly.")
            if col2.button("STILL NO LIGHTS"):
                st.error("### STEP 3: Ignition Switch & Harness")
                st.write("Check the **Grey wire** on the back of the key switch for 12V when turned to 'ON'. If 0V, the ignition switch is fried.")

    # --- ISSUE 2: CHARGING SYSTEM ---
    elif issue_cat == "Battery Not Charging (Electrical System)":
        st.header("🔌 Charging System (18X Style)")
        test_type = st.radio("Which test are you performing?", ["Stator AC Test (Engine Plug)", "Battery DC Test (Battery Terminals)"])

        if test_type == "Stator AC Test (Engine Plug)":
            st.subheader("Alternator AC Output")
            st.write("Unplug the 2-wire connector from engine. Set meter to **AC Volts**. Run engine at mid-throttle.")
            ac_val = st.number_input("Enter AC Voltage:", min_value=0.0, step=0.1)
            if ac_val >= 20:
                st.success(f"✅ Alternator is GOOD ({ac_val}V AC). If battery isn't charging, replace Regulator.")
            elif 0 < ac_val < 20:
                st.error("❌ Low AC Output: Check fan belt tension.")
            elif ac_val == 0:
                st.error("❌ Alternator is DEAD.")
        else:
            st.subheader("Battery Charging Voltage")
            st.write("Measure DC Volts at battery with engine running at mid-throttle.")
            dc_val = st.number_input("Enter DC Voltage:", min_value=0.0, step=0.1)
            if 13.6 <= dc_val <= 14.8:
                st.success(f"✅ System Healthy ({dc_val}V DC). Battery is charging.")
            elif 12.8 < dc_val < 13.6:
                st.warning("⚠️ Marginal Charging. Check for loose grounds or old battery.")
            elif dc_val <= 12.8:
                st.error("❌ Not Charging. Check Stator AC output (Step 1).")

    # --- ISSUE 3: STARTER ---
    elif issue_cat == "Engine Won't Start (Starter/Battery Issues)":
        st.header("⚡ Starter System Diagnostic")
        st.subheader("The 'TAP' Test")
        st.write("Tap starter body with a wrench while turning the key.")
        if st.button("IT FIRED UP"):
            st.warning("⚠️ Starter brushes are worn. Replace starter.")
        else:
            st.subheader("Voltage Drop Test")
            st.write("Check battery voltage WHILE cranking.")
            drop = st.radio("Result:", ["Stays at 12.6V (No crank)", "Drops below 10V (Weak crank)"])
            if "Stays" in drop:
                st.error("❌ Power not reaching starter. Check solenoid/terminals.")
            else:
                st.error("❌ Battery is weak/dead.")

    # --- ISSUE 4: TRACKS ---
    elif issue_cat == "Track Issues (Slipping / No Movement)":
        st.header("🚜 Track & Drive System Diagnostic")
        track_issue_type = st.radio("Select the type of track failure:", ["Track is physically loose/slipping (Mechanical)", "Tracks won't move / no power to levers (Hydraulic)"])
        
        if track_issue_type == "Track is physically loose/slipping (Mechanical)":
            st.subheader("⚙️ Mechanical Track Adjustment")
            st.info("Required Tools: 32mm Wrench (Locknut) & 11/16\" Wrench (Adjuster Bolt)")
            st.write("1. Use the blade/boom to lift the track off the ground.")
            st.write("2. Clean the adjuster bolt threads with a wire brush to prevent seizing.")
            st.warning("DO NOT force the 11/16\" bolt without loosening the 32mm locknut first!")
            action = st.radio("What is the goal?", ["Tighten Loose Track", "Loosen Over-tight Track"])
            if action == "Tighten Loose Track":
                st.markdown("### 🛠️ Execution")
                st.write("1. Loosen the **32mm Locknut**.\n2. Turn the **11/16\" Bolt** CLOCKWISE to push the idler out.\n3. Stop when sag is **0.5 to 1.0 inches**.\n4. Tighten the 32mm Locknut to secure the setting.")
                if st.button("Tension Set & Locked"):
                    st.success("✅ Track tensioned. Mechanical lock engaged.")
            elif action == "Loosen Over-tight Track":
                st.markdown("### 🛠️ Execution")
                st.write("1. Loosen the **32mm Locknut**.\n2. Turn the **11/16\" Bolt** COUNTER-CLOCKWISE.\n3. Tap the idler with a hammer if it doesn't slide back on its own.\n4. Re-tighten the 32mm Locknut.")

        elif track_issue_type == "Tracks won't move / no power to levers (Hydraulic)":
            st.subheader("💧 Hydraulic & Drive Motor Test")
            st.write("Does the engine 'bog down' when you pull the track levers, or do the levers feel limp?")
            drive_feel = st.radio("Lever Response:", ["Engine bogs / Tracks won't move", "Levers feel limp / No engine load"])
            if drive_feel == "Engine bogs / Tracks won't move":
                st.error("❌ Mechanical Jam or Drive Motor Brake.")
                st.info("💡 **FIX:** Check for debris in the sprocket. If clear, the internal parking brake in the drive motor may be seized. This usually requires a motor rebuild.")
            else:
                st.error("❌ Pilot Pressure Loss (The 'Limp Lever' Issue).")
                st.write("1. **Check Safety Lever:** Ensure the left-hand safety console is fully down and the internal micro-switch is clicking.\n2. **Jumper Test:** Bypass the safety switch. If tracks move, the switch is bad.\n3. **Check Pilot Relief:** Locate the small pilot manifold. If the relief valve is stuck with a piece of metal/dirt, you will have 0 pilot pressure.")

    st.markdown("---")
    if st.button("Return to Sitrep"):
        st.session_state.current_page = "Dashboard"
        st.rerun()

# --- PAGE: ADD / RECEIVE STOCK ---
elif page == "Add New Stock":
    st.title("➕ Logistics: Stock & Inbound Management")
    
    tab1, tab2 = st.tabs(["Log New Stock / Orders", "Receive Arrived Stock"])
    
    with tab1:
        st.markdown("### Register Inventory or Inbound Orders")
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                stock_status = st.radio("Stock State:", ["On Hand (Available)", "On Order (In Transit)"])
                new_id = st.text_input("Item ID / VIN (Leave blank if On Order/Unknown)")
                new_model = st.selectbox("Model Name", APP_CONFIG["machine_models"])
                new_type = st.selectbox("Machine Type", APP_CONFIG["machine_types"])
                new_qty = st.number_input("Quantity", min_value=1, step=1)
                
            with col2:
                new_cat = st.selectbox("Category", APP_CONFIG["categories"])
                new_size = st.selectbox("Size", ["N/A", "8\"", "12\"", "18\"", "24\"", "36\"", "40\"", "48\"", "Small", "Medium", "Large"])
                new_desc = st.selectbox("Part Description", ["N/A", "Air Filter", "Oil Filter", "Hydraulic Filter", "Fuel Filter", "Hydraulic Hose", "O-Rings / Seals", "Track Assembly", "Sprocket / Idler", "Teeth / Cutting Edge", "Pins & Bushings", "Electrical Relay / Fuse", "Sensors", "Hardware / Fasteners", "Fluids / Grease", "Other"])
                new_loc = st.text_input("Location", value="Warehouse")
                
            if st.form_submit_button("Commit to Database"):
                now = datetime.now(CLIENT_TZ).strftime("%Y-%m-%d %H:%M:%S")
                trx_id = f"TRX-{datetime.now().strftime('%f')}" 
                
                # Auto-generate temporary PO ID if left blank
                final_id = new_id if new_id else f"PO-{new_model}-{datetime.now().strftime('%m%d%H%M')}"
                
                qty_hand = int(new_qty) if stock_status == "On Hand (Available)" else 0
                qty_order = int(new_qty) if stock_status == "On Order (In Transit)" else 0
                db_status = "Available" if stock_status == "On Hand (Available)" else "In Transit"
                
                new_item = {
                    "ID": final_id, 
                    "Model": new_model, 
                    "Type": new_type, 
                    "Qty_On_Hand": qty_hand,
                    "Qty_On_Order": qty_order,
                    "Location": new_loc, 
                    "Category": new_cat, 
                    "Size": new_size, 
                    "Description": new_desc, 
                    "Status": db_status
                }
                try:
                    supabase.table(APP_CONFIG["table_inventory"]).insert(new_item).execute()
                    desc_log = f" - {new_desc}" if new_desc != "N/A" else ""
                    log_entry = {"Transaction #": trx_id, "Timestamp": now, "ID": final_id, "Model": new_model, "Change": f"Logged {stock_status}: {new_qty} units ({new_size}{desc_log})", "User": st.session_state.get('user_email', 'Admin')}
                    supabase.table(APP_CONFIG["table_activity"]).insert(log_entry).execute()
                    st.success(f"✅ {new_model} successfully stored as {stock_status}!")
                except Exception as e:
                    st.error(f"Database Error: {e}")

    with tab2:
        st.markdown("### Process Arrived Freight")
        df = load_inventory()
        
        if not df.empty and 'Qty_On_Order' in df.columns:
            # Locate all items actively in transit
            df['Qty_On_Order'] = pd.to_numeric(df['Qty_On_Order'], errors='coerce').fillna(0)
            inbound_items = df[df['Qty_On_Order'] > 0]
            
            if not inbound_items.empty:
                inbound_items_display = inbound_items.copy()
                inbound_items_display['display'] = inbound_items_display['ID'] + " | " + inbound_items_display['Model'] + " (On Order: " + inbound_items_display['Qty_On_Order'].astype(int).astype(str) + ")"
                
                selected_inbound_str = st.selectbox("Select Arriving Shipment:", inbound_items_display['display'].tolist())
                
                if selected_inbound_str:
                    target_id = selected_inbound_str.split(" | ")[0]
                    target_item = inbound_items[inbound_items['ID'] == target_id].iloc[0]
                    max_qty = int(target_item['Qty_On_Order'])
                    is_machine = target_item['Category'] == 'Machine'
                    
                    st.info(f"Receiving: **{target_item['Model']}** | Outstanding Order: **{max_qty}**")
                    
                    # Not using a form here so the VIN text boxes can render dynamically
                    receive_qty = st.number_input("How many units arrived today?", min_value=1, max_value=max_qty, step=1)
                    
                    new_vins = []
                    if is_machine:
                        st.warning("⚠️ Machines require unique VINs. Please enter the VIN for each arriving unit below:")
                        for i in range(int(receive_qty)):
                            vin = st.text_input(f"VIN / Serial Number for Unit {i+1}", key=f"vin_{i}")
                            new_vins.append(vin)
                            
                    if st.button("Process Arrival & Update Ledgers", type="primary"):
                        now = datetime.now(CLIENT_TZ).strftime("%Y-%m-%d %H:%M:%S")
                        
                        if is_machine and any(not v.strip() for v in new_vins):
                            st.error("❌ All incoming machines must have a valid VIN entered before processing.")
                        else:
                            try:
                                # 1. Update the original placeholder PO record
                                new_on_order = max_qty - receive_qty
                                new_po_status = "Received" if new_on_order == 0 else "In Transit"
                                
                                supabase.table(APP_CONFIG["table_inventory"]).update({
                                    "Qty_On_Order": new_on_order,
                                    "Status": new_po_status
                                }).eq("ID", target_id).execute()
                                
                                # 2. Process the actual stock taking
                                if is_machine:
                                    for vin in new_vins:
                                        machine_item = {
                                            "ID": vin.strip(), "Model": target_item['Model'], "Type": target_item['Type'], 
                                            "Qty_On_Hand": 1, "Qty_On_Order": 0, "Location": "Warehouse", 
                                            "Category": "Machine", "Size": target_item['Size'], 
                                            "Description": target_item['Description'], "Status": "Available"
                                        }
                                        supabase.table(APP_CONFIG["table_inventory"]).insert(machine_item).execute()
                                    log_change = f"RECEIVED {receive_qty}x {target_item['Model']}. Logged new VINs. Remaining on PO: {new_on_order}"
                                else:
                                    current_hand = int(target_item.get('Qty_On_Hand', 0))
                                    new_hand = current_hand + receive_qty
                                    
                                    update_data = {"Qty_On_Hand": new_hand}
                                    if new_on_order == 0:
                                        update_data["Status"] = "Available"
                                        
                                    supabase.table(APP_CONFIG["table_inventory"]).update(update_data).eq("ID", target_id).execute()
                                    log_change = f"RECEIVED {receive_qty}x {target_item['Model']}. Transferred to Qty_On_Hand. Remaining on PO: {new_on_order}"
                                    
                                log_entry = {"Transaction #": f"RCV-{datetime.now().strftime('%f')}", "Timestamp": now, "ID": target_id, "Model": target_item['Model'], "Change": log_change, "User": st.session_state.get('user_email', 'Admin')}
                                supabase.table(APP_CONFIG["table_activity"]).insert(log_entry).execute()
                                
                                st.success("✅ Arrived stock processed successfully! Ledgers updated.")
                            except Exception as e:
                                st.error(f"Database Error: {e}")
            else:
                st.info("No items currently marked as 'On Order' in the system.")
        else:
            st.info("No order data available.")

# --- PAGE: SELL INVENTORY (WITH AUTO-BUNDLE LOGIC) ---
elif page == "Sell Inventory":
    st.title("🛒 Logistics: Dispatch / Sell")
    df = load_inventory()
    if not df.empty and 'ID' in df.columns:
        df['Qty_On_Hand'] = pd.to_numeric(df['Qty_On_Hand'], errors='coerce').fillna(0)
        available_items = df[(df['Qty_On_Hand'] > 0) & (df['Status'] != 'Sold')]
        
        if not available_items.empty:
            selected_id = st.selectbox("Select Primary Item to Dispatch", available_items['ID'].dropna().tolist())
            
            if selected_id:
                current_item = available_items[available_items['ID'] == selected_id].iloc[0]
                current_qty = int(current_item['Qty_On_Hand'])
                st.info(f"Target: **{current_item.get('Model', 'Unknown')}** | Current Stock: **{current_qty}**")
                
                # Check for standard bundle
                is_bundled_machine = current_item.get('Model') in ['12X', '18X', '20X']
                if is_bundled_machine:
                    st.warning("⚠️ **Standard Bundle Detected:** Dispatching this machine will automatically attempt to deduct 1x Ripper, 1x 40\" Bucket, and 1x 8\" Bucket from your active inventory.")

                attachments_df = available_items[(available_items['Category'] == 'Attachment') & (available_items['ID'] != selected_id)]
                attachment_options = ["None"] + attachments_df['ID'].dropna().tolist()
                
                with st.form("sell_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        sell_qty = st.number_input("Quantity Dispatched", min_value=1, max_value=current_qty, step=1)
                        salesperson = st.selectbox("Salesperson", APP_CONFIG["sales_team"])
                        buyer_notes = st.text_input("Dispatch Notes / Buyer Name")
                        
                    with col2:
                        transport_co = st.text_input("Transport Company")
                        st.markdown("**Bundle an Additional Attachment?**")
                        addon_id = st.selectbox("Select Extra Add-on", attachment_options)
                        addon_qty = st.number_input("Extra Add-on Quantity", min_value=1, step=1)
                        
                    if st.form_submit_button("Execute Dispatch"):
                        now = datetime.now(CLIENT_TZ).strftime("%Y-%m-%d %H:%M:%S")
                        new_qty = current_qty - sell_qty
                        new_status = "Sold" if new_qty == 0 else current_item.get('Status', 'Available')
                        
                        addon_success = True
                        auto_bundle_log = ""
                        manual_addon_log = ""
                        
                        # Process Manual Add-on Attachment First
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
                                    supabase.table(APP_CONFIG["table_inventory"]).update({"Qty_On_Hand": addon_new_qty, "Status": addon_new_status}).eq("ID", addon_id).execute()
                                    manual_addon_log = f" | Extra Add-on: {addon_qty}x {addon_id}"
                                    log_entry_addon = {"Transaction #": f"TRX-{datetime.now().strftime('%f')}-M", "Timestamp": now, "ID": addon_id, "Model": addon_item.get('Model', 'Unknown'), "Change": f"DISPATCHED {addon_qty} units (Manual Bundle). Remaining: {addon_new_qty}", "User": salesperson}
                                    supabase.table(APP_CONFIG["table_activity"]).insert(log_entry_addon).execute()
                                except Exception as e:
                                    st.error(f"Database Error on Manual Add-on: {e}")
                                    addon_success = False

                        # Process Auto-Bundles (Ripper, 40" Bucket, 8" Bucket) if applicable
                        if addon_success and is_bundled_machine:
                            required_attachments = [
                                {'Model': 'Ripper', 'Size': 'N/A'},
                                {'Model': 'Bucket 40"', 'Size': '40"'},
                                {'Model': 'Bucket 8"', 'Size': '8"'}
                            ]
                            
                            for req in required_attachments:
                                if req['Model'] == 'Ripper':
                                    match = available_items[(available_items['Model'] == 'Ripper') & (available_items['Qty_On_Hand'] > 0)]
                                else:
                                    match = available_items[(available_items['Model'] == req['Model']) & (available_items['Size'] == req['Size']) & (available_items['Qty_On_Hand'] > 0)]
                                
                                if not match.empty:
                                    target = match.iloc[0]
                                    target_id = target['ID']
                                    target_qty = int(target['Qty_On_Hand'])
                                    deduct_qty = sell_qty 
                                    
                                    if deduct_qty > target_qty:
                                        deduct_qty = target_qty # Deduct up to what is available
                                        
                                    new_att_qty = target_qty - deduct_qty
                                    new_att_status = "Sold" if new_att_qty == 0 else target.get('Status', 'Available')
                                    
                                    try:
                                        supabase.table(APP_CONFIG["table_inventory"]).update({"Qty_On_Hand": new_att_qty, "Status": new_att_status}).eq("ID", target_id).execute()
                                        auto_bundle_log += f" | Auto-Bundled: {deduct_qty}x {req['Model']} ({req['Size']})"
                                        log_entry_auto = {"Transaction #": f"TRX-{datetime.now().strftime('%f')}-B", "Timestamp": now, "ID": target_id, "Model": target.get('Model', 'Unknown'), "Change": f"AUTO-DISPATCHED {deduct_qty} units (Standard Bundle). Remaining: {new_att_qty}", "User": salesperson}
                                        supabase.table(APP_CONFIG["table_activity"]).insert(log_entry_auto).execute()
                                    except Exception as e:
                                        st.error(f"Failed to auto-bundle {req['Model']}: {e}")
                                else:
                                    st.warning(f"⚠️ Insufficient active stock for Standard Bundle item: {req['Model']} ({req['Size']}). Not fully deducted.")

                        # Process Primary Machine
                        if addon_success:
                            try:
                                supabase.table(APP_CONFIG["table_inventory"]).update({"Qty_On_Hand": new_qty, "Status": new_status}).eq("ID", selected_id).execute()
                                notes_str = f" | Buyer: {buyer_notes}" if buyer_notes else ""
                                trans_str = f" | Trans: {transport_co}" if transport_co else ""
                                full_change_log = f"DISPATCHED {sell_qty} units. Remaining: {new_qty}{auto_bundle_log}{manual_addon_log}{notes_str}{trans_str}"
                                
                                log_entry = {"Transaction #": f"TRX-{datetime.now().strftime('%f')}", "Timestamp": now, "ID": selected_id, "Model": current_item.get('Model', 'Unknown'), "Change": full_change_log, "User": salesperson}
                                supabase.table(APP_CONFIG["table_activity"]).insert(log_entry).execute()
                                st.success(f"✅ Dispatch executed for {sell_qty}x {current_item.get('Model', 'Unknown')}! All bundle items tracked and updated.")
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
                        supabase.table(APP_CONFIG["table_inventory"]).update({"Qty_On_Hand": int(new_qty), "Location": new_loc, "Status": new_status}).eq("ID", selected_id).execute()
                        now = datetime.now(CLIENT_TZ).strftime("%Y-%m-%d %H:%M:%S")
                        log_entry = {"Transaction #": f"TRX-{datetime.now().strftime('%f')}", "Timestamp": now, "ID": selected_id, "Model": current_item.get('Model', 'Unknown'), "Change": f"Updated Status: {new_status}. Qty: {new_qty}", "User": "Admin"}
                        supabase.table(APP_CONFIG["table_activity"]).insert(log_entry).execute()
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
