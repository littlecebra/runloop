# RunLoop – Agent-Instruktionen

Dieses Dokument beschreibt das Projekt für KI-Agenten (OpenAI, Copilot, etc.).

## Projekt-Übersicht

"RunLoop" ist ein lokales Lauftraining-Analyse-System. Es nutzt einen MCP Server um Daten von Garmin Connect abzurufen, analysiert diese lokal und erstellt adaptive Trainingspläne.

## Architektur

```
Garmin Connect ←→ Garmin MCP Server ←→ KI-Agent ←→ Lokale Dateien (data/, config/)
                                                  ↓
                                          Scripts (Python) → Dashboard (HTML)
```

## Anleitungen (IMMER lesen bevor du handelst)

| Datei | Wann lesen |
|-------|-----------|
| `skills/garmin_data.md` | Bevor du Daten von Garmin holst oder Workouts pushst |
| `skills/garmin_coach.md` | Bevor du Analysen machst oder Trainingspläne erstellst |
| `config/athlete.json` | Für persönliche Werte (HF-Zonen, Gewicht, Coach-Typ) |
| `config/coach_types.json` | Für Trainingsphilosophie-Details |

## MCP Server Setup

### Garmin MCP (https://github.com/Taxuspt/garmin_mcp)

**Voraussetzung:** `uv` / `uvx` muss installiert sein (Python Package Manager).

**Konfiguration:**
```json
{
  "mcpServers": {
    "garmin": {
      "command": "uvx",
      "args": ["--python", "3.12", "--from", "git+https://github.com/Taxuspt/garmin_mcp", "garmin-mcp"]
    }
  }
}
```

**Erster Start:** Beim ersten Aufruf eines Garmin-Tools wird nach Credentials gefragt. Diese werden lokal gecacht.

## Regeln

1. **Garmin-Sync = immer alles holen**: Aktivitäten + Gewicht + Recovery + Training Status
2. **Design**: Dark Theme, Purple/Pink Accent, keine Emojis, SVG-Icons
3. **Design-Skills**: Falls `frontend-design` oder `ui-ux-pro-max` im Projekt vorhanden sind (unter `.kiro/skills/` oder `.kiro/steering/`), nutze sie bei UI-Änderungen. Falls nicht vorhanden, halte dich an das Design-System unten.
4. **Persistenz**: Alle Daten in `data/` als JSON – KI hat kein Gedächtnis zwischen Sessions
5. **Scripts**: Standalone lauffähig mit `python3 scripts/<name>.py`
6. **Coach-Typ**: Lies `config/athlete.json` → `coach_typ.aktiv` und wende die Regeln aus `config/coach_types.json` an
7. **Workouts**: Nur auf explizite Nutzer-Anfrage zu Garmin pushen

## Design-System

Falls die Skills `frontend-design` oder `ui-ux-pro-max` im Projekt vorhanden sind, nutze sie. Ansonsten gelten diese Regeln:

- Background: #050507 (OLED Dark)
- Surface: #0f0f14, Elevated: #1a1a22
- Primary: #a855f7 (Lila), Accent: #f43f5e (Pink)
- Text: #f0f0f5 (primary), #9d9daa (secondary), #5c5c6b (muted)
- Font: Outfit (Display, 300-900) + JetBrains Mono (Daten/Zahlen)
- Radius: 10-20px
- Charts: Chart.js 4.x
- Keine Emojis als UI-Icons
- Atmosphäre: Gradient-Orbs + Noise-Textur
- Hover: Purple-Glow auf interaktiven Elementen
