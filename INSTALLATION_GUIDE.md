# ProTrack-RPT Installation Guide

## Overview
ProTrack-RPT is a comprehensive Inventory & Consumable Asset Management System built with Python Flask and MySQL. This guide will help you set up the system on your local machine using XAMPP.

## Prerequisites
- Windows 10/11 (or compatible OS)
- XAMPP (with Apache and MySQL)
- Python 3.8 or higher
- pip (Python package installer)

## Step 1: Install XAMPP
1. Download XAMPP from [https://www.apachefriends.org/](https://www.apachefriends.org/)
2. Run the installer and follow the setup wizard
3. Ensure both Apache and MySQL are selected during installation
4. Complete the installation

## Step 2: Start XAMPP Services
1. Open XAMPP Control Panel
2. Start Apache and MySQL services
3. Verify both services are running (green status)

## Step 3: Create Database
1. Open your web browser and go to `http://localhost/phpmyadmin`
2. Click "New" to create a new database
3. Enter database name: `protrack_rpt`
4. Click "Create"
5. Select the `protrack_rpt` database
6. Go to "Import" tab
7. Choose the `database_schema.sql` file from this project
8. Click "Go" to import the database structure and sample data

## Step 4: Install Python Dependencies
1. Open Command Prompt or PowerShell
2. Navigate to the project directory:
   ```bash
   cd "C:\Users\mazim\Desktop\ProTrack Tumba"
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Step 5: Configure Database Connection
1. Open `app.py` in a text editor
2. Verify the database configuration matches your XAMPP setup:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': '',
       'database': 'protrack_rpt'
   }
   ```
3. If you've set a MySQL root password, update the `password` field

## Step 6: Run the Application
1. In the project directory, run:
   ```bash
   python app.py
   ```
2. The application will start and initialize the database
3. Open your web browser and go to `http://localhost:5000`

## Step 7: Access the System
1. **Public Access**: Browse consumables, add items to cart, and place orders
2. **Admin Access**: Go to `http://localhost:5000/admin/login`
   - Username: `admin`
   - Password: `admin123`

## Default Data
The system comes with sample data:
- **Sample Consumables**: Office supplies, writing materials, electronics
- **Sample Orders**: Various order examples with different statuses
- **Admin User**: Default admin account for system management

## Features Available

### Public Users (No Login Required)
- Browse consumables with search and filtering
- Add items to shopping cart
- Place orders with user details
- View order status

### Admin Users (Login Required)
- Dashboard with system statistics
- Manage inventory (add, edit, delete items)
- Review and approve/reject orders
- Export data to CSV/Excel
- View audit logs

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
- Ensure MySQL service is running in XAMPP
- Verify database name is correct
- Check if MySQL root password is set

#### 2. Port Already in Use
- Change the port in `app.py`:
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```

#### 3. Module Not Found Errors
- Ensure all dependencies are installed:
  ```bash
  pip install -r requirements.txt
  ```

#### 4. Permission Errors
- Run Command Prompt as Administrator
- Ensure write permissions in project directory

### Database Issues
- If tables aren't created, manually run the SQL commands from `database_schema.sql`
- Check MySQL error logs in XAMPP Control Panel

### Python Version Issues
- Ensure Python 3.8+ is installed and in PATH
- Use `python --version` to verify

## Security Considerations

### Production Deployment
- Change default admin password
- Set strong SECRET_KEY in environment variables
- Enable HTTPS
- Configure proper firewall rules
- Regular database backups

### Development Environment
- Keep XAMPP services stopped when not in use
- Don't expose the application to external networks
- Use strong passwords for development databases

## File Structure
```
ProTrack Tumba/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database_schema.sql    # Database structure
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Public home page
│   ├── cart.html        # Shopping cart
│   ├── place_order.html # Order placement
│   └── admin/           # Admin templates
│       ├── login.html   # Admin login
│       └── dashboard.html # Admin dashboard
└── INSTALLATION_GUIDE.md # This file
```

## Support and Maintenance

### Regular Tasks
- Monitor database performance
- Review audit logs for suspicious activity
- Backup database regularly
- Update dependencies as needed

### Monitoring
- Check XAMPP service status
- Monitor application logs
- Review system statistics in admin dashboard

## Additional Resources
- Flask Documentation: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- MySQL Connector Documentation: [https://dev.mysql.com/doc/connector-python/en/](https://dev.mysql.com/doc/connector-python/en/)
- Bootstrap 5 Documentation: [https://getbootstrap.com/docs/5.3/](https://getbootstrap.com/docs/5.3/)

## License
This project is provided as-is for educational and development purposes.

---

**Note**: This is a development system. For production use, implement proper security measures, error handling, and monitoring systems. 