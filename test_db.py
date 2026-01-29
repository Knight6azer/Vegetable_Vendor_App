from vegetable_database import VegetableDatabase
import os
import json

def test_persistence():
    # remove json if exists to start fresh
    if os.path.exists("inventory_data.json"):
        os.remove("inventory_data.json")
    
    # 1. Init DB (should load default)
    db = VegetableDatabase()
    potato_stock = db.get_vegetable_by_name("Potato")["stock"]
    print(f"Initial Potato Stock: {potato_stock}")
    
    # 2. Update Stock (should save)
    db.update_stock("Potato", 5.0)
    print("Sold 5.0kg Potato")
    
    # 3. Verify file exists
    if os.path.exists("inventory_data.json"):
        print("inventory_data.json created.")
        with open("inventory_data.json") as f:
            data = json.load(f)
            saved_stock = data["Ground"]["Potato"]["stock"]
            print(f"Saved Potato Stock in JSON: {saved_stock}")
            assert saved_stock == potato_stock - 5.0, "Saved stock mismatch!"
    else:
        print("ERROR: inventory_data.json NOT created!")
        return

    # 4. Reload DB (should load from file)
    db2 = VegetableDatabase()
    reloaded_stock = db2.get_vegetable_by_name("Potato")["stock"]
    print(f"Reloaded Potato Stock: {reloaded_stock}")
    
    assert reloaded_stock == potato_stock - 5.0, "Reloaded stock mismatch!"
    
    print("Persistence Test PASSED!")

if __name__ == "__main__":
    test_persistence()
