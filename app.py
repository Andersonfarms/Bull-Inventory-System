import streamlit as st
    import pandas as pd
    import os
    from datetime import datetime
    
    # --- CONFIGURATION ---
    INV_FILE = "bull_inventory.csv"
    LOG_FILE = "activity_log.csv"
    
    # Set page config
    st.set_page_config(page_title="Bull Inventory System", layout="wide")
    st.title("🐃 Anderson Farms Bull Inventory")
    
    # --- DATA LOAD ---
    if os.path.exists(INV_FILE):
        df = pd.read_csv(INV_FILE)
    else:
        st.error("Inventory file not found!")
        st.stop()
    
    # --- DASHBOARD TABS ---
    tab1, tab2, tab3 = st.tabs(["📈 Current Inventory", "📊 Analytics", "🕓 Recent Activity"])
    
    with tab1:
        st.subheader("Live Warehouse Stock")
        st.divider()
    
        # Show only Available items in the main table
        available_df = df[df['Qty_On_Hand'] > 0]
    
        # --- FILTERS ---
        st.sidebar.header("Filters")
        categories = ['All'] + sorted(available_df['Category'].unique())
        selected_category = st.sidebar.selectbox("Category", categories)
    
        models = ['All'] + sorted(available_df['Model'].unique())
        selected_model = st.sidebar.selectbox("Model", models)
    
        locations = ['All'] + sorted(available_df['Location'].unique())
        selected_location = st.sidebar.selectbox("Location", locations)
    
        # Apply filters
        filtered_df = available_df.copy()
        if selected_category != 'All':
            filtered_df = filtered_df[filtered_df['Category'] == selected_category]
        if selected_model != 'All':
            filtered_df = filtered_df[filtered_df['Model'] == selected_model]
        if selected_location != 'All':
            filtered_df = filtered_df[filtered_df['Location'] == selected_location]
    
        st.dataframe(filtered_df, use_container_width=True)
    
        st.divider()
        st.subheader("Manage Inventory")
        col1, col2 = st.columns(2)
        with col1:
            st.info("Update Quantity")
            item_ids = df['ID'].unique().tolist()
            selected_id = st.selectbox("Select Item ID", item_ids, key="update_id")
            new_qty = st.number_input("New Quantity On Hand", min_value=0, step=1, key="new_qty")
            if st.button("Update Quantity", key="update_qty_btn"):
                df.loc[df['ID'] == selected_id, 'Qty_On_Hand'] = new_qty
                df.to_csv(INV_FILE, index=False)
                st.success(f"Quantity for {selected_id} updated to {new_qty}.")
                # Log the activity with the selected user
                log_entry = pd.DataFrame({
                    "Timestamp": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                    "ID": [selected_id],
                    "Action": [f"Quantity updated to {new_qty}"],
                    "User": ["system"] # Assuming system user for now
                })
                if not os.path.isfile(LOG_FILE):
                    log_entry.to_csv(LOG_FILE, index=False)
                else:
                    log_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)
                st.experimental_rerun()
    
        with col2:
            st.warning("Feature Coming Soon") # Placeholder for future feature
    
    
    with tab2:
        st.subheader("📊 Inventory Metrics")
        total_units = df['Qty_On_Hand'].sum()
        st.metric("Total Units in Stock", int(total_units))
    
        st.divider()
        # st.subheader("Stock by Category")
    
        # # Calculate totals per Category
        # category_counts = df[df['Qty_On_Hand'] > 0].groupby('Category')['Qty_On_Hand'].sum()
    
        # if not category_counts.empty:
            # # Create columns to display each category as a big number
            # cols = st.columns(len(category_counts))
            # for i, (category, count) in enumerate(category_counts.items()):
                # with cols[i]:
                    # st.metric(label=f"Total {category}", value=int(count))
        # else:
            # st.info("No stock currently available to show.")
        st.subheader("Stock by Model")
        model_counts = df[df['Qty_On_Hand'] > 0].groupby('Model')['Qty_On_Hand'].sum()
        if not model_counts.empty:
            st.dataframe(model_counts)
        else:
            st.info("No stock currently available to show for models.")
    
    
    with tab3:
        st.subheader("🕓 Recent Activity")
        if os.path.exists(LOG_FILE):
            log_df = pd.read_csv(LOG_FILE)
            st.table(log_df.sort_values(by="Timestamp", ascending=False).head(20))
        else:
            st.info("No transactions logged yet.")
    
    
