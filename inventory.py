import csv
import os
import random
import string
from datetime import datetime

INV_FILE = "bull_inventory.csv"
LOG_FILE = "inventory_log.csv"def bulk_populate():
    """Fast entry for initial setup of physical stock."""
    print("\n[ QUICK POPULATE: INITIAL STOCK ]")
    print("Categories: (M)achine, (A)ttachment, (P)arts")
    cat_input = input("Which category are you adding now? ").upper()
    category = "Machine" if cat_input == 'M' else "Attachment" if cat_input == 'A' else "Parts"
    
    print(f"\n--- Adding {category}s ---")
    print("Type 'done' for Model to switch categories or exit.")
    
    while True:
        model = input("\nModel Name: ")
        if model.lower() == 'done': break
        
        qty = input(f"How many {model} units on hand? ")
        try:
            qty = int(qty)
        except ValueError:
            print("❌ Invalid number. Skipping.")
            continue
            
        asset_id = generate_id(category)
        with open(INV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([asset_id, category, "Initial Load", model, "N/A", "Available", "Warehouse", qty, 0, 2])
        
        log_transaction(asset_id, "BULK_POPULATE", f"Initial setup: {qty} x {model}")
        print(f"✅ Saved: {asset_id} | {model} | Qty: {qty}")

def main_menu():
    initialize_inventory()
    while True:
        print("\n--- BULL EQUIPMENT INVENTORY ---")
        print("1. Add Single Asset")
        print("2. Receive Shipment")
        print("3. Bulk Populate (Initial Setup)")
        print("4. View Low Stock Alerts")
        print("5. View Activity Logs")
        print("6. Exit")
        
        choice = input("Select: ")
        if choice == '1':
            add_asset() # Ensure you have an add_asset function defined
        elif choice == '2':
            receive_shipment() # Ensure you have a receive_shipment function defined
        elif choice == '3':
            bulk_populate()
        elif choice == '4':
            if os.path.exists(INV_FILE):
                with open(INV_FILE, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if int(row['Qty_On_Hand']) <= int(row['Reorder_Level']):
                            print(f"⚠️ LOW STOCK: {row['Model']} ({row['Qty_On_Hand']} left)")
        elif choice == '5':
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    for line in f.readlines()[-10:]: print(line.strip())
        elif choice == '6':
            break
