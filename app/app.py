import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

import streamlit as st
import redis

import time
from datetime import datetime

from exceptions import ImproperConfiguration

# Redis connection settings
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

if not REDIS_PASSWORD:
    raise ImproperConfiguration("REDIS_PASSWORD environment variable is required but not set.")

def get_redis_connection():
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        return r
    except Exception as e:
        st.error(f"Failed to connect to Redis: {e}")
        return None

def get_redis_info(r):
    if not r:
        return {}
    
    try:
        info = r.info()
        return info
    except Exception as e:
        st.error(f"Failed to get Redis info: {e}")
        return {}

def main():
    # Connect to Redis
    r = get_redis_connection()
    if not r:
        st.error("Cannot connect to Redis server. Please check your connection settings.")
        return
    
    try:
        ping_result = r.ping()
        st.success(f"Connected to Redis server: {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        st.error(f"Redis connection error: {e}")
        return

    # Get Redis Info
    info = get_redis_info(r)

    # st.set_page_config(
    #     page_title="Redis Data Explorer",
    #     page_icon="🔄",
    #     layout="wide"
    # )
    
    def redis_stat():
        st.title("Redis Data Explorer")

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Write Data", "Read Data", "Monitoring", "Redis Info"])
        
        # Tab 1: Write data to Redis
        with tab1:
            st.header("Write Data to Redis")
            
            # Select data type
            data_type = st.selectbox(
                "Select Redis Data Type",
                ["String", "Hash", "List", "Set", "Sorted Set"]
            )
            
            # String Data
            if data_type == "String":
                col1, col2 = st.columns(2)
                with col1:
                    key = st.text_input("Key")
                    value = st.text_area("Value")
                    expiry = st.number_input("Expiry (seconds, 0 for no expiry)", min_value=0, value=None)
                    
                    if st.button("Save String"):
                        if key and value:
                            try:
                                r.set(key, value, ex=expiry)
                                st.success(f"String saved with key: {key}")
                            except Exception as e:
                                st.error(f"Error saving string: {e}")
                        else:
                            st.warning("Both key and value are required")
                
            # Hash Data
            elif data_type == "Hash":
                hash_key = st.text_input("Hash Key")
                
                col1, col2 = st.columns(2)
                with col1:
                    field_key = st.text_input("Field")
                    field_value = st.text_area("Value")
                    
                    if st.button("Add Hash Field"):
                        if hash_key and field_key and field_value:
                            try:
                                r.hset(hash_key, field_key, field_value)
                                st.success(f"Hash field added: {hash_key} -> {field_key}")
                            except Exception as e:
                                st.error(f"Error saving hash: {e}")
                        else:
                            st.warning("Hash key, field and value are required")
                
                with col2:
                    st.subheader("Current Hash Fields")
                    if hash_key:
                        try:
                            hash_data = r.hgetall(hash_key)
                            if hash_data:
                                for k, v in hash_data.items():
                                    st.text(f"{k}: {v}")
                            else:
                                st.info("No hash fields found")
                        except Exception as e:
                            st.error(f"Error retrieving hash data: {e}")
            
            # List Data
            elif data_type == "List":
                list_key = st.text_input("List Key")
                list_value = st.text_input("Value")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Push to Right"):
                        if list_key and list_value:
                            try:
                                r.rpush(list_key, list_value)
                                st.success(f"Added to list: {list_key}")
                            except Exception as e:
                                st.error(f"Error adding to list: {e}")
                        else:
                            st.warning("Both key and value are required")
                
                with col2:
                    if st.button("Push to Left"):
                        if list_key and list_value:
                            try:
                                r.lpush(list_key, list_value)
                                st.success(f"Added to list: {list_key}")
                            except Exception as e:
                                st.error(f"Error adding to list: {e}")
                        else:
                            st.warning("Both key and value are required")
                
                if list_key:
                    try:
                        list_items = r.lrange(list_key, 0, -1)
                        if list_items:
                            st.subheader("Current List Items")
                            for idx, item in enumerate(list_items):
                                st.text(f"{idx}: {item}")
                        else:
                            st.info("No items in list")
                    except Exception as e:
                        st.error(f"Error retrieving list data: {e}")
            
            # Set Data
            elif data_type == "Set":
                set_key = st.text_input("Set Key")
                set_value = st.text_input("Value")
                
                if st.button("Add to Set"):
                    if set_key and set_value:
                        try:
                            r.sadd(set_key, set_value)
                            st.success(f"Added to set: {set_key}")
                        except Exception as e:
                            st.error(f"Error adding to set: {e}")
                    else:
                        st.warning("Both key and value are required")
                
                if set_key:
                    try:
                        set_items = r.smembers(set_key)
                        if set_items:
                            st.subheader("Current Set Members")
                            for item in set_items:
                                st.text(item)
                        else:
                            st.info("No items in set")
                    except Exception as e:
                        st.error(f"Error retrieving set data: {e}")
            
            # Sorted Set Data
            elif data_type == "Sorted Set":
                zset_key = st.text_input("Sorted Set Key")
                zset_value = st.text_input("Value")
                score = st.number_input("Score", value=1.0)
                
                if st.button("Add to Sorted Set"):
                    if zset_key and zset_value:
                        try:
                            r.zadd(zset_key, {zset_value: score})
                            st.success(f"Added to sorted set: {zset_key}")
                        except Exception as e:
                            st.error(f"Error adding to sorted set: {e}")
                    else:
                        st.warning("Key, value and score are required")
                
                if zset_key:
                    try:
                        zset_items = r.zrange(zset_key, 0, -1, withscores=True)
                        if zset_items:
                            st.subheader("Current Sorted Set Members")
                            for item, score in zset_items:
                                st.text(f"{item}: {score}")
                        else:
                            st.info("No items in sorted set")
                    except Exception as e:
                        st.error(f"Error retrieving sorted set data: {e}")
        
        # Tab 2: Read data from Redis
        with tab2:
            st.header("Read Data from Redis")
            
            # Get all keys
            try:
                all_keys = r.keys("*")
                
                if not all_keys:
                    st.info("No keys found in Redis")
                    return
                    
                selected_key = st.selectbox("Select a key", all_keys)
                
                if selected_key:
                    # Get key type
                    key_type = r.type(selected_key)
                    ttl = r.ttl(selected_key)
                    
                    st.subheader(f"Key: {selected_key}")
                    st.text(f"Type: {key_type}")
                    st.text(f"TTL: {ttl if ttl > -1 else 'No expiry'}")
                    
                    # Display data based on type
                    if key_type == "string":
                        value = r.get(selected_key)
                        st.text_area("Value", value, height=200, disabled=True)
                    
                    elif key_type == "hash":
                        hash_data = r.hgetall(selected_key)
                        st.json(hash_data)
                    
                    elif key_type == "list":
                        list_items = r.lrange(selected_key, 0, -1)
                        for idx, item in enumerate(list_items):
                            st.text(f"{idx}: {item}")
                    
                    elif key_type == "set":
                        set_items = r.smembers(selected_key)
                        for item in set_items:
                            st.text(item)
                    
                    elif key_type == "zset":
                        zset_items = r.zrange(selected_key, 0, -1, withscores=True)
                        for item, score in zset_items:
                            st.text(f"{item}: {score}")
                    
                    # Delete key option
                    if st.button("Delete Key"):
                        r.delete(selected_key)
                        st.success(f"Deleted key: {selected_key}")
                        st.experimental_rerun()
                        
            except Exception as e:
                st.error(f"Error retrieving keys: {e}")
        
        # Tab 3: Monitoring
        with tab3:
            st.header("Redis Monitoring")
            
            # Auto-refresh
            refresh = st.checkbox("Auto-refresh (5s)", value=False)
            
            if refresh:
                st.experimental_rerun()
                time.sleep(5)
            
            # Memory usage
            st.subheader("Memory Usage")
            try:
                memory_info = r.info("memory")
                used_memory = memory_info.get("used_memory_human", "N/A")
                used_memory_peak = memory_info.get("used_memory_peak_human", "N/A")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Used Memory", used_memory)
                with col2:
                    st.metric("Peak Memory", used_memory_peak)
                    
                # Memory usage over time would require storing historical data
                
            except Exception as e:
                st.error(f"Error retrieving memory info: {e}")
            
            # Operations stats
            st.subheader("Operations")
            try:
                stats = r.info("stats")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Commands Processed", stats.get("total_commands_processed", "N/A"))
                    st.metric("Connected Clients", info.get("connected_clients", "N/A"))
                with col2:
                    st.metric("Keyspace Hits", stats.get("keyspace_hits", "N/A"))
                    st.metric("Keyspace Misses", stats.get("keyspace_misses", "N/A"))
                    
            except Exception as e:
                st.error(f"Error retrieving stats: {e}")
            
            # Key statistics
            st.subheader("Keyspace")
            try:
                keyspace = info.get("keyspace", {})
                if keyspace:
                    for db, stats in keyspace.items():
                        st.text(f"{db}: {stats}")
                else:
                    st.info("No keyspace information available")
            except Exception as e:
                st.error(f"Error retrieving keyspace info: {e}")
        
        # Tab 4: Redis Info
        with tab4:
            st.header("Redis Server Information")
            
            try:
                server_info = r.info("server")
                
                st.subheader("Server")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Redis Version", server_info.get("redis_version", "N/A"))
                    st.metric("Uptime", f"{server_info.get('uptime_in_days', 'N/A')} days")
                with col2:
                    st.metric("Process ID", server_info.get("process_id", "N/A"))
                    st.metric("TCP Port", server_info.get("tcp_port", "N/A"))
                
                st.subheader("Persistence")
                persistence = r.info("persistence")
                st.text(f"AOF Enabled: {persistence.get('aof_enabled', 'N/A')}")
                st.text(f"RDB Saves: {persistence.get('rdb_changes_since_last_save', 'N/A')} changes since last save")
                
                # Display full info as JSON
                with st.expander("Show All Redis Info"):
                    st.json(info)
                    
            except Exception as e:
                st.error(f"Error retrieving Redis info: {e}")

    def checkout():
        st.title("Checkout")

        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Browse Products", 
            "User Management", 
            "Shopping Cart", 
            "Checkout", 
            "Order History"
        ])
        
        # Tab 1: Browse Products
        with tab1:
            st.header("Browse Products")
            
            # Filter by category
            categories = []
            for cat_id in r.smembers("categories:index"):
                cat_data = r.hgetall(f"category:{cat_id}")
                categories.append({"id": cat_id, "name": cat_data["name"]})
            
            all_option = {"id": "all", "name": "All Categories"}
            categories.insert(0, all_option)
            
            selected_category = st.selectbox(
                "Filter by Category",
                options=[cat["id"] for cat in categories],
                format_func=lambda x: next((cat["name"] for cat in categories if cat["id"] == x), x)
            )
            
            # Display products
            st.subheader("Products")
            
            if selected_category == "all":
                product_ids = r.smembers("products:index")
            else:
                product_ids = r.smembers(f"category:{selected_category}:products")
            
            if not product_ids:
                st.info("No products found")
            else:
                # Create 2 columns for products display
                cols = st.columns(2)
                
                for i, product_id in enumerate(product_ids):
                    product_data = r.hgetall(f"product:{product_id}")
                    if not product_data:
                        continue
                    
                    # Get product categories
                    category_ids = r.smembers(f"product:{product_id}:categories")
                    category_names = []
                    for cat_id in category_ids:
                        cat_data = r.hgetall(f"category:{cat_id}")
                        if cat_data:
                            category_names.append(cat_data["name"])
                    
                    # Display product card
                    with cols[i % 2]:
                        st.markdown(f"### {product_data['name']}")
                        st.write(product_data['description'])
                        st.write(f"**Price:** ${product_data['price']}")
                        st.write(f"**Stock:** {product_data['stock']}")
                        st.write(f"**Categories:** {', '.join(category_names)}")
                        
                        # Add to cart section
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            qty = st.number_input(f"Qty", min_value=1, value=1, key=f"qty_{product_id}")
                        
                        # Get current user from session state
                        current_user = st.session_state.get('current_user', None)
                        
                        with col2:
                            if current_user:
                                if st.button("Add to Cart", key=f"add_{product_id}"):
                                    # Add to cart in Redis
                                    current_qty = r.hget(f"cart:{current_user}", product_id) or 0
                                    new_qty = int(current_qty) + qty
                                    r.hset(f"cart:{current_user}", product_id, new_qty)
                                    st.success(f"Added {qty} x {product_data['name']} to cart!")
                            else:
                                st.warning("Please log in to add items to cart")
                        
                        st.markdown("---")
        
        # Tab 2: User Management
        with tab2:
            st.header("User Management")
            
            # Simple login/register functionality
            login_option = st.radio("Choose Option", ["Login", "Register"])
            
            if login_option == "Login":
                st.subheader("Login")
                
                # Get all users for dropdown
                user_ids = r.smembers("users:index")
                user_options = []
                
                for user_id in user_ids:
                    user_data = r.hgetall(f"user:{user_id}")
                    if user_data:
                        user_options.append({
                            "id": user_id,
                            "display": f"{user_data['username']} ({user_data['email']})"
                        })
                
                if not user_options:
                    st.warning("No users found. Please register a new user.")
                else:
                    selected_user = st.selectbox(
                        "Select User",
                        options=[user["id"] for user in user_options],
                        format_func=lambda x: next((user["display"] for user in user_options if user["id"] == x), x)
                    )
                    
                    if st.button("Login"):
                        st.session_state['current_user'] = selected_user
                        user_data = r.hgetall(f"user:{selected_user}")
                        st.success(f"Logged in as {user_data['username']}!")
            
            else:  # Register
                st.subheader("Register")
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                
                if st.button("Register"):
                    if new_username and new_email:
                        # Create new user
                        new_user_id = f"user{len(r.smembers('users:index')) + 1}"
                        r.hset(f"user:{new_user_id}", mapping={
                            "username": new_username,
                            "email": new_email,
                            "created_at": datetime.now().strftime("%Y-%m-%d")
                        })
                        r.sadd("users:index", new_user_id)
                        
                        st.session_state['current_user'] = new_user_id
                        st.success(f"Registered and logged in as {new_username}!")
                    else:
                        st.error("Username and email are required")
            
            # Display current user
            current_user = st.session_state.get('current_user', None)
            if current_user:
                st.subheader("Current User")
                user_data = r.hgetall(f"user:{current_user}")
                st.write(f"Username: {user_data['username']}")
                st.write(f"Email: {user_data['email']}")
                
                if st.button("Logout"):
                    st.session_state.pop('current_user', None)
                    st.experimental_rerun()
                    
        # Tab 3: Shopping Cart
        with tab3:
            st.header("Shopping Cart")
            
            current_user = st.session_state.get('current_user', None)
            if not current_user:
                st.warning("Please log in to view your cart")
            else:
                cart_items = r.hgetall(f"cart:{current_user}")
                
                if not cart_items:
                    st.info("Your cart is empty")
                else:
                    # Display cart items in a table
                    st.subheader("Cart Items")
                    
                    cart_data = []
                    total = 0
                    
                    for product_id, qty in cart_items.items():
                        product_data = r.hgetall(f"product:{product_id}")
                        if product_data:
                            qty = int(qty)
                            price = float(product_data['price'])
                            subtotal = qty * price
                            total += subtotal
                            
                            cart_data.append({
                                "Product ID": product_id,
                                "Product": product_data['name'],
                                "Price": f"${price:.2f}",
                                "Quantity": qty,
                                "Subtotal": f"${subtotal:.2f}"
                            })
                    
                    # Display as table
                    st.table(cart_data)
                    st.subheader(f"Total: ${total:.2f}")
                    
                    # Clear cart button
                    if st.button("Clear Cart"):
                        r.delete(f"cart:{current_user}")
                        st.success("Cart cleared!")
                        st.experimental_rerun()
                    
                    # Update cart button (we'd need more UI to make this work well)
                    st.write("To update quantities, go back to the Browse Products tab.")
        
        # Tab 4: Checkout
        with tab4:
            st.header("Checkout")
            
            current_user = st.session_state.get('current_user', None)
            if not current_user:
                st.warning("Please log in to checkout")
            else:
                cart_items = r.hgetall(f"cart:{current_user}")
                
                if not cart_items:
                    st.info("Your cart is empty")
                else:
                    # Display cart summary
                    st.subheader("Order Summary")
                    
                    cart_data = []
                    total = 0
                    
                    for product_id, qty in cart_items.items():
                        product_data = r.hgetall(f"product:{product_id}")
                        if product_data:
                            qty = int(qty)
                            price = float(product_data['price'])
                            subtotal = qty * price
                            total += subtotal
                            
                            cart_data.append({
                                "Product": product_data['name'],
                                "Quantity": qty,
                                "Subtotal": f"${subtotal:.2f}"
                            })
                    
                    for item in cart_data:
                        st.write(f"{item['Product']} (x{item['Quantity']}) - {item['Subtotal']}")
                    
                    st.subheader(f"Total: ${total:.2f}")
                    
                    # Simple checkout form
                    st.subheader("Shipping Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("Address Line 1")
                        st.text_input("City")
                        st.text_input("Postal Code")
                    
                    with col2:
                        st.text_input("Address Line 2 (Optional)")
                        st.text_input("State/Province")
                        st.text_input("Country")
                    
                    st.subheader("Payment Method")
                    payment_method = st.selectbox("Select Payment Method", ["Credit Card", "PayPal", "Bank Transfer"])
                    
                    if payment_method == "Credit Card":
                        cc_number = st.text_input("Card Number", type="password")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.text_input("Expiration Date (MM/YY)")
                        with col2:
                            st.text_input("CVV", type="password")
                    
                    # Place order button
                    if st.button("Place Order"):
                        # Generate order ID
                        order_id = f"order{int(time.time())}"
                        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Create order in Redis
                        r.hset(f"order:{order_id}", mapping={
                            "user_id": current_user,
                            "total": total,
                            "status": "pending",
                            "created_at": order_time
                        })
                        
                        # Add order items
                        for product_id, qty in cart_items.items():
                            r.hset(f"order:{order_id}:items", product_id, qty)
                            
                            # Update stock (decrement)
                            current_stock = int(r.hget(f"product:{product_id}", "stock"))
                            new_stock = max(0, current_stock - int(qty))
                            r.hset(f"product:{product_id}", "stock", new_stock)
                        
                        # Add to user orders list
                        r.lpush(f"user:{current_user}:orders", order_id)
                        
                        # Clear cart
                        r.delete(f"cart:{current_user}")
                        
                        st.success(f"Order placed successfully! Order ID: {order_id}")
        
        # Tab 5: Order History
        with tab5:
            st.header("Order History")
            
            current_user = st.session_state.get('current_user', None)
            if not current_user:
                st.warning("Please log in to view your order history")
            else:
                # Get user orders
                order_ids = r.lrange(f"user:{current_user}:orders", 0, -1)
                
                if not order_ids:
                    st.info("You haven't placed any orders yet")
                else:
                    st.subheader("Your Orders")
                    
                    for order_id in order_ids:
                        order_data = r.hgetall(f"order:{order_id}")
                        if not order_data:
                            continue
                        
                        with st.expander(f"Order {order_id} - {order_data['created_at']} - ${float(order_data['total']):.2f}"):
                            st.write(f"Status: {order_data['status'].capitalize()}")
                            
                            # Get order items
                            items = r.hgetall(f"order:{order_id}:items")
                            
                            if items:
                                st.write("Items:")
                                for product_id, qty in items.items():
                                    product_data = r.hgetall(f"product:{product_id}")
                                    if product_data:
                                        st.write(f"- {product_data['name']} x {qty} - ${float(product_data['price']) * int(qty):.2f}")
                            
                            # Add a button to cancel order if it's still pending
                            if order_data['status'] == "pending":
                                if st.button("Cancel Order", key=f"cancel_{order_id}"):
                                    r.hset(f"order:{order_id}", "status", "cancelled")
                                    st.success("Order cancelled successfully!")
                                    st.experimental_rerun()


    pg = st.navigation([
        st.Page(redis_stat, title="Redis Data Explorer", icon="🔍"),
        st.Page(checkout, title="Checkout", icon="🛒"),
    ])

    pg.run()

if __name__ == "__main__":
    main()
