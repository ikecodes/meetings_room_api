#!/bin/bash

# Docker development helper script

case "$1" in
    "start")
        echo "🚀 Starting FastAPI in development mode..."
        docker-compose --profile dev up api-dev
        ;;
    "build")
        echo "🔨 Building Docker image..."
        docker-compose build
        ;;
    "test")
        echo "🧪 Running tests..."
        docker-compose --profile test run --rm test
        ;;
    "prod")
        echo "🌟 Starting in production mode..."
        docker-compose up api
        ;;
    "stop")
        echo "⏹️  Stopping all services..."
        docker-compose down
        ;;
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker-compose down --volumes --remove-orphans
        docker system prune -f
        ;;
    *)
        echo "Usage: $0 {start|build|test|prod|stop|clean}"
        echo ""
        echo "Commands:"
        echo "  start  - Start development server with hot reload"
        echo "  build  - Build Docker image"
        echo "  test   - Run test suite"
        echo "  prod   - Start production server"
        echo "  stop   - Stop all services"
        echo "  clean  - Clean up Docker resources"
        exit 1
        ;;
esac