# Mama's Rezepte

Eine Vue.js Webanwendung zur Anzeige von Mama's Rezepten.

## Funktionen

- 📋 Übersicht aller Rezepte
- 🔍 Suchfunktion für Rezepte und Zutaten
- 📖 Detailansicht für jedes Rezept
- 🇩🇪 Komplett auf Deutsch
- 🐳 Docker-Container für einfache Bereitstellung

## Schnellstart

### Entwicklung

```bash
# Entwicklungsumgebung starten
make dev

# Alternative:
docker-compose --profile dev up frontend-dev
```

Die Anwendung ist dann unter http://localhost:5173 verfügbar.

### Produktion

```bash
# Produktionsumgebung starten
make up

# Alternative:
docker-compose up frontend
```

Die Anwendung ist dann unter http://localhost:3000 verfügbar.

## Befehle

- `make dev` - Startet die Entwicklungsumgebung
- `make up` - Startet die Produktionsumgebung
- `make build` - Baut die Docker Images
- `make down` - Stoppt alle Container
- `make clean` - Entfernt alle Container und Images

## Datenstruktur

Die Rezepte werden aus `data/recipes.json` geladen. Jedes Rezept hat folgende Struktur:

```json
{
  "title": "Rezeptname",
  "ingredients": ["Zutat 1", "Zutat 2"],
  "instructions": "Zubereitungsanleitung",
  "parent_recipe": null
}
```

## Technologie-Stack

- **Frontend**: Vue.js 3 + Vue Router
- **Build-Tool**: Vite
- **Container**: Docker + Docker Compose
- **Webserver**: Nginx (Produktion)
