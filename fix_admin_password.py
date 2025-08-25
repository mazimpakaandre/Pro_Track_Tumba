#!/usr/bin/env python3
"""
Script to fix the admin password issue in ProTrack-RPT
This script will properly hash the admin password and update the database
"""

import mysql.connector
import bcrypt
import sys

# Database configuration (same as in app.py)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'protrack_rpt'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def fix_admin_password():
    """Fix the admin password by properly hashing it"""
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to database")
        return False
    
    cursor = connection.cursor()
    
    try:
        # Check if admin user exists
        cursor.execute("SELECT COUNT(*) FROM admin_users WHERE username = 'admin'")
        admin_exists = cursor.fetchone()[0] > 0
        
        if admin_exists:
            # Update existing admin password
            print("Admin user exists. Updating password...")
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                UPDATE admin_users 
                SET password = %s 
                WHERE username = 'admin'
            """, (hashed_password.decode('utf-8'),))
        else:
            # Create new admin user
            print("Admin user doesn't exist. Creating new admin user...")
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO admin_users (username, password) 
                VALUES ('admin', %s)
            """, (hashed_password.decode('utf-8'),))
        
        connection.commit()
        print("Admin password fixed successfully!")
        print("Username: admin")
        print("Password: admin123")
        return True
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False
    finally:
        cursor.close()
        connection.close()

def main():
    print("ProTrack-RPT Admin Password Fix Tool")
    print("=" * 40)
    
    # Test database connection
    print("Testing database connection...")
    if not get_db_connection():
        print("ERROR: Cannot connect to database!")
        print("Please make sure:")
        print("1. XAMPP is running")
        print("2. MySQL service is started")
        print("3. Database 'protrack_rpt' exists")
        print("4. Database credentials are correct")
        sys.exit(1)
    
    print("Database connection successful!")
    
    # Fix the admin password
    if fix_admin_password():
        print("\nSUCCESS: Admin password has been fixed!")
        print("You can now login with:")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("\nERROR: Failed to fix admin password!")
        sys.exit(1)

if __name__ == '__main__':
    main() 