#!/bin/bash

# HRM Demo - Complete Setup Script
# This script runs all setup steps: init properties, generate data, and run tests

set -e

echo "========================================"
echo "HRM Demo - Complete Setup"
echo "========================================"

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Parse arguments
CONTACTS=${1:-1000}

echo "This script will:"
echo "1. Initialize default properties"
echo "2. Generate $CONTACTS fake contacts"
echo "3. Run the complete test suite"
echo ""

# Make scripts executable
chmod +x scripts/*.sh

# Step 1: Initialize properties
echo "Step 1: Initializing properties..."
./scripts/init_properties.sh

if [ $? -ne 0 ]; then
    echo "❌ Failed at step 1"
    exit 1
fi

# Step 2: Generate fake data
echo ""
echo "Step 2: Generating fake data..."
./scripts/generate_fake_data.sh $CONTACTS

if [ $? -ne 0 ]; then
    echo "❌ Failed at step 2"
    exit 1
fi

# Step 3: Run tests
echo ""
echo "Step 3: Running tests..."
./scripts/run_tests.sh

if [ $? -ne 0 ]; then
    echo "❌ Failed at step 3"
    exit 1
fi

echo ""
echo "========================================"
echo "🎉 Complete setup finished successfully!"
echo "========================================"
echo ""
echo "Your HRM Demo is ready to use:"
echo "- API: http://localhost:8000/api/v1/contacts/"
echo "- Admin: http://localhost:8000/admin/"
echo "- API Docs: http://localhost:8000/api/docs/"
echo "- ReDoc: http://localhost:8000/api/redoc/"
echo ""
echo "To start the server:"
echo "python manage.py runserver"