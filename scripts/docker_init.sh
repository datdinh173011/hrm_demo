#!/bin/bash

# HRM Demo - Docker Initialization Script
# This script runs inside the Docker container to set up the application

set -e

echo "=== Setting up HRM Contact Management System ==="

# Step 1: Wait for database to be ready
echo "1. Waiting for database to be ready..."
while ! pg_isready -h db -p 5432 -U postgres; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo "PostgreSQL is ready!"

# Step 2: Run database migrations
echo "2. Running database migrations..."
python manage.py migrate

# Step 3: Create superuser
echo "3. Creating superuser (admin/admin123)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123');
    print('Superuser created: admin/admin123');
else:
    print('Superuser already exists')
"

# Step 4: Initialize properties
echo "4. Initializing default properties..."
python manage.py initproperty

# Step 5: Generate sample data
echo "5. Generating sample data (1000 contacts)..."
python manage.py fake_millions_contact 1000

# Step 6: Run tests
echo "6. Running unit tests..."
python manage.py test contacts.tests.ContactListAPIViewTest -v 2

# Step 7: Display access information
echo "=== Setup Complete! ==="
echo ""
echo "HRM Contact Management System is ready!"
echo ""
echo "Access your application:"
echo "- API: http://localhost:8000/api/v1/contacts/"
echo "- Admin: http://localhost:8000/admin/ (admin/admin)"
echo "- API Docs: http://localhost:8000/api/docs/"
echo "- ReDoc: http://localhost:8000/api/redoc/"
echo ""

# Step 8: Start the development server
echo "7. Starting development server..."
python manage.py runserver 0.0.0.0:8000