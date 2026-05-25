#!/usr/bin/env python3
"""
Report-Generator: Erstellt web/index.html mit modernem Dark-Theme Dashboard.

Liest:
- data/analysis.json
- data/plan.json
- data/history.json
- data/coach_history.json
- data/athlete_profile.json
- config/athlete.json

Schreibt:
- web/index.html (vollständig neu generiert)

Standalone lauffähig: python scripts/generate_report.py
"""

import json
from datetime import datetime, date
from pathlib import Path

# Projektverzeichnis
PROJEKT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJEKT_DIR / "data"
CONFIG_DIR = PROJEKT_DIR / "config"
WEB_DIR = PROJEKT_DIR / "web"

ANALYSIS_FILE = DATA_DIR / "analysis.json"
PLAN_FILE = DATA_DIR / "plan.json"
HISTORY_FILE = DATA_DIR / "history.json"
COACH_HISTORY_FILE = DATA_DIR / "coach_history.json"
PROFILE_FILE = DATA_DIR / "athlete_profile.json"
ATHLETE_FILE = CONFIG_DIR / "athlete.json"
OUTPUT_FILE = WEB_DIR / "index.html"


def lade_json(pfad):
    """Lädt eine JSON-Datei, gibt leeres Dict zurück bei Fehler."""
    try:
        with open(pfad, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def format_pace(sek_pro_km):
    """Konvertiert Sekunden/km in min:ss Format."""
    if not sek_pro_km or sek_pro_km <= 0:
        return "--:--"
    minuten = int(sek_pro_km // 60)
    sekunden = int(sek_pro_km % 60)
    return f"{minuten}:{sekunden:02d}"


def berechne_countdown(ziel_datum_str):
    """Berechnet Tage bis zum Zielrennen."""
    try:
        ziel = datetime.strptime(ziel_datum_str, "%Y-%m-%d").date()
        heute = date.today()
        diff = (ziel - heute).days
        return max(0, diff)
    except (ValueError, TypeError):
        return 0


def generiere_coach_kommentar(analyse, plan, profil):
    """Generiert Coach-Kommentar basierend auf Profil und Analyse."""
    if not analyse or analyse.get("status") == "keine_daten":
        return "Noch keine Trainingsdaten vorhanden. Starte mit einem lockeren Lauf!"

    aktuell = analyse.get("aktuell", {})
    verteilung = analyse.get("intensitaetsverteilung", {})
    tsb = aktuell.get("tsb", 0)

    teile = []

    # TSB
    if tsb < -20:
        teile.append("⚠️ Hohe Ermüdung – Recovery-Phase dringend empfohlen.")
    elif tsb < -10:
        teile.append("Leichte Ermüdung erkennbar. Lockere Einheiten stehen im Vordergrund.")
    elif tsb > 5:
        teile.append("Gut erholt – bereit für intensivere Reize.")
    else:
        teile.append("Gute Balance zwischen Belastung und Erholung.")

    # Intensitätsverteilung
    z2_pct = verteilung.get("leicht_prozent", 0)
    if z2_pct < 20:
        teile.append(f"Dein Z1-Z2-Anteil liegt bei nur {z2_pct}% – das muss deutlich steigen. Ziel: mindestens 60%.")

    # Profil-basiert
    if profil:
        lf = profil.get("limitierender_faktor", "")
        if lf == "aerobe_basis":
            teile.append("Fokus: Aerobe Basis aufbauen durch konsequente Z2-Läufe.")

    return " ".join(teile)


def generiere_plan_html(plan):
    """Generiert HTML für den Trainingsplan."""
    tage = plan.get("tage", [])
    if not tage:
        return "<p style='color: var(--text-muted)'>Noch kein Plan erstellt.</p>"

    html_parts = []
    for tag in tage:
        zone = tag.get("ziel_zone", "Z2").replace("-", "").lower().replace("z2z3", "z3").replace("z2z4", "z4")
        zone_class = f"zone-{zone[:2].lower()}" if zone != "-" else "zone-z2"

        # Aufbau-Liste
        aufbau_html = ""
        aufbau = tag.get("aufbau", [])
        if aufbau:
            aufbau_html = "<ul class='plan-tag-details'>" + "".join(f"<li>{s}</li>" for s in aufbau) + "</ul>"

        # Coach-Notiz
        coach_html = ""
        notiz = tag.get("coach_notiz", "")
        if notiz:
            # Emojis aus Coach-Notizen entfernen
            import re
            notiz_clean = re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA6F\U0000FE00-\U0000FE0F\U0000200D]', '', notiz).strip()
            coach_html = f"<div class='plan-tag-coach'>{notiz_clean}</div>"

        # Ruhetag kompakt
        if tag.get("typ") == "ruhe":
            html_parts.append(f"""
            <div class="plan-tag ruhe">
                <div class="plan-tag-header">
                    <span class="plan-tag-datum">{tag.get("wochentag", "")} {tag.get("datum", "")}</span>
                    <span class="plan-tag-zone zone-z1">Ruhe</span>
                </div>
                <div class="plan-tag-titel">{tag.get("beschreibung", "Ruhetag")}</div>
            </div>""")
        else:
            html_parts.append(f"""
            <div class="plan-tag">
                <div class="plan-tag-header">
                    <span class="plan-tag-datum">{tag.get("wochentag", "")} {tag.get("datum", "")}</span>
                    <span class="plan-tag-zone {zone_class}">{tag.get("ziel_zone", "")}</span>
                </div>
                <div class="plan-tag-titel">{tag.get("beschreibung", "")}</div>
                <div class="plan-tag-meta">
                    <span>{tag.get("dauer_min", "")} min</span>
                    <span>{tag.get("distanz_km", "")} km</span>
                    <span>{tag.get("ziel_hf_bereich", tag.get("ziel_pace_bereich", ""))}</span>
                </div>
                {aufbau_html}
                {coach_html}
            </div>""")

    return "\n".join(html_parts)


def generiere_timeline_html(coach_history):
    """Generiert HTML für die Coach-Historie Timeline inkl. Wochen-Zusammenfassungen."""
    eintraege = coach_history.get("eintraege", [])

    # Wochen-Zusammenfassungen laden und als Timeline-Einträge formatieren
    try:
        with open(DATA_DIR / "weekly_summaries.json", "r", encoding="utf-8") as f:
            weekly = json.load(f)
        for ws in weekly.get("zusammenfassungen", []):
            eintraege.append({
                "datum": ws.get("datum_bis", ""),
                "titel": f"Wochen-Zusammenfassung {ws.get('woche', '')}",
                "zusammenfassung": f"{ws.get('laeufe', 0)} Läufe, {ws.get('gesamt_km', 0)} km, CTL {ws.get('ctl_ende', '--')} ({'+' if ws.get('ctl_veraenderung', 0) >= 0 else ''}{ws.get('ctl_veraenderung', 0)})",
                "erkenntnisse": [ws["highlight"]] if ws.get("highlight") else [],
                "probleme": [ws["problem"]] if ws.get("problem") else [],
                "empfehlung": ws.get("naechste_woche", ""),
                "kennzahlen": {
                    "ctl": ws.get("ctl_ende"),
                    "tsb": ws.get("tsb_ende"),
                    "wochen_km": ws.get("gesamt_km")
                }
            })
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    if not eintraege:
        return "<p style='color: var(--text-muted)'>Noch keine Coach-Einträge vorhanden.</p>"

    # Nach Datum sortieren (neueste zuerst)
    eintraege.sort(key=lambda e: e.get("datum", ""), reverse=True)

    html_parts = []
    for eintrag in eintraege:  # Bereits nach Datum sortiert (neueste zuerst)
        # Erkenntnisse
        erkenntnisse_html = ""
        if eintrag.get("erkenntnisse"):
            items = "".join(f"<li>{e}</li>" for e in eintrag["erkenntnisse"])
            erkenntnisse_html = f"""
            <div class="timeline-section">
                <div class="timeline-section-title">Erkenntnisse</div>
                <ul class="timeline-list">{items}</ul>
            </div>"""

        # Probleme
        probleme_html = ""
        if eintrag.get("probleme"):
            items = "".join(f"<li>{p}</li>" for p in eintrag["probleme"])
            probleme_html = f"""
            <div class="timeline-section">
                <div class="timeline-section-title">Probleme</div>
                <ul class="timeline-list problems">{items}</ul>
            </div>"""

        # Kennzahlen
        kz_html = ""
        kz = eintrag.get("kennzahlen", {})
        if kz:
            kz_items = []
            if "ctl" in kz:
                kz_items.append(f"<span class='timeline-kz'>CTL: <strong>{kz['ctl']}</strong></span>")
            if "atl" in kz:
                kz_items.append(f"<span class='timeline-kz'>ATL: <strong>{kz['atl']}</strong></span>")
            if "tsb" in kz:
                kz_items.append(f"<span class='timeline-kz'>TSB: <strong>{kz['tsb']}</strong></span>")
            if "wochen_km" in kz:
                kz_items.append(f"<span class='timeline-kz'>Wochen-km: <strong>{kz['wochen_km']}</strong></span>")
            if "z2_anteil_prozent" in kz:
                kz_items.append(f"<span class='timeline-kz'>Z2-Anteil: <strong>{kz['z2_anteil_prozent']}%</strong></span>")
            kz_html = f"<div class='timeline-kennzahlen'>{''.join(kz_items)}</div>"

        html_parts.append(f"""
        <div class="timeline-entry">
            <div class="timeline-datum">{eintrag.get("datum", "")}</div>
            <div class="timeline-titel">{eintrag.get("titel", "")}</div>
            <div class="timeline-zusammenfassung">{eintrag.get("zusammenfassung", "")}</div>
            {erkenntnisse_html}
            {probleme_html}
            <div class="timeline-section">
                <div class="timeline-section-title">Empfehlung</div>
                <p style="font-size: 0.8rem; color: var(--primary-light)">{eintrag.get("empfehlung", "")}</p>
            </div>
            {kz_html}
        </div>""")

    return "\n".join(html_parts)


def generiere_html(analyse, plan, history, config, coach_history, profil,
                   race_prognosis, weight_history, recovery_log, weekly_summaries):
    """Generiert das vollständige HTML-Dashboard."""

    # Chart-Daten
    ctl_atl_tsb = analyse.get("ctl_atl_tsb", [])
    wochen_km = analyse.get("wochen_km", [])
    ae = analyse.get("aerobic_efficiency", [])
    aktuell = analyse.get("aktuell", {})

    ctl_labels = json.dumps([d["datum"] for d in ctl_atl_tsb[-56:]])
    ctl_daten = json.dumps([d["ctl"] for d in ctl_atl_tsb[-56:]])
    atl_daten = json.dumps([d["atl"] for d in ctl_atl_tsb[-56:]])
    tsb_daten = json.dumps([d["tsb"] for d in ctl_atl_tsb[-56:]])

    # Trainingstage markieren (Tage mit tatsächlichem Training, TSS > 0)
    trainingstage = json.dumps([d["tss"] > 0 for d in ctl_atl_tsb[-56:]])

    km_labels = json.dumps([w["woche"] for w in wochen_km])
    km_daten = json.dumps([w["km"] for w in wochen_km])
    ae_labels = json.dumps([e["datum"] for e in ae])
    ae_daten = json.dumps([e["effizienz"] for e in ae])

    # Letzter Lauf
    aktivitaeten = history.get("aktivitaeten", [])
    letzter = aktivitaeten[-1] if aktivitaeten else None

    # Cardiac Drift Daten (aus Aktivitäten berechnen)
    drift_daten = []
    for akt_file in sorted((PROJEKT_DIR / "data" / "activities").glob("*.json")):
        try:
            with open(akt_file, "r") as f:
                akt = json.load(f)
            if akt.get("typ") != "running":
                continue
            hf_avg = akt.get("herzfrequenz", {}).get("durchschnitt", 0)
            dauer = akt.get("dauer_sekunden", 0)
            if hf_avg and dauer > 2400:  # Nur Läufe > 40 min
                hf_max = akt.get("herzfrequenz", {}).get("max", hf_avg)
                drift_pct = round((hf_max - hf_avg) / hf_avg * 100, 1) if hf_avg > 0 else 0
                drift_daten.append({"datum": akt.get("datum", ""), "drift": min(drift_pct, 20)})
        except (json.JSONDecodeError, KeyError):
            pass

    drift_labels = json.dumps([d["datum"] for d in drift_daten])
    drift_werte = json.dumps([d["drift"] for d in drift_daten])

    # Gewichtsdaten für Chart
    gewicht_eintraege = weight_history.get("eintraege", [])
    gewicht_labels = json.dumps([e["datum"] for e in gewicht_eintraege])
    gewicht_werte = json.dumps([e["gewicht_kg"] for e in gewicht_eintraege])
    gewicht_ziel = weight_history.get("ziel_kg", config.get("gewicht", {}).get("ziel_kg", 74))

    # Pace/HF Dual-Chart (letzte 10 Läufe)
    pace_hf_daten = []
    for akt in aktivitaeten[-10:]:
        pace = akt.get("pace_durchschnitt_sek_pro_km", 0)
        hf = akt.get("herzfrequenz_durchschnitt", 0)
        if pace and hf:
            pace_hf_daten.append({"datum": akt.get("datum", ""), "pace": pace, "hf": hf})
    pace_hf_labels = json.dumps([d["datum"] for d in pace_hf_daten])
    pace_hf_pace = json.dumps([d["pace"] for d in pace_hf_daten])
    pace_hf_hf = json.dumps([d["hf"] for d in pace_hf_daten])

    # Recovery-Ampel Daten
    recovery_eintraege = recovery_log.get("eintraege", [])
    recovery_aktuell = recovery_eintraege[-1] if recovery_eintraege else None

    # Zielrennen
    zielrennen = config.get("zielrennen", {})
    countdown = berechne_countdown(zielrennen.get("datum", ""))

    # Coach-Kommentar
    kommentar = generiere_coach_kommentar(analyse, plan, profil)

    # Plan HTML
    plan_html = generiere_plan_html(plan)

    # Timeline HTML
    timeline_html = generiere_timeline_html(coach_history)

    # Generiert am
    generiert_am = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Intensitätsverteilung
    verteilung = analyse.get("intensitaetsverteilung", {})

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Garmin Coach – Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
    <div class="app-container">
        <header>
            <div class="header-left">
                <h1>Garmin Coach</h1>
                <p class="subtitle">Generiert am {generiert_am}</p>
            </div>
            <div class="header-right">
                <div class="countdown">{countdown}</div>
                <span class="countdown-label">Tage bis {zielrennen.get("name", "Zielrennen")}</span>
            </div>
        </header>

        <!-- Navigation -->
        <nav class="nav-tabs">
            <button class="nav-tab active" data-tab="tab-dashboard">Dashboard</button>
            <button class="nav-tab" data-tab="tab-plan">Training</button>
            <button class="nav-tab" data-tab="tab-prognose">Prognose</button>
            <button class="nav-tab" data-tab="tab-charts">Statistiken</button>
            <button class="nav-tab" data-tab="tab-coach">Coach-Typ</button>
            <button class="nav-tab" data-tab="tab-historie">Historie</button>
        </nav>

        <!-- TAB: Dashboard -->
        <div id="tab-dashboard" class="tab-content active">

            <!-- Coach-Kommentar -->
            <div class="card coach-card">
                <h2>Coach-Einschätzung</h2>
                <p>{kommentar}</p>
            </div>

            <!-- Recovery-Ampel + Radial Gauge -->
            <div class="card">
                <h2>Tagesform</h2>
                <div class="recovery-row">
                    <div class="radial-gauge-container">
                        <svg class="radial-gauge" viewBox="0 0 120 120">
                            <circle class="gauge-bg" cx="60" cy="60" r="50" />
                            <circle class="gauge-fill" cx="60" cy="60" r="50"
                                style="stroke-dasharray: {round((recovery_aktuell.get('training_readiness', 50) / 100) * 314, 1) if recovery_aktuell else 0} 314"
                            />
                            <text class="gauge-value" x="60" y="55">{recovery_aktuell.get('training_readiness', '--') if recovery_aktuell else '--'}</text>
                            <text class="gauge-label" x="60" y="72">Readiness</text>
                        </svg>
                    </div>
                    <div class="recovery-details">
                        <div class="recovery-ampel {'ampel-gruen' if recovery_aktuell and recovery_aktuell.get('empfehlung') == 'normal' else 'ampel-gelb' if recovery_aktuell and recovery_aktuell.get('empfehlung') in ('nur_z2', 'reduziert') else 'ampel-rot' if recovery_aktuell and recovery_aktuell.get('empfehlung') == 'pause' else 'ampel-grau'}">
                            <span class="ampel-dot"></span>
                            <span class="ampel-text">{'Bereit' if recovery_aktuell and recovery_aktuell.get('empfehlung') == 'normal' else 'Nur locker' if recovery_aktuell and recovery_aktuell.get('empfehlung') in ('nur_z2', 'reduziert') else 'Pause' if recovery_aktuell and recovery_aktuell.get('empfehlung') == 'pause' else 'Keine Daten'}</span>
                        </div>
                        <div class="recovery-metrics">
                            <span>HRV: <strong>{recovery_aktuell.get('hrv_nacht_ms', '--') if recovery_aktuell else '--'} ms</strong></span>
                            <span>Puls: <strong>{recovery_aktuell.get('ruhepuls', '--') if recovery_aktuell else '--'} bpm</strong></span>
                            <span>Schlaf: <strong>{recovery_aktuell.get('schlaf_stunden', '--') if recovery_aktuell else '--'}h</strong></span>
                            <span>Battery: <strong>{recovery_aktuell.get('body_battery_morgens', '--') if recovery_aktuell else '--'}</strong></span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- KPIs -->
            <div class="card">
                <h2>Aktueller Stand</h2>
                <div class="kpi-grid">
                    <div class="kpi has-tooltip" tabindex="0">
                        <span class="kpi-wert">{aktuell.get('ctl', '--')}</span>
                        <span class="kpi-label">CTL (Fitness)</span>
                        <button class="kpi-info" aria-label="Info zu CTL">i</button>
                        <div class="kpi-tooltip">
                            <strong>CTL &ndash; Chronic Training Load</strong>
                            <p>Dein Fitness-Level als 42-Tage-Durchschnitt der Trainingsbelastung. Steigt langsam durch konsistentes Training.</p>
                            <div class="tooltip-meta">
                                <span class="tooltip-good">Gut: 40&ndash;80 (ambitionierter Hobbyläufer)</span>
                                <span class="tooltip-bad">Niedrig: &lt;20 = wenig Grundfitness aufgebaut</span>
                                <span class="tooltip-target">Ziel: Langsam steigern, nie &gt;5 Punkte/Woche</span>
                            </div>
                        </div>
                    </div>
                    <div class="kpi has-tooltip" tabindex="0">
                        <span class="kpi-wert danger">{aktuell.get('atl', '--')}</span>
                        <span class="kpi-label">ATL (Ermüdung)</span>
                        <button class="kpi-info" aria-label="Info zu ATL">i</button>
                        <div class="kpi-tooltip">
                            <strong>ATL &ndash; Acute Training Load</strong>
                            <p>Deine aktuelle Ermüdung als 7-Tage-Durchschnitt. Reagiert schnell auf harte Trainingswochen.</p>
                            <div class="tooltip-meta">
                                <span class="tooltip-bad">Hoch (&gt;CTL): Du bist überlastet</span>
                                <span class="tooltip-good">Ideal: Leicht über CTL = produktiver Reiz</span>
                                <span class="tooltip-target">Ziel: Sollte nach Erholung unter CTL fallen</span>
                            </div>
                        </div>
                    </div>
                    <div class="kpi has-tooltip" tabindex="0">
                        <span class="kpi-wert warning">{aktuell.get('tsb', '--')}</span>
                        <span class="kpi-label">TSB (Form)</span>
                        <button class="kpi-info" aria-label="Info zu TSB">i</button>
                        <div class="kpi-tooltip">
                            <strong>TSB &ndash; Training Stress Balance</strong>
                            <p>Deine aktuelle Form = CTL minus ATL. Zeigt ob du erholt oder ermüdet bist.</p>
                            <div class="tooltip-meta">
                                <span class="tooltip-good">Positiv (&gt;0): Erholt, bereit für Wettkampf</span>
                                <span class="tooltip-neutral">-10 bis 0: Normaler Trainingsreiz</span>
                                <span class="tooltip-bad">Unter -20: Übertraining-Risiko, Recovery nötig</span>
                                <span class="tooltip-target">Ziel am Renntag: +5 bis +15 (frisch &amp; fit)</span>
                            </div>
                        </div>
                    </div>
                    <div class="kpi has-tooltip" tabindex="0">
                        <span class="kpi-wert">{plan.get('wochen_km_ziel', '--')}</span>
                        <span class="kpi-label">km-Ziel/Woche</span>
                        <button class="kpi-info" aria-label="Info zu Wochenkilometer">i</button>
                        <div class="kpi-tooltip">
                            <strong>Wochenkilometer-Ziel</strong>
                            <p>Geplantes Laufvolumen für diese Woche. Wird adaptiv angepasst basierend auf Erholung und Phase.</p>
                            <div class="tooltip-meta">
                                <span class="tooltip-neutral">Aktueller Schnitt: ~{round(sum(w.get('km',0) for w in analyse.get('wochen_km',[]))/ max(len(analyse.get('wochen_km',[])),1),0):.0f} km/Woche</span>
                                <span class="tooltip-target">Steigerung: Max. 10% pro Woche</span>
                                <span class="tooltip-good">HM-Vorbereitung: 40&ndash;60 km/Woche ideal</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Intensitätsverteilung -->
            <div class="card alert-card">
                <h2>Intensitätsverteilung (4 Wochen)</h2>
                <div class="kpi-grid">
                    <div class="kpi">
                        <span class="kpi-wert success">{verteilung.get('leicht_prozent', 0)}%</span>
                        <span class="kpi-label">Z1-Z2 (Ziel: 80%)</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert warning">{verteilung.get('zone3_prozent', 0)}%</span>
                        <span class="kpi-label">Z3 (Ziel: &lt;10%)</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert danger">{verteilung.get('intensiv_prozent', 0)}%</span>
                        <span class="kpi-label">Z4-Z5 (Ziel: 20%)</span>
                    </div>
                </div>
            </div>

            <!-- Letzter Lauf -->
            {"" if not letzter else f'''
            <div class="card">
                <h2>Letzter Lauf &mdash; {letzter.get("datum", "")}</h2>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">{round(letzter.get("distanz_meter", 0) / 1000, 1)}</div>
                        <div class="stat-label">km</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{format_pace(letzter.get("pace_durchschnitt_sek_pro_km", 0))}</div>
                        <div class="stat-label">Pace /km</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{letzter.get("herzfrequenz_durchschnitt", "--")}</div>
                        <div class="stat-label">Avg HF</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{letzter.get("training_load", "--")}</div>
                        <div class="stat-label">Load</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{letzter.get("kalorien", "--")}</div>
                        <div class="stat-label">kcal</div>
                    </div>
                </div>
            </div>
            '''}

            <!-- Zielrennen -->
            <div class="card goal-card">
                <h2>Zielrennen</h2>
                <div class="goal-title">{zielrennen.get("name", "")} &mdash; {zielrennen.get("datum", "")}</div>
                <div class="goal-details">{zielrennen.get("distanz_km", "")} km in {zielrennen.get("zielzeit", "")} (Ziel: {format_pace(zielrennen.get("ziel_pace_sek_pro_km", 0))}/km)</div>
                <span class="goal-phase">{plan.get("phase", "").replace("_", " ")}</span>
            </div>
        </div>

        <!-- TAB: Trainingsplan -->
        <div id="tab-plan" class="tab-content">
            <div class="card">
                <h2>Wochenfokus: {plan.get("fokus_diese_woche", "")}</h2>
                <p class="plan-intro">{plan.get("begruendung", "")}</p>
            </div>
            {plan_html}
        </div>

        <!-- TAB: Prognose & Recovery -->
        <div id="tab-prognose" class="tab-content">
            <!-- Rennprognose -->
            <div class="card">
                <h2>Rennprognose: {race_prognosis.get("zielrennen", {}).get("name", "Zielrennen")}</h2>
                <div class="kpi-grid">
                    <div class="kpi">
                        <span class="kpi-wert">{race_prognosis.get("prognose_aktuell", {}).get("geschaetzte_zeit", "--")}</span>
                        <span class="kpi-label">Aktuelle Prognose</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert">{race_prognosis.get("zielrennen", {}).get("zielzeit", "--")}</span>
                        <span class="kpi-label">Zielzeit</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert">{race_prognosis.get("prognose_aktuell", {}).get("konfidenz", "--").title()}</span>
                        <span class="kpi-label">Konfidenz</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert">{countdown}</span>
                        <span class="kpi-label">Tage verbleibend</span>
                    </div>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.8rem; margin-top: 16px; line-height: 1.6">{race_prognosis.get("prognose_aktuell", {}).get("begruendung", "")}</p>
            </div>

            <!-- Prognose-Faktoren -->
            <div class="card">
                <h2>Einflussfaktoren auf die Prognose</h2>
                <div class="kpi-grid">
                    <div class="kpi has-tooltip" tabindex="0">
                        <span class="kpi-wert">{race_prognosis.get("faktoren", {}).get("aerobic_efficiency", {}).get("aktuell", "--")}</span>
                        <span class="kpi-label">Aerobic Efficiency</span>
                        <button class="kpi-info" aria-label="Info">i</button>
                        <div class="kpi-tooltip">
                            <strong>Aerobic Efficiency</strong>
                            <p>Pace (sek/km) geteilt durch HF. Niedrigere Werte = effizienter.</p>
                            <div class="tooltip-meta">
                                <span class="tooltip-neutral">Aktuell: {race_prognosis.get("faktoren", {}).get("aerobic_efficiency", {}).get("aktuell", "--")}</span>
                                <span class="tooltip-target">Ziel Sub-1:26: {race_prognosis.get("faktoren", {}).get("aerobic_efficiency", {}).get("ziel_fuer_sub_126", "--")}</span>
                            </div>
                        </div>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert">{format_pace(race_prognosis.get("faktoren", {}).get("schwellenpace", {}).get("aktuell_sek_pro_km", 0))}/km</span>
                        <span class="kpi-label">Schwellenpace</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert">{race_prognosis.get("faktoren", {}).get("langstrecken_drift", {}).get("aktuell_sek_pro_km", "--")}s</span>
                        <span class="kpi-label">Pace-Drift/km</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert">{race_prognosis.get("faktoren", {}).get("gewicht", {}).get("aktuell_kg", "--")} kg</span>
                        <span class="kpi-label">Gewicht</span>
                    </div>
                </div>
            </div>

            <!-- Recovery Status -->
            <div class="card {'alert-success' if not recovery_log.get('eintraege') else ''}">
                <h2>Recovery-Status</h2>
                {"<p style='color: var(--text-muted); font-size: 0.85rem'>Noch keine Recovery-Daten. Werden beim nächsten Morgen-Check abgerufen (HRV, Ruhepuls, Schlaf, Body Battery).</p>" if not recovery_log.get("eintraege") else "<p style='color: var(--success); font-size: 0.85rem'>Recovery-Daten vorhanden. Letzte Messung: " + recovery_log["eintraege"][-1].get("datum", "") + "</p>"}
            </div>

            <!-- Gewichtsverlauf -->
            <div class="card">
                <h2>Gewichtsverlauf</h2>
                {"<p style='color: var(--text-muted); font-size: 0.85rem'>Noch keine Gewichtsdaten. Werden beim nächsten Sync von Garmin abgerufen.</p>" if not weight_history.get("eintraege") else ""}
                <div class="kpi-grid" style="margin-top: 12px">
                    <div class="kpi">
                        <span class="kpi-wert">{weight_history.get("start_kg", config.get("gewicht", {}).get("aktuell_kg", "--"))}</span>
                        <span class="kpi-label">Start (kg)</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert">{weight_history.get("ziel_kg", config.get("gewicht", {}).get("ziel_kg", "--"))}</span>
                        <span class="kpi-label">Ziel (kg)</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert">{round(weight_history.get("start_kg", 82) - weight_history.get("ziel_kg", 74), 1)}</span>
                        <span class="kpi-label">Noch abzunehmen</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-wert">{config.get("gewicht", {}).get("ziel_datum", "--")}</span>
                        <span class="kpi-label">Zieldatum</span>
                    </div>
                </div>
                <p style="color: var(--text-muted); font-size: 0.75rem; margin-top: 12px">Jedes kg weniger = ca. 2-3 sek/km schneller im Rennen</p>
            </div>
        </div>

        <!-- TAB: Statistiken -->
        <div id="tab-charts" class="tab-content">
            <div class="card chart-container">
                <h2>Fitness / Ermüdung / Form (8 Wochen)</h2>
                <canvas id="ctlChart"></canvas>
            </div>
            <div class="card chart-container">
                <h2>Pace und Herzfrequenz pro Lauf</h2>
                <canvas id="paceHfChart"></canvas>
            </div>
            <div class="card chart-container">
                <h2>Cardiac Drift (niedriger = fitter)</h2>
                <canvas id="driftChart"></canvas>
            </div>
            <div class="card chart-container">
                <h2>Wochenkilometer</h2>
                <canvas id="kmChart"></canvas>
            </div>
            <div class="card chart-container">
                <h2>Aerobic Efficiency (niedriger = besser)</h2>
                <canvas id="aeChart"></canvas>
            </div>
            <div class="card chart-container">
                <h2>Gewichtsverlauf</h2>
                <canvas id="weightChart"></canvas>
            </div>
        </div>

        <!-- TAB: Coach-Typ -->
        <div id="tab-coach" class="tab-content">
            <div class="card coach-card">
                <h2>Aktiver Coach-Typ</h2>
                <p style="font-size: 1.1rem; font-weight: 600; color: var(--primary-light); margin-bottom: 8px">{config.get("coach_typ", {}).get("aktiv", "adaptiv").title()}</p>
                <p style="color: var(--text-secondary); font-size: 0.85rem">{config.get("coach_typ", {}).get("beschreibung", "")}</p>
                <p style="color: var(--text-muted); font-size: 0.75rem; margin-top: 12px">Ändern in: <code>config/athlete.json</code> → <code>coach_typ.aktiv</code></p>
            </div>

            <!-- Alle Coach-Typen -->
            <div class="card">
                <h2>Verfügbare Coach-Typen</h2>
                <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 20px">Wähle den Ansatz, der zu deiner aktuellen Situation passt. Setze den Wert in <code>config/athlete.json</code>.</p>
            </div>

            <div class="plan-tag">
                <div class="plan-tag-header">
                    <span class="plan-tag-datum">100% Z1-Z2</span>
                    <span class="plan-tag-zone zone-z2">MAF</span>
                </div>
                <div class="plan-tag-titel">Maffetone (MAF-Methode)</div>
                <div class="plan-tag-meta">
                    <span>Schlüssel: <code>maffetone</code></span>
                </div>
                <ul class="plan-tag-details">
                    <li>Nur unter MAF-HF laufen (180 - Alter). Bei dir: 146 bpm</li>
                    <li>Keine Intensität bis aerobe Basis steht (3+ Monate)</li>
                    <li>Ideal für: Anfänger, Übertrainierte, Gewichtsreduktion, Comeback</li>
                    <li>Fortschritt messen: Gleiche Strecke, gleiche HF → Pace wird schneller</li>
                </ul>
                <div class="plan-tag-coach">Empfohlen wenn du gerade erst anfängst oder deine aerobe Basis komplett fehlt. Geduld ist der Schlüssel.</div>
            </div>

            <div class="plan-tag">
                <div class="plan-tag-header">
                    <span class="plan-tag-datum">80% Z1-Z2 | 20% Z4-Z5</span>
                    <span class="plan-tag-zone zone-z2">80/20</span>
                </div>
                <div class="plan-tag-titel">Polarisiert (Seiler)</div>
                <div class="plan-tag-meta">
                    <span>Schlüssel: <code>polarisiert</code></span>
                </div>
                <ul class="plan-tag-details">
                    <li>80% leicht (Z1-Z2), 20% hart (Z4-Z5), Zone 3 vermeiden</li>
                    <li>Leichte Tage LEICHT, harte Tage HART – kein Mittelding</li>
                    <li>Ideal für: Fortgeschrittene, Marathon/HM-Vorbereitung</li>
                    <li>Wissenschaftlich am besten belegt für Ausdauersportler</li>
                </ul>
                <div class="plan-tag-coach">Der Klassiker. Funktioniert für die meisten Läufer. Erfordert Disziplin, die leichten Tage wirklich leicht zu halten.</div>
            </div>

            <div class="plan-tag">
                <div class="plan-tag-header">
                    <span class="plan-tag-datum">75% Z1 | 15% Z2-Z3 | 10% Z4-Z5</span>
                    <span class="plan-tag-zone zone-z3">Pyramidal</span>
                </div>
                <div class="plan-tag-titel">Pyramidal (Esteve-Lanao)</div>
                <div class="plan-tag-meta">
                    <span>Schlüssel: <code>pyramidal</code></span>
                </div>
                <ul class="plan-tag-details">
                    <li>Mehr moderate Einheiten (Z3) erlaubt als bei polarisiert</li>
                    <li>Braucht hohes Gesamtvolumen (50+ km/Woche) damit es wirkt</li>
                    <li>Ideal für: Erfahrene Läufer mit viel Trainingszeit</li>
                    <li>Tempo-Dauerläufe in Z3 sind ein Kernbestandteil</li>
                </ul>
                <div class="plan-tag-coach">Natürlichere Verteilung, aber nur sinnvoll bei hohem Volumen. Für 3 Lauftage/Woche eher nicht geeignet.</div>
            </div>

            <div class="plan-tag">
                <div class="plan-tag-header">
                    <span class="plan-tag-datum">60% Z1-Z2 | 20% Z3 | 20% Z4-Z5</span>
                    <span class="plan-tag-zone zone-z4">Schwelle</span>
                </div>
                <div class="plan-tag-titel">Threshold (Canova)</div>
                <div class="plan-tag-meta">
                    <span>Schlüssel: <code>threshold</code></span>
                </div>
                <ul class="plan-tag-details">
                    <li>Schwellenläufe (Z4) als Herzstück des Trainings</li>
                    <li>Spezifische Renntempo-Blöcke ab 8 Wochen vor dem Rennen</li>
                    <li>Ideal für: Wettkampforientierte mit klarem Zeitziel und guter Basis</li>
                    <li>Nur mit CTL > 30 starten – sonst Verletzungsrisiko</li>
                </ul>
                <div class="plan-tag-coach">Aggressiv und effektiv, aber riskant. Nur wenn deine aerobe Basis solide ist (CTL > 30).</div>
            </div>

            <div class="plan-tag">
                <div class="plan-tag-header">
                    <span class="plan-tag-datum">65% Z1-Z2 | 25% Z3 | 10% Z4-Z5</span>
                    <span class="plan-tag-zone zone-z3">Norwegisch</span>
                </div>
                <div class="plan-tag-titel">Norwegisch (Ingebrigtsen-Methode)</div>
                <div class="plan-tag-meta">
                    <span>Schlüssel: <code>norwegisch</code></span>
                </div>
                <ul class="plan-tag-details">
                    <li>2x/Woche Doppel-Schwellen-Training (knapp unter Laktatschwelle)</li>
                    <li>Hohes Gesamtvolumen nötig (60+ km/Woche)</li>
                    <li>Ideal für: Sehr ambitionierte Läufer mit viel Zeit</li>
                    <li>Idealerweise mit Laktat-Messung oder sehr guter HF-Kenntnis</li>
                </ul>
                <div class="plan-tag-coach">Die Methode der norwegischen Weltklasse-Läufer. Extrem effektiv, aber braucht hohes Volumen und gute Selbstkenntnis.</div>
            </div>

            <div class="plan-tag" style="border-color: var(--primary)">
                <div class="plan-tag-header">
                    <span class="plan-tag-datum">Variabel – KI entscheidet</span>
                    <span class="plan-tag-zone" style="background: var(--primary-subtle); color: var(--primary-light)">KI</span>
                </div>
                <div class="plan-tag-titel">Adaptiv (KI-gesteuert)</div>
                <div class="plan-tag-meta">
                    <span>Schlüssel: <code>adaptiv</code></span>
                </div>
                <ul class="plan-tag-details">
                    <li>KI analysiert deine Daten und wählt den besten Ansatz</li>
                    <li>Kann phasenweise zwischen Methoden wechseln</li>
                    <li>Anfangs Maffetone → dann Polarisiert → wettkampfnah Threshold</li>
                    <li>Maximal individuell, reagiert auf deine Fortschritte</li>
                </ul>
                <div class="plan-tag-coach">Die KI entscheidet basierend auf deinen Daten. Aktuell empfiehlt sie einen Maffetone-nahen Ansatz, weil deine aerobe Basis fehlt.</div>
            </div>
        </div>

        <!-- TAB: Coach-Historie -->
        <div id="tab-historie" class="tab-content">
            <div class="card">
                <h2>Coach-Analyse-Historie</h2>
                <p style="color: var(--text-secondary); font-size: 0.85rem;">Alle Analysen, Wochen-Zusammenfassungen und Empfehlungen chronologisch dokumentiert.</p>
            </div>
            <div class="timeline">
                {timeline_html}
            </div>
        </div>

        <footer>
            <p>Garmin Coach · Datenquelle: Garmin Connect via MCP · Automatisch generiert · <a href="setup.html" style="color: var(--primary-light)">Setup-Wizard</a></p>
        </footer>
    </div>

    <script src="charts.js"></script>
    <script>
        const chartData = {{
            ctl: {{ labels: {ctl_labels}, ctl: {ctl_daten}, atl: {atl_daten}, tsb: {tsb_daten}, trainingstage: {trainingstage} }},
            km: {{ labels: {km_labels}, werte: {km_daten} }},
            ae: {{ labels: {ae_labels}, werte: {ae_daten} }},
            drift: {{ labels: {drift_labels}, werte: {drift_werte} }},
            weight: {{ labels: {gewicht_labels}, werte: {gewicht_werte}, ziel: {gewicht_ziel} }},
            paceHf: {{ labels: {pace_hf_labels}, pace: {pace_hf_pace}, hf: {pace_hf_hf} }}
        }};
        initCharts(chartData);
    </script>
</body>
</html>"""

    return html


def main():
    """Hauptfunktion."""
    print("📄 Report-Generierung gestartet...")

    analyse = lade_json(ANALYSIS_FILE)
    plan = lade_json(PLAN_FILE)
    history = lade_json(HISTORY_FILE)
    config = lade_json(ATHLETE_FILE)
    coach_history = lade_json(COACH_HISTORY_FILE)
    profil = lade_json(PROFILE_FILE)

    # Neue Datenquellen
    race_prognosis = lade_json(DATA_DIR / "race_prognosis.json")
    weight_history = lade_json(DATA_DIR / "weight_history.json")
    recovery_log = lade_json(DATA_DIR / "recovery_log.json")
    weekly_summaries = lade_json(DATA_DIR / "weekly_summaries.json")

    html = generiere_html(analyse, plan, history, config, coach_history, profil,
                          race_prognosis, weight_history, recovery_log, weekly_summaries)

    WEB_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Report generiert: {OUTPUT_FILE}")
    print(f"   Öffne im Browser: file://{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
