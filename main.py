import streamlit as st
import json
from datetime import datetime
from vegetable_database import VegetableDatabase
from cart_manager import CartManager
from receipt_generator import ReceiptGenerator
from payment_processor import PaymentProcessor
import plotly.express as px

if 'cart_manager' not in st.session_state:
    st.session_state.cart_manager = CartManager()

if 'vegetable_db' not in st.session_state:
    st.session_state.vegetable_db = VegetableDatabase()

if 'receipt_generator' not in st.session_state:
    st.session_state.receipt_generator = ReceiptGenerator()

if 'payment_processor' not in st.session_state:
    st.session_state.payment_processor = PaymentProcessor()

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'inventory'

if 'order_queue' not in st.session_state:
    st.session_state.order_queue = []


def main():
    st.set_page_config(
        page_title="Vegetable Market Vendor",
        page_icon="🥕",
        layout="wide"
    )

    st.title("🥕 Vegetable Market Vendor System")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📦 Inventory", use_container_width=True):
            st.session_state.current_page = 'inventory'
            st.rerun()

    with col2:
        if st.button("🛒 Shopping Cart", use_container_width=True):
            st.session_state.current_page = 'cart'
            st.rerun()

    with col3:
        if st.button("📋 Order Queue", use_container_width=True):
            st.session_state.current_page = 'queue'
            st.rerun()

    with col4:
        if st.button("📈 Analytics", use_container_width=True):
            st.session_state.current_page = 'analytics'
            st.rerun()

    st.markdown("---")

    if st.session_state.current_page == 'inventory':
        show_inventory_page()
    elif st.session_state.current_page == 'cart':
        show_cart_page()
    elif st.session_state.current_page == 'queue':
        show_queue_page()
    elif st.session_state.current_page == 'receipt':
        show_receipt_page()
    elif st.session_state.current_page == 'analytics':
        show_analytics_page()
    elif st.session_state.current_page == 'payment':
        show_payment_page()


def show_inventory_page():
    st.header("📦 Vegetable Inventory")
    
    # Search Bar
    search_term = st.text_input("🔍 Search for vegetables...", "")
    
    vegetables = st.session_state.vegetable_db.get_all_vegetables()
    
    for category, items in vegetables.items():
        # Filter logic
        filtered_items = {k:v for k,v in items.items() if search_term.lower() in k.lower()}
        
        if filtered_items:
            st.subheader(f"🥬 {category.title()} Vegetables")
            
            cols = st.columns(3)
            col_idx = 0
            
            for vegetable, details in filtered_items.items():
                with cols[col_idx % 3]:
                    st.write(f"**{vegetable}**")
                    st.write(f"Price: ₹{details['price']}/kg")
                    
                    # Low Stock Indicator
                    if details['stock'] < 5:
                        st.error(f"⚠️ Low Stock: {details['stock']} kg")
                    else:
                        st.write(f"Stock: {details['stock']} kg")
                    
                    quantity = st.number_input(
                        f"Quantity (kg)",
                        min_value=0.0,
                        max_value=float(details['stock']),
                        step=0.5,
                        key=f"qty_{vegetable}",
                        format="%.1f"
                    )
                    
                    if st.button(f"Add to Cart", key=f"add_{vegetable}"):
                        if quantity > 0:
                            success = st.session_state.cart_manager.add_item(
                                vegetable, quantity, details['price'], category
                            )
                            if success:
                                st.session_state.vegetable_db.update_stock(vegetable, quantity)
                                st.success(f"Added {quantity} kg of {vegetable} to cart!")
                                st.rerun()
                            else:
                                st.error("Failed to add item to cart!")
                        else:
                            st.warning("Please enter a valid quantity!")
                            
                    st.markdown("---")
                
                col_idx += 1


