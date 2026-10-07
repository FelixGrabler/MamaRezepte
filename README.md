# Mama's Rezepte

Vue 3 frontend, FastAPI backend, and PostgreSQL 16. Anonymous visitors can browse public recipes. Existing Grabler.me accounts can create, edit, and delete their own recipes. New recipes are public by default; private recipes, their parts, tags, and images are visible only to their owner.

## Deployment

The hub stack (`../grabler.me-hub`) must be running, with `shared-auth` on `grabler-network`. This app delegates login and account validation to that service over the internal network. It needs neither the hub signing secret nor access to the hub user database. Login uses the same account credentials; it does not automatically share sessions with other subdomains. Accounts are provisioned through the existing hub account management.

```sh
./scripts/setup-secrets.sh
cp .env.example .env
# Set BACKUP_DIR to a durable location on the server if desired.
docker compose up -d --build
```

Production URL: `https://rezepte.grabler.me`. Point the Cloudflared Tunnel at `http://mamarezepte-frontend:80` on `grabler-network`. The tunnel connects directly to the frontend container, so the hub proxy is not involved and needs no configuration changes. Nginx inside the frontend container serves the Vue application and forwards `/api/` to the backend; its configuration allows 20 MB photo uploads (22 MB request limit) and serves private images through the API. Host port `8050` is optional direct access; the tunnel uses the container port. The database and backend have no published host ports.

On first start, Postgres creates the database, the backend imports the existing collection once, and the backup service takes an initial snapshot. Sign in as `felix` to bind ownership and enable editing of the imported recipes. Later `docker compose up -d --build` runs keep the data and skip the completed import. `docker compose down` is optional when stopping the stack; `docker compose down -v` removes the recipe database and uploaded-photo volumes and is not part of setup or upgrades.

After setup, migration-only code, the old SQLite database, parsing scripts, and the secret-generation helper can be removed in a follow-up cleanup. Before removing the old image directory/mount, its photos must be moved into the permanent uploads volume and their database references updated, then backed up and checked. Keep the actual database secret and the recurring backup/restore tooling.

For HTTP access on localhost, set `SITE_ORIGIN=http://localhost:8050` and `COOKIE_SECURE=false`. Keep secure cookies enabled for HTTPS production. State-changing API requests require an `Origin` header equal to `SITE_ORIGIN`, including scripted requests.

## Existing recipes

The first startup imports all 88 records from `backend/data/recipes.db`, including the 10 recipe parts, ingredients, tags, image references, and original IDs. The import is transactional, protected against concurrent startup, and recorded in `migration_history`, so restarting never duplicates recipes. PostgreSQL ID sequences advance past the imported IDs. The original SQLite file stays mounted read-only and is not modified.

All existing recipes remain public and belong to the hub account `felix`. The import records this username; the first verified login/request by `felix` binds the recipes and their parts to his real hub user ID. Other accounts cannot claim the collection. Once bound, ownership stays attached to that ID. Felix can edit, tag, categorize, change visibility, or delete these recipes directly. There is no copy action. Original image files remain a read-only mount from `frontend/public/data/images`; uploaded photos are stored separately in the `recipe-uploads` Docker volume. Parts are submitted with the main recipe and inherit its owner, visibility, category, and base portion count. Part IDs are preserved when reordering/editing existing parts, including their image references.

## Categories, tags, favourites, and portions

Each recipe has one category: `Suppe`, `Hauptspeiße`, `Nachspeiße`, `Frühstück`, or `sonstiges`. The existing collection gets an initial classification, plus `Mama-Rezept` on each main recipe; Felix can adjust both. New recipes initially use `sonstiges` and four portions.

Owners can select existing tags or create new ones while editing their recipes. Suggested tags include `süß`, `Fleisch`, `vegetarisch`, and `Mama-Rezept`. Tags are deduplicated without regard to case. Tags used exclusively on someone else's private recipes do not appear in suggestions or filtering options.

