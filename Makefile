.PHONY: dev up build down clean logs install convert-db

# Start development environment
dev:
	docker-compose --profile dev up backend-dev frontend-dev

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

# Convert JSON to SQLite database
convert-db:
	cd backend && python scripts/convert_json_to_db.py

# Setup database (create directories and convert)
setup-db:
	mkdir -p data
	cd backend && python scripts/convert_json_to_db.py
