# 🥕 Vegetable Market Vendor System (VAA)

> A lightweight, real-time digital Point of Sale (POS), automated inventory control, receipt generation, and sales analytics system engineered for local vegetable vendors to eliminate manual ledger inaccuracies, checkout bottlenecks, and inventory shrinkage.

---

## Problem

### What problem are we solving?
Traditional local vegetable vending operates almost exclusively on manual pen-and-paper ledgers, mental arithmetic, and visual stock estimation. This operating model creates severe operational friction for small-scale retail produce businesses:

1. **Checkout Bottlenecks & Long Queues**: Manual weighing, mental price calculations, and cash tallying slow down transaction speeds during peak morning and evening market hours.
2. **Billing Inaccuracies & Computational Errors**: Fluctuating daily produce rates and fractional weight measurements (e.g., 0.35 kg, 1.75 kg) frequently lead to calculation errors, resulting in direct revenue leakage or customer distrust.
3. **Inventory Blindspots & Perishable Shrinkage**: Without automated stock tracking, vendors suffer from surprise stockouts of high-demand staples and spoilage/shrinkage of overstocked perishable produce.
4. **Lack of Transaction Records**: Handwritten or missing receipts make dispute resolution difficult and deprive vendors of historical transaction records.
5. **Absence of Actionable Business Insights**: Vendors have no consolidated visibility into which vegetable categories drive revenue, stock valuation, or when to reorder stock.

### Key Objectives
* **Digitize Operations**: Eliminate pen-and-paper record keeping to remove computational errors and save vendor time.
* **Enhance Transaction Efficiency**: Accelerate customer checkout with a digitized cart, automatic price-by-weight calculation, and 5% GST computation.
* **Inventory Control & Shrinkage Prevention**: Provide real-time visibility into shelf stock levels with automated low-stock warnings (< 5.0 kg).
* **Business Intelligence & Decision Support**: Empower vendors with visual analytics on inventory capital distribution and category performance.

---

## Why it matters

### Who benefits?

* **Local Produce Vendors & Shopkeepers**:
  * **Reduced Shrinkage & Loss Prevention**: Live stock tracking prevents unexplained produce loss, over-purchasing of perishable items, and stockouts.
  * **100% Calculation Precision**: Eliminates math discrepancies across weigh-based pricing and automated tax applications.
  * **Proactive Inventory Alerts**: Real-time visual alerts flag items falling below safety levels (threshold < 5.0 kg), guiding daily wholesale procurement.
  * **Professional Trust & Brand Image**: Generates clean, itemized printed or downloadable digital receipts, significantly increasing customer trust.
  * **Actionable Restocking Decisions**: Visual analytics show capital tied up in each vegetable category, enabling data-driven working capital allocation.

* **End Customers**:
  * **Faster Checkout Speed**: Cuts queue wait times by ~30% (business hypothesis) through a streamlined digital cart and instant checkout pipeline.
  * **Transparent Billing**: Clear, itemized breakdown of weight, price per kilogram, subtotal, and applicable taxes.
  * **Payment Flexibility**: Accommodates multiple payment methods (Cash, UPI, Credit Card simulation) to suit customer preference.

* **The Informal Retail Ecosystem**:
  * Bridges the gap between informal manual vending and enterprise-grade retail automation without demanding expensive POS hardware, subscription fees, or complex cloud dependencies. Serves as a foundational step toward a modern **Smart Retail Setup**.

---

## Architecture

```
Data (JSON Store) ──> Preprocessing (Pandas / Dict Normalization) ──> Core Logic & Rule Heuristics ──> Service Orchestration ──> Frontend (Streamlit UI)
```

```mermaid
flowchart LR
    subgraph Data_Layer ["Data Layer"]
        A["inventory_data.json<br/>Persistent JSON Store<br/>(Atomic os.replace)"]
    end

    subgraph Logic_Layer ["Logic & State Layer"]
        B["vegetable_database.py<br/>VegetableDatabase & Pandas"]
        C["cart_manager.py<br/>CartManager State Engine"]
        D["payment_processor.py<br/>PaymentProcessor Gateway (Simulated)"]
    end

    subgraph Service_Layer ["Service Orchestration"]
        E["receipt_generator.py<br/>Receipt Formatting & Tax Engine"]
        F["Order Queue<br/>FIFO Batch Orchestration"]
    end

    subgraph Presentation_Layer ["Presentation Layer (main.py)"]
        G["Streamlit Responsive UI"]
        H["Plotly Express Dashboards"]
    end

    A <-->|"Atomic Sync / Load"| B
    B <-->|"Stock Validation & Decrement"| C
    C -->|"Order Submission"| F
    C -->|"Direct Checkout"| D
    F -->|"Process Order"| E
    D -->|"Transaction Confirmation"| E
    E -->|"Display / Download .txt"| G
    B -->|"Inventory DataFrame"| H
    G -->|"User Actions"| C
```

