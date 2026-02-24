# ==========================================
# Bull Inventory TERMINAL // DATA-LINK 
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

# --- 3. SIDEBAR & LOGO ---
st.sidebar.image("bull.png", width=200)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Add New Stock", "Activity Log"])

# --- PAGE: DASHBOARD ---
if page == "Dashboard":
    st.title("🏗️ Bull Inventory Dashboard")
    df = load_inventory()
    
    if not df.empty:
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Models", len(df))
        
        # Using your exact Supabase column name: Qty_On_Hand
        target_qty_col = 'Qty_On_Hand'
        
        if target_qty_col in df.columns:
            # Convert to numeric just in case there are strings, then sum
            total_units = pd.to_numeric(df[target_qty_col], errors='coerce').sum()
            col2.metric("Total Units", int(total_units))
        else:
            col2.metric("Total Units", "Error: Col Missing")
            
        col3.metric("Categories", len(df['Category'].unique()) if 'Category' in df.columns else 0)
        st.markdown("---")
        
        # Search and Table
        search = st.text_input("🔍 Search by Model or ID:")
        if search:
            df = df[df['Model'].str.contains(search, case=False) | df['ID'].str.contains(search, case=False)]
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No inventory found in Supabase.")

# --- PAGE: ADD NEW STOCK ---
elif page == "Add New Stock":
    st.title("➕ Register New Inventory")
    
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("Item ID (e.g., A-9PWW)")
            new_model = st.text_input("Model Name")
            new_qty = st.number_input("Quantity", min_value=1, step=1)
        with col2:
            new_cat = st.selectbox("Category", ["Bucket", "Attachment", "Machine", "Parts", "Other"])
            new_loc = st.text_input("Location")
            
        submit = st.form_submit_button("Add to Supabase Inventory")
        
        if submit:
            if new_id and new_model:
                now = datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S")
                
                # 1. Insert into Inventory
                new_item = {
                    "ID": new_id,
                    "Model": new_model,
                    "Quantity": int(new_qty),
                    "Location": new_loc,
                    "Category": new_cat,
                    "Status": "In Stock",
                    "Last_Updated": now
                }
                supabase.table("bull_inventory").insert(new_item).execute()
                
                # 2. Log Activity
                log_entry = {
                    "Timestamp": now,
                    "Transaction #": f"TRX-{datetime.now().strftime('%f')}",
                    "ID": new_id,
                    "Model": new_model,
                    "Change": f"Added {new_qty} units",
                    "User": "Admin"
                }
                supabase.table("bull_activity_log").insert(log_entry).execute()
                
                st.success(f"✅ {new_model} successfully stored in Supabase!")
                st.balloons()
            else:
                st.error("Please provide both an ID and a Model name.")

# --- PAGE: ACTIVITY LOG ---
elif page == "Activity Log":
    st.title("📖 Transaction History")
    log_df = load_activity()
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity recorded yet.")
