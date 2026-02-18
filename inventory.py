import csv
    import os
    
    INV_FILE = "bull_inventory.csv"
    
    # Category Definitions
    # MACHINES: Skid Steers, Excavators, Telehandlers
    # ATTACHMENTS: Buckets, Grapples, Augers, Pallet Forks
    # PARTS: Filters, Seals, Teeth, Fluids
    
    def initialize_inventory():
        if not os.path.exists(INV_FILE):
            with open(INV_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Category", "Type", "Model", "Serial_Number", "Status", "Location"])
            print("--- Bull Inventory System Initialized ---")
    
    def main_menu():
        initialize_inventory()
        while True:
            print("
--- BULL EQUIPMENT INVENTORY ---")
            print("1. Add Asset (Machine/Attachment)")
            print("2. Search Inventory")
            print("3. Exit")
            choice = input("Select Option: ")
            if choice == '3': break
    
    if __name__ == "__main__":
        main_menu()
    
