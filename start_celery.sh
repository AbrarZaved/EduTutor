#!/bin/bash

# Quick Start Script for EduTutor with Celery
# This script starts all necessary services

echo "=========================================="
echo "EduTutor Celery Quick Start"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "Activating virtual environment..."
    source myenv/bin/activate
fi

# Check if Redis is running
echo "Checking Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running"
    echo "Please start Redis with: redis-server"
    exit 1
fi

echo ""
echo "=========================================="
echo "To run the application, open 3 terminals:"
echo "=========================================="
echo ""
echo "Terminal 1 - Django Server:"
echo "  source myenv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Terminal 2 - Celery Worker:"
echo "  source myenv/bin/activate"
echo "  celery -A EduTutor worker --loglevel=info --pool=solo"
echo ""
echo "Terminal 3 - Celery Beat (optional):"
echo "  source myenv/bin/activate"
echo "  celery -A EduTutor beat --loglevel=info"
echo ""
echo "=========================================="
echo "Monitoring (optional):"
echo "=========================================="
echo ""
echo "Install and run Flower for web monitoring:"
echo "  pip install flower"
echo "  celery -A EduTutor flower"
echo "  Open: http://localhost:5555"
echo ""
