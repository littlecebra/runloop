# RunLoop – Lokales Lauftraining-Analyse-System

Ein KI-gestütztes, adaptives Trainingsanalyse-System, das über den [Garmin MCP Server](https://github.com/Taxuspt/garmin_mcp) Trainingsdaten abruft, analysiert und einen personalisierten Trainingsplan erstellt.

## Schnellstart

### Voraussetzungen

- **Python 3.10+** (für die Analyse-Scripts)
- **uv / uvx** (Python Package Manager für den MCP Server)
- **Ein KI-Tool** mit MCP-Support: Kiro, Claude Code, Cursor, oder ähnlich
- **Garmin Connect Account** mit aufgezeichneten Laufaktivitäten

### 1. uv installieren (falls nicht vorhanden)

```bash
# macOS
brew install uv

# Linux/macOS (alternativ)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Garmin MCP Server konfigurieren

Der MCP Server verbindet dein KI-Tool mit Garmin Connect. Füge folgende Konfiguration hinzu:

**Für Kiro** (`.kiro/settings/mcp.json` – User-Level oder Workspace-Level):
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

**Für Claude Desktop** (`claude_desktop_config.json`):
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

### 3. Garmin MCP erstmalig authentifizieren

Beim **ersten Aufruf** eines Garmin-MCP-Tools wirst du nach deinen Garmin Connect Credentials gefragt:
- E-Mail-Adresse (dein Garmin Connect Login)
- Passwort

Diese werden lokal gecacht – du musst sie nur einmal eingeben.

**Tipp:** Teste die Verbindung indem du die KI bittest:
> "Rufe mein Garmin-Profil ab" oder "Zeige meine letzte Aktivität"

Wenn das funktioniert, ist der MCP korrekt eingerichtet.

### 4. Persönliche Werte eintragen

**Option A: Setup-Wizard (empfohlen für Einsteiger)**

Öffne `web/setup.html` im Browser. Der Wizard führt dich durch 4 Schritte und generiert die fertige `config/athlete.json` als Download. Lege die Datei in `config/` ab.

**Option B: Manuell**

```bash
cp config/athlete.example.json config/athlete.json
```

Bearbeite `config/athlete.json` mit deinen persönlichen Werten (alle Felder sind kommentiert).

### 5. Initialer Daten-Import

Sage der KI:

> "Hole meine Laufdaten ab dem 01.01.2025"

Die KI wird:
1. Alle Aktivitäten im Zeitraum von Garmin laden
2. Dich fragen ob du alle oder eine Auswahl importieren möchtest
3. Die gewählten Aktivitäten mit allen Details speichern
4. Die erste Analyse durchführen

---

## Täglicher Workflow

Nach jedem Lauf reicht ein Satz:

> "Neuer Lauf heute, analysiere und aktualisiere alles."

Die KI führt dann automatisch aus:
1. Neue Aktivitäten + Gewicht + Recovery-Daten von Garmin holen
2. Rohdaten speichern
3. CTL/ATL/TSB, Trends, Verletzungsrisiko berechnen
4. Trainingsplan adaptiv anpassen
5. Dashboard neu generieren
6. Coach-Kommentar + nächste Einheit ausgeben

Weitere nützliche Befehle:
- "Schau bei Garmin nach neuen Daten" – Sync ohne neue Aktivität
- "Push den nächsten Workout zu Garmin" – Workout hochladen + planen
- "Gib mir die Wochen-Zusammenfassung" – Rückblick der Woche
- "Vergleiche meinen letzten Lauf mit dem vom [Datum]" – Fortschritt sehen

---

## Initialer Prompt (für neue Sessions)

Wenn du eine neue Chat-Session startest und die KI den Kontext nicht kennt, nutze diesen Prompt:

> Ich arbeite am Projekt "RunLoop" – ein lokales Lauftraining-Analyse-System.
> Lies bitte `skills/garmin_data.md` und `skills/garmin_coach.md` für die Anleitungen.
> Meine persönlichen Werte stehen in `config/athlete.json`.
> Alle Trainingsdaten liegen in `data/`.
> Bei Dashboard-Änderungen nutze das Dark Theme (Purple/Pink Accent, keine Emojis).
> Bei Garmin-Sync hole immer auch Gewicht, Recovery und Training Status mit.

---

## KI-Tool-Kompatibilität

Dieses Projekt enthält Instruktions-Dateien für verschiedene KI-Tools:

| Tool | Instruktions-Datei | Automatisch geladen? |
|------|-------------------|---------------------|
| **Kiro** | `.kiro/steering/garmin-coach.md` | Ja (auto-inclusion) |
| **Claude Code** | `CLAUDE.md` | Ja |
| **Cursor** | `.cursorrules` | Ja |
| **OpenAI / Andere** | `AGENTS.md` | Manuell referenzieren |
| **Alle** | `skills/*.md` | Manuell via # oder Prompt |

---

## Projektstruktur

```
garmin-coach/
├── skills/
│   ├── garmin_data.md            # Skill: Daten abrufen und speichern
│   └── garmin_coach.md           # Skill: Adaptive Analyse und Trainingsplanung
├── data/
│   ├── activities/               # Rohdaten je Aktivität als JSON
│   ├── history.json              # Aggregierte Trainingshistorie
│   ├── plan.json                 # Aktueller 7-Tage-Trainingsplan
│   ├── analysis.json             # Berechnete Metriken (CTL/ATL/TSB etc.)
│   ├── athlete_profile.json      # Automatisch erkannte Stärken/Schwächen
│   ├── race_prognosis.json       # Rennprognose mit Trend
│   ├── recovery_log.json         # Erholungs-Tracking (HRV, Schlaf, etc.)
│   ├── weight_history.json       # Gewichtsverlauf
│   ├── coach_history.json        # Coach-Analyse-Historie
│   └── weekly_summaries.json     # Wochen-Zusammenfassungen
├── config/
│   ├── athlete.json              # Persönliche Werte + Coach-Typ-Auswahl
│   ├── coach_types.json          # Alle verfügbaren Trainingsphilosophien
│   └── mcp.json                  # MCP-Tool-Mapping (Referenz)
├── scripts/
│   ├── analyze.py                # CTL/ATL/TSB, Pace-Effizienz, Trends
│   ├── generate_report.py        # HTML-Dashboard generieren
│   └── push_workout.py           # Workout-JSON für Garmin vorbereiten
├── web/
│   ├── index.html                # Dashboard (wird automatisch generiert)
│   ├── setup.html                # Setup-Wizard für neue Nutzer
│   ├── style.css                 # Dark Theme Styling
│   └── charts.js                 # Chart.js Visualisierungen
├── CLAUDE.md                     # Instruktionen für Claude Code
├── AGENTS.md                     # Instruktionen für OpenAI/andere
├── .cursorrules                  # Instruktionen für Cursor
├── backlog.md                    # Feature-Backlog mit User Stories
└── README.md
```

## Coach-Typen

Wählbar in `config/athlete.json` → `coach_typ.aktiv`:

| Typ | Schlüssel | Verteilung | Für wen |
|-----|-----------|-----------|---------|
| **Maffetone** | `maffetone` | 100% Z1-Z2 | Anfänger, Übertrainierte, Gewichtsreduktion |
| **Polarisiert** | `polarisiert` | 80% Z1-Z2, 20% Z4-Z5 | Fortgeschrittene, Marathon/HM |
| **Pyramidal** | `pyramidal` | 75% Z1, 15% Z2-Z3, 10% Z4-Z5 | Erfahrene mit hohem Volumen |
| **Threshold** | `threshold` | 60% Z1-Z2, 20% Z3, 20% Z4-Z5 | Wettkampforientiert, gute Basis |
| **Norwegisch** | `norwegisch` | 65% Z1-Z2, 25% Z3, 10% Z4-Z5 | Sehr ambitioniert, viel Zeit |
| **Adaptiv** | `adaptiv` | Variabel (KI) | Alle – KI wählt den besten Ansatz |

Details zu jedem Coach-Typ findest du in `config/coach_types.json` oder im Dashboard unter dem Tab "Coach-Typ".

## Dashboard

Öffne `web/index.html` im Browser. 6 Tabs:

- **Dashboard** – KPIs (CTL/ATL/TSB) mit Erklärungen, Recovery-Ampel, Radial-Gauge, letzter Lauf
- **Training** – Detaillierter 7-Tage-Plan mit Aufbau-Schritten und Coach-Notizen
- **Prognose** – Rennprognose, Einflussfaktoren, Gewichtsverlauf
- **Statistiken** – Charts: CTL/ATL/TSB, Pace/HF-Dual, Cardiac Drift, Wochenkilometer, Aerobic Efficiency, Gewicht
- **Coach-Typ** – Übersicht aller Trainingsphilosophien
- **Historie** – Timeline mit Coach-Analysen und Wochen-Zusammenfassungen

## Scripts standalone ausführen

```bash
python3 scripts/analyze.py          # Analyse berechnen
python3 scripts/generate_report.py  # Dashboard generieren
python3 scripts/push_workout.py     # Nächsten Workout als JSON ausgeben
```

## Technologie

- **Datenquelle**: Garmin Connect via [garmin_mcp](https://github.com/Taxuspt/garmin_mcp)
- **Analyse**: Python 3 (keine externen Dependencies)
- **Visualisierung**: Chart.js 4.x (via CDN)
- **Design**: Dark OLED Theme, Purple/Pink Accent, Inter Font
- **KI-Integration**: Skills + Steering-Dateien für Kiro, Claude, Cursor, OpenAI


---

## English

### What is RunLoop?

RunLoop is a local, AI-driven running analysis system that connects to Garmin Connect via MCP. It tracks your fitness metrics, detects strengths and weaknesses, and generates adaptive training plans based on your actual performance data – not generic templates.

### Quick Setup

1. **Install uv**: `brew install uv` (macOS) or see [uv docs](https://docs.astral.sh/uv/getting-started/installation/)
2. **Configure Garmin MCP** in your AI tool's MCP settings:
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
3. **Authenticate**: On first MCP tool call, enter your Garmin Connect email + password (cached locally)
4. **Configure profile**: `cp config/athlete.example.json config/athlete.json` and edit your values (or use the Setup Wizard at `web/setup.html`)
5. **Import data**: Tell the AI: *"Import my running data since 2025-01-01"*

### Daily Workflow

After each run, just say:

> "New run today, analyze and update everything."

The AI will: sync Garmin data → analyze metrics → adapt training plan → regenerate dashboard.

### Coach Types

Choose in `config/athlete.json` → `coach_typ.aktiv`:

| Type | Key | Distribution | Best for |
|------|-----|-------------|----------|
| Maffetone | `maffetone` | 100% Z1-Z2 | Beginners, weight loss, recovery |
| Polarized | `polarisiert` | 80% Z1-Z2, 20% Z4-Z5 | Most runners, marathon prep |
| Pyramidal | `pyramidal` | 75/15/10 | High-volume experienced runners |
| Threshold | `threshold` | 60/20/20 | Race-focused, strong base needed |
| Norwegian | `norwegisch` | 65/25/10 | Very ambitious, 60+ km/week |
| Adaptive | `adaptiv` | AI decides | Everyone – AI picks best approach |

### Dashboard

Open `web/index.html` in your browser. Use the DE/EN toggle in the top-right corner to switch languages.

### AI Tool Compatibility

| Tool | Config file | Auto-loaded? |
|------|------------|-------------|
| Kiro | `.kiro/steering/garmin-coach.md` | Yes |
| Claude Code | `CLAUDE.md` | Yes |
| Cursor | `.cursorrules` | Yes |
| OpenAI/Other | `AGENTS.md` | Reference manually |
