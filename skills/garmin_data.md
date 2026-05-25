---
inclusion: manual
---

# Garmin Data – Daten abrufen, speichern und synchronisieren

Dieser Skill beschreibt, wie Trainingsdaten vom Garmin MCP Server abgerufen, normalisiert und lokal persistiert werden.

## Verwendete Garmin MCP Tools

### Aktivitäten abrufen
- `mcp_garmin_get_activities_by_date(start_date, end_date)` – Alle Aktivitäten in einem Zeitraum
- `mcp_garmin_get_activity(activity_id)` – Basis-Infos einer Aktivität
- `mcp_garmin_get_activity_splits(activity_id)` – Kilometer-Splits
- `mcp_garmin_get_activity_split_summaries(activity_id)` – Split-Zusammenfassungen
- `mcp_garmin_get_activity_hr_in_timezones(activity_id)` – Herzfrequenz-Zonen
- `mcp_garmin_get_activity_power_in_timezones(activity_id)` – Leistungszonen (falls vorhanden)
- `mcp_garmin_get_activity_weather(activity_id)` – Wetterdaten
- `mcp_garmin_get_activity_gear(activity_id)` – Ausrüstung
- `mcp_garmin_get_training_effect(activity_id)` – Trainingseffekt (aerob/anaerob)

### Fitness & Recovery
- `mcp_garmin_get_training_status(date)` – Trainingsstatus, VO2max, Load
- `mcp_garmin_get_hrv_data(date)` – HRV-Daten
- `mcp_garmin_get_training_readiness(date)` – Trainingsbereitschaft
- `mcp_garmin_get_training_load_trend(start_date, end_date)` – CTL/ATL/TSB Trend

### Workouts pushen
- `mcp_garmin_upload_workout(workout_data)` – Workout erstellen
- `mcp_garmin_schedule_workout(workout_id, calendar_date)` – Workout im Kalender planen
- `mcp_garmin_create_walk_run_workout(...)` – Walk/Run Intervall-Workout erstellen

## Ablauf: Aktivitäten abrufen (Initial & Update)

### Schritt 1: Zeitraum bestimmen

Zwei Varianten:
- **Mit Stichtag**: Nutzer gibt ein Datum an → Alle Aktivitäten ab diesem Datum bis heute
- **Ohne Stichtag (Standard)**: Letzte 365 Tage ab heute

Falls bereits Daten in `data/history.json` vorhanden sind und der Nutzer nur "aktualisiere" sagt:
→ Nimm das Datum der letzten gespeicherten Aktivität als Stichtag (inkrementelles Update).

### Schritt 2: Aktivitäten laden und Auswahl anbieten

1. Rufe `mcp_garmin_get_activities_by_date(stichtag, heute)` auf.
2. **Frage den Nutzer:**

> Ich habe **X Aktivitäten** im Zeitraum [Stichtag] bis heute gefunden.
> 
> Möchtest du:
> - **a) Alle importieren**
> - **b) Eine Auswahl treffen**

3. **Bei Option b)** – Liste die Aktivitäten auf:

```
Nr. | Sportart   | Datum      | Distanz
----|-----------|------------|--------
1   | running    | 2026-05-25 | 9.8 km
2   | running    | 2026-05-21 | 10.4 km
3   | cycling    | 2026-05-20 | 35.2 km
4   | running    | 2026-05-19 | 15.3 km
...
```

4. **Nutzer wählt** eine der folgenden Optionen:
   - Einzelne Nummern: `1, 2, 4, 7`
   - Sportart-Filter: `running` (importiert alle Läufe)
   - Alles: `alle`

### Schritt 3: Gewählte Aktivitäten verarbeiten

Für jede ausgewählte Aktivität (die noch nicht in `data/activities/` liegt):
   - Rufe alle Detail-Tools parallel ab (Splits, HR-Zonen, Wetter, Gear, Trainingseffekt)
   - Normalisiere die Daten in ein einheitliches JSON-Format
   - Speichere als `data/activities/YYYY-MM-DD_<activity_id>.json`

### Schritt 4: History aktualisieren

Ergänze `data/history.json` um die neuen Einträge (Zusammenfassung pro Aktivität).

### Beispiel-Interaktion:

> **Nutzer:** "Hole meine Trainingsdaten ab dem 01.01.2026"
> 
> **Coach:** Ich habe 47 Aktivitäten zwischen 01.01.2026 und heute gefunden:
> - 13x Running
> - 8x Cycling  
> - 5x Strength Training
> - 21x Walking
> 
> Möchtest du a) alle importieren oder b) eine Auswahl treffen?
>
> **Nutzer:** "Nur running"
>
> **Coach:** OK, importiere 13 Laufaktivitäten...

### Inkrementelles Update (nach dem ersten Import):

Wenn der Nutzer sagt "Neuer Lauf heute, analysiere alles" oder "Schau nach neuen Daten":
- Stichtag = Datum der letzten Aktivität in `data/history.json`
- Nur neue Aktivitäten seit diesem Datum abrufen
- Keine Auswahl-Frage nötig (nur neue Daten werden geholt)
- Direkt verarbeiten und analysieren

### Bei JEDEM Garmin-Sync automatisch mitholen:

Folgende Daten werden bei JEDER Anfrage an Garmin immer automatisch abgerufen – unabhängig davon ob neue Aktivitäten vorliegen:

1. **Gewicht**: `mcp_garmin_get_weigh_ins(letzte_messung_datum, heute)` → Neue Einträge in `data/weight_history.json` ergänzen
2. **Recovery-Daten** (falls verfügbar für heute):
   - `mcp_garmin_get_hrv_data(heute)`
   - `mcp_garmin_get_rhr_day(heute)`
   - `mcp_garmin_get_sleep_summary(heute)`
   - `mcp_garmin_get_training_readiness(heute)`
   - `mcp_garmin_get_body_battery(heute, heute)`
3. **Training Status**: `mcp_garmin_get_training_status(heute)` (VO2max, Load)

Diese Daten werden IMMER geholt wenn der Nutzer um einen Abgleich/Sync mit Garmin bittet, auch wenn keine neue Aktivität vorliegt.

## Daten-Normalisierung

Jede Aktivität wird als JSON mit folgender Struktur gespeichert:

```json
{
  "activity_id": 123456789,
  "datum": "2025-05-20",
  "typ": "running",
  "name": "Morgenlauf",
  "dauer_sekunden": 3600,
  "dauer_bewegung_sekunden": 3540,
  "distanz_meter": 10000,
  "kalorien": 650,
  "herzfrequenz": {
    "durchschnitt": 145,
    "max": 172,
    "zonen": [
      {"zone": 1, "sekunden": 120},
      {"zone": 2, "sekunden": 1800},
      {"zone": 3, "sekunden": 1200},
      {"zone": 4, "sekunden": 420},
      {"zone": 5, "sekunden": 60}
    ]
  },
  "pace": {
    "durchschnitt_sek_pro_km": 360,
    "max_sek_pro_km": 300
  },
  "hoehenmeter": {
    "aufstieg": 120,
    "abstieg": 115
  },
  "kadenz": {
    "durchschnitt": 172,
    "max": 185
  },
  "trainingseffekt": {
    "aerob": 3.2,
    "anaerob": 1.5
  },
  "splits": [...],
  "wetter": {...},
  "gear": [...],
  "leistung": null
}
```

## History-Format (data/history.json)

```json
{
  "letzte_aktualisierung": "2025-05-20T18:30:00",
  "aktivitaeten": [
    {
      "activity_id": 123456789,
      "datum": "2025-05-20",
      "typ": "running",
      "distanz_meter": 10000,
      "dauer_sekunden": 3600,
      "herzfrequenz_durchschnitt": 145,
      "pace_durchschnitt_sek_pro_km": 360,
      "trainingseffekt_aerob": 3.2,
      "kalorien": 650
    }
  ]
}
```

## Workouts zu Garmin pushen

1. Lies `data/plan.json` für den nächsten geplanten Workout
2. Konvertiere in Garmin-Workout-Format (siehe MCP `upload_workout` Schema)
3. Lade hoch via `mcp_garmin_upload_workout`
4. Plane im Kalender via `mcp_garmin_schedule_workout`
5. Bestätige dem Nutzer mit Workout-Name und geplantem Datum

**Wichtig**: Workouts werden NUR auf explizite Anfrage des Nutzers gepusht, nie automatisch.

## Fehlerbehandlung

- **MCP nicht erreichbar**: Melde dem Nutzer, dass der Garmin MCP Server nicht verfügbar ist. Vorschlag: MCP-Konfiguration prüfen.
- **Keine neuen Aktivitäten**: Melde „Keine neuen Aktivitäten seit [Datum] gefunden."
- **Detail-Abfrage fehlgeschlagen** (z.B. keine Power-Daten): Überspringe das Feld, setze auf `null`. Kein Fehler.
- **Doppelte Aktivitäten**: Prüfe anhand der `activity_id` ob bereits in `data/activities/` vorhanden. Falls ja, überspringe.
- **Schreibfehler**: Falls `data/` nicht beschreibbar, melde Fehler und breche ab.

## Erholungs-Tracking (Morgen-Check)

Wird idealerweise morgens abgerufen oder bei jeder Analyse-Anfrage:

1. **HRV abrufen**: `mcp_garmin_get_hrv_data(heute)` → Nacht-HRV
2. **Ruhepuls**: `mcp_garmin_get_rhr_day(heute)` → Resting Heart Rate
3. **Schlaf**: `mcp_garmin_get_sleep_summary(heute)` → Schlafdauer, Qualität
4. **Training Readiness**: `mcp_garmin_get_training_readiness(heute)` → Garmin-Score
5. **Body Battery**: `mcp_garmin_get_body_battery(heute, heute)` → Energielevel

Speichere in `data/recovery_log.json`:
```json
{
  "datum": "2026-05-24",
  "hrv_nacht_ms": 45,
  "hrv_7tage_avg_ms": 42,
  "ruhepuls": 54,
  "schlaf_stunden": 7.2,
  "schlaf_score": 78,
  "training_readiness": 62,
  "body_battery_morgens": 75,
  "empfehlung": "normal"
}
```

### Entscheidungslogik:
- HRV > 10ms unter 7-Tage-Schnitt → "nur_z2" (keine Intensität)
- Training Readiness < 40 → "pause" (Ruhetag empfehlen)
- Body Battery < 30 morgens → "pause"
- Schlaf < 5h → "reduziert" (kürzere Einheit)
- Alles normal → "normal"

## Gewichtsverlauf abrufen

1. `mcp_garmin_get_weigh_ins(start_date, end_date)` → Gewichtsmessungen
2. Speichere in `data/weight_history.json`
3. Berechne Trend (7-Tage-Durchschnitt, Veränderung/Woche)

## Lauf-Vergleich (gleiche Strecke)

Für den Lauf-Vergleich werden Aktivitäten anhand folgender Kriterien als "gleiche Strecke" identifiziert:
- Distanz innerhalb ±500m
- Ähnliche Höhenmeter (±20%)
- Gleicher Startbereich (wenn GPS-Daten vorhanden, sonst Name-Matching)

Vergleichsmetriken:
- Pace bei gleicher Durchschnitts-HF
- HF bei gleicher Pace
- Aerobic Efficiency (Pace/HF)
- Kadenz-Unterschied
- Pace-Drift (letzte 25% vs. erste 25%)

## Wochen-Zusammenfassung generieren

Jeden Sonntag (oder auf Anfrage) wird eine Zusammenfassung erstellt:
1. Lies alle Aktivitäten der Woche aus `data/history.json`
2. Berechne: Gesamt-km, Anzahl Läufe, Durchschnitts-Pace, Durchschnitts-HF
3. Vergleiche mit Vorwoche (Veränderung in %)
4. CTL-Veränderung der Woche
5. Gewichtsveränderung (falls Daten vorhanden)
6. Speichere in `data/weekly_summaries.json`
