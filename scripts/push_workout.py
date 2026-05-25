#!/usr/bin/env python3
"""
Workout-Push-Script: Liest den nächsten geplanten Workout aus data/plan.json
und gibt das Garmin-kompatible Workout-JSON aus.

Dieses Script bereitet die Daten vor – der eigentliche Push erfolgt über den
Garmin MCP (mcp_garmin_upload_workout + mcp_garmin_schedule_workout).

Standalone lauffähig: python scripts/push_workout.py
Gibt das Workout-JSON auf stdout aus, das dann via MCP gepusht werden kann.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Projektverzeichnis
PROJEKT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJEKT_DIR / "data"
CONFIG_DIR = PROJEKT_DIR / "config"
PLAN_FILE = DATA_DIR / "plan.json"
ATHLETE_FILE = CONFIG_DIR / "athlete.json"


def lade_json(pfad):
    """Lädt eine JSON-Datei."""
    with open(pfad, "r", encoding="utf-8") as f:
        return json.load(f)


def pace_zu_geschwindigkeit(sek_pro_km):
    """Konvertiert Pace (sek/km) in Geschwindigkeit (m/s) für Garmin."""
    if sek_pro_km <= 0:
        return 0
    return round(1000 / sek_pro_km, 4)


def erstelle_garmin_workout(tag, config):
    """
    Konvertiert einen Trainingsplan-Tag in ein Garmin-kompatibles Workout-JSON.

    Unterstützte Typen:
    - leichter_lauf: Aufwärmen + Dauerlauf in Z2 + Auslaufen
    - intervalle: Aufwärmen + Wiederholungen + Auslaufen
    - langer_lauf: Aufwärmen + langer Dauerlauf in Z2 + Auslaufen
    - tempo: Aufwärmen + Tempoblock in Z3-Z4 + Auslaufen
    """
    typ = tag.get("typ", "leichter_lauf")
    name = tag.get("beschreibung", f"Training {tag.get('datum', '')}")
    dauer_min = tag.get("dauer_min", 40)
    ziel_zone = tag.get("ziel_zone", "Z2")

    # HF-Zone als Nummer (Z2 -> 2)
    zone_nr = int(ziel_zone.replace("Z", "")) if ziel_zone.startswith("Z") else 2

    # Basis-Workout-Struktur
    workout = {
        "workoutName": name,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSegments": [{
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSteps": []
        }]
    }

    steps = workout["workoutSegments"][0]["workoutSteps"]
    step_order = 1

    if typ in ("leichter_lauf", "langer_lauf"):
        # Aufwärmen (10 min)
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
            "endConditionValue": 600.0,
            "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
            "zoneNumber": 1
        })
        step_order += 1

        # Hauptteil
        hauptteil_min = dauer_min - 15  # 10 Aufwärmen + 5 Auslaufen abziehen
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
            "endConditionValue": hauptteil_min * 60.0,
            "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
            "zoneNumber": zone_nr
        })
        step_order += 1

        # Auslaufen (5 min)
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
            "endConditionValue": 300.0,
            "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
            "zoneNumber": 1
        })

    elif typ == "intervalle":
        # Aufwärmen (15 min)
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
            "endConditionValue": 900.0,
            "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
            "zoneNumber": 1
        })
        step_order += 1

        # Intervall-Block (6 Wiederholungen als Standard)
        wiederholungen = tag.get("wiederholungen", 6)
        steps.append({
            "type": "RepeatGroupDTO",
            "stepOrder": step_order,
            "numberOfIterations": wiederholungen,
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                    "endConditionValue": 180.0,  # 3 min schnell
                    "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                    "zoneNumber": 4
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery"},
                    "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                    "endConditionValue": 90.0,  # 1:30 min Pause
                    "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                    "zoneNumber": 1
                }
            ]
        })
        step_order += 1

        # Auslaufen (10 min)
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
            "endConditionValue": 600.0,
            "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
            "zoneNumber": 1
        })

    elif typ == "tempo":
        # Aufwärmen (15 min)
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
            "endConditionValue": 900.0,
            "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
            "zoneNumber": 1
        })
        step_order += 1

        # Tempo-Block (20 min in Z3-Z4)
        tempo_min = tag.get("tempo_dauer_min", 20)
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
            "endConditionValue": tempo_min * 60.0,
            "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
            "zoneNumber": zone_nr
        })
        step_order += 1

        # Auslaufen (10 min)
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
            "endConditionValue": 600.0,
            "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
            "zoneNumber": 1
        })

    return workout


def main():
    """Hauptfunktion: Liest Plan und gibt nächsten Workout als JSON aus."""
    print("🏋️ Workout-Vorbereitung gestartet...", file=sys.stderr)

    plan = lade_json(PLAN_FILE)
    config = lade_json(ATHLETE_FILE)

    tage = plan.get("tage", [])
    if not tage:
        print("  ⚠️  Kein Trainingsplan vorhanden.", file=sys.stderr)
        sys.exit(1)

    # Nächsten zukünftigen Tag finden
    heute = datetime.now().strftime("%Y-%m-%d")
    naechster = None
    for tag in tage:
        if tag.get("datum", "") >= heute and tag.get("typ") != "ruhe":
            naechster = tag
            break

    if not naechster:
        print("  ⚠️  Kein zukünftiger Trainingstag im Plan.", file=sys.stderr)
        sys.exit(1)

    print(f"  Nächster Workout: {naechster['datum']} – {naechster.get('typ', '')}", file=sys.stderr)

    # Garmin-Workout generieren
    workout = erstelle_garmin_workout(naechster, config)

    # JSON auf stdout ausgeben (für MCP-Upload)
    print(json.dumps(workout, indent=2, ensure_ascii=False))

    print(f"\n✅ Workout bereit zum Push: {workout['workoutName']}", file=sys.stderr)
    print(f"   Datum: {naechster['datum']}", file=sys.stderr)
    print("   → Nutze den Garmin MCP zum Hochladen.", file=sys.stderr)


if __name__ == "__main__":
    main()
