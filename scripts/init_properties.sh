#!/bin/bash

# HRM Demo - Initialize Properties Script
# This script initializes default contact properties

set -e

echo "========================================"
echo "HRM Demo - Initialize Properties"
echo "========================================"

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the project root directory."
    exit 1
fi

echo "Initializing default contact properties..."

# Run the management command
python manage.py initproperty

if [ $? -eq 0 ]; then
    echo "✅ Properties initialized successfully!"
    echo ""
    echo "Default properties created:"
    echo "- first_name (singleline)"
    echo "- last_name (singleline)"
    echo "- email (singleline)"
    echo "- phone_number (singleline)"
    echo "- location (singleline)"
    echo "- department (option)"
    echo "- status (option)"
    echo ""
    echo "You can now generate fake data using: ./scripts/generate_fake_data.sh"
else
    echo "❌ Failed to initialize properties"
    exit 1
fi