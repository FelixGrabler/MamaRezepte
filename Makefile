.PHONY: up build down clean logs install

# Start the application
up:
	docker-compose up backend frontend

# Build Docker images
build:
	docker-compose build

# Stop all containers
down:
	docker-compose down

# Clean up containers and images
clean:
	docker-compose down -v --rmi all

# Show logs
logs:
	docker-compose logs -f

# Install frontend dependencies
install:
	cd frontend && npm install
