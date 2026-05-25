#!/usr/bin/env python3
"""
Trainingsanalyse-Script: Berechnet CTL, ATL, TSB, Aerobic Efficiency und Trends.

Liest Daten aus data/history.json und data/activities/
Schreibt Ergebnisse in data/analysis.json

Standalone lauffähig: python scripts/analyze.py
"""

import json
import os
import math
from datetime import datetime, timedelta
from pathlib import Path

# Projektverzeichnis ermitteln (relativ zum Script)
PROJEKT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJEKT_DIR / "data"
ACTIVITIES_DIR = DATA_DIR / "activities"
CONFIG_DIR = PROJEKT_DIR / "config"
HISTORY_FILE = DATA_DIR / "history.json"
ANALYSIS_FILE = DATA_DIR / "analysis.json"
ATHLETE_FILE = CONFIG_DIR / "athlete.json"


def lade_config():
    """Lädt die Athleten-Konfiguration."""
    with open(ATHLETE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def lade_history():
    """Lädt die Trainingshistorie."""
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def lade_aktivitaeten():
    """Lädt alle Aktivitäts-JSONs aus dem activities-Ordner."""
    aktivitaeten = []
    if not ACTIVITIES_DIR.exists():
        return aktivitaeten

    for datei in sorted(ACTIVITIES_DIR.glob("*.json")):
        with open(datei, "r", encoding="utf-8") as f:
            try:
                aktivitaeten.append(json.load(f))
            except json.JSONDecodeError:
                print(f"  Warnung: {datei.name} konnte nicht gelesen werden")
    return aktivitaeten


def berechne_training_stress(aktivitaet, config):
    """
    Berechnet den Training Stress Score (vereinfacht) basierend auf
    Dauer und Herzfrequenz relativ zur maximalen HF.

    Formel: TSS ≈ (Dauer_min * IF²) / 60 * 100
    IF (Intensity Factor) = Durchschnitts-HF / Laktatschwellen-HF
    """
    hf_avg = aktivitaet.get("herzfrequenz_durchschnitt") or aktivitaet.get("herzfrequenz", {}).get("durchschnitt")
    dauer_sek = aktivitaet.get("dauer_sekunden", 0)
    laktatschwelle_hf = config["herzfrequenz"]["laktatschwelle"]

    if not hf_avg or not dauer_sek or not laktatschwelle_hf:
        return 0

    dauer_min = dauer_sek / 60
    intensity_factor = hf_avg / laktatschwelle_hf
    tss = (dauer_min * intensity_factor ** 2) / 60 * 100
    return round(tss, 1)


def berechne_ctl_atl_tsb(aktivitaeten, config):
    """
    Berechnet CTL (42-Tage), ATL (7-Tage) und TSB für jeden Tag.

    CTL = exponentiell gewichteter Durchschnitt über 42 Tage
    ATL = exponentiell gewichteter Durchschnitt über 7 Tage
    TSB = CTL - ATL
    """
    if not aktivitaeten:
        return []

    # Alle Aktivitäten nach Datum sortieren
    sortiert = sorted(aktivitaeten, key=lambda a: a.get("datum", ""))

    # Zeitraum bestimmen
    erstes_datum = datetime.strptime(sortiert[0]["datum"], "%Y-%m-%d")
    heute = datetime.now()

    # TSS pro Tag berechnen
    tss_pro_tag = {}
    for akt in sortiert:
        datum = akt.get("datum", "")
        tss = berechne_training_stress(akt, config)
        tss_pro_tag[datum] = tss_pro_tag.get(datum, 0) + tss

    # CTL/ATL/TSB Tag für Tag berechnen
    ergebnisse = []
    ctl = 0
    atl = 0
    tag = erstes_datum

    while tag <= heute:
        datum_str = tag.strftime("%Y-%m-%d")
        tss_heute = tss_pro_tag.get(datum_str, 0)

        # Exponentieller gleitender Durchschnitt
        ctl = ctl + (tss_heute - ctl) / 42
        atl = atl + (tss_heute - atl) / 7
        tsb = ctl - atl

        ergebnisse.append({
            "datum": datum_str,
            "tss": tss_heute,
            "ctl": round(ctl, 1),
            "atl": round(atl, 1),
            "tsb": round(tsb, 1)
        })

        tag += timedelta(days=1)

    return ergebnisse


def berechne_aerobic_efficiency(aktivitaeten):
    """
    Berechnet die aerobe Effizienz: Pace (sek/km) pro Herzschlag.
    Niedrigere Werte = bessere Effizienz.

    Nur Laufaktivitäten mit gültiger Pace und HF werden berücksichtigt.
    """
    ergebnisse = []

    for akt in aktivitaeten:
        typ = akt.get("typ", "")
        if typ != "running":
            continue

        # Pace ermitteln
        pace = None
        if "pace" in akt and isinstance(akt["pace"], dict):
            pace = akt["pace"].get("durchschnitt_sek_pro_km")
        elif "pace_durchschnitt_sek_pro_km" in akt:
            pace = akt["pace_durchschnitt_sek_pro_km"]

        # HF ermitteln
        hf = None
        if "herzfrequenz" in akt and isinstance(akt["herzfrequenz"], dict):
            hf = akt["herzfrequenz"].get("durchschnitt")
        elif "herzfrequenz_durchschnitt" in akt:
            hf = akt["herzfrequenz_durchschnitt"]

        if pace and hf and hf > 0:
            effizienz = round(pace / hf, 3)
            ergebnisse.append({
                "datum": akt.get("datum", ""),
                "pace_sek_pro_km": pace,
                "hf_durchschnitt": hf,
                "effizienz": effizienz
            })

    return ergebnisse


def berechne_wochen_km(aktivitaeten, wochen=8):
    """Berechnet die Wochenkilometer der letzten N Wochen."""
    heute = datetime.now()
    start = heute - timedelta(weeks=wochen)

    wochen_daten = {}

    for akt in aktivitaeten:
        datum_str = akt.get("datum", "")
        if not datum_str:
            continue

        datum = datetime.strptime(datum_str, "%Y-%m-%d")
        if datum < start:
            continue

        # Kalenderwoche bestimmen
        kw = datum.isocalendar()
        kw_key = f"{kw[0]}-KW{kw[1]:02d}"

        distanz_m = akt.get("distanz_meter", 0)
        wochen_daten[kw_key] = wochen_daten.get(kw_key, 0) + distanz_m

    # In km umrechnen und sortieren
    ergebnis = []
    for kw, meter in sorted(wochen_daten.items()):
        ergebnis.append({
            "woche": kw,
            "km": round(meter / 1000, 1)
        })

    return ergebnis


def berechne_kadenz_trend(aktivitaeten):
    """Berechnet Kadenz-Durchschnitt und Trend der letzten Läufe."""
    kadenz_werte = []

    for akt in aktivitaeten:
        if akt.get("typ") != "running":
            continue

        kadenz = None
        if "kadenz" in akt and isinstance(akt["kadenz"], dict):
            kadenz = akt["kadenz"].get("durchschnitt")

        if kadenz and kadenz > 0:
            kadenz_werte.append({
                "datum": akt.get("datum", ""),
                "kadenz": kadenz
            })

    if not kadenz_werte:
        return {"durchschnitt": 0, "trend": "keine_daten", "werte": []}

    # Durchschnitt der letzten 10 Läufe
    letzte = kadenz_werte[-10:]
    durchschnitt = round(sum(k["kadenz"] for k in letzte) / len(letzte), 0)

    # Trend: Vergleich erste Hälfte vs. zweite Hälfte
    if len(letzte) >= 4:
        mitte = len(letzte) // 2
        erste_haelfte = sum(k["kadenz"] for k in letzte[:mitte]) / mitte
        zweite_haelfte = sum(k["kadenz"] for k in letzte[mitte:]) / (len(letzte) - mitte)
        if zweite_haelfte > erste_haelfte + 1:
            trend = "steigend"
        elif zweite_haelfte < erste_haelfte - 1:
            trend = "fallend"
        else:
            trend = "stabil"
    else:
        trend = "zu_wenig_daten"

    return {
        "durchschnitt": durchschnitt,
        "trend": trend,
        "werte": kadenz_werte[-20:]
    }


def berechne_intensitaetsverteilung(aktivitaeten):
    """
    Berechnet die Verteilung der Trainingszeit auf die HF-Zonen
    der letzten 4 Wochen. Ziel: 80% Z1-Z2, 20% Z4-Z5.
    """
    vor_4_wochen = (datetime.now() - timedelta(weeks=4)).strftime("%Y-%m-%d")

    zeit_pro_zone = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for akt in aktivitaeten:
        if akt.get("datum", "") < vor_4_wochen:
            continue

        zonen = None
        if "herzfrequenz" in akt and isinstance(akt["herzfrequenz"], dict):
            zonen = akt["herzfrequenz"].get("zonen", [])

        if not zonen:
            continue

        for zone in zonen:
            z_nr = zone.get("zone", 0)
            z_sek = zone.get("sekunden", 0)
            if z_nr in zeit_pro_zone:
                zeit_pro_zone[z_nr] += z_sek

    gesamt = sum(zeit_pro_zone.values())
    if gesamt == 0:
        return {"leicht_prozent": 0, "intensiv_prozent": 0, "zone3_prozent": 0, "bewertung": "keine_daten"}

    leicht = zeit_pro_zone[1] + zeit_pro_zone[2]
    intensiv = zeit_pro_zone[4] + zeit_pro_zone[5]
    zone3 = zeit_pro_zone[3]

    leicht_pct = round(leicht / gesamt * 100, 1)
    intensiv_pct = round(intensiv / gesamt * 100, 1)
    zone3_pct = round(zone3 / gesamt * 100, 1)

    # Bewertung
    if leicht_pct >= 75 and intensiv_pct >= 15:
        bewertung = "gut_polarisiert"
    elif zone3_pct > 30:
        bewertung = "zu_viel_zone3"
    elif intensiv_pct < 10:
        bewertung = "zu_wenig_intensitaet"
    elif leicht_pct < 60:
        bewertung = "zu_wenig_grundlage"
    else:
        bewertung = "akzeptabel"

    return {
        "leicht_prozent": leicht_pct,
        "intensiv_prozent": intensiv_pct,
        "zone3_prozent": zone3_pct,
        "bewertung": bewertung,
        "details": {z: round(zeit_pro_zone[z] / gesamt * 100, 1) for z in range(1, 6)}
    }


def main():
    """Hauptfunktion: Führt alle Analysen durch und speichert Ergebnisse."""
    print("🏃 Trainingsanalyse gestartet...")

    # Konfiguration laden
    config = lade_config()
    print(f"  Athlet: {config.get('name', 'Unbekannt')}, HFmax: {config['herzfrequenz']['max']}")

    # Aktivitäten laden
    aktivitaeten = lade_aktivitaeten()
    history = lade_history()

    # Alle Datenquellen zusammenführen (Aktivitäts-JSONs haben Vorrang)
    alle_aktivitaeten = aktivitaeten if aktivitaeten else history.get("aktivitaeten", [])
    print(f"  {len(alle_aktivitaeten)} Aktivitäten geladen")

    if not alle_aktivitaeten:
        print("  ⚠️  Keine Aktivitäten vorhanden. Bitte zuerst Daten abrufen.")
        ergebnis = {
            "berechnet_am": datetime.now().isoformat(),
            "status": "keine_daten",
            "ctl_atl_tsb": [],
            "aerobic_efficiency": [],
            "wochen_km": [],
            "kadenz": {"durchschnitt": 0, "trend": "keine_daten", "werte": []},
            "intensitaetsverteilung": {}
        }
    else:
        # Analysen durchführen
        print("  📊 Berechne CTL/ATL/TSB...")
        ctl_atl_tsb = berechne_ctl_atl_tsb(alle_aktivitaeten, config)

        print("  📊 Berechne Aerobic Efficiency...")
        ae = berechne_aerobic_efficiency(alle_aktivitaeten)

        print("  📊 Berechne Wochenkilometer...")
        wochen_km = berechne_wochen_km(alle_aktivitaeten)

        print("  📊 Berechne Kadenz-Trend...")
        kadenz = berechne_kadenz_trend(alle_aktivitaeten)

        print("  📊 Berechne Intensitätsverteilung...")
        verteilung = berechne_intensitaetsverteilung(alle_aktivitaeten)

        # Aktueller Stand (letzte Werte)
        aktuell = {}
        if ctl_atl_tsb:
            letzter = ctl_atl_tsb[-1]
            aktuell = {
                "ctl": letzter["ctl"],
                "atl": letzter["atl"],
                "tsb": letzter["tsb"],
                "datum": letzter["datum"]
            }

        ergebnis = {
            "berechnet_am": datetime.now().isoformat(),
            "status": "ok",
            "aktuell": aktuell,
            "ctl_atl_tsb": ctl_atl_tsb[-56:],  # Letzte 8 Wochen
            "aerobic_efficiency": ae[-20:],  # Letzte 20 Läufe
            "wochen_km": wochen_km,
            "kadenz": kadenz,
            "intensitaetsverteilung": verteilung
        }

    # Ergebnis speichern
    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(ergebnis, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Analyse abgeschlossen. Ergebnis in {ANALYSIS_FILE}")

    if ergebnis.get("aktuell"):
        a = ergebnis["aktuell"]
        print(f"   CTL: {a['ctl']} | ATL: {a['atl']} | TSB: {a['tsb']}")

    return ergebnis


if __name__ == "__main__":
    main()
