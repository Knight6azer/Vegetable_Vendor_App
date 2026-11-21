import streamlit as st
import json
import re
from datetime import datetime
from vegetable_database import VegetableDatabase
from cart_manager import CartManager
from receipt_generator import ReceiptGenerator
from payment_processor import PaymentProcessor
import plotly.express as px

# Initialize session state singletons and queues
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

if 'completed_orders' not in st.session_state:
    st.session_state.completed_orders = []


def main():
    st.set_page_config(
        page_title="Vegetable Market Vendor POS",
        page_icon="🥕",
        layout="wide"
    )

    st.title("🥕 Vegetable Market Vendor System")
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("📦 Inventory", use_container_width=True):
            st.session_state.current_page = 'inventory'
            st.rerun()

    with col2:
        cart_count = st.session_state.cart_manager.get_cart_count()
        cart_label = f"🛒 Cart ({cart_count})" if cart_count > 0 else "🛒 Shopping Cart"
        if st.button(cart_label, use_container_width=True):
            st.session_state.current_page = 'cart'
            st.rerun()

    with col3:
        queue_count = len(st.session_state.order_queue)
        queue_label = f"📋 Queue ({queue_count})" if queue_count > 0 else "📋 Order Queue"
        if st.button(queue_label, use_container_width=True):
            st.session_state.current_page = 'queue'
            st.rerun()

    with col4:
        if st.button("🧾 Receipts", use_container_width=True):
            st.session_state.current_page = 'receipt'
            st.rerun()

    with col5:
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

    search_term = st.text_input("🔍 Search vegetables (e.g. Potato, Tomato, Spinach)...", "")
    search_clean = search_term.strip().lower()

    vegetables = st.session_state.vegetable_db.get_all_vegetables()

    for category, items in vegetables.items():
        # Match against raw key or normalized produce name
        filtered_items = {}
        for veg_name, details in items.items():
            veg_clean = veg_name.replace("_", " ").lower()
            if not search_clean or search_clean in veg_name.lower() or search_clean in veg_clean:
                filtered_items[veg_name] = details

        if filtered_items:
            category_title = category.replace("_", " ").title()
            st.subheader(f"🥬 {category_title} Vegetables")

            cols = st.columns(3)
            col_idx = 0

            for vegetable, details in filtered_items.items():
                display_name = vegetable.replace("_", " ").title()
                stock_val = float(details["stock"])
                price_val = float(details["price"])

                with cols[col_idx % 3]:
                    st.write(f"**{display_name}**")
                    st.write(f"Price: ₹{price_val:.2f}/kg")

                    # Stock level badge
                    if stock_val <= 0.0:
                        st.error("❌ Out of Stock (0 kg)")
                        is_disabled = True
                    elif stock_val < 5.0:
                        st.warning(f"⚠️ Low Stock: {stock_val:.1f} kg")
                        is_disabled = False
                    else:
                        st.info(f"In Stock: {stock_val:.1f} kg")
                        is_disabled = False

                    quantity = st.number_input(
                        "Quantity (kg)",
                        min_value=0.0,
                        max_value=max(0.0, stock_val),
                        step=0.5,
                        key=f"qty_{vegetable}",
                        format="%.1f",
                        disabled=is_disabled
                    )

                    if st.button("Add to Cart", key=f"add_{vegetable}", disabled=is_disabled):
                        if quantity > 0:
                            if st.session_state.vegetable_db.check_availability(vegetable, quantity):
                                if st.session_state.vegetable_db.update_stock(vegetable, quantity):
                                    st.session_state.cart_manager.add_item(
                                        vegetable, quantity, price_val, category
                                    )
                                    st.success(f"Added {quantity:.1f} kg of {display_name} to cart!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update inventory stock!")
                            else:
                                st.error("Requested quantity exceeds available shelf stock!")
                        else:
                            st.warning("Please enter a quantity greater than 0 kg!")

                    st.markdown("---")

                col_idx += 1


def show_cart_page():
    st.header("🛒 Shopping Cart")

    cart_items = st.session_state.cart_manager.get_cart_items()

    if not cart_items:
        st.info("Your shopping cart is currently empty. Browse the Inventory to add produce!")
        return

    total_amount = st.session_state.cart_manager.get_cart_total()

    for item_id, item in cart_items.items():
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])

        display_name = item["name"].replace("_", " ").title()
        category_name = item["category"].replace("_", " ").title()

        with col1:
            st.write(f"**{display_name}**")
            st.caption(f"Category: {category_name}")

        with col2:
            st.write(f"₹{item['price']:.2f}/kg")

        with col3:
            st.write(f"{item['quantity']:.1f} kg")

        with col4:
            st.write(f"₹{item['subtotal']:.2f}")

        with col5:
            if st.button("🗑️", key=f"remove_{item_id}", help=f"Remove {display_name} and restore stock"):
                st.session_state.vegetable_db.return_stock(item["name"], item["quantity"])
                st.session_state.cart_manager.remove_item(item_id)
                st.success(f"Removed {display_name} from cart and restored stock!")
                st.rerun()

        st.markdown("---")

    st.subheader(f"Cart Subtotal: ₹{total_amount:.2f}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Clear Cart", use_container_width=True):
            for item in cart_items.values():
                st.session_state.vegetable_db.return_stock(item["name"], item["quantity"])
            st.session_state.cart_manager.clear_cart()
            st.success("Cart cleared and stock restored!")
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
                st.success("Order queued successfully!")
                st.rerun()

    with col3:
        if st.button("Proceed to Checkout", use_container_width=True, type="primary"):
            if cart_items:
                st.session_state.current_page = 'payment'
                st.rerun()


