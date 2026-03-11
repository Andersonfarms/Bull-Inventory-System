# ==========================================
# Bull Inventory TERMINAL // DATA-LINK v2.1
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
    color: var(--accent-orange) !important;
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
            new_loc = st.text_input("Location", value="Warehouse")
            
        submit = st.form_submit_button("Commit to Database")
        
        if submit and new_id:
            now = datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S")
            trx_id = f"TRX-{datetime.now().strftime('%f')}" 
            new_item = {"ID": new_id, "Model": new_model, "Type": new_type, "Qty_On_Hand": int(new_qty), "Location": new_loc, "Category": new_cat, "Size": new_size, "Status": "Available"}
            try:
                supabase.table("bull_inventory").insert(new_item).execute()
                log_entry = {"Transaction #": trx_id, "Timestamp": now, "ID": new_id, "Model": new_model, "Change": f"Added {new_qty} units ({new_size})", "User": "Admin"}
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
            selected_id = st.selectbox("Select Item ID to Dispatch", available_items['ID'].dropna().tolist())
            if selected_id:
                current_item = available_items[available_items['ID'] == selected_id].iloc[0]
                current_qty = int(current_item['Qty_On_Hand'])
                st.info(f"Target: **{current_item.get('Model', 'Unknown')}** | Current Stock: **{current_qty}**")
                
                with st.form("sell_form"):
                    sell_qty = st.number_input("Quantity Dispatched", min_value=1, max_value=current_qty, step=1)
                    buyer_notes = st.text_input("Dispatch Notes / Buyer Name")
                    sell_btn = st.form_submit_button("Execute Dispatch")
                    
                    if sell_btn:
                        now = datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S")
                        new_qty = current_qty - sell_qty
                        new_status = "Sold" if new_qty == 0 else current_item.get('Status', 'Available')
                        try:
                            supabase.table("bull_inventory").update({"Qty_On_Hand": new_qty, "Status": new_status}).eq("ID", selected_id).execute()
                            log_entry = {"Transaction #": f"TRX-{datetime.now().strftime('%f')}", "Timestamp": now, "ID": selected_id, "Model": current_item.get('Model', 'Unknown'), "Change": f"DISPATCHED {sell_qty} units. Remaining: {new_qty}", "User": "Admin"}
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
