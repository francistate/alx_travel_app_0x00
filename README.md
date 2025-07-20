# ALX Travel App

A Django REST API application for managing travel listings, bookings, and reviews. This project implements robust APIs following Django best practices with comprehensive models, serializers, and database seeding capabilities.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Models](#models)
- [API Endpoints](#api-endpoints)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Seeding Data](#seeding-data)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)

## 🚀 Project Overview

The ALX Travel App is a comprehensive travel listing platform that allows users to:
- Create and manage property listings
- Make bookings for available properties
- Leave reviews and ratings for properties
- Search and filter listings by various criteria

This milestone focuses on creating robust data models, API serializers, and populating the database with sample data.

## ✨ Features

### Core Functionality
- **User Management**: User authentication and profile management
- **Listing Management**: Create, update, and manage property listings
- **Booking System**: Complete booking workflow with validation
- **Review System**: Rating and review system for properties
- **Data Validation**: Comprehensive validation for all models
- **Database Seeding**: Management command to populate sample data

### API Features
- RESTful API endpoints
- Nested serialization for related data
- Custom validation and error handling
- Proper HTTP status codes
- Comprehensive documentation via Swagger

## 🏗️ Models

### Listing Model
```python
class Listing(models.Model):
    listing_id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    max_guests = models.PositiveIntegerField()
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    # ... amenities and availability fields
```

**Key Features:**
- UUID primary keys for security
- Property type choices (apartment, house, hotel, villa, cabin)
- Amenities tracking (WiFi, parking, kitchen, pool, pets)
- Automatic timestamps
- Database indexing for performance
- Average rating calculation

### Booking Model
```python
class Booking(models.Model):
    booking_id = models.UUIDField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
```

**Key Features:**
- Status tracking (pending, confirmed, cancelled, completed)
- Date validation constraints
- Guest capacity validation
- Automatic price calculation
- Conflict detection for overlapping bookings

### Review Model
```python
class Review(models.Model):
    review_id = models.UUIDField(primary_key=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
```

**Key Features:**
- 1-5 star rating system
- One review per user per listing constraint
- Optional booking linkage
- Timestamp tracking

## 🌐 API Endpoints

### Listings
- `GET /api/listings/` - List all available listings
- `POST /api/listings/` - Create a new listing (authenticated users)
- `GET /api/listings/{id}/` - Retrieve specific listing details
- `PUT/PATCH /api/listings/{id}/` - Update listing (owner only)
- `DELETE /api/listings/{id}/` - Delete listing (owner only)

### Bookings
- `GET /api/bookings/` - List user's bookings
- `POST /api/bookings/` - Create a new booking
- `GET /api/bookings/{id}/` - Retrieve booking details
- `PUT/PATCH /api/bookings/{id}/` - Update booking
- `DELETE /api/bookings/{id}/` - Cancel booking

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create a review
- `GET /api/reviews/{id}/` - Retrieve review details
- `PUT/PATCH /api/reviews/{id}/` - Update review (author only)
- `DELETE /api/reviews/{id}/` - Delete review (author only)

## 🛠️ Installation

### Prerequisites
- Python 
- Django 
- Django REST Framework
- MySQL (configured in Milestone 1)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/your-username/alx_travel_app_0x00.git
cd alx_travel_app_0x00/alx_travel_app
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Create .env file with your database credentials
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Start development server**
```bash
python manage.py runserver
```

## 🗄️ Database Setup

The application uses MySQL as configured in Milestone 1. The models include:

### Database Features
- **UUID Primary Keys**: Enhanced security and scalability
- **Indexes**: Optimized query performance on frequently searched fields
- **Constraints**: Data integrity through database-level constraints
- **Relationships**: Proper foreign key relationships with cascade options

### Migration Commands
```bash
# Create migrations for the models
python manage.py makemigrations listings

# Apply migrations to database
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

## 🌱 Seeding Data

The application includes a comprehensive management command to populate the database with sample data.

### Using the Seed Command

```bash
# Seed with default amounts (20 listings, 50 bookings, 30 reviews)
python manage.py seed

# Seed with custom amounts
python manage.py seed --listings 50 --bookings 100 --reviews 75

# Clear existing data and reseed
python manage.py seed --clear --listings 30

# Get help on available options
python manage.py seed --help
```

### Sample Data Created
- **Users**: 8 sample users (4 hosts, 4 guests)
- **Listings**: Variety of property types across different cities
- **Bookings**: Random bookings with realistic date ranges
- **Reviews**: Authentic reviews with ratings 3-5 stars

## 📖 Usage Examples

### Creating a Listing
```python
POST /api/listings/
{
    "title": "Beachfront Condo",
    "description": "Beautiful oceanview condo with modern amenities",
    "location": "Miami Beach, FL",
    "price_per_night": "250.00",
    "property_type": "apartment",
    "max_guests": 4,
    "bedrooms": 2,
    "bathrooms": 2,
    "has_wifi": true,
    "has_parking": true,
    "has_kitchen": true,
    "has_pool": false,
    "allows_pets": false
}
```

### Making a Booking
```python
POST /api/bookings/
{
    "listing_id": "123e4567-e89b-12d3-a456-426614174000",
    "check_in_date": "2025-08-15",
    "check_out_date": "2025-08-20",
    "number_of_guests": 2,
    "special_requests": "Late check-in requested"
}
```

### Creating a Review
```python
POST /api/reviews/
{
    "listing": "123e4567-e89b-12d3-a456-426614174000",
    "rating": 5,
    "comment": "Amazing place! The view was spectacular and the host was very accommodating. Would definitely stay here again!"
}
```

## 📁 Project Structure

```
alx_travel_app/
├── alx_travel_app/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── listings/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── seed.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── requirements.txt
├── manage.py
└── README.md
```

## 🔧 Technologies Used

- **Django**: Web framework
- **Django REST Framework**: API development
- **MySQL**: Database
- **django-environ**: Environment variable management
- **django-cors-headers**: CORS handling
- **drf-yasg**: Swagger documentation
- **UUID**: Primary key generation


## 📚 API Documentation

The API is automatically documented using Swagger/OpenAPI. Access the documentation at:
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