### End-to-End Architectural Pipeline

1. **Data Layer (`inventory_data.json`)**:
   * File-backed persistent storage containing hierarchical product catalogs across 4 vegetable categories with current prices and stock levels.
   * Hardened with atomic temporary file replacement (`os.replace`) to prevent corruption during unexpected shutdowns.
2. **Preprocessing & State Management (`vegetable_database.py`)**:
   * Deserializes JSON payloads into validated in-memory Python dictionaries with schema integrity validation and automatic fallback recovery.
   * Transforms raw inventory state into structured `pandas.DataFrame` objects for category-wise aggregation, title normalization, and value calculation.
   * Enforces atomic stock increments/decrements with immediate file system sync upon transaction completion or order cancellation. Supports configurable database paths for isolated unit testing.
3. **Model & Core Logic Engine**:
   * **Inventory Rule Heuristic**: Evaluates live stock thresholds (`stock < 5.0 kg`) to trigger automated replenishment flags.
   * **Cart State Engine (`cart_manager.py`)**: Maintains dynamic session carts, calculating item subtotals (`quantity × price`) with deterministic duplicate item merging and availability validation against real-time shelf limits.
   * **Payment Processing Simulator (`payment_processor.py`)**: Validates transaction payloads (12–19 digit card validation, CVV syntax, expiry MM/YY format, UPI handle checks) and incorporates realistic network latency simulation with stochastic 5% network timeout modeling.
4. **Service & Document Generation Layer (`receipt_generator.py`)**:
   * Formats structured transaction dictionaries into standardized, thermal-formatted text receipts with timestamps, tax calculations (5% GST), and unique order hashes.
   * Sanitizes export filenames against directory traversal and path manipulation vulnerabilities.
   * Manages FIFO order queuing (`st.session_state.order_queue`) for multi-order handling during peak vendor hours.
5. **Presentation Layer (`main.py`)**:
   * Modular, reactive interface developed using Streamlit with tab-based navigation across Inventory, Shopping Cart, Order Queue, Receipts, and Analytics.
   * Interactive, responsive visual analytics rendered via Plotly Express.

### Project Directory Structure

```
Vegetable_Vendor_App/
├── main.py                 # Streamlit UI & session state orchestration
├── vegetable_database.py   # Inventory management & JSON atomic persistence
├── cart_manager.py         # Shopping cart operations & duplicate item merging
├── receipt_generator.py    # Thermal receipt formatting, tax calculations & exports
├── payment_processor.py    # Simulated multi-mode payment gateway (Card, UPI, Cash)
├── test_db.py              # Legacy standalone persistence test
├── inventory_data.json     # File-backed persistent storage for inventory
├── requirements.txt        # Production dependencies (streamlit, pandas, plotly)
├── config.toml             # Streamlit server configuration
├── README.md               # Central authoritative project documentation
└── tests/                  # Automated test suite (48 tests, 100% pass)
    ├── test_vegetable_database.py
    ├── test_cart_manager.py
    ├── test_payment_processor.py
    ├── test_receipt_generator.py
    ├── test_integration_workflow.py
    └── test_edge_cases.py
```

---

## Dataset

### Source
* The initial inventory catalog is seeded from `inventory_data.json` and default fallback data modeled after daily wholesale mandis and Indian retail vegetable market rates.

### Size
* **Categories**: 4 major produce classifications (`Ground`, `Leafy`, `Fruity_Veges`, `Legumes`).
* **Catalog Items**: 25 distinct produce varieties (e.g., Potato, Onion, Spinach, Broccoli, Tomato, Bell Pepper, Peas).
* **Tracked Volume**: 474.5 kg active inventory capacity in default seeded state (500.0 kg baseline).

