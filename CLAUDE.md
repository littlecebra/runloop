# Garmin Coach – Projekt-Instruktionen

Du arbeitest am Projekt "Garmin Coach" – ein lokales, KI-gestütztes Lauftraining-Analyse-System.

## Projektstruktur

- `skills/garmin_data.md` – Anleitung: Daten von Garmin abrufen, normalisieren, speichern
- `skills/garmin_coach.md` – Anleitung: Trainingsanalyse, adaptive Plansteuerung, Coach-Logik
- `config/athlete.json` – Persönliche Werte des Athleten (HF-Zonen, Gewicht, Coach-Typ, Zielrennen)
- `config/coach_types.json` – Alle verfügbaren Trainingsphilosophien
- `data/` – Alle persistierten Daten (Aktivitäten, History, Plan, Analyse, Recovery, Gewicht)
- `scripts/` – Standalone Python-Scripts (analyze.py, generate_report.py, push_workout.py)
- `web/` – Dashboard (HTML/CSS/JS, wird von generate_report.py generiert)

## MCP Server: Garmin Connect

Dieses Projekt nutzt den Garmin MCP Server: https://github.com/Taxuspt/garmin_mcp

### Konfiguration (MCP):
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

### Erster Start:
Beim ersten Aufruf eines Garmin-MCP-Tools wird nach Garmin Connect Credentials gefragt (E-Mail + Passwort). Diese werden lokal gecacht.

## Wichtige Regeln

1. **Lies `skills/garmin_data.md`** bevor du Daten von Garmin holst
2. **Lies `skills/garmin_coach.md`** bevor du Trainingspläne erstellst oder Analysen machst
3. **Bei jedem Garmin-Sync** immer auch Gewicht, Recovery-Daten und Training Status mitholen
4. **Dashboard-Design**: Dark Theme, Purple (#a855f7) / Pink (#f43f5e) Accent, Inter Font, keine Emojis als Icons
5. **Daten lokal persistieren** – die KI hat kein Gedächtnis zwischen Sessions, alles muss in `data/` stehen
6. **Scripts standalone lauffähig** halten (keine externen Python-Dependencies)
7. **Coach-Typ** aus `config/athlete.json` → `coach_typ.aktiv` beachten
8. **Workouts nur auf explizite Anfrage** zu Garmin pushen

## Typische Befehle

- "Neuer Lauf, analysiere alles" → garmin_data.md + analyze.py + Plan anpassen + Report generieren
- "Schau bei Garmin nach" → Sync: Aktivitäten + Gewicht + Recovery holen
- "Hole meine Daten ab [Datum]" → Initialer Import mit Auswahl-Dialog
- "Push den nächsten Workout" → Workout zu Garmin Connect hochladen + planen

## Design-Richtlinien (bei UI-Änderungen)

Falls die Skills `frontend-design` oder `ui-ux-pro-max` im Projekt vorhanden sind (unter `.kiro/skills/` oder `.kiro/steering/`), nutze sie. Falls nicht, halte dich an diese Regeln:

- Dark OLED Background (#050507), Surface (#0f0f14)
- Primary: #a855f7 (Lila), Accent: #f43f5e (Pink/Rose)
- Success: #10b981, Warning: #f59e0b
- Font: Outfit (Display) + JetBrains Mono (Daten/Zahlen) – serifenlos, mit Charakter
- Keine Emojis – SVG-Icons oder reine Typografie
- Tooltips für KPI-Erklärungen
- Chart.js 4.x für Visualisierungen
- Responsive: 375px / 768px / 1024px
- `prefers-reduced-motion` respektieren
- Atmosphäre: Subtile Gradient-Orbs + Noise-Textur im Hintergrund
- Hover: Glow-Effekte auf interaktiven Elementen
