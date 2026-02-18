import csv
import os
import random
import string
from datetime import datetime

INV_FILE = "bull_inventory.csv"
LOG_FILE = "inventory_log.csv"

def initialize_inventory():
    """Initializes the inventory and logging files with headers if they don't exist."""
    # Initialize Inventory File
    if not os.path.exists(INV_FILE):
        with open(INV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "ID", "Category", "Type", "Model", "Serial_Number", 
                "Status", "Location", "Qty_On_Hand", "Qty_On_Order", "Reorder_Level"
            ])
        print("--- Bull Inventory System Initialized ---")
    
    # Initialize Log File
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Asset_ID", "Action", "Details"])

def log_transaction(asset_id, action, details):
    """Records every change made to the inventory."""
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
    cat_input = input("Category: ").upper()
    category = "Machine" if cat_input == 'M' else "Attachment" if cat_input == 'A' else "Parts"
    
    asset_id = generate_id(category)
    asset_type = input("Type: ")
    model = input("Model: ")
    serial = input("Serial Number: ")
    status = "Available"
    location = "Warehouse"
    
    print("\n--- Inventory Levels ---")
    try:
        qty_hand = int(input("Number on Hand: ") or 0)
        qty_order = int(input("Number Ordered/Enroute: ") or 0)
        reorder_point = int(input("Reorder Level: ") or 0)
    except ValueError:
        print("⚠️ Invalid number. Defaulting to 0.")
        qty_hand = qty_order = reorder_point = 0

    with open(INV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            asset_id, category, asset_type, model, serial, 
            status, location, qty_hand, qty_order, reorder_point
        ])
    
    log_transaction(asset_id, "ADD_ASSET", f"Registered {model} (Qty: {qty_hand})")
    print(f"\n✅ ASSET REGISTERED: {asset_id}")

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
                    received = int(input(f"How many units of {row['Model']} received? ") or 0)
                    old_hand = int(row['Qty_On_Hand'])
                    old_order = int(row['Qty_On_Order'])
                    
                    row['Qty_On_Hand'] = str(old_hand +
