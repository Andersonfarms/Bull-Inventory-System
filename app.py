# ==========================================
# Bull Inventory TERMINAL // DATA-LINK v1.10
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
    --bg-base: #0a0a0a;         /* Deep Black */
    --surface-level: #1c1c1c;   /* Elevated Dark Grey for inventory cards */
    --accent-orange: #ff5500;   /* High-Vis Tactical Orange */
    --text-main: #ffffff;       /* Crisp White */
    --text-muted: #888888;      /* Grey for secondary intel */
    --border-grid: #333333;     /* Subtle grid lines */
}

/* Force Streamlit's main app container to use the Deep Black background */
.stApp {
    background-color: var(--bg-base);
    color: var(--text-main);
    font-family: 'Courier New', Courier, monospace;
}

/* ---------------------------------------------------------
   INVENTORY CARDS (The Iron Roster)
--------------------------------------------------------- */
.inventory-card {
    background-color: var(--surface-level);
    border: 1px solid var(--border-grid);
    border-left: 5px solid var(--accent-orange);
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 4px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.5);
}

.inventory-card h2 {
    color: var(--text-main);
    margin-top: 0;
    font-size: 1.2rem;
    text-transform: uppercase;
}

/* ---------------------------------------------------------
   ACTION BUTTONS (e.g., The "Sell" Feature)
--------------------------------------------------------- */
.tactical-btn {
    background-color: transparent;
    color: var(--accent-orange);
    border: 2px solid var(--accent-orange);
    padding: 10px 20px;
    font-size: 1rem;
    font-weight: bold;
    text-transform: uppercase;
    cursor: pointer;
    border-radius: 3px;
    transition: all 0.2s ease-in-out;
    width: 100%; /* Finger-friendly for mobile */
    margin-top: 10px;
}

.tactical-btn:active {
    background-color: var(--accent-orange);
    color: var(--bg-base);
}

/* ---------------------------------------------------------
   DATA LABELS (Supabase Readouts)
--------------------------------------------------------- */
.data-label {
    color: var(--accent-orange);
    font-size: 0.85rem;
    display: block;
    margin-bottom: 3px;
}