def show_queue_page():
    st.header("📋 Order Queue")

    if 'last_receipt' in st.session_state and st.session_state.last_receipt:
        last_id = st.session_state.get('last_order_id', 'order')
        safe_fname = st.session_state.receipt_generator.sanitize_filename(last_id)
        st.success(f"✅ Order {last_id} processed successfully!")
        st.markdown("### 🧾 Processed Receipt")
        st.text(st.session_state.last_receipt)
        st.download_button(
            label="Download Receipt (.txt)",
            data=st.session_state.last_receipt,
            file_name=safe_fname,
            mime="text/plain",
            key="download_last_receipt"
        )
        if st.button("Dismiss Receipt Banner"):
            st.session_state.last_receipt = None
            st.session_state.last_order_id = None
            st.rerun()
        st.markdown("---")

    if not st.session_state.order_queue:
        st.info("No orders currently waiting in queue.")
        return

    st.write(f"**Active Orders in Queue: {len(st.session_state.order_queue)}**")
    st.markdown("---")

    for idx, order in enumerate(st.session_state.order_queue):
        with st.expander(f"Order #{idx + 1}: {order['order_id']} — ₹{order['total_amount']:.2f}"):
            st.write(f"**Timestamp:** {order['timestamp']}")
            st.write(f"**Total Amount:** ₹{order['total_amount']:.2f}")

            st.write("**Items:**")
            for item in order['items'].values():
                name_disp = item['name'].replace('_', ' ').title()
                st.write(
                    f"- {name_disp}: {item['quantity']:.1f} kg × ₹{item['price']:.0f} = ₹{item['quantity'] * item['price']:.2f}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Process Order", key=f"process_{idx}"):
                    # Dequeue the exact selected order
                    processed_order = st.session_state.order_queue.pop(idx)
                    receipt = st.session_state.receipt_generator.generate_receipt(processed_order)
                    st.session_state.completed_orders.append(processed_order)
                    st.session_state.last_receipt = receipt
                    st.session_state.last_order_id = processed_order['order_id']
                    st.rerun()

            with col2:
                if st.button("Cancel Order", key=f"cancel_{idx}"):
                    # Return reserved stock to inventory
                    cancelled_order = st.session_state.order_queue.pop(idx)
                    for item in cancelled_order['items'].values():
                        st.session_state.vegetable_db.return_stock(item['name'], item['quantity'])
                    st.warning("Order cancelled and stock returned to shelf.")
                    st.rerun()


def show_receipt_page():
    st.header("🧾 Receipt Inspection & Download")

    tab_completed, tab_queue = st.tabs(["Completed Orders", "Queued Orders"])

    with tab_completed:
        if not st.session_state.completed_orders:
            st.info("No completed orders recorded in this session.")
        else:
            completed_options = [
                f"{o['order_id']} — ₹{o.get('total_amount', 0.0):.2f} ({o.get('payment_method', 'Processed')})"
                for o in st.session_state.completed_orders
            ]
            sel_comp_idx = st.selectbox(
                "Select Completed Order:",
                range(len(completed_options)),
                format_func=lambda x: completed_options[x],
                key="sel_completed_order"
            )
            selected_order = st.session_state.completed_orders[sel_comp_idx]
            receipt_text = st.session_state.receipt_generator.generate_receipt(selected_order)
            safe_filename = st.session_state.receipt_generator.sanitize_filename(selected_order["order_id"])

            st.markdown("### Generated Receipt")
            st.text(receipt_text)
            st.download_button(
                label="Download Receipt (.txt)",
                data=receipt_text,
                file_name=safe_filename,
                mime="text/plain",
                key=f"dl_comp_{sel_comp_idx}"
            )

    with tab_queue:
        if not st.session_state.order_queue:
            st.info("No pending orders in the queue.")
        else:
            queue_options = [
                f"{o['order_id']} — ₹{o.get('total_amount', 0.0):.2f}"
                for o in st.session_state.order_queue
            ]
            sel_queue_idx = st.selectbox(
                "Select Queued Order Preview:",
                range(len(queue_options)),
                format_func=lambda x: queue_options[x],
                key="sel_queue_order"
            )
            queue_order = st.session_state.order_queue[sel_queue_idx]
            receipt_preview = st.session_state.receipt_generator.generate_receipt(queue_order)
            safe_q_filename = st.session_state.receipt_generator.sanitize_filename(queue_order["order_id"])

            st.markdown("### Queued Order Preview")
            st.text(receipt_preview)
            st.download_button(
                label="Download Queue Voucher (.txt)",
                data=receipt_preview,
                file_name=safe_q_filename,
                mime="text/plain",
                key=f"dl_queue_{sel_queue_idx}"
            )


