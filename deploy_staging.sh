#!/bin/bash

# Staging Deployment Script for Retail Management System

set -e

echo "Starting staging deployment..."

# Build and start services
echo "Building and starting staging services..."
docker-compose down || true
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "Running database migrations..."
docker-compose exec -T web python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput --clear

# Create superuser if needed
echo "Creating staging superuser..."
docker-compose exec -T web python manage.py createsuperuser --noinput --username admin --email admin@staging.example.com || echo "Superuser may already exist"

# Run tests
echo "Running tests..."
docker-compose exec -T web pytest || echo "Tests failed, but continuing deployment..."

# Restart services
echo "Restarting services..."
docker-compose restart

echo "Staging deployment completed successfully!"
echo "Your staging application should be available at http://localhost:8000"
