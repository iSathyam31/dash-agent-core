import os
import random
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv
from faker import Faker

# Load environment variables
load_dotenv()

# Database connection configuration
DB_CONFIG = {
    "host": os.getenv("PGHOST"),
    "port": os.getenv("PGPORT", 5432),
    "user": os.getenv("PGUSER"),
    "password": os.getenv("PGPASSWORD"),
    "database": os.getenv("PGDATABASE")
}

fake = Faker()

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_schema_and_tables(cur):
    print("Creating schema and tables...")
    
    # Drop schema if exists for a clean start
    cur.execute("DROP SCHEMA IF EXISTS ecommerce CASCADE;")
    cur.execute("CREATE SCHEMA ecommerce;")
    
    # Set search path to ecommerce
    cur.execute("SET search_path TO ecommerce;")
    
    # 1. Users table
    cur.execute("""
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(50),
            address TEXT,
            city VARCHAR(50),
            zip_code VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # 2. Categories table
    cur.execute("""
        CREATE TABLE categories (
            category_id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            description TEXT
        );
    """)
    
    # 3. Products table
    cur.execute("""
        CREATE TABLE products (
            product_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            stock_quantity INTEGER NOT NULL,
            category_id INTEGER REFERENCES categories(category_id)
        );
    """)
    
    # 4. Orders table
    cur.execute("""
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) NOT NULL,
            total_amount DECIMAL(12, 2) NOT NULL
        );
    """)
    
    # 5. Order Items table
    cur.execute("""
        CREATE TABLE order_items (
            order_item_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(product_id),
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL
        );
    """)
    
    # 6. Reviews table
    cur.execute("""
        CREATE TABLE reviews (
            review_id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(product_id),
            user_id INTEGER REFERENCES users(user_id),
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # 7. Payments table
    cur.execute("""
        CREATE TABLE payments (
            payment_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(order_id),
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            amount DECIMAL(12, 2) NOT NULL,
            payment_method VARCHAR(50),
            status VARCHAR(50) NOT NULL
        );
    """)
    
    # 8. Shipping Details table
    cur.execute("""
        CREATE TABLE shipping_details (
            shipping_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(order_id),
            tracking_number VARCHAR(100) UNIQUE,
            carrier VARCHAR(50),
            shipping_status VARCHAR(50) NOT NULL,
            estimated_delivery DATE
        );
    """)
    
    print("Schema and tables created successfully.")

def seed_data(cur):
    print("Seeding sample data...")
    
    # Set search path
    cur.execute("SET search_path TO ecommerce;")
    
    # Seed Categories
    categories = [
        ("Electronics", "Gadgets, devices and hardware"),
        ("Fashion", "Clothing, shoes and accessories"),
        ("Home & Garden", "Furniture, decor and tools"),
        ("Beauty", "Skincare, makeup and personal care"),
        ("Sports", "Equipment and activewear"),
        ("Books", "Fiction, non-fiction and educational"),
        ("Toys", "Games and playthings for all ages"),
        ("Health", "Supplements and medical supplies"),
        ("Automotive", "Car parts and accessories"),
        ("Grocery", "Food and household essentials")
    ]
    cur.executemany("INSERT INTO categories (name, description) VALUES (%s, %s);", categories)
    cur.execute("SELECT category_id FROM categories;")
    category_ids = [r[0] for r in cur.fetchall()]
    
    # Seed Users
    user_data = []
    for _ in range(50):
        user_data.append((
            fake.first_name(),
            fake.last_name(),
            fake.unique.email(),
            fake.phone_number(),
            fake.address().replace('\n', ', '),
            fake.city(),
            fake.zipcode(),
            fake.date_time_between(start_date='-1y', end_date='now')
        ))
    cur.executemany("""
        INSERT INTO users (first_name, last_name, email, phone, address, city, zip_code, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """, user_data)
    cur.execute("SELECT user_id FROM users;")
    user_ids = [r[0] for r in cur.fetchall()]
    
    # Seed Products
    product_data = []
    for _ in range(50):
        product_data.append((
            fake.catch_phrase(),
            fake.paragraph(),
            round(random.uniform(10.0, 1000.0), 2),
            random.randint(5, 500),
            random.choice(category_ids)
        ))
    cur.executemany("""
        INSERT INTO products (name, description, price, stock_quantity, category_id)
        VALUES (%s, %s, %s, %s, %s) RETURNING product_id;
    """, product_data)
    cur.execute("SELECT product_id, price FROM products;")
    products_db = cur.fetchall()
    product_map = {p[0]: p[1] for p in products_db}
    product_ids = list(product_map.keys())
    
    # Seed Orders
    order_data = []
    statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
    for _ in range(100):
        order_date = fake.date_time_between(start_date='-6m', end_date='now')
        order_data.append((
            random.choice(user_ids),
            order_date,
            random.choice(statuses),
            0  # Placeholder total, will update after items
        ))
    
    # Insert orders and get IDs
    order_ids = []
    for order in order_data:
        cur.execute("""
            INSERT INTO orders (user_id, order_date, status, total_amount)
            VALUES (%s, %s, %s, %s) RETURNING order_id;
        """, order)
        order_ids.append(cur.fetchone()[0])
    
    # Seed Order Items and calculate Order Totals
    for order_id in order_ids:
        num_items = random.randint(1, 5)
        selected_products = random.sample(product_ids, num_items)
        total_order_amount = 0
        
        for pid in selected_products:
            qty = random.randint(1, 3)
            price = product_map[pid]
            total_order_amount += (price * qty)
            
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s);
            """, (order_id, pid, qty, price))
        
        # Update order total
        cur.execute("UPDATE orders SET total_amount = %s WHERE order_id = %s;", (total_order_amount, order_id))
    
    # Seed Reviews
    review_data = []
    for _ in range(100):
        review_data.append((
            random.choice(product_ids),
            random.choice(user_ids),
            random.randint(1, 5),
            fake.sentence(),
            fake.date_time_between(start_date='-6m', end_date='now')
        ))
    cur.executemany("""
        INSERT INTO reviews (product_id, user_id, rating, comment, created_at)
        VALUES (%s, %s, %s, %s, %s);
    """, review_data)
    
    # Seed Payments
    methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Stripe']
    for order_id in order_ids:
        cur.execute("SELECT total_amount, order_date, status FROM orders WHERE order_id = %s;", (order_id,))
        amount, o_date, o_status = cur.fetchone()
        
        # Only pay for non-cancelled orders usually, but let's seed some regardless
        pay_status = 'Success' if o_status != 'Cancelled' else 'Failed'
        if o_status == 'Pending' and random.random() > 0.5:
             pay_status = 'Pending'
             
        cur.execute("""
            INSERT INTO payments (order_id, payment_date, amount, payment_method, status)
            VALUES (%s, %s, %s, %s, %s);
        """, (order_id, o_date + timedelta(minutes=random.randint(1, 60)), amount, random.choice(methods), pay_status))
        
    # Seed Shipping Details
    carriers = ['FedEx', 'UPS', 'DHL', 'USPS']
    ship_statuses = ['In Transit', 'Out for Delivery', 'Delivered', 'Pending']
    for order_id in order_ids:
        cur.execute("SELECT status, order_date FROM orders WHERE order_id = %s;", (order_id,))
        o_status, o_date = cur.fetchone()
        
        if o_status in ['Shipped', 'Delivered']:
            s_status = 'Delivered' if o_status == 'Delivered' else random.choice(['In Transit', 'Out for Delivery'])
            est_del = (o_date + timedelta(days=random.randint(3, 7))).date()
            
            cur.execute("""
                INSERT INTO shipping_details (order_id, tracking_number, carrier, shipping_status, estimated_delivery)
                VALUES (%s, %s, %s, %s, %s);
            """, (order_id, fake.bothify(text='??#########'), random.choice(carriers), s_status, est_del))

    print("Data seeding completed successfully.")

def main():
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = False # Use transactions
        
        with conn.cursor() as cur:
            create_schema_and_tables(cur)
            seed_data(cur)
        
        conn.commit()
        print("\nAll operations completed successfully!")
        
        # Print summary
        with conn.cursor() as cur:
            cur.execute("SET search_path TO ecommerce;")
            tables = ['users', 'categories', 'products', 'orders', 'order_items', 'reviews', 'payments', 'shipping_details']
            print("\nSummary of records created:")
            for table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table};")
                count = cur.fetchone()[0]
                print(f"- {table}: {count} rows")
                
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
