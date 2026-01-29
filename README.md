# 🥕 Vegetable Market Vendor System

A comprehensive, Streamlit-based application designed to modernize vegetable vending operations. This system streamlines inventory management, billing, and sales analytics, providing a seamless experience for both vendors and customers.

## 🚀 Features

### 📦 Smart Inventory Management
-   **Real-time Stock Tracking**: Monitor vegetable stock levels instantly.
-   **Categorized Inventory**: Organized display of Ground, Leafy, Fruity, and Legume vegetables.
-   **Low Stock Alerts**: Visual indicators for items running low (below 5kg).
-   **Search Functionality**: Quick search to find specific vegetables.

### 🛒 Intuitive Shopping Cart
-   **Dynamic Cart**: Add, remove, or modify item quantities with ease.
-   **Live Calculations**: Automatic subtotal and total cost updates.
-   **Category Breakdown**: View items sorted by their types.

### 💳 Integrated Payment Gateway (Simulated)
-   **Multi-Mode Support**: Accepts Credit Cards, UPI, and Cash.
-   **Secure Verification**: Basic validation for card details and UPI IDs.
-   **Transaction Simulation**: Realistic processing delays and success/failure scenarios.

### 🧾 Automated Billing & Receipts
-   **Professional Receipts**: Generates detailed text-based receipts.
-   **Tax Calculation**: Automatically applies taxes (e.g., 5% GST).
-   **Downloadable Records**: Receipts can be downloaded as text files for record-keeping.
-   **Order Queue**: Manage multiple orders effectively with a queue system.

### 📈 Vendor Analytics
-   **Visual Dashboard**: Interactive charts powered by Plotly.
-   **Stock Insights**: Bar charts showing current stock vs. sales.
-   **Value Distribution**: Pie charts displaying inventory value by category.

## 🛠️ Technology Stack

-   **Frontend & Framework**: [Streamlit](https://streamlit.io/)
-   **Data Processing**: Python, Pandas
-   **Visualization**: Plotly Express
-   **Data Storage**: JSON (File-based persistence)

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Knight6azer/Vegetable_Vendor_App.git
    cd Vegetable_Vendor_App
    ```

2.  **Create a Virtual Environment (Optional but Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install streamlit pandas plotly
    ```

4.  **Run the Application**
    ```bash
    streamlit run main.py
    ```

## 📂 Project Structure

```
Vegetable_Vendor_App/
├── main.py                 # Application entry point and UI logic
├── vegetable_database.py   # Inventory management and data persistence
├── cart_manager.py         # Shopping cart operations
├── receipt_generator.py    # Receipt formatting and file generation
├── payment_processor.py    # Mock payment gateway logic
├── inventory_data.json     # Persistent storage for inventory
└── README.md               # Project documentation
```

## 🔮 Future Enhancements

-   [ ] **Authentication**: User login for multiple vendors.
-   [ ] **Database Integration**: Migrate from JSON to SQL/NoSQL for scalability.
-   [ ] **Customer App**: Separate interface for customers to pre-order.
-   [ ] **AI Forecasting**: Predict demand based on past sales using ML.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

## 📄 License

This project is open-source and available for educational and personal use.