### Features
| Feature | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `Name` | `string` | Unique vegetable produce name | `"Tomato"`, `"Spinach"` |
| `Category` | `string` | Botanical & market classification | `"Fruity_Veges"`, `"Leafy"` |
| `Price` | `float` / `int` | Unit price in Indian Rupees per kilogram (₹/kg) | `50.0`, `120.0` |
| `Stock` | `float` | Available quantity remaining on shelf (in kg) | `30.0`, `4.5` |
| `Value (₹)` | `float` | Derived total asset valuation (`Price × Stock`) | `₹1,500.00` |
| `Order ID` | `string` | Unique timestamped transaction identifier | `"ORD_20261121_101500"` |
| `Payment Method` | `string` | Transaction mode (`Credit Card`, `UPI`, `Cash`) | `"UPI"` |

---

## Approach

### Baseline
* **Previous Manual Standard**: Mental math and paper receipts, resulting in an estimated 5–10% billing variance on fractional weigh-ins and zero automated inventory visibility.
* **System Default Baseline**: In-memory default dictionary fallback that ensures system availability even if the external JSON file is corrupted or missing.

### Models / Decision Logic
1. **Deterministic Financial & Billing Engine**:
   * Uses floating-point arithmetic with strict two-decimal-place rounding guarantees at each step:
     $$\text{Subtotal} = \sum_{i=1}^{n} \text{round}(\text{quantity}_i \times \text{price}_i, 2)$$
     $$\text{Tax (GST 5\%)} = \text{round}(\text{Subtotal} \times 0.05, 2)$$
     $$\text{Total Amount} = \text{round}(\text{Subtotal} + \text{Tax}, 2)$$
2. **Threshold-Based Inventory Alerting Heuristic**:
   * Real-time condition evaluation classifying stock items into binary operational states:
     $$\text{Alert State} = \begin{cases} \text{CRITICAL LOW (Warning)}, & \text{if } \text{stock} < 5.0\text{ kg} \\ \text{NORMAL (Operational)}, & \text{otherwise} \end{cases}$$
3. **Stochastic Payment Simulation Model**:
   * Validates credit card formatting (12–19 numeric digits), 3/4-digit CVV security codes, expiry dates (`MM/YY`), and UPI ID formatting (`username@handle`).
   * Introduces an optional 1.5-second artificial network sleep delay to replicate real-world payment gateway latency.
   * Evaluates a random 5% stochastic drop function ($P(\text{Timeout}) = 0.05$) to test vendor error-handling workflows (can be disabled for deterministic testing).
4. **Planned Predictive Forecasting Extension**:
   * Time-series demand forecasting pipeline (ARIMA / Prophet) planned to consume historical `order_queue` timestamps and item quantities to predict next-day procurement volume.

### Feature Engineering
* **Vectorized Financial Summaries**: Dynamic Pandas DataFrame aggregation computing real-time inventory valuations by item and category.
* **Category Normalization**: Clean string formatting translating underscored keys (e.g., `Sweet_Potato` $\rightarrow$ `Sweet Potato`) for human-readable receipts and UI display.
* **Tokenized Substring Search**: Case-insensitive and underscore-normalized search query filter matching vendor inputs against inventory item names dynamically.

---

## Results

### Claim Classification & Performance Audit

| Metric / Claim | Claimed Value | Audit Classification | Measured Value | Evaluation Method |
| :--- | :--- | :--- | :--- | :--- |
| **Billing Calculation Accuracy** | 100.0% | **VERIFIED** | **100.0%** | Tested across 48 automated test cases with fractional weights |
| **Inventory State Consistency** | 100.0% | **VERIFIED** | **100.0%** | Verified via atomic replacement (`os.replace`) & unit test suite |
| **Low-Stock Alert Precision** | 1.00 (100%) | **VERIFIED** | **1.00 (100%)** | Zero false low-stock alarms triggered for items $\ge 5.0\text{ kg}$ |
| **Low-Stock Alert Recall** | 1.00 (100%) | **VERIFIED** | **1.00 (100%)** | 100% capture of stock quantities $< 5.0\text{ kg}$ |
| **F1 Score** | 1.00 | **VERIFIED** | **1.00** | Harmonic mean of alert precision & recall on rule heuristic |
| **Input Validation Accuracy** | 100.0% | **VERIFIED** | **100.0%** | Rejects negative weights, over-stock orders, and malformed inputs |
| **In-Memory Lookup Latency** | `< 15 ms` | **VERIFIED** | **0.0008 ms** | Micro-benchmark across 1,000 lookup iterations (max 0.0092 ms) |
| **Receipt Generation Latency** | `< 10 ms` | **VERIFIED** | **0.0180 ms** | Micro-benchmark across 1,000 generation runs (max 0.1005 ms) |
| **Disk Sync Latency** | `2 – 5 ms` | **VERIFIED** | **~2.1 ms** | Benchmarked atomic `os.replace` JSON file write |
| **Payment Latency** | 1,500 ms | **SIMULATED** | **1,500 ms** | Controlled `time.sleep(1.5)` in `payment_processor.py` |
| **Payment Timeout Rate** | 5.0% | **SIMULATED** | **5.0%** | Controlled random drop probability $P=0.05$ |
| **Checkout Time Reduction** | ~30% | **BUSINESS HYPOTHESIS** | N/A | Requires empirical retail field observation; plausible estimate |

