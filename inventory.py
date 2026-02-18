import csv
import os
import random
import string

INV_FILE = "bull_inventory.csv"

def initialize_inventory():
    if not os.path.exists(INV_FILE):
        with open(INV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "ID", "Category", "Type", "Model", "Serial_Number", 
                "Status", "Location", "Qty_On_Hand", "Qty_On_Order", "Reorder_Level"
            ])
        print("--- Bull Inventory System Initialized with Tracking ---")

def generate_id(category):
    prefix = category[0].upper()
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{suffix}"

def add_asset():
    print("\n[ COMMAND: REGISTER NEW ASSET ]")
    print("Categories: (M)achine, (A)ttachment, (P)arts")
    cat_input = input("Category: ").upper()
    category = "Machine" if cat_input == 'M' else "Attachment" if cat_input == 'A' else "Parts"
    
    asset_id = generate_id(category)
    asset_type = input("Type (e.g. Skid Steer, Bucket): ")
    model = input("Model: ")
    serial = input("Serial Number: ")
    status = "Available"
    location = "Warehouse"
    
    print("\n--- Inventory Levels ---")
    try:
        qty_hand = int(input("Number on Hand: ") or 0)
        qty_order = int(input("Number Ordered/Enroute: ") or 0)
        reorder_point = int(input("Reorder Level (Alert when at or below x): ") or 0)
    except ValueError:
        print("⚠️ Invalid number entered. Defaulting to 0.")
        qty_hand = qty_order = reorder_point = 0

    with open(INV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            asset_id, category, asset_type, model, serial, 
            status, location, qty_hand, qty_order, reorder_point
        ])
    
    print(f"\n✅ ASSET REGISTERED: {asset_id} | {model}")
    if qty_hand <= reorder_point:
        print(f"⚠️ ALERT: Stock is low ({qty_hand}/{reorder_point})")

def receive_shipment():
    print("\n[ COMMAND: RECEIVE SHIPMENT ]")
    target_id = input("Enter Asset ID being received: ").upper()
    updated_rows = []
    found = False

    if not os.path.exists(INV_FILE):
        print("No inventory found.")
        return

    with open(INV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['ID'] == target_id:
                found = True
                print(f"Current Stats for {row['Model']}:")
                print(f" - On Hand: {row['Qty_On_Hand']}")
                print(f" - Enroute: {row['Qty_On_Order']}")
                
                try:
                    received = int(input("\nHow many units received? ") or 0)
                    
                    # Update counts
                    current_hand = int(row['Qty_On_Hand'])
                    current_order = int(row['Qty_On_Order'])
                    
                    row['Qty_On_Hand'] = str(current_hand + received)
                    # Subtract from order, but don't go below zero
                    row['Qty_On_Order'] = str(max(0, current_order - received))
                    
                    print(f"✅ Updated {row['Model']}. New Total On Hand: {row['Qty_On_Hand']}")
                except ValueError:
                    print("⚠️ Invalid number. No changes made.")
            
            updated_rows.append(row)

    if found:
        with open(INV_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
    else:
        print("ID not found.")

def update_status():
    print("\n[ COMMAND: UPDATE ASSET ]")
    target_id = input("Enter Asset ID to update: ").upper()
    updated_rows = []
    found = False

    if not os.path.exists(INV_FILE):
        print("No inventory found.")
        return

    with open(INV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['ID'] == target_id:
                found = True
                print(f"Current: {row['Qty_On_Hand']} on hand | Status: {row['Status']}")
                
                new_status = input("New Status (Leave blank to keep current): ")
                new_loc = input("New Location (Leave blank to keep current): ")
                new_qty = input("New Quantity on Hand (Leave blank to keep current): ")

                if new_status: row['Status'] = new_status
                if new_loc: row['Location'] = new_loc
                if new_qty: row['Qty_On_Hand'] = new_qty
            
            updated_rows.append(row)

    if found:
        with open(INV_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        print("✅ Asset Updated.")
    else:
        print("ID not found.")

def view_low_stock_report():
    print("\n[ COMMAND: REORDER ALERT REPORT ]")
    found_low_stock = False
    if not os.path.exists(INV_FILE):
        print("No inventory found.")
        return

    with open(INV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        print(f"{'MODEL':<15} | {'ON HAND':<8} | {'REORDER AT':<10} | {'ENROUTE':<8}")
        print("-" * 50)
        for row in reader:
            if int(row['Qty_On_Hand']) <= int(row['Reorder_Level']):
                print(f"{row['Model']:<15} | {row['Qty_On_Hand']:<8} | {row['Reorder_Level']:<10} | {row['Qty_On_Order']:<8}")
                found_low_stock = True
    
    if not found_low_stock:
        print("✅ All stock levels are healthy.")

def view_inventory_report():
    print("\n[ COMMAND: FULL FLEET REPORT ]")
    if not os.path.exists(INV_FILE):
        print("No assets found.")
        return
    with open(INV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        print(f"{'ID':<8} | {'MODEL':<15} | {'STATUS':<12} | {'ON HAND':<8} | {'ENROUTE':<8}")
        print("-" * 65)
        for row in reader:
            print(f"{row['ID']:<8} | {row['Model']:<15} | {row['Status']:<12} | {row['Qty_On_Hand']:<8} | {row['Qty_On_Order']:<8}")

def main_menu():
    initialize_inventory()
    while True:
        print("\n--- BULL EQUIPMENT INVENTORY ---")
        print("1. Add Asset")
        print("2. Update Asset Status/Quantity")
        print("3. View Fleet Report")
        print("4. View Reorder Alerts (Low Stock)")
        print("5. Receive Shipment")
        print("6. Exit")
        choice = input("Select: ")
        if choice == '1':
            add_asset()
        elif choice == '2':
            update_status()
        elif choice == '3':
            view_inventory_report()
        elif choice == '4':
            view_low_stock_report()
        elif choice == '5':
            receive_shipment()
        elif choice == '6':
            break

if __name__ == '__main__':
    main_menu()



