def show_cart_page():
    st.header("🛒 Shopping Cart")

    cart_items = st.session_state.cart_manager.get_cart_items()

    if not cart_items:
        st.info("Your cart is empty. Go to inventory to add items!")
        return

    total_amount = 0

    for item_id, item in cart_items.items():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])

        with col1:
            st.write(f"**{item['name']}**")
            st.write(f"Category: {item['category']}")

        with col2:
            st.write(f"₹{item['price']}/kg")

        with col3:
            st.write(f"{item['quantity']} kg")

        with col4:
            item_total = item['quantity'] * item['price']
            st.write(f"₹{item_total:.2f}")
            total_amount += item_total

        with col5:
            if st.button("🗑️", key=f"remove_{item_id}"):
                st.session_state.vegetable_db.return_stock(item['name'], item['quantity'])
                st.session_state.cart_manager.remove_item(item_id)
                st.success(f"Removed {item['name']} from cart!")
                st.rerun()

        st.markdown("---")

    st.subheader(f"Total Amount: ₹{total_amount:.2f}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Clear Cart", use_container_width=True):
            for item in cart_items.values():
                st.session_state.vegetable_db.return_stock(item['name'], item['quantity'])
            st.session_state.cart_manager.clear_cart()
            st.success("Cart cleared!")
            st.rerun()

    with col2:
        if st.button("Add to Order Queue", use_container_width=True):
            if cart_items:
                order = {
                    'order_id': f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'items': cart_items,
                    'total_amount': total_amount,
                    'timestamp': datetime.now().isoformat()
                }
                st.session_state.order_queue.append(order)
                st.session_state.cart_manager.clear_cart()
                st.success("Order added to queue!")
                st.rerun()

    with col3:
        if st.button("Proceed to Checkout", use_container_width=True):
            if cart_items:
                st.session_state.current_page = 'payment'
                st.rerun()


def show_queue_page():
    st.header("📋 Order Queue")

    if not st.session_state.order_queue:
        st.info("No orders in queue.")
        return

    st.write(f"**Orders in queue: {len(st.session_state.order_queue)}**")
    st.markdown("---")

    for idx, order in enumerate(st.session_state.order_queue):
        with st.expander(f"Order {order['order_id']} - ₹{order['total_amount']:.2f}"):
            st.write(f"**Timestamp:** {order['timestamp']}")
            st.write(f"**Total Amount:** ₹{order['total_amount']:.2f}")

            st.write("**Items:**")
            for item in order['items'].values():
                st.write(
                    f"- {item['name']}: {item['quantity']} kg × ₹{item['price']} = ₹{item['quantity'] * item['price']:.2f}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Process Order", key=f"process_{idx}"):
                    # Process (dequeue) the order
                    processed_order = st.session_state.order_queue.pop(0)
                    receipt = st.session_state.receipt_generator.generate_receipt(processed_order)

                    st.success("✅ Order processed successfully!")
                    st.markdown("### 🧾 Receipt")
                    st.text(receipt)

                    # Download receipt
                    st.download_button(
                        label="Download Receipt",
                        data=receipt,
                        file_name=f"receipt_{processed_order['order_id']}.txt",
                        mime="text/plain",
                        key=f"download_{idx}"
                    )
                    st.rerun()

            with col2:
                if st.button(f"Cancel Order", key=f"cancel_{idx}"):
                    # Return stock for cancelled order
                    cancelled_order = st.session_state.order_queue.pop(idx)
                    for item in cancelled_order['items'].values():
                        st.session_state.vegetable_db.return_stock(item['name'], item['quantity'])
                    st.warning("Order cancelled and stock returned.")
                    st.rerun()


def show_receipt_page():
    st.header("🧾 Receipt Generator")

    if not st.session_state.order_queue:
        st.info("No orders available for receipt generation.")
        return

    order_options = [f"{order['order_id']} - ₹{order['total_amount']:.2f}"
                     for order in st.session_state.order_queue]

    selected_order_idx = st.selectbox(
        "Select order for receipt generation:",
        range(len(order_options)),
        format_func=lambda x: order_options[x]
    )

    if st.button("Generate Receipt"):
        selected_order = st.session_state.order_queue[selected_order_idx]
        receipt = st.session_state.receipt_generator.generate_receipt(selected_order)

        st.markdown("### Generated Receipt")
        st.text(receipt)

        st.download_button(
            label="Download Receipt",
            data=receipt,
            file_name=f"receipt_{selected_order['order_id']}.txt",
            mime="text/plain"
        )


