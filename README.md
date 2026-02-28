# Mama's Rezepte

Eine Vue.js Webanwendung zur Anzeige von Mama's Rezepten.

## Funktionen

- 📋 Übersicht aller Rezepte
- 🔍 Suchfunktion für Rezepte und Zutaten
- 📖 Detailansicht für jedes Rezept
- 🇩🇪 Komplett auf Deutsch
- 🐳 Docker-Container für einfache Bereitstellung

## Schnellstart

```bash
# Anwendung starten
make up

# Alternative:
docker-compose up frontend
```

Die Anwendung ist dann unter http://localhost:8050 verfügbar.

## Befehle

- `make up` - Startet die Anwendung
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
- **Webserver**: Nginx
