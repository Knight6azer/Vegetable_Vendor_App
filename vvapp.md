# Vegetable Market Vendor System

## Overview
A Streamlit-based POS and analytics suite for vegetable vendors. Manage inventory, build shopping carts, simulate payments, queue orders, generate receipts, and inspect stock analytics. The main entry point is `main.py` and the core modules are small, modular, and focused.

## Project Structure
- `main.py`: Streamlit UI and session state orchestration
- `vegetable_database.py`: Inventory management and JSON file-backed persistence
- `cart_manager.py`: Shopping cart operations and item summaries
- `receipt_generator.py`: Receipt formatting, tax calculations, and file exports
- `payment_processor.py`: Simulated multi-mode payment gateway (Card, UPI, Cash)
- `inventory_data.json`: File-backed persistent storage for inventory
- `test_db.py`: Persistence test suite for inventory verification
- `config.toml`: Optional Streamlit server config

## Run Locally
- Install Python 3.11+
- Install deps: `pip install -r requirements.txt`
- Start: `streamlit run main.py`

## How It Works
- Inventory loaded and synced via `VegetableDatabase` with atomic updates to `inventory_data.json`
- Items added to cart via `CartManager.add_item()` with immediate stock decrement
- Orders queued in `st.session_state.order_queue`
- Receipts created via `ReceiptGenerator.generate_receipt(order)` and offered for download
- Analytics rendered via Plotly Express for stock levels and category valuations
- Payments simulated via `PaymentProcessor` supporting multi-mode checkout

## Clean Up
The app does not rely on Replit or IDE-specific files. You can remove these safely:
- `.idea/`, `__pycache__/`
- `vvapp.toml`, `vvapp.lock`, `user.xml`