The overview supports category, tag, text/ingredient search, and “Nur meine Rezepte” filters. Selecting several tags requires all selected tags. Logged-in users can star any recipe they can access. Stars persist in PostgreSQL per hub user ID and appear in the `Favouriten` menu; another user's favourites are not exposed. Recipes that become inaccessible also disappear from favourites. Deleting a recipe removes its favourites automatically.

Each recipe stores the number of portions its ingredient amounts were written for. It defaults to four and is editable by the owner. The detail view starts at that count; its +/− buttons or numeric input change the viewed portion count and scale all numeric ingredient amounts, including those in recipe parts. Units and ingredient descriptions stay unchanged. Ingredients without an amount (such as salt to taste) stay unchanged. Viewing another portion count does not save changes; resetting or reopening restores the recipe's base count.

## Photos

The API accepts JPEG, PNG, and WebP images up to 20 MB. It validates the decoded image, applies EXIF rotation, limits the longest edge to 1,600 pixels, and re-encodes as JPEG at quality 82. EXIF/GPS metadata is discarded. Uploaded images are served through permission-checked recipe endpoints, with `private, no-store` cache headers. There is no public uploads directory.

Replacing/removing a photo or deleting its recipe removes its API reference. The old file is retained in the volume to keep concurrent database/image backups consistent; it cannot be fetched through the API once unreferenced. For this small site, storage grows with all uploaded photos. Offline cleanup can be added if that ever becomes significant.

## Backups and recovery

The backup service takes an initial snapshot, then one every seven days, keeping the latest eight completed snapshots. It checks hourly and catches up on startup. Each snapshot includes `database.dump`, `uploads.tar.gz`, and SHA-256 checksums. Failed snapshots are not published or counted toward retention; failures retry hourly. `docker compose ps` reports the backup service unhealthy if the last success is over eight days old. Database, uploads, and snapshots live in separate storage locations.

```sh
make backup                      # Take an extra snapshot now
ls backups/                      # Or your configured BACKUP_DIR
./scripts/restore.sh 20261007T180000Z  # Use an actual snapshot name
```

Restore verifies checksums, stops backend writes and the scheduler, restores images, then restores the database in one transaction. The backend and backup service restart only after success. A failed restore leaves both stopped for investigation. Do not restore while another backend instance is writing to this database.

`BACKUP_DIR` defaults to a host bind mount at `./backups`, so deleting the Postgres Docker volume does not delete these snapshots. Copy this directory to another machine periodically if you also want recovery from host/disk loss. Keep the repository's original image directory and SQLite file. These snapshots cover recipe data, categories, tags, base portion counts, personal favourites, and uploads; the hub's user database and credentials are managed and backed up separately. Restored recipe ownership relies on those same hub user IDs.

`make down` and `make clean` preserve data volumes. Avoid `docker compose down -v` unless intentionally deleting application data.

## Local development and checks

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt -r backend/requirements-dev.txt
# Tests use a temporary SQLite database by default; hub responses are mocked.
.venv/bin/pytest -q backend/tests
# To exercise Postgres, use a dedicated empty test database:
DATABASE_URL=postgresql+psycopg://user:password@localhost/recipes_test .venv/bin/pytest -q backend/tests
# The recovery test requires pg_dump/pg_restore and flock on PATH and deletes/restores
# that TEST database schema. Never point tests at your production database.

cd frontend
npm ci
npm run build
npm run test:e2e  # Requires Chromium: npx playwright install chromium
```

For backend development, set `DATABASE_URL` to a development PostgreSQL database (or `sqlite:////absolute/path/to/dev.db`), `LEGACY_DATABASE` to the absolute path of `backend/data/recipes.db`, `LEGACY_IMAGES` to `frontend/public/data/images`, `UPLOAD_DIR` to a writable directory, `SITE_ORIGIN=http://localhost:5173`, and `COOKIE_SECURE=false`. Run `uvicorn app.main:app` from `backend/`; `npm run dev` proxies `/api` to port 8000. Point `AUTH_SERVICE_URL` at the running hub service.
