"""
This file creates the sample manufacturing database with correct schema.
Run this once to initialize the database, then the app will work correctly.
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

DB_PATH = 'data/sample_manufacturing.db'

def create_database():
    """Create and populate the manufacturing database."""
    # Remove old database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating tables...")
    
    # ===== TABLE 1: line_master =====
    cursor.execute('''
        CREATE TABLE line_master (
            line_id TEXT PRIMARY KEY,
            line_name TEXT NOT NULL,
            capacity_per_hour INTEGER,
            location TEXT,
            status TEXT
        )
    ''')
    
    lines = [
        ('LINE-1', 'Assembly Line 1', 500, 'Building A', 'active'),
        ('LINE-2', 'Assembly Line 2', 450, 'Building A', 'active'),
        ('LINE-3', 'Packaging Line 1', 800, 'Building B', 'active'),
        ('LINE-4', 'Quality Control Line', 300, 'Building C', 'active'),
    ]
    cursor.executemany('INSERT INTO line_master VALUES (?, ?, ?, ?, ?)', lines)
    print(f"  ✓ line_master: {len(lines)} records")
    
    # ===== TABLE 2: products =====
    cursor.execute('''
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            product_type TEXT,
            unit TEXT,
            standard_cost REAL
        )
    ''')
    
    products = [
        ('PROD-101', 'ChemX-500', 'Chemical', 'kg', 45.50),
        ('PROD-102', 'PolyBlend-A', 'Polymer', 'kg', 62.00),
        ('PROD-103', 'SurfaceCoat-Pro', 'Coating', 'liter', 78.25),
        ('PROD-104', 'AdhesivePrime', 'Adhesive', 'kg', 52.75),
    ]
    cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?)', products)
    print(f"  ✓ products: {len(products)} records")
    
    # ===== TABLE 3: recipes =====
    cursor.execute('''
        CREATE TABLE recipes (
            recipe_id TEXT PRIMARY KEY,
            product_id TEXT,
            recipe_name TEXT,
            version TEXT,
            cycle_time_minutes INTEGER,
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    ''')
    
    recipes = [
        ('RCP-A1', 'PROD-101', 'ChemX Standard Process', 'v2.1', 45),
        ('RCP-B2', 'PROD-102', 'PolyBlend Fast Cure', 'v1.3', 60),
        ('RCP-C3', 'PROD-103', 'SurfaceCoat High Gloss', 'v3.0', 30),
        ('RCP-D4', 'PROD-104', 'AdhesivePrime Quick Set', 'v2.5', 40),
    ]
    cursor.executemany('INSERT INTO recipes VALUES (?, ?, ?, ?, ?)', recipes)
    print(f"  ✓ recipes: {len(recipes)} records")
    
    # ===== TABLE 4: staff =====
    cursor.execute('''
        CREATE TABLE staff (
            staff_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT,
            shift_preference TEXT,
            hire_date TEXT
        )
    ''')
    
    staff = [
        ('EMP-001', 'John Davis', 'Supervisor', 'day', '2024-06-15'),
        ('EMP-002', 'Sarah Chen', 'Supervisor', 'night', '2024-07-20'),
        ('EMP-003', 'Michael Brown', 'Operator', 'day', '2024-08-10'),
        ('EMP-004', 'Lisa Wang', 'Operator', 'night', '2024-08-15'),
        ('EMP-005', 'Robert Taylor', 'QC Inspector', 'day', '2024-09-01'),
        ('EMP-006', 'Emily Martinez', 'Supervisor', 'day', '2024-05-10'),
    ]
    cursor.executemany('INSERT INTO staff VALUES (?, ?, ?, ?, ?)', staff)
    print(f"  ✓ staff: {len(staff)} records")
    
    # ===== TABLE 5: shift_logs =====
    cursor.execute('''
        CREATE TABLE shift_logs (
            shift_id TEXT PRIMARY KEY,
            line_id TEXT,
            supervisor_id TEXT,
            shift_date TEXT,
            start_time TEXT,
            end_time TEXT,
            shift_type TEXT,
            notes TEXT,
            FOREIGN KEY(line_id) REFERENCES line_master(line_id),
            FOREIGN KEY(supervisor_id) REFERENCES staff(staff_id)
        )
    ''')
    
    # Generate 30 days of shift logs
    start_date = datetime(2026, 1, 20)
    shift_counter = 1000
    shift_logs = []
    
    for day_offset in range(30):
        shift_date = (start_date + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        
        for line_id in ['LINE-1', 'LINE-2', 'LINE-3', 'LINE-4']:
            # Day shift
            shift_logs.append((
                f'SH-{shift_counter}',
                line_id,
                random.choice(['EMP-001', 'EMP-002', 'EMP-006']),
                shift_date,
                '06:00:00',
                '14:00:00',
                'day',
                None
            ))
            shift_counter += 1
            
            # Night shift
            shift_logs.append((
                f'SH-{shift_counter}',
                line_id,
                random.choice(['EMP-002', 'EMP-004']),
                shift_date,
                '22:00:00',
                '06:00:00',
                'night',
                None
            ))
            shift_counter += 1
    
    cursor.executemany('INSERT INTO shift_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)', shift_logs)
    print(f"  ✓ shift_logs: {len(shift_logs)} records")
    
    # ===== TABLE 6: production_orders =====
    cursor.execute('''
        CREATE TABLE production_orders (
            order_id TEXT PRIMARY KEY,
            product_id TEXT,
            recipe_id TEXT,
            line_id TEXT,
            shift_id TEXT,
            quantity_planned REAL,
            quantity_actual REAL,
            unit TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT,
            FOREIGN KEY(product_id) REFERENCES products(product_id),
            FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
            FOREIGN KEY(line_id) REFERENCES line_master(line_id),
            FOREIGN KEY(shift_id) REFERENCES shift_logs(shift_id)
        )
    ''')
    
    # Generate 117 production orders
    order_counter = 1000
    production_orders = []
    
    for day_offset in range(30):
        base_date = (start_date + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        
        # 3-5 random orders per day
        num_orders = random.randint(3, 5)
        for _ in range(num_orders):
            line_id = random.choice(['LINE-1', 'LINE-2', 'LINE-3', 'LINE-4'])
            product_id = random.choice(['PROD-101', 'PROD-102', 'PROD-103', 'PROD-104'])
            
            # Find matching recipe
            recipe_id = {
                'PROD-101': 'RCP-A1',
                'PROD-102': 'RCP-B2',
                'PROD-103': 'RCP-C3',
                'PROD-104': 'RCP-D4',
            }[product_id]
            
            quantity_planned = random.randint(500, 2000)
            yield_pct = random.uniform(85, 98)
            quantity_actual = int(quantity_planned * (yield_pct / 100))
            
            start_hour = 6 if random.random() > 0.5 else 22
            start_time = f"{base_date}T{start_hour:02d}:{random.randint(0, 59):02d}:00"
            end_time = f"{base_date}T{(start_hour + random.randint(1, 3)):02d}:{random.randint(0, 59):02d}:00"
            
            production_orders.append((
                f'PO-{order_counter}',
                product_id,
                recipe_id,
                line_id,
                None,  # shift_id
                quantity_planned,
                quantity_actual,
                'kg' if product_id in ['PROD-101', 'PROD-102', 'PROD-104'] else 'liter',
                start_time,
                end_time,
                'completed'
            ))
            order_counter += 1
    
    cursor.executemany('INSERT INTO production_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', production_orders)
    print(f"  ✓ production_orders: {len(production_orders)} records")
    
    # ===== TABLE 7: production_steps =====
    cursor.execute('''
        CREATE TABLE production_steps (
            step_id TEXT PRIMARY KEY,
            order_id TEXT,
            step_number INTEGER,
            step_name TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT,
            operator_id TEXT,
            temperature REAL,
            pressure REAL,
            notes TEXT,
            FOREIGN KEY(order_id) REFERENCES production_orders(order_id),
            FOREIGN KEY(operator_id) REFERENCES staff(staff_id)
        )
    ''')
    
    # Generate production steps
    step_counter = 1
    production_steps = []
    step_names = ['Material Preparation', 'Mixing', 'Heating', 'Reaction', 'Cooling', 'Quality Check', 'Packaging']
    
    for order_id in [f'PO-{i}' for i in range(1000, order_counter)]:
        num_steps = random.randint(4, 6)
        for step_num in range(1, num_steps + 1):
            production_steps.append((
                f'STEP-{step_counter}',
                order_id,
                step_num,
                random.choice(step_names),
                f'2026-01-{random.randint(20, 31):02d}T{random.randint(6, 22):02d}:{random.randint(0, 59):02d}:00',
                f'2026-01-{random.randint(20, 31):02d}T{random.randint(6, 22):02d}:{random.randint(0, 59):02d}:00',
                'completed',
                random.choice(['EMP-003', 'EMP-004']),
                random.uniform(20, 90) if random.random() > 0.5 else None,
                random.uniform(1, 10) if random.random() > 0.5 else None,
                None
            ))
            step_counter += 1
    
    cursor.executemany('INSERT INTO production_steps VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', production_steps)
    print(f"  ✓ production_steps: {len(production_steps)} records")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database created successfully at {DB_PATH}")
    print(f"Total records: {len(lines) + len(products) + len(recipes) + len(staff) + len(shift_logs) + len(production_orders) + len(production_steps)}")

if __name__ == '__main__':
    print("🔨 Generating Manufacturing Database...\n")
    try:
        create_database()
        print("\n✓ Database is ready to use!")
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        raise
