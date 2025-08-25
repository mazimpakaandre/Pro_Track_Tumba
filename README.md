# ProTrack-RPT - Inventory & Consumable Asset Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple.svg)](https://getbootstrap.com)

A comprehensive web-based inventory management system built with Python Flask and MySQL, designed for managing consumable assets with a user-friendly interface and robust admin controls.

## 🚀 Features

### Public User Features (No Login Required)
- **Browse Inventory**: View all available consumables with images and descriptions
- **Advanced Search**: Search and filter items by name, description, and category
- **Shopping Cart**: Session-based cart system for easy item selection
- **Order Management**: Place orders with detailed information (name, department, purpose, date needed)
- **Real-time Updates**: Live stock quantity updates and low stock warnings

### Admin Features (Secure Login Required)
- **Dashboard Analytics**: Comprehensive statistics and overview
- **Inventory Management**: Add, edit, delete consumables with full CRUD operations
- **Order Processing**: Review, approve, or reject orders with automatic stock updates
- **Data Export**: Export orders to CSV and inventory to Excel formats
- **Audit Trail**: Complete logging of all admin actions for compliance
- **User Management**: Secure admin authentication system

### Technical Features
- **Responsive Design**: Bootstrap 5 powered mobile-first interface
- **Database Security**: Parameterized queries preventing SQL injection
- **CSRF Protection**: Built-in security for all forms
- **Session Management**: Secure cart and user session handling
- **Performance Optimized**: Efficient database queries with proper indexing

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: MySQL (via MySQL Connector)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Security**: bcrypt password hashing, CSRF protection
- **Data Export**: CSV and Excel (openpyxl) support
- **Authentication**: Session-based admin login system

## 📋 Requirements

- Python 3.8 or higher
- XAMPP (Apache + MySQL)
- pip package manager

## 🚀 Quick Start

### 1. Clone/Download Project
```bash
# Navigate to your desired directory
cd "C:\Users\mazim\Desktop\ProTrack Tumba"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
1. Start XAMPP (Apache + MySQL)
2. Create database `protrack_rpt` in phpMyAdmin
3. Import `database_schema.sql`

### 4. Run Application
```bash
python app.py
```

### 5. Access System
- **Public**: http://localhost:5000
- **Admin**: http://localhost:5000/admin/login
  - Username: `admin`
  - Password: `admin123`

## 📁 Project Structure

```
ProTrack Tumba/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database_schema.sql    # Database structure & sample data
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Public home page
│   ├── cart.html        # Shopping cart interface
│   ├── place_order.html # Order placement form
│   └── admin/           # Admin interface templates
│       ├── login.html   # Admin authentication
│       └── dashboard.html # Admin dashboard
├── INSTALLATION_GUIDE.md # Detailed setup instructions
└── README.md            # This file
```

## 🗄️ Database Schema

### Core Tables
- **consumables**: Inventory items with categories and quantities
- **orders**: User order requests with status tracking
- **order_items**: Individual items within orders
- **admin_users**: Admin authentication credentials
- **audit_logs**: Complete action logging for compliance

### Key Features
- Foreign key relationships ensuring data integrity
- Automatic timestamps for audit trails
- Enum status fields for order management
- Optimized indexes for performance

## 🔐 Security Features

- **Password Hashing**: bcrypt encryption for admin passwords
- **SQL Injection Prevention**: Parameterized queries throughout
- **CSRF Protection**: Built-in form security
- **Session Security**: Secure session management
- **Input Validation**: Comprehensive form validation
- **Audit Logging**: Complete action tracking

## 📊 Admin Dashboard

The admin dashboard provides:
- **Real-time Statistics**: Total items, orders, pending requests
- **Quick Actions**: Direct access to common tasks
- **Recent Orders**: Latest order activity
- **Low Stock Alerts**: Automatic warnings for inventory management
- **Export Tools**: Data export capabilities

## 🛒 Shopping Cart System

- **Session-based**: No database storage required
- **Persistent**: Maintains cart across page visits
- **Quantity Management**: Easy quantity adjustments
- **Stock Validation**: Prevents over-ordering
- **Clear Cart**: One-click cart clearing

## 📈 Order Management

- **Status Tracking**: Pending → Approved/Rejected workflow
- **Automatic Stock Updates**: Inventory reduction on approval
- **Department Organization**: Structured request management
- **Purpose Documentation**: Detailed reasoning for requests
- **Date Prioritization**: Urgency-based processing

## 🔄 Data Export

### Orders Export (CSV)
- Complete order details
- Item breakdowns
- Status information
- Timestamps and user data

### Inventory Export (Excel)
- All consumable items
- Stock quantities
- Categories and descriptions
- Formatted with proper styling

## 🎨 User Interface

- **Responsive Design**: Works on all device sizes
- **Modern UI**: Bootstrap 5 components and styling
- **Interactive Elements**: Modals, tooltips, and animations
- **Accessibility**: Proper ARIA labels and semantic HTML
- **User Experience**: Intuitive navigation and workflows

## 🚨 Error Handling

- **Database Errors**: Graceful fallbacks and user notifications
- **Validation Errors**: Clear feedback on form submissions
- **Stock Validation**: Prevents invalid order quantities
- **User Feedback**: Flash messages for all actions
- **Logging**: Comprehensive error logging for debugging

## 📱 Mobile Responsiveness

- **Mobile-First Design**: Optimized for small screens
- **Touch-Friendly**: Large buttons and touch targets
- **Responsive Tables**: Horizontal scrolling on mobile
- **Adaptive Layout**: Flexible grid system
- **Mobile Navigation**: Collapsible navigation menu

## 🔧 Configuration

### Database Settings
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'protrack_rpt'
}
```

### Application Settings
```python
app.secret_key = 'your-secret-key-change-in-production'
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 🚀 Deployment

### Development
- Run directly with `python app.py`
- Debug mode enabled
- Local database connection

### Production
- Use WSGI server (Gunicorn, uWSGI)
- Set production secret key
- Configure production database
- Enable HTTPS
- Set up proper logging

## 🧪 Testing

The system includes:
- **Form Validation**: Client and server-side validation
- **Database Integrity**: Foreign key constraints
- **Session Security**: Proper session handling
- **Error Scenarios**: Comprehensive error handling
- **User Flows**: Complete user journey testing

## 📚 API Endpoints

### Public Routes
- `GET /` - Home page with inventory
- `POST /add_to_cart` - Add item to cart
- `GET /cart` - View cart contents
- `POST /update_cart` - Update cart quantities
- `GET/POST /place_order` - Order placement

### Admin Routes
- `GET/POST /admin/login` - Admin authentication
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/inventory` - Inventory management
- `GET /admin/orders` - Order management
- `GET /admin/export/*` - Data export functions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and development purposes.

## 🆘 Support

For support and questions:
1. Check the installation guide
2. Review the troubleshooting section
3. Check error logs and console output
4. Verify database connectivity

## 🔮 Future Enhancements

- **Email Notifications**: Order status updates
- **Barcode Scanning**: Inventory management
- **Advanced Reporting**: Analytics and insights
- **Multi-language Support**: Internationalization
- **API Integration**: Third-party system connections
- **Mobile App**: Native mobile application

---

**Built with ❤️ using Flask, MySQL, and Bootstrap 5**

*ProTrack-RPT - Professional Inventory Management Made Simple* 