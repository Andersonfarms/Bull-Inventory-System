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
        
        target_qty_col = 'Qty_On_Hand'
        if target_qty_col in df.columns:
            total_units = pd.to_numeric(df[target_qty_col], errors='coerce').sum()
            col2.metric("Total Units", int(total_units))
        
        col3.metric("Categories", len(df['Category'].unique()) if 'Category' in df.columns else 0)

        # --- NEW: FLEET BREAKDOWN ---
        st.markdown("### 📊 Fleet Breakdown")
        breakdown_col1, breakdown_col2 = st.columns(2)
        
        with breakdown_col1:
            if 'Model' in df.columns:
                st.write("**By Specific Model:**")
                # Group by Model and sum the Qty_On_Hand
                model_counts = df.groupby('Model')[target_qty_col].sum().reset_index()
                # Sort it so the highest quantities are at the top
                model_counts = model_counts.sort_values(by=target_qty_col, ascending=False)
                st.dataframe(model_counts, hide_index=True, use_container_width=True)
        
        with breakdown_col2:
            if 'Category' in df.columns:
                st.write("**By Category:**")
                # Group by Category and sum the Qty_On_Hand
                cat_counts = df.groupby('Category')[target_qty_col].sum().reset_index()
                st.dataframe(cat_counts, hide_index=True, use_container_width=True)

        st.markdown("---")
        
        # Search and Table
        search = st.text_input("🔍 Search by Model, Type, or ID:")
        if search:
            # Enhanced search to include the 'Type' column
            df = df[
                df['Model'].str.contains(search, case=False) | 
                df['ID'].str.contains(search, case=False) |
                (df['Type'].str.contains(search, case=False) if 'Type' in df.columns else False)
            ]
        
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
            
            # --- DROPDOWN: MODELS ---
            model_options = ["12X", "18X", "22X", "25X", "40X", "1100X", "Rake", "Bucket", "Auger", "Hammer", "Other"]
            new_model = st.selectbox("Model Name", model_options)
            
            new_type = st.selectbox("Machine Type", ["Excavator", "Skid Steer", "Other"])
            new_qty = st.number_input("Quantity", min_value=1, step=1)
            
        with col2:
            new_cat = st.selectbox("Category", ["Machine", "Attachment", "Parts", "Other"])
            
            # --- DROPDOWN: SIZES ---
            size_options = ["N/A", "8\"", "12\"", "18\"", "24\"", "36\"", "40\"", "48\"", "Small", "Medium", "Large"]
            new_size = st.selectbox("Size", size_options)
            
            new_loc = st.text_input("Location", value="Warehouse")
            
        submit = st.form_submit_button("Add to Supabase Inventory")
        
        if submit:
            if new_id:
                now = datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S")
                
                # --- 1. PREPARE DATA (MATCHING SUPABASE EXACTLY) ---
                new_item = {
                    "ID": new_id,
                    "Model": new_model,
                    "Type": new_type,
                    "Qty_On_Hand": int(new_qty), # Match your 'int8' column in Supabase
                    "Location": new_loc,
                    "Category": new_cat,
                    "Size": new_size,
                    "Status": "Available",
                    "Last_Updated": now
                }
                
                try:
                    # --- 2. INSERT INTO INVENTORY ---
                    supabase.table("bull_inventory").insert(new_item).execute()
                    
                    # --- 3. LOG ACTIVITY ---
                    log_entry = {
                        "Timestamp": now,
                        "ID": new_id,
                        "Model": new_model,
                        "Change": f"Added {new_qty} units ({new_size})",
                        "User": "Admin"
                    }
                    supabase.table("bull_activity_log").insert(log_entry).execute()
                    
                    st.success(f"✅ {new_model} ({new_size}) successfully stored in Supabase!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.error("Please provide an Item ID.")
                
# --- PAGE: ACTIVITY LOG ---
elif page == "Activity Log":
    st.title("📖 Transaction History")
    log_df = load_activity()
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity recorded yet.")
