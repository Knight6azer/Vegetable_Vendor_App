from vegetable_database import VegetableDatabase
import os
import json

TEST_DB_FILE = "test_inventory_data.json"

def test_persistence():
    # remove test json if exists to start fresh
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    
    try:
        # 1. Init DB (should load default)
        db = VegetableDatabase(db_file=TEST_DB_FILE)
        potato_stock = db.get_vegetable_by_name("Potato")["stock"]
        print(f"Initial Potato Stock: {potato_stock}")
        
        # 2. Update Stock (should save)
        db.update_stock("Potato", 5.0)
        print("Sold 5.0kg Potato")
        
        # 3. Verify file exists
        if os.path.exists(TEST_DB_FILE):
            print(f"{TEST_DB_FILE} created.")
            with open(TEST_DB_FILE) as f:
                data = json.load(f)
                saved_stock = data["Ground"]["Potato"]["stock"]
                print(f"Saved Potato Stock in JSON: {saved_stock}")
                assert saved_stock == potato_stock - 5.0, "Saved stock mismatch!"
        else:
            print(f"ERROR: {TEST_DB_FILE} NOT created!")
            return

        # 4. Reload DB (should load from file)
        db2 = VegetableDatabase(db_file=TEST_DB_FILE)
        reloaded_stock = db2.get_vegetable_by_name("Potato")["stock"]
        print(f"Reloaded Potato Stock: {reloaded_stock}")
        
        assert reloaded_stock == potato_stock - 5.0, "Reloaded stock mismatch!"
        
        print("Persistence Test PASSED!")
    finally:
        # Clean up test file to keep workspace clean
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)

if __name__ == "__main__":
    test_persistence()
