import csv
    import os
    import random
    import string
    
    INV_FILE = "bull_inventory.csv"
    
    def initialize_inventory():
        if not os.path.exists(INV_FILE):
            with open(INV_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Category", "Type", "Model", "Serial_Number", "Status", "Location"])
            print("--- Bull Inventory System Initialized ---")
    
    def generate_id(category):
        # Creates a placeholder ID like M-XXXX (Machine) or A-XXXX (Attachment)
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
    
        with open(INV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([asset_id, category, asset_type, model, serial, status, location])
        
        print(f"\n✅ ASSET REGISTERED: {asset_id} | {model}")
        print(f"PLACEHOLDER QR LINK: https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={asset_id}")
    
    def main_menu():
        initialize_inventory()
        while True:
            print("\n--- BULL EQUIPMENT INVENTORY ---")
            print("1. Add Asset (Machine/Attachment)")
            print("2. Search Inventory")
            print("3. Exit")
            choice = input("Select Option: ")
            if choice == '1': add_asset()
            elif choice == '3': break
    
    if __name__ == "__main__":
        main_menu()
    
