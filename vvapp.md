# Vegetable Market Vendor System

## Overview
A Streamlit-based POS for vegetable vendors. Manage inventory, build carts, queue orders, and generate receipts. The main entry point is `main.py` and the core modules are small and focused.

## Project Structure
- `main.py`: Streamlit UI and session state orchestration
- `vegetable_database.py`: In-memory inventory with categories and stock updates
- `cart_manager.py`: Cart operations and summaries
- `receipt_generator.py`: Receipt formatting and totals
- `config.toml`: Optional Streamlit server config

## Run Locally
- Install Python 3.11+
- Install deps: `pip install streamlit pandas`
- Start: `streamlit run main.py`

## How It Works
- Inventory shown from `VegetableDatabase.get_all_vegetables()`
- Items added to cart via `CartManager.add_item()` and stock decremented
- Orders queued in `st.session_state.order_queue`
- Receipts created via `ReceiptGenerator.generate_receipt(order)` and offered for download

## Clean Up
The app does not rely on Replit or IDE-specific files. You can remove these safely:
- `.idea/`, `__pycache__/`
- `vvapp.toml`, `vvapp.lock`, `user.xml`

## Notes
- No changes were made to `main.py` logic
- Data is in-memory; restart clears state
- Consider a database if persistence is required