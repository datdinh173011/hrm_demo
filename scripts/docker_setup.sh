#!/bin/bash

# HRM Demo - Docker Setup Script
# This script builds and runs the application using Docker Compose

set -e

echo "========================================"
echo "HRM Demo - Docker Setup"
echo "========================================"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: docker-compose.yml not found. Please run this script from the project root directory."
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "Error: docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

echo "Building and starting HRM Demo with Docker..."
echo ""
echo "This will:"
echo "1. Build the Docker image"
echo "2. Start PostgreSQL database"
echo "3. Run migrations"
echo "4. Create admin user (admin/admin)"
echo "5. Initialize properties"
echo "6. Generate 1000 sample contacts"
echo "7. Run unit tests"
echo "8. Start the development server"
echo ""

# Build and start services
docker-compose up --build

echo ""
echo "========================================"
echo "🎉 Docker setup complete!"
echo "========================================"
echo ""
echo "Access your application:"
echo "- API: http://localhost:8000/api/v1/contacts/"
echo "- Admin: http://localhost:8000/admin/ (admin/admin)"
echo "- API Docs: http://localhost:8000/api/docs/"
echo "- ReDoc: http://localhost:8000/api/redoc/"
echo ""
echo "To stop the services:"
echo "docker-compose down"
echo ""
echo "To view logs:"
echo "docker-compose logs -f web"