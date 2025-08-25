-- ProTrack-RPT Database Schema
-- Create database
CREATE DATABASE IF NOT EXISTS protrack_rpt;
USE protrack_rpt;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS consumables;
DROP TABLE IF EXISTS laboratory;
DROP TABLE IF EXISTS admin_users;
DROP TABLE IF EXISTS audit_logs;

-- Create consumables table
CREATE TABLE consumables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    quantity INT DEFAULT 0,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    purpose TEXT NOT NULL,
    date_needed DATE NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create order_items table
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    consumable_id INT,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (consumable_id) REFERENCES consumables(id) ON DELETE CASCADE
);

-- Create admin_users table
CREATE TABLE admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit_logs table
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_username VARCHAR(100),
    action VARCHAR(255),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create laboratory table
CREATE TABLE laboratory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status ENUM('Active', 'Inactive', 'Maintenance') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create lab_assets table
CREATE TABLE lab_assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lab_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    status ENUM('Available', 'In Use', 'Maintenance', 'Retired') DEFAULT 'Available',
    purchase_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (lab_id) REFERENCES laboratory(id) ON DELETE CASCADE
);

-- Insert default admin user (password: admin123)
INSERT INTO admin_users (username, password) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.Gi');

-- Insert sample consumables
INSERT INTO consumables (name, description, category, quantity, image_url) VALUES
('Office Paper A4', 'High quality A4 paper for printing, 80gsm, 500 sheets per ream', 'Office Supplies', 500, '/static/images/paper.jpg'),
('Blue Pens', 'Blue ballpoint pens, pack of 10, smooth writing experience', 'Writing Supplies', 100, '/static/images/pens.jpg'),
('Stapler', 'Heavy duty stapler with 1000 staples included', 'Office Equipment', 25, '/static/images/stapler.jpg'),
('Notebooks', 'Spiral bound notebooks, A5 size, 100 pages, lined paper', 'Writing Supplies', 75, '/static/images/notebooks.jpg'),
('USB Cables', 'USB Type-C cables, 1m length, high-speed data transfer', 'Electronics', 50, '/static/images/usb.jpg'),
('Whiteboard Markers', 'Dry erase markers, pack of 8 colors, low odor', 'Office Supplies', 30, '/static/images/markers.jpg'),
('Paper Clips', 'Assorted paper clips, 100 pieces per box', 'Office Supplies', 200, '/static/images/paperclips.jpg'),
('Scissors', 'Office scissors, 8-inch blade, comfortable grip', 'Office Equipment', 15, '/static/images/scissors.jpg'),
('Sticky Notes', 'Post-it notes, 3x3 inches, 100 sheets per pad', 'Office Supplies', 40, '/static/images/stickynotes.jpg'),
('Calculator', 'Basic desktop calculator with 12-digit display', 'Electronics', 20, '/static/images/calculator.jpg'),
('File Folders', 'Manila file folders, letter size, 100 per box', 'Office Supplies', 150, '/static/images/folders.jpg'),
('Desk Lamp', 'LED desk lamp with adjustable brightness', 'Office Equipment', 10, '/static/images/desklamp.jpg');

-- Insert sample orders
INSERT INTO orders (user_name, department, purpose, date_needed, status) VALUES
('John Smith', 'IT Department', 'Office supplies for new team members', '2024-01-15', 'Pending'),
('Sarah Johnson', 'HR Department', 'Training materials for onboarding', '2024-01-20', 'Approved'),
('Mike Wilson', 'Marketing', 'Promotional materials for campaign', '2024-01-25', 'Pending'),
('Lisa Brown', 'Finance', 'Office equipment for new branch', '2024-01-30', 'Rejected');

-- Insert sample order items
INSERT INTO order_items (order_id, consumable_id, quantity) VALUES
(1, 1, 5),  -- 5 reams of paper
(1, 2, 2),  -- 2 packs of pens
(1, 4, 3),  -- 3 notebooks
(2, 1, 2),  -- 2 reams of paper
(2, 4, 5),  -- 5 notebooks
(2, 6, 1),  -- 1 pack of markers
(3, 1, 3),  -- 3 reams of paper
(3, 5, 2),  -- 2 packs of paper clips
(3, 9, 4),  -- 4 pads of sticky notes
(4, 7, 1),  -- 1 pair of scissors
(4, 8, 2);  -- 2 pads of sticky notes

-- Insert sample audit logs
INSERT INTO audit_logs (admin_username, action, details) VALUES
('admin', 'System Setup', 'Database initialized with sample data'),
('admin', 'Login', 'Admin admin logged in'),
('admin', 'Add Consumable', 'Added: Office Paper A4'),
('admin', 'Edit Consumable', 'Edited: Blue Pens'),
('admin', 'Approve Order', 'Approved order #2');

-- Create indexes for better performance
CREATE INDEX idx_consumables_category ON consumables(category);
CREATE INDEX idx_consumables_name ON consumables(name);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_user_name ON orders(user_name);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_consumable_id ON order_items(consumable_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_admin_username ON audit_logs(admin_username);

-- Show table structure
DESCRIBE consumables;
DESCRIBE orders;
DESCRIBE order_items;
DESCRIBE admin_users;
DESCRIBE audit_logs;

-- Show sample data
SELECT 'Consumables' as table_name, COUNT(*) as record_count FROM consumables
UNION ALL
SELECT 'Orders', COUNT(*) FROM orders
UNION ALL
SELECT 'Order Items', COUNT(*) FROM order_items
UNION ALL
SELECT 'Admin Users', COUNT(*) FROM admin_users
UNION ALL
SELECT 'Audit Logs', COUNT(*) FROM audit_logs; 