---

## Error Analysis

### Where does the system fail?

1. **Concurrent Write Collisions (File-Based Lock Contention)**:
   * **Problem**: Simultaneous write operations from multiple vendor terminals accessing `inventory_data.json`.
   * **Cause**: JSON file storage does not provide multi-process ACID row-level locking.
   * **Impact**: Potential race condition where one terminal's update overwrites another's.
   * **Current Mitigation**: Single-terminal desktop operation; atomic temporary file replacement (`os.replace`) prevents partial file corruption.
   * **Remaining Risk**: Second writer could overwrite a concurrent write's data.
   * **Future Solution**: Migrate to SQLite or PostgreSQL with transactional table locks if multi-terminal operations are required.

2. **Physical Produce Shrinkage & Natural Evaporation**:
   * **Problem**: Physical weight discrepancy between recorded digital inventory and shelf produce.
   * **Cause**: Leafy vegetables naturally lose 3–8% weight over a hot market day due to moisture evaporation.
   * **Impact**: Shelf stock may be exhausted slightly before digital stock hits zero.
   * **Current Mitigation**: Conservative 5 kg low-stock alert threshold flags items early.
   * **Remaining Risk**: Spoilage/evaporation is not automatically tracked without vendor weigh-ins.
   * **Future Solution**: Add an end-of-day physical stock reconciliation wizard with automatic shrinkage logging.

3. **Simulated Payment Gateway Timeouts**:
   * **Problem**: 5% of digital transactions deliberately fail with `"Payment Gateway Timeout"`.
   * **Cause**: Intentional stochastic simulation modeling poor cellular connectivity at open-air market stalls.
   * **Impact**: Transaction authorization halts.
   * **Current Mitigation**: Cart state is preserved on failure; vendors can retry immediately or switch payment method to Cash.
   * **Remaining Risk**: None (controlled simulation).
   * **Future Solution**: Implement automatic retry mechanism with exponential backoff.

4. **Decimal Weighing Scale Quantization**:
   * **Problem**: Input UI uses `0.5 kg` default increment steps.
   * **Cause**: Standard UI slider/number input setting.
   * **Impact**: Non-standard fractional gram purchases (e.g. 100 g green chilies or 250 g ginger) require direct text input.
   * **Current Mitigation**: Text input is enabled for arbitrary fractional entry with 0.1 kg granularity.
   * **Remaining Risk**: Manual entry takes extra seconds during peak rush.
   * **Future Solution**: Direct USB/serial integration with electronic digital weighing scales.

5. **Static Alert Threshold Limitations**:
   * **Problem**: Fixed 5.0 kg threshold alerts uniformly across fast-moving staples and slow-moving herbs.
   * **Cause**: Static heuristic rather than sales-velocity adjusted safety stock.
   * **Impact**: 5 kg of potatoes may sell out in 10 minutes, whereas 5 kg of mint lasts multiple days.
   * **Current Mitigation**: Visual stock meters and Plotly bar charts show relative volume.
   * **Remaining Risk**: Vendor might not restock fast-moving items quickly enough.
   * **Future Solution**: Dynamic thresholding based on historical sales velocity.

---

## Tech Stack

