# Retail Management System

A comprehensive Django-based enterprise solution for managing retail operations, built with Python 3.13 and Django 5.2.4. This system provides end-to-end functionality for inventory management, sales processing, human resources, procurement, and business analytics across multiple store locations.

## 🚀 Features

### Core Modules
- **🏪 Store Management**: Multi-store support with centralized management and local inventory tracking
- **📦 Inventory Management**: Real-time stock tracking, product categorization, brand management, and low-stock alerts
- **👥 Human Resources**: Employee lifecycle management, attendance tracking, payroll processing, and performance analytics
- **💰 Sales & POS**: Point-of-sale system with transaction processing, multiple payment methods, and receipt generation
- **🛒 Procurement**: Supplier relationship management, purchase order processing, and delivery tracking
- **🛍️ E-Commerce**: Online sales platform with customer accounts, shopping cart, and order fulfillment
- **📊 Reporting & Analytics**: Comprehensive business intelligence with customizable dashboards and export capabilities
- **🔐 Security**: Role-based access control, audit logging, and enterprise-grade security features

### Technical Features
- **Scalable Architecture**: Modular Django apps with clean separation of concerns
- **Database Support**: SQLite for development, PostgreSQL for production
- **Responsive UI**: Bootstrap 5.1.3 with Font Awesome icons and custom styling
- **API Ready**: RESTful API framework prepared for future integrations
- **Security First**: CSRF protection, SQL injection prevention, XSS protection, and HTTPS enforcement
- **Logging & Monitoring**: Comprehensive logging system with security, audit, performance, and error logs
- **Testing Suite**: Automated penetration testing, security scanning, and unit tests

## 📋 Requirements

- Python 3.11+ (compiled with Python 3.13)
- Django 5.2.4
- SQLite (development) or PostgreSQL (production)
- Bootstrap 5.1.3, Font Awesome 6.0.0

## 🛠️ Installation

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd retail_management_system
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv env
   .\env\Scripts\activate

   # macOS/Linux
   python -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000/`
   - Log in with your superuser credentials

### Production Deployment

For production deployment, see [Deployment & Configuration](RETAIL_MANAGEMENT_SYSTEM_COMPREHENSIVE_DOCUMENTATION.md#12-deployment--configuration) in the comprehensive documentation.

## 📖 Usage

### User Roles & Access

- **Super Admin**: Full system access and configuration
- **Store Manager**: Store operations, inventory, and sales management
- **HR Manager**: Employee management, attendance, and payroll
- **Procurement Officer**: Supplier and purchase order management
- **Sales Person**: Point-of-sale operations
- **Customer**: E-commerce access for online shopping

### Getting Started

1. **Initial Setup**: After installation, create stores, categories, and initial inventory
2. **Add Employees**: Set up HR module with employee records
3. **Configure Products**: Add products, brands, and categories
4. **Set Up Suppliers**: Create supplier relationships for procurement
5. **Start Operations**: Begin sales processing and inventory management

## 🏗️ System Architecture

The system follows a modular architecture with the following Django apps:

- `accounts`: User authentication and authorization
- `dashboards`: Main dashboard and landing pages
- `human_resources`: Employee, attendance, and payroll management
- `inventory`: Product and stock management
- `procurement`: Supplier and purchase order management
- `sales`: Sales transactions and customer orders
- `store_management`: Multi-store configuration
- `e_commerce`: Online sales platform
- `reporting`: Analytics and reporting
- `api`: RESTful API endpoints (framework ready)

## 📚 Documentation

### Quick References
- **[System Overview](RETAIL_MANAGEMENT_SYSTEM_COMPREHENSIVE_DOCUMENTATION.md)**: Complete system documentation
- **[Database Schema](DATABASE_SCHEMA.md)**: Database structure and relationships
- **[Security Protocols](SECURITY_PROTOCOLS.md)**: Security features and best practices
- **[Production Readiness](PRODUCTION_READINESS_ASSESSMENT.md)**: Deployment checklist

### Detailed Documentation
- **[Full System Documentation](RETAIL_MANAGEMENT_SYSTEM_FULL_DOCUMENTATION.md)**: Consolidated technical documentation
- **[System File Hierarchy](SYSTEM_FILE_HIERARCHY.md)**: Complete file structure
- **[System Flowcharts](SYSTEM_FLOWCHARTS.md)**: Business process diagrams
- **[Permissions Guide](PERMISSIONS_GUIDE.md)**: Access control and roles

### Module-Specific Guides
- **[Employee Management](EMPLOYEE_MANAGEMENT_COMPLETE.md)**: HR module documentation
- **[Payroll Views](PAYROLL_VIEWS_COMPLETE.md)**: Payroll processing guide
- **[Shared Styles](SHARED_STYLES_GUIDE.md)**: UI/UX guidelines

## 🔧 Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
- Follow Django best practices
- Use descriptive commit messages
- Maintain test coverage above 80%

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 🔒 Security

This system implements enterprise-grade security measures:

- **Authentication**: Django's robust authentication system
- **Authorization**: Role-based access control
- **Data Protection**: Encryption for sensitive data
- **Audit Logging**: Comprehensive activity logging
- **Penetration Testing**: Automated security testing suite

See [Security Protocols](SECURITY_PROTOCOLS.md) for detailed security information.

## 📞 Support

### Technical Support
- **Email**: support@retailmgmt.com
- **Phone**: +268 (7811) 7803
- **Hours**: Monday-Friday, 9:00 AM - 5:00 PM

### Documentation
- [User Manual](RETAIL_MANAGEMENT_SYSTEM_COMPREHENSIVE_DOCUMENTATION.md)
- [API Documentation](api/) - Framework ready
- [Troubleshooting Guide](RETAIL_MANAGEMENT_SYSTEM_COMPREHENSIVE_DOCUMENTATION.md#15-troubleshooting)

## 📈 Roadmap

### Current Status
- ✅ Core modules implemented
- ✅ Database schema finalized
- ✅ Security features deployed
- ✅ Production configuration ready
- 🔄 Testing in progress
- 🔄 Documentation completion

### Future Enhancements
- Mobile application development
- Advanced AI analytics
- Third-party integrations (accounting, CRM)
- Multi-language support
- Cloud-native deployment options

## 📄 License

This project is proprietary software. All rights reserved.

## 👥 Contributors

- Thembinkosi and Team

---

**Version**: 1.0.0  
**Last Updated**: September 2025  
**Django Version**: 5.2.4  
**Python Version**: 3.13