def show_analytics_page():
    st.header("📈 Vendor Analytics Dashboard")

    inv_df = st.session_state.vegetable_db.get_inventory_summary()

    if not inv_df.empty and (inv_df["Stock (kg)"].sum() > 0 or inv_df["Value (₹)"].sum() > 0):
        # Metric KPI cards
        total_items = len(inv_df)
        total_stock = inv_df["Stock (kg)"].sum()
        total_valuation = inv_df["Value (₹)"].sum()
        low_stock_count = len(inv_df[inv_df["Stock (kg)"] < 5.0])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Catalog Varieties", f"{total_items}")
        col2.metric("Total Shelf Stock", f"{total_stock:.1f} kg")
        col3.metric("Inventory Valuation", f"₹{total_valuation:,.2f}")
        col4.metric("Low Stock Alerts (< 5kg)", f"{low_stock_count}")

        st.markdown("---")

        # Visualizations
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("Stock Remaining by Item")
            fig_stock = px.bar(
                inv_df,
                x="Name",
                y="Stock (kg)",
                color="Category",
                title="Shelf Stock Levels by Vegetable"
            )
            fig_stock.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_stock, use_container_width=True)

        with col_chart2:
            st.subheader("Inventory Capital Allocation")
            fig_val = px.pie(
                inv_df,
                values="Value (₹)",
                names="Category",
                title="Capital Distribution by Category"
            )
            st.plotly_chart(fig_val, use_container_width=True)
    else:
        st.warning("No inventory data available to render analytics.")


def show_payment_page():
    st.header("💳 Payment Gateway (Simulation)")

    if st.button("🔙 Back to Cart"):
        st.session_state.current_page = 'cart'
        st.rerun()

    st.markdown("---")

    cart_items = st.session_state.cart_manager.get_cart_items()
    if not cart_items:
        st.error("Cart is empty! Return to inventory to add items.")
        st.session_state.current_page = 'inventory'
        st.rerun()
        return

    totals = st.session_state.receipt_generator.calculate_totals(cart_items)
    subtotal = totals["subtotal"]
    tax_amount = totals["tax_amount"]
    total_amount = totals["total"]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Order Summary")
        for item in cart_items.values():
            disp_name = item["name"].replace("_", " ").title()
            st.write(f"• {disp_name} ({item['quantity']:.1f} kg) — ₹{item['subtotal']:.2f}")

        st.markdown("---")
        st.write(f"Subtotal: ₹{subtotal:.2f}")
        st.write(f"Tax (5% GST): ₹{tax_amount:.2f}")
        st.markdown(f"### Total Amount: ₹{total_amount:.2f}")

    with col2:
        st.subheader("Payment Details")
        st.caption("ℹ️ Demo Mode: Real payment credentials are not processed or stored.")

        method = st.radio(
            "Select Payment Method",
            ["Cash", "UPI", "Credit Card"],
            key="payment_method"
        )

        payment_details = {}

        if method == "Cash":
            st.info("Collect physical cash from customer at the counter.")

        elif method == "UPI":
            payment_details["upi_id"] = st.text_input("Customer UPI ID", placeholder="vendor@okhdfcbank")

        elif method == "Credit Card":
            payment_details["card_number"] = st.text_input("Card Number (16 digits)", max_chars=19, placeholder="4111 2222 3333 4444")
            payment_details["cvv"] = st.text_input("CVV (3 digits)", max_chars=4, type="password", placeholder="123")
            payment_details["expiry"] = st.text_input("Expiry (MM/YY)", max_chars=5, placeholder="12/28")

        st.markdown("---")

        if st.button(f"Authorize Payment ₹{total_amount:.2f}", use_container_width=True, type="primary"):
            with st.spinner("Authorizing transaction (Simulated)..."):
                success, message, txn_id = st.session_state.payment_processor.process_payment(
                    total_amount, method, payment_details
                )

                if success:
                    order = {
                        'order_id': f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'items': cart_items,
                        'total_amount': total_amount,
                        'timestamp': datetime.now().isoformat(),
                        'payment_method': method,
                        'transaction_id': txn_id
                    }

                    receipt = st.session_state.receipt_generator.generate_receipt(order)
                    st.session_state.completed_orders.append(order)
                    st.session_state.cart_manager.clear_cart()

                    st.success(f"Payment Approved! {txn_id}")
                    st.balloons()

                    st.markdown("### 🧾 Payment Receipt")
                    st.text(receipt)

                    safe_filename = st.session_state.receipt_generator.sanitize_filename(order["order_id"])
                    st.download_button(
                        label="Download Receipt (.txt)",
                        data=receipt,
                        file_name=safe_filename,
                        mime="text/plain"
                    )

                    if st.button("Start New Order"):
                        st.session_state.current_page = 'inventory'
                        st.rerun()
                else:
                    st.error(f"Payment Authorization Failed: {message}")
                    st.warning("Your cart items are retained. You may retry or choose another payment method.")


if __name__ == "__main__":
    main()
