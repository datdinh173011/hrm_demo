# HRM Contact Management System

A comprehensive Human Resource Management API for contact management with flexible property-based attributes, built with Django REST Framework.

## Features

- **Dynamic Property System**: Flexible contact attributes with different property types (text, textarea, options)
- **Dynamic API Filtering**: Filter by any contact property using URL parameters
- **Flexible Display Control**: Choose which fields to display using the `display` parameter
- **Type-Aware Search**: Automatically handles different property types (text, textarea, options)
- **Rate Limited**: Protected against abuse with configurable rate limits
- **OpenAPI Documentation**: Interactive API documentation with Swagger/ReDoc
- **Bulk Data Operations**: Efficient handling of millions of contact records
- **Comprehensive Admin Interface**: Full Django admin integration

## Tech Stack

- **Backend**: Django 5.0.2, Django REST Framework 3.14.0
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: JWT with SimpleJWT
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Rate Limiting**: Custom middleware implementation
- **Testing**: Django TestCase with comprehensive coverage

## Project Structure

```
hrm_demo/
├── config/                 # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py           # URL routing
│   └── middleware.py     # Rate limiting middleware
├── contacts/              # Contact management app
│   ├── models/           # Database models
│   ├── views/            # API views
│   ├── serializers/      # DRF serializers
│   ├── admin/            # Django admin
│   ├── management/       # Custom commands
│   └── tests.py          # Unit tests
├── users/                 # User management
├── scripts/              # Automation scripts
├── docker-compose.yml    # Docker configuration
└── requirements.txt      # Python dependencies
```

## Quick Start

### Using Docker (Recommended)

1. **Clone and start the application:**
   ```bash
   git clone <repository-url>
   cd hrm_demo
   docker-compose up --build
   ```

2. **The docker-compose will automatically:**
   - Set up the database
   - Run migrations
   - Initialize default properties
   - Generate sample data
   - Run unit tests
   - Start the development server

3. **Access the application:**
   - API: http://localhost:8000/api/v1/contacts/
   - Admin: http://localhost:8000/admin/
   - API Docs: http://localhost:8000/api/docs/
   - ReDoc: http://localhost:8000/api/redoc/

### Manual Setup

1. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database setup:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Initialize data:**
   ```bash
   # Initialize default properties
   python manage.py initproperty
   
   # Generate sample data (optional)
   python manage.py fake_millions_contact 1000
   ```

4. **Run the server:**
   ```bash
   python manage.py runserver
   ```

## API Usage

### Authentication

The API supports multiple authentication methods:
- JWT Bearer tokens (recommended)
- Session authentication
- Token authentication

**Get JWT Token:**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### Contact API Examples

**List all contacts:**
```bash
curl http://localhost:8000/api/v1/contacts/
```

**Filter by properties:**
```bash
curl "http://localhost:8000/api/v1/contacts/?department=it&status=active"
```

**Search across all properties:**
```bash
curl "http://localhost:8000/api/v1/contacts/?search=john"
```

**Control displayed fields:**
```bash
curl "http://localhost:8000/api/v1/contacts/?display=first_name,last_name,email,department"
```

**Pagination:**
```bash
curl "http://localhost:8000/api/v1/contacts/?page=2&page_size=20"
```

### API Response Format

```json
{
  "count": 1500,
  "next": "http://localhost:8000/api/v1/contacts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "created_at": "2023-01-15T10:30:00Z",
      "updated_at": "2023-01-15T10:30:00Z",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@company.com",
      "department": {
        "code": "it",
        "value": "IT Department",
        "id": "456e7890-e89b-12d3-a456-426614174001"
      },
      "status": {
        "code": "active",
        "value": "Active",
        "id": "789e0123-e89b-12d3-a456-426614174002"
      }
    }
  ]
}
```

## Property System

The system supports three types of properties:

### 1. Single Line Text (`singleline`)
- Simple text fields like names, emails, phone numbers
- Stored in `singleline_value` field
- Supports partial matching with `icontains`

### 2. Textarea (`textarea`)
- Long text fields like notes, descriptions
- Stored in `richtext_value` field
- Supports full-text search

### 3. Options (`option`)
- Select fields with predefined choices
- Linked to `Option` model with code/value pairs
- Stored in `singleoption_value` field
- Supports filtering by both code and display value

## Rate Limiting

The API includes built-in rate limiting:
- **Contact API**: 100 requests per 5 minutes
- **General API**: 200 requests per 5 minutes
- **Admin**: 50 requests per 5 minutes

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: When the limit resets

## Management Commands

### Initialize Properties
```bash
python manage.py initproperty
```
Creates default contact properties: first_name, last_name, email, phone_number, location, department, status.

### Generate Fake Data
```bash
# Generate 1000 contacts
python manage.py fake_millions_contact 1000

# Generate 1 million contacts
python manage.py fake_millions_contact 1000000

# With custom batch size and reset
python manage.py fake_millions_contact 1000000 --batch-size 500 --reset
```

## Testing

### Run All Tests
```bash
python manage.py test
```

### Run Contact Tests Only
```bash
python manage.py test contacts
```

### Run Specific Test Class
```bash
python manage.py test contacts.tests.ContactListAPIViewTest
```

### Run with Coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Using Docker
```bash
docker-compose run --rm web python manage.py test
```

## Development

### Database Schema

**Core Models:**
- `Contact`: Main contact entity with audit fields
- `Property`: Defines available contact attributes
- `Option`: Values for option-type properties
- `ContactProperty`: Links contacts to their property values

**Key Features:**
- UUID primary keys for security
- Audit trail (created_by, changed_by, timestamps)
- Flexible property system supporting multiple data types
- Optimized queries with prefetch_related

### Adding New Property Types

1. Update `Property.TYPE_CHOICES` in `contacts/models/property.py`
2. Add corresponding field to `ContactProperty` model
3. Update filtering logic in `contacts/views/contact.py`
4. Update serializer in `contacts/serializers/contact.py`

### Performance Considerations

- Uses `bulk_create` for efficient data insertion
- Implements `prefetch_related` for optimized queries
- Database indexes on frequently queried fields
- Pagination to handle large datasets
- Rate limiting to prevent abuse

## Deployment

### Production Settings

1. **Environment Variables:**
   ```bash
   DJANGO_SECRET_KEY=your-secret-key
   DJANGO_DEBUG=False
   DATABASE_URL=postgresql://user:pass@localhost/dbname
   ALLOWED_HOSTS=yourdomain.com
   ```

2. **Database Migration:**
   ```bash
   python manage.py migrate
   python manage.py initproperty
   python manage.py collectstatic
   ```

3. **Using PostgreSQL:**
   Update `DATABASES` setting in `settings.py` and install `psycopg2-binary`.

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python manage.py test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the API documentation at `/api/docs/`
- Review the test cases in `contacts/tests.py`
- Open an issue in the repository

## Changelog

### v1.0.0
- Initial release with dynamic property system
- REST API with filtering and search
- Rate limiting and security features
- Comprehensive test suite
- Docker support
- OpenAPI documentation