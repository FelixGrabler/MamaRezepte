.PHONY: up build down clean logs install backup
up:
	docker compose up -d --build
build:
	docker compose build
down:
	docker compose down
# Preserve persistent recipe data even during cleanup.
clean:
	docker compose down --rmi local
logs:
	docker compose logs -f
install:
	cd frontend && npm ci
backup:
	docker compose exec backup /bin/sh /ops/backup.sh
