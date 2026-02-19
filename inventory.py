import csv
import os
import random
import string
from datetime import datetime

INV_FILE = "bull_inventory.csv"
LOG_FILE = "inventory_log.csv"

def initialize_inventory():
    """Safely initializes the inventory and logging files."""
    if not os.path.exists(INV_FILE):
        with open(INV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "ID", "Category", "Type", "Model", "Serial_Number", 
                "Status", "Location", "Qty_On_Hand", "Qty_On_Order", "Reorder_Level"
            ])
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Asset_ID", "Action", "Details"])

def log_transaction(asset_id, action, details):
    """Records every manual change made to the inventory."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, asset_id, action, details])

def generate_id(category):
    prefix = category[0].upper()
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{suffix}"

def add_asset():
    print("\n[ COMMAND: REGISTER NEW ASSET ]")
    print("Categories: (M)achine, (A)ttachment, (P)arts")
    cat_input = input("Category (M/A/P): ").upper()
    category = "Machine" if cat_input == 'M' else "Attachment" if cat_input == 'A' else "Parts"
    asset_id = generate_id(category)
    model = input("Model: ")
    try:
        qty_hand = int(input("Qty on Hand: ") or 0)
        qty_order = int(input("Qty on Order: ") or 0)
        reorder = int(input("Reorder Level: ") or 5)
    except ValueError:
        qty_hand = qty_order = 0; reorder = 5
    
    with open(INV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([asset_id, category, "Manual Add", model, "N/A", "Available", "Warehouse", qty_hand, qty_order, reorder])
    log_transaction(asset_id, "ADD_ASSET", f"Added {model}")
    print(f"✅ Registered: {asset_id}")

def bulk_populate():
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
        
        qty_input = input(f"How many {model} units on hand? ")
        try:
            qty = int(qty_input)
        except ValueError:
            print("❌ Invalid number. Skipping.")
            continue
            
        asset_id = generate_id(category)
        with open(INV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([asset_id, category, "Initial Load", model, "N/A", "Available", "Warehouse", qty, 0, 2])
        
        log_transaction(asset_id, "BULK_POPULATE", f"Initial setup: {qty} x {model}")
        print(f"✅ Saved: {asset_id} | {model} | Qty: {qty}")

def receive_shipment():
    print("\n[ COMMAND: RECEIVE SHIPMENT ]")
    target_id = input("Enter Asset ID: ").upper()
    updated_rows = []
    found = False
    with open(INV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['ID'] == target_id:
                found = True
                try:
                    received = int(input(f"How many {row['Model']} units arrived? ") or 0)
                    row['Qty_On_Hand'] = str(int(row['Qty_On_Hand']) + received)
                    row['Qty_On_Order'] = str(max(0, int(row['Qty_On_Order']) - received))
                    log_transaction(target_id, "RECEIVE", f"Received {received}")
                except ValueError:
                    print("❌ Invalid entry.")
            updated_rows.append(row)
    if found:
        with open(INV_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader(); writer.writerows(updated_rows)
        print("✅ Inventory Updated.")
    else:
        print("❌ ID not found.")

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
        if choice == '1': add_asset()
        elif choice == '2': receive_shipment()
        elif choice == '3': bulk_populate()
        elif choice == '4':
            if os.path.exists(INV_FILE):
                with open(INV_FILE, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if int(row['Qty_On_Hand']) <= int(row['Reorder_Level']):
                            print(f"⚠️ LOW STOCK: {row['Model']} ({row['Qty_On_Hand']} units)")
        elif choice == '5':
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    for line in f.readlines()[-10:]: print(line.strip())
        elif choice == '6': break

if __name__ == '__main__':
    main_menu()