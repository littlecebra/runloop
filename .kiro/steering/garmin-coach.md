---
inclusion: auto
---

# RunLoop – Projekt-Instruktionen

Du arbeitest am Projekt "RunLoop" – ein lokales, KI-gestütztes Lauftraining-Analyse-System.

## Kontext

Dieses Projekt nutzt den Garmin MCP Server um Trainingsdaten abzurufen, zu analysieren und adaptive Trainingspläne zu erstellen. Die Daten werden lokal in JSON-Dateien persistiert.

## Verfügbare Skills (manuell via # im Chat)

- **skills/garmin_data.md** – Daten von Garmin abrufen, normalisieren, speichern. Nutze diesen Skill wenn Daten geholt, synchronisiert oder Workouts gepusht werden sollen.
- **skills/garmin_coach.md** – Trainingsanalyse, adaptive Plansteuerung, Coach-Logik. Nutze diesen Skill wenn Trainingspläne erstellt, angepasst oder Analysen durchgeführt werden sollen.
- **skills/garmin_strength.md** – Kräftigung, Mobilität, Beschwerdemanagement. Nutze diesen Skill wenn der Nutzer nach Übungen fragt, Beschwerden meldet, oder Kraft/Mobility-Routinen benötigt.

## Verfügbare Steering (automatisch geladen)

- **.kiro/steering/ui-ux-pro-max/** – UX-Richtlinien, Accessibility, Performance, Charts

## Optionale Design-Skills (falls installiert)

Falls folgende Skills im Workspace oder auf User-Level vorhanden sind, NUTZE sie bei jeder Erstellung/Änderung von HTML/CSS/JS in `web/`:

- **frontend-design** – Visuelles Design: Typografie, Farbe, Motion, Komposition. Sorgt für ein unverwechselbares, nicht-generisches UI.
- **ui-ux-pro-max** – UX-Qualität: Accessibility, Touch-Targets, Performance, Chart-Best-Practices

Diese Skills sind NICHT zwingend erforderlich. Wenn sie nicht vorhanden sind, halte dich an die Design-Regeln unten.

## Design-Regeln für das Dashboard (gelten immer)

Bei jeder Änderung an `web/` Dateien:
- Dark OLED Theme mit Purple (#a855f7) / Pink (#f43f5e) Accent
- Serifenlose Schrift mit Charakter (z.B. Outfit, NICHT Inter/Arial/Roboto)
- Monospace-Font für Zahlen/Daten (z.B. JetBrains Mono)
- Atmosphärische Hintergründe (subtile Gradient-Orbs, Noise-Textur)
- Keine Emojis als Icons – SVG oder reine Typografie
- Hover-States mit Glow-Effekt
- `prefers-reduced-motion` respektieren
- Responsive: 375px / 768px / 1024px

## MCP Server

- **garmin** – Garmin Connect MCP Server (https://github.com/Taxuspt/garmin_mcp). Stellt alle Garmin-Daten bereit (Aktivitäten, HRV, Schlaf, Gewicht, Workouts etc.)

## Wichtige Regeln

1. **Bei jedem Garmin-Sync** immer auch Gewicht, Recovery-Daten und Training Status mitholen (siehe garmin_data.md)
2. **Bei Dashboard-Änderungen** immer den ui-ux-pro-max Skill/Steering nutzen: Dark Theme, Purple/Pink Accent, keine Emojis als Icons, SVG-Icons verwenden
3. **Daten werden lokal persistiert** in `data/` – die KI hat kein Gedächtnis zwischen Sessions
4. **Scripts standalone lauffähig** halten (python3 scripts/analyze.py etc.)
5. **Coach-Typ** aus `config/athlete.json` → `coach_typ.aktiv` beachten
6. **Workouts nur auf explizite Anfrage** zu Garmin pushen, nie automatisch
