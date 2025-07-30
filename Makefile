.PHONY: dev up build down clean logs install

# Start development environment
dev:
	docker-compose --profile dev up backend-dev frontend-dev -d

# Start production environment
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

# Install dependencies in development
install:
	cd frontend && npm install