def show_analytics_page():
    st.header("📈 Vendor Analytics Dashboard")
    
    # 1. Inventory Levels Chart
    st.subheader("Current Stock Levels")
    inv_df = st.session_state.vegetable_db.get_inventory_summary()
    
    if not inv_df.empty:
        # Bar chart for stock
        fig_stock = px.bar(
            inv_df, 
            x="Name", 
            y="Stock (kg)", 
            color="Category",
            title="Stock remaining by Item"
        )
        st.plotly_chart(fig_stock, use_container_width=True)
        
        # Pie chart for Inventory Value
        fig_val = px.pie(
            inv_df, 
            values="Value (₹)", 
            names="Category", 
            title="Inventory Value Distribution"
        )
        st.plotly_chart(fig_val, use_container_width=True)
    else:
        st.warning("No inventory data available.")


def show_payment_page():
    st.header("💳 Payment Gateway")
    
    if st.button("🔙 Back to Cart"):
        st.session_state.current_page = 'cart'
        st.rerun()

    st.markdown("---")

    cart_items = st.session_state.cart_manager.get_cart_items()
    if not cart_items:
        st.error("Cart is empty!")
        st.session_state.current_page = 'inventory'
        st.rerun()
        return

    # Calculate Total
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items.values())

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Order Summary")
        for item in cart_items.values():
            st.write(f"• {item['name']} ({item['quantity']} kg) - ₹{item['price'] * item['quantity']:.2f}")
        
        st.markdown("### Total: ₹{:.2f}".format(total_amount))

    with col2:
        st.subheader("Payment Details")
        
        method = st.radio(
            "Select Payment Method",
            ["Credit Card", "UPI", "Cash"],
            key="payment_method"
        )
        
        payment_details = {}
        
        if method == "Credit Card":
            payment_details["card_number"] = st.text_input("Card Number (16 digits)", max_chars=16)
            payment_details["cvv"] = st.text_input("CVV (3 digits)", max_chars=3, type="password")
            payment_details["expiry"] = st.text_input("Expiry (MM/YY)")
            
        elif method == "UPI":
            payment_details["upi_id"] = st.text_input("UPI ID (e.g., user@bank)")
            
        elif method == "Cash":
            st.info("Please pay cash at the counter upon receipt.")

        st.markdown("---")
        
        if st.button(f"Pay ₹{total_amount:.2f}", use_container_width=True, type="primary"):
            with st.spinner("Processing Payment..."):
                success, message, txn_id = st.session_state.payment_processor.process_payment(
                    total_amount, method, payment_details
                )
                
                if success:
                    # Create the final order
                    order = {
                        'order_id': f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'items': cart_items,
                        'total_amount': total_amount,
                        'timestamp': datetime.now().isoformat(),
                        'payment_method': method,
                        'transaction_id': txn_id
                    }
                    
                    # Generate receipt
                    receipt = st.session_state.receipt_generator.generate_receipt(order)
                    
                    # Clear cart logic
                    st.session_state.cart_manager.clear_cart()
                    
                    # Show Success
                    st.success(f"Payment Successful! Transaction ID: {txn_id}")
                    st.balloons()
                    
                    st.markdown("### 🧾 Payment Receipt")
                    st.text(receipt)
                    
                    st.download_button(
                        label="Download Receipt",
                        data=receipt,
                        file_name=f"receipt_{order['order_id']}.txt",
                        mime="text/plain"
                    )
                    
                    if st.button("Start New Order"):
                        st.session_state.current_page = 'inventory'
                        st.rerun()
                        
                else:
                    st.error(f"Payment Failed: {message}")


if __name__ == "__main__":
    main()

