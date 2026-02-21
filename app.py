

    with tab2:
        st.subheader("📊 Detailed Unit Counts")
        st.markdown("### 🏗️ Machines")
        machines_df = df[(df['Category'] == 'Machine') & (df['Qty_On_Hand'] > 0)]
        if not machines_df.empty:
            m_counts = machines_df.groupby('Model')['Qty_On_Hand'].sum()
            cols = st.columns(len(m_counts) if len(m_counts) > 0 else 1)
            for i, (model, count) in enumerate(m_counts.items()):
                cols[i].metric(label=model, value=int(count))
    
        st.divider()
        st.markdown("### 🛠️ Attachments & Implements")
        attach_df = df[(df['Category'].isin(['Attachment', 'Implement'])) & (df['Qty_On_Hand'] > 0)]
        if not attach_df.empty:
            a_counts = attach_df.groupby(['Model', 'Size'])['Qty_On_Hand'].sum()
            for (model, size), count in a_counts.items():
                label = f"{size} {model}" if size and size != "N/A" else model
                st.metric(label=label, value=int(count))
    
    with tab3:
        st.subheader("🕒 Recent Activity")
        if os.path.exists(LOG_FILE):
            try:
                log_df = pd.read_csv(LOG_FILE, on_bad_lines='skip')
                if not log_df.empty:
                    st.dataframe(log_df.sort_values(by=log_df.columns[0], ascending=False), use_container_width=True)
                else:
                    st.info("No activity recorded yet.")
            except Exception as e:
                st.error(f"Log Error: {e}")
        else:
            st.info("No transactions logged yet.")
    
    with tab4:
        st.subheader("➕ Add New Inventory")
        with st.form("new_item_form", clear_on_submit=True):
            f_id = st.text_input("Item ID (VIN)")
            f_cat = st.selectbox("Category", ["Machine", "Attachment", "Implement"])
            f_model = st.text_input("Model Name")
            f_size_choice = st.selectbox("Select Size", ["N/A", "12\"", "18\"", "24\"", "36\"", "40\"", "48\"", "Small", "Large", "Custom"])
            f_custom_size = st.text_input("If Custom, enter size here:")
            f_size = f_custom_size if f_size_choice == "Custom" else f_size_choice
            f_loc = st.text_input("Location")
            f_qty = st.number_input("Starting Quantity", min_value=1, value=1, step=1)
            
            submitted = st.form_submit_button("Add to Inventory")
            if submitted:
                if not f_id or not f_model:
                    st.error("Missing info.")
                else:
                    new_row = pd.DataFrame([{
                        "ID": f_id, "Category": f_cat, "Model": f_model, "Size": f_size,
                        "Status": "Available", "Location": f_loc, "Qty_On_Hand": f_qty
                    }])
                    pd.concat([df, new_row], ignore_index=True).to_csv(INV_FILE, index=False)
                    
                    log_add = pd.DataFrame([{
                        "Timestamp": datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S"),
                        "ID": f_id, "Model": f_model, "Size": f_size,
                        "Action": "Added New Stock", "User": "Captain"
                    }])
                    log_add.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)
                    
                    st.success("Added to stock.")
                    try:
                        st.rerun()
                    except AttributeError:
                        st.experimental_rerun()
    
