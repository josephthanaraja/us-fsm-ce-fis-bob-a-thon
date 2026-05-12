#!/usr/bin/env python3
"""
Setup script to create and populate the demo database.

This script creates a sample SQLite database with realistic data
for demonstrating the database operations MCP server.
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = "example.db"

def create_demo_database():
    """Create and populate the demo database."""
    
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        print(f"Removing existing database: {DB_PATH}")
        os.remove(DB_PATH)
    
    print(f"Creating new database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    print("Creating 'users' table...")
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Insert sample users
    users_data = [
        ("Alice Johnson", "alice@example.com", "admin", "2024-01-15"),
        ("Bob Smith", "bob@example.com", "developer", "2024-01-16"),
        ("Carol White", "carol@example.com", "developer", "2024-01-17"),
        ("David Brown", "david@example.com", "manager", "2024-01-18"),
        ("Eve Davis", "eve@example.com", "designer", "2024-01-19"),
    ]
    
    cursor.executemany(
        "INSERT INTO users (name, email, role, created_at) VALUES (?, ?, ?, ?)",
        users_data
    )
    print(f"  Inserted {len(users_data)} users")
    
    # Create products table
    print("Creating 'products' table...")
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            description TEXT
        )
    """)
    
    # Insert sample products
    products_data = [
        ("Laptop Pro 15", "Electronics", 1299.99, 15, "High-performance laptop with 16GB RAM"),
        ("Wireless Mouse", "Electronics", 29.99, 50, "Ergonomic wireless mouse with USB receiver"),
        ("Mechanical Keyboard", "Electronics", 89.99, 30, "RGB mechanical keyboard with blue switches"),
        ("USB-C Hub", "Electronics", 49.99, 25, "7-in-1 USB-C hub with HDMI and ethernet"),
        ("Desk Lamp", "Office", 39.99, 40, "LED desk lamp with adjustable brightness"),
        ("Office Chair", "Office", 299.99, 12, "Ergonomic office chair with lumbar support"),
        ("Notebook Set", "Stationery", 12.99, 100, "Set of 3 lined notebooks"),
        ("Pen Pack", "Stationery", 8.99, 75, "Pack of 10 ballpoint pens"),
    ]
    
    cursor.executemany(
        "INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)",
        products_data
    )
    print(f"  Inserted {len(products_data)} products")
    
    # Create orders table
    print("Creating 'orders' table...")
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # Insert sample orders
    orders_data = [
        (1, 1, 2, 59.98, "completed", "2024-02-01"),
        (2, 2, 1, 1299.99, "completed", "2024-02-02"),
        (1, 3, 1, 89.99, "shipped", "2024-02-03"),
        (3, 5, 2, 79.98, "completed", "2024-02-04"),
        (4, 6, 1, 299.99, "processing", "2024-02-05"),
        (2, 4, 1, 49.99, "completed", "2024-02-06"),
        (5, 7, 3, 38.97, "shipped", "2024-02-07"),
        (3, 8, 2, 17.98, "completed", "2024-02-08"),
        (1, 2, 1, 29.99, "processing", "2024-02-09"),
        (4, 1, 1, 1299.99, "pending", "2024-02-10"),
    ]
    
    cursor.executemany(
        "INSERT INTO orders (user_id, product_id, quantity, total_price, status, order_date) VALUES (?, ?, ?, ?, ?, ?)",
        orders_data
    )
    print(f"  Inserted {len(orders_data)} orders")
    
    # Create tasks table
    print("Creating 'tasks' table...")
    cursor.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            assigned_to INTEGER,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            due_date TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
    """)
    
    # Insert sample tasks
    tasks_data = [
        ("Update user documentation", "Review and update all user-facing documentation", 2, "high", "in_progress", "2024-02-15", "2024-02-01"),
        ("Fix login bug", "Users reporting intermittent login failures", 2, "critical", "completed", "2024-02-05", "2024-02-02"),
        ("Design new landing page", "Create mockups for homepage redesign", 5, "medium", "in_progress", "2024-02-20", "2024-02-03"),
        ("Database optimization", "Optimize slow queries in production", 3, "high", "todo", "2024-02-18", "2024-02-04"),
        ("Team meeting preparation", "Prepare slides for quarterly review", 4, "medium", "completed", "2024-02-08", "2024-02-05"),
        ("Code review", "Review pull requests from last week", 2, "low", "todo", "2024-02-12", "2024-02-06"),
        ("Security audit", "Conduct security review of authentication system", 3, "critical", "in_progress", "2024-02-25", "2024-02-07"),
    ]
    
    cursor.executemany(
        "INSERT INTO tasks (title, description, assigned_to, priority, status, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        tasks_data
    )
    print(f"  Inserted {len(tasks_data)} tasks")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"\n✅ Demo database created successfully: {DB_PATH}")
    print("\nDatabase contains:")
    print(f"  - {len(users_data)} users")
    print(f"  - {len(products_data)} products")
    print(f"  - {len(orders_data)} orders")
    print(f"  - {len(tasks_data)} tasks")
    print("\nYou can now run the MCP server with: python main.py")

if __name__ == "__main__":
    create_demo_database()

# Made with Bob
