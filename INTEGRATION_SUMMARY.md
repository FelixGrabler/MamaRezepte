# Integration status

The previous SQLite-backed API has been replaced by an owned-recipe API with PostgreSQL, hub account validation, private recipe access, nested recipe parts, and image uploads. Existing SQLite data is imported once without modifying the source. All imported recipes remain public and are assigned to the verified hub account `felix`. Categories, editable tags, personal favourites, and base portion counts are stored in PostgreSQL. The frontend filters the collection and scales viewed ingredient quantities across all recipe parts.

See [README.md](README.md) for the current architecture, deployment instructions, backup/restore workflow, and verification commands. The Cloudflared Tunnel connects directly to the frontend container. Its Nginx handles API routing and photo upload limits; the hub proxy requires no changes.