.data-value {
    color: var(--text-main);
    font-size: 1rem;
    margin-bottom: 10px;
    display: block;
}
</style>
"""

# Execute the CSS Override
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

# --- 3. SIDEBAR & LOGO ---
st.sidebar.image("bull.png", width=200)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Add New Stock", "Sell Inventory", "Update Inventory", "Activity Log"])

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
        else:
            col2.metric("Total Units", 0)
            
        col3.metric("Categories", len(df['Category'].unique()) if 'Category' in df.columns else 0)

        # --- FLEET BREAKDOWN ---
        st.markdown("### 📊 Fleet Breakdown")
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

        st.markdown("---")
        
        # Search and Table 
        search = st.text_input("🔍 Search by Model, Type, or ID:")
        if search:
            mask = pd.Series(False, index=df.index)
            if 'Model' in df.columns:
                mask |= df['Model'].astype(str).str.contains(search, case=False, na=False)
            if 'ID' in df.columns:
                mask |= df['ID'].astype(str).str.contains(search, case=False, na=False)
            if 'Type' in df.columns:
                mask |= df['Type'].astype(str).str.contains(search, case=False, na=False)
            df = df[mask]
        
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
            model_options = ["12X", "18X", "22X", "25X", "40X", "1100X", "Bucket", "Auger", "Ripper", "Rake", "Forks", "Wood Splitter", "Hedge Trimmers", "Hammer", "Other"]
            new_model = st.selectbox("Model Name", model_options)
            new_type = st.selectbox("Machine Type", ["Excavator", "Skid Steer", "Other"])
            new_qty = st.number_input("Quantity", min_value=1, step=1)
            
        with col2:
            new_cat = st.selectbox("Category", ["Machine", "Attachment", "Parts", "Other"])
            size_options = ["N/A", "8\"", "12\"", "18\"", "24\"", "36\"", "40\"", "48\"", "Small", "Medium", "Large"]
            new_size = st.selectbox("Size", size_options)
            new_loc = st.text_input("Location", value="Warehouse")
            
        submit = st.form_submit_button("Add to Supabase Inventory")
        
        if submit:
            if new_id:
                now = datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S")
                trx_id = f"TRX-{datetime.now().strftime('%f')}" 
                
                new_item = {
                    "ID": new_id,
                    "Model": new_model,
                    "Type": new_type,
                    "Qty_On_Hand": int(new_qty),
                    "Location": new_loc,
                    "Category": new_cat,
                    "Size": new_size,
                    "Status": "Available"
                }
                
                try:
                    supabase.table("bull_inventory").insert(new_item).execute()
                    
                    log_entry = {
                        "Transaction #": trx_id,
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
                    if "23505" in str(e):
                        st.error(f"🚫 The ID '{new_id}' already exists in the system. Please use a unique ID.")
                    else:
                        st.error(f"Database Error: {e}")
            else:
                st.error("Please provide an Item ID.")

# --- PAGE: SELL INVENTORY ---
elif page == "Sell Inventory":
    st.title("🛒 Sell Inventory")
    df = load_inventory()
    
    if not df.empty and 'ID' in df.columns:
        # Filter for items that actually have quantity > 0
        df['Qty_On_Hand'] = pd.to_numeric(df['Qty_On_Hand'], errors='coerce').fillna(0)
        available_items = df[df['Qty_On_Hand'] > 0]
        
        if not available_items.empty:
            item_list = available_items['ID'].dropna().tolist()
            selected_id = st.selectbox("Select Item ID to Sell", item_list)
            
            if selected_id:
                current_item = available_items[available_items['ID'] == selected_id].iloc[0]
                current_qty = int(current_item['Qty_On_Hand'])
                
                st.info(f"Selling: **{current_item.get('Model', 'Unknown')}** ({current_item.get('Size', 'N/A')}) | Currently in stock: **{current_qty}**")
                
                with st.form("sell_form"):
                    sell_qty = st.number_input("Quantity Sold", min_value=1, max_value=current_qty, step=1)
                    buyer_notes = st.text_input("Buyer Name / Sale Notes (Optional)")
                    
                    sell_btn = st.form_submit_button("Process Sale")
                    
                    if sell_btn:
                        now = datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S")
                        trx_id = f"TRX-{datetime.now().strftime('%f')}"
                        
                        new_qty = current_qty - sell_qty
                        # Auto-update status to 'Sold' if they bought the last one
                        new_status = "Sold" if new_qty == 0 else current_item.get('Status', 'Available')
                        
                        try:
                            # 1. Update Inventory Table
                            supabase.table("bull_inventory").update({
                                "Qty_On_Hand": new_qty,
                                "Status": new_status
                            }).eq("ID", selected_id).execute()
                            
                            # 2. Log the Sale
                            notes_str = f" | Notes: {buyer_notes}" if buyer_notes else ""
                            change_desc = f"SOLD {sell_qty} units. Remaining: {new_qty}{notes_str}"
                            
                            log_entry = {
                                "Transaction #": trx_id,
                                "Timestamp": now,
                                "ID": selected_id,
                                "Model": current_item.get('Model', 'Unknown'),
                                "Change": change_desc,
                                "User": "Admin"
                            }
                            supabase.table("bull_activity_log").insert(log_entry).execute()
                            
                            st.success(f"✅ Successfully sold {sell_qty}x {current_item.get('Model', 'Unknown')}!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Database Error: {e}")
        else:
            st.warning("No items currently available to sell (All quantities are 0).")
    else:
        st.warning("No inventory found.")

# --- PAGE: UPDATE INVENTORY ---
elif page == "Update Inventory":
    st.title("🔄 Update Existing Stock")
    df = load_inventory()
    
    if not df.empty and 'ID' in df.columns:
        item_list = df['ID'].dropna().tolist()
        selected_id = st.selectbox("Select Item ID to Update", item_list)
        
        if selected_id:
            current_item = df[df['ID'] == selected_id].iloc[0]
            st.info(f
