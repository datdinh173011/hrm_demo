#!/bin/bash

# HRM Demo - Generate Fake Data Script
# This script generates fake contact data for testing

set -e

echo "========================================"
echo "HRM Demo - Generate Fake Data"
echo "========================================"

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Default number of contacts
CONTACTS=${1:-1000}

# Validate input
if ! [[ "$CONTACTS" =~ ^[0-9]+$ ]] || [ "$CONTACTS" -lt 1 ]; then
    echo "Error: Please provide a valid number of contacts (positive integer)"
    echo "Usage: $0 [number_of_contacts]"
    echo "Example: $0 5000"
    exit 1
fi

echo "Generating $CONTACTS fake contacts..."
echo "This may take a while for large numbers..."
echo ""

# Start timing
start_time=$(date +%s)

# Run the management command
python manage.py fake_millions_contact $CONTACTS

if [ $? -eq 0 ]; then
    # Calculate duration
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo ""
    echo "✅ Successfully generated $CONTACTS contacts!"
    echo "⏱️  Time taken: ${duration} seconds"
    echo ""
    echo "You can now:"
    echo "- View contacts in admin: http://localhost:8000/admin/"
    echo "- Test API: http://localhost:8000/api/v1/contacts/"
    echo "- Run tests: ./scripts/run_tests.sh"
else
    echo "❌ Failed to generate fake data"
    exit 1
fi