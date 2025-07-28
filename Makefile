.PHONY: dev up build down clean logs

# Start development environment
dev:
	docker-compose --profile dev up frontend-dev

# Start production environment
up:
	docker-compose up frontend

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

# Install dependencies in development
install:
	cd frontend && npm install
