# Recipe API

See the [project README](../README.md) for deployment, database upgrades, backups, and development.

- `GET /api/auth/me`: current hub account or `null`.
- `POST /api/auth/register`: create a shared hub account and start a session (username and password; password 8–72 UTF-8 bytes).
- `POST /api/auth/login`, `POST /api/auth/logout`: site session in an HTTP-only cookie.
- `GET /api/recipes/`: public roots plus the logged-in user's private roots, with nested parts. Optional `category`, repeated `tags` (AND), and `favourites=true` filters. Favourites require login.
- `GET /api/recipes/{id}`: permission-checked recipe or part.
- `POST /api/recipes/`: create an owned recipe (`is_public` defaults to `true`).
- `PUT /api/recipes/{id}`, `DELETE /api/recipes/{id}`: owner-only root management.
- `POST /api/recipes/{id}/image`: owner-only multipart upload, field `image`.
- `GET /api/recipes/{id}/image`: permission-checked image, never publicly cached.
- `DELETE /api/recipes/{id}/image`: remove image reference.
- `GET /api/tags/`: suggested tags plus tags belonging to accessible root recipes, deduplicated by case.
- `PUT /api/recipes/{id}/favourite`: idempotently star an accessible main recipe for the current user.
- `DELETE /api/recipes/{id}/favourite`: remove the current user's star.

All state-changing requests require the configured `Origin`. Unknown/inaccessible recipes return 404; writes to another user's public recipe return 403. Parts inherit access from the root and are edited through the root. Legacy `/recipes` and `/tags` routes have the same access rules; standalone tag mutation endpoints have been removed. New tags are saved as part of an owned recipe. The migrated recipes retain their existing visibility and owner IDs. Owners can change the category, tags, and base portion count for their recipes. Responses include `category`, `servings`, and the current user's `is_favourite` flag.

When editing, send each existing part's `id` to preserve its identity and image. New parts omit `id`. IDs from other recipes and duplicate IDs are rejected. Removing a part from the payload deletes it. New recipes cannot reuse existing part IDs.

Request example:

```json
{
  "title": "Kuchen",
  "instructions": "Backen.",
  "is_public": true,
  "category": "Nachspeise",
  "servings": 4,
  "ingredients": [{"amount": 250, "unit": "g", "ingredient": "Mehl"}],
  "tags": ["süß"],
  "parts": [{"title": "Glasur", "instructions": "Verrühren.", "ingredients": []}]
}
```