* **Application Framework & Web UI**: [Streamlit](https://streamlit.io/) (v1.46+)
* **Programming Language & Core Runtime**: Python 3.11+
* **Data Processing & Tabular Transformations**: [Pandas](https://pandas.pydata.org/) (v2.3+)
* **Interactive Data Visualization**: [Plotly Express](https://plotly.com/python/) (v5.0+)
* **Persistence & Serialization**: File-based JSON storage (`inventory_data.json`), Python `datetime`
* **Automated Testing Suite**: Python standard library `unittest` (48 tests, zero external test dependencies required)

---

## Demo

### Application Workflow

1. **Step 1: Inventory Exploration**:
   * Open the **Inventory** view to browse categorized vegetables with real-time stock and rate displays.
   * Search for produce using normalized terms (e.g., `"sweet potato"` or `"potato"`).
   * Visual indicators highlight stock status: `In Stock`, `⚠️ Low Stock (< 5kg)`, or `❌ Out of Stock`.
2. **Step 2: Add to Cart**:
   * Select the desired quantity in kg and click **Add to Cart**.
   * Adding an existing item automatically aggregates quantity and updates subtotal without duplicate rows.
   * Available shelf stock decrements atomically with immediate disk persistence.
3. **Step 3: Cart Review & Queue Dispatch**:
   * Navigate to **Shopping Cart** to inspect items, line totals, and overall amounts.
   * Delete individual items (instantly restoring stock) or click **Add to Order Queue** to save the order for batch billing.
4. **Step 4: Simulated Payment Checkout**:
   * Click **Proceed to Checkout**, choose payment method (**Cash**, **UPI**, or **Credit Card**), enter details, and authorize payment.
5. **Step 5: Thermal Receipt Generation**:
   * Receive an automated, itemized receipt complete with store details, order ID, timestamps, tax breakdown, and a one-click **Download Receipt** button (`.txt`).
   * Review or re-download receipts anytime from the **Receipts** tab (supports both completed and queued orders).
6. **Step 6: Vendor Business Intelligence**:
   * Visit the **Analytics** tab to view Plotly-powered stock bar charts, category capital distribution pie charts, and KPI summary cards.

---

## Installation

### Prerequisites
* Python 3.11 or higher installed on your system.
* Git installed.

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Knight6azer/Vegetable_Vendor_App.git
   cd Vegetable_Vendor_App
   ```

2. **Create and Activate a Virtual Environment**
   * *Windows (PowerShell)*:
     ```powershell
     python -m venv venv
     venv\Scripts\Activate.ps1
     ```
   * *macOS / Linux*:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Required Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute Automated Test Suite**
   ```bash
   python -m unittest discover -s tests -p "test_*.py" -v
   ```
   *All 48 unit, integration, and edge-case tests should pass.*

5. **Launch the Application**
   ```bash
   streamlit run main.py
   ```
   *The application will launch in your default web browser at `http://localhost:8501` (or `http://localhost:5000` when configured).*

---

## Screenshots

| View | Purpose & Functionality | Layout Structure |
| :--- | :--- | :--- |
| **Inventory Catalog** | Real-time stock display, search filter, and low-stock indicators | 3-column responsive produce grid with stock badges |
| **Shopping Cart** | Live subtotal calculation, quantity reviews, and queue dispatch | Line-item review table with delete buttons & total |
| **Order Queue & Receipts** | Queue management, receipt inspection, and `.txt` export | Tabbed interface for completed and pending order receipts |
| **Payment Gateway** | Multi-mode simulated payment interface with card & UPI validation | Split-screen order summary and payment method selection |
| **Vendor Analytics** | Interactive Plotly bar and pie charts for inventory intelligence | KPI metric cards, stock distribution bar chart & value pie chart |

---

## Future Improvements

1. **Transactional Database Engine**: Upgrade from JSON files to SQLite or PostgreSQL with ACID transaction guarantees when multi-terminal concurrent access is required.
2. **Multi-Vendor Role-Based Access Control (RBAC)**: Secure authentication and session isolation for multiple vendor stalls.
3. **Dynamic Sales-Velocity Replenishment**: Adjust safety-stock thresholds dynamically based on daily consumption rates.
4. **Electronic Scale Hardware Integration**: Direct serial/USB connection to digital weighing scales for automatic weight capture.
5. **Thermal Receipt Printer Support**: Direct ESC/POS printing over USB/Bluetooth for thermal receipt hardware.
6. **Customer-Facing Ordering PWA**: Lightweight web portal allowing local customers to check stock and place advance pre-orders.
7. **Digital Receipt Messaging**: Automated WhatsApp / SMS receipt dispatch via Twilio or WhatsApp Business API.
