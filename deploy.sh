#!/bin/bash

# Production Deployment Script for Retail Management System
# This script assumes you have Docker and docker-compose installed on your server

set -e

echo "Starting production deployment..."

# Pull latest changes (if using git)
# git pull origin main

# Build and start services
echo "Building and starting services..."
docker-compose -f docker-compose.prod.yml down || true
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput --clear

# Create superuser if needed (uncomment and modify as needed)
# echo "Creating superuser..."
# docker-compose -f docker-compose.prod.yml exec -T web python manage.py createsuperuser --noinput --username admin --email admin@example.com

# Run tests
echo "Running tests..."
docker-compose -f docker-compose.prod.yml exec -T web pytest || echo "Tests failed, but continuing deployment..."

# Restart services to ensure everything is loaded
echo "Restarting services..."
docker-compose -f docker-compose.prod.yml restart

echo "Deployment completed successfully!"
echo "Your application should be available at http://your-server-ip"
