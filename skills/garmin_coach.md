---
inclusion: manual
---

# Garmin Coach – Adaptives Lauftraining

Dieser Skill beschreibt ein **adaptives, datengetriebenes Coaching-System**. Kein statischer Plan – stattdessen wird nach jedem Lauf analysiert, was funktioniert hat, wo Potential liegt, und welcher Reiz als nächstes den größten Fortschritt bringt.

## Coaching-Philosophie

### Coach-Typen (wählbar in config/athlete.json → coach_typ.aktiv)

Der Athlet kann zwischen verschiedenen Trainingsphilosophien wählen. Die vollständige Beschreibung aller Typen liegt in `config/coach_types.json`.

| Coach | Verteilung | Kernidee |
|-------|-----------|----------|
| **Maffetone** | 100% Z1-Z2 | Nur unter MAF-HF laufen bis Basis steht |
| **Polarisiert** | 80% Z1-Z2, 20% Z4-Z5 | Leicht ODER hart, nie dazwischen |
| **Pyramidal** | 75% Z1, 15% Z2-Z3, 10% Z4-Z5 | Mehr Mitte erlaubt, hohes Volumen |
| **Threshold** | 60% Z1-Z2, 20% Z3, 20% Z4-Z5 | Schwellenarbeit als Herzstück |
| **Norwegisch** | 65% Z1-Z2, 25% Z3, 10% Z4-Z5 | Doppel-Schwelle, laktatgesteuert |
| **Adaptiv** | Variabel | KI wählt je nach Phase den besten Ansatz |

### Wie der Coach-Typ die Planung beeinflusst:

1. Lies `config/athlete.json` → `coach_typ.aktiv`
2. Lade die Regeln aus `config/coach_types.json` → `typen[aktiv]`
3. Wende die Intensitätsverteilung und erlaubten Trainingstypen an
4. Bei "adaptiv": Analysiere Daten und wähle den passenden Ansatz für die aktuelle Phase

### Adaptiv statt statisch

Der Coach lernt aus deinen Daten:
- **Was funktioniert bei DIR?** Manche Läufer reagieren stark auf Intervalle, andere brauchen mehr Volumen. Der Coach erkennt das über Zeit.
- **Wo liegt dein Potential?** Aerobe Basis schwach? Laktatschwelle zu niedrig? Pace-Effizienz stagniert? → Der Reiz wird gezielt gesetzt.
- **Wie erholt sich dein Körper?** HRV-Trend, Ruhepuls-Entwicklung und TSB zeigen, wann du bereit bist für den nächsten harten Reiz.

### Grundregeln (die der Coach dynamisch anpasst)

- **Polarisiert als Basis**: ~80% leicht, ~20% intensiv – aber die Verteilung wird angepasst wenn die Daten zeigen, dass du anders besser reagierst
- **Progressive Überlastung**: Volumen und Intensität steigen nur, wenn die Daten Erholung bestätigen
- **Variation**: Nie zwei identische Wochen hintereinander – der Körper braucht wechselnde Reize
- **Spezifität steigt**: Je näher das Zielrennen, desto spezifischer die Einheiten

## Athleten-Profiling (automatisch aus Daten)

Der Coach erstellt und aktualisiert ein Profil in `data/athlete_profile.json`:

### Erkannte Stärken und Schwächen

Aus den letzten 4–8 Wochen Daten werden ermittelt:

| Metrik | Wie erkannt | Bedeutung |
|--------|-------------|-----------|
| **Aerobe Basis** | Pace bei Z2-HF über Zeit | Kann der Athlet schnell laufen ohne hohe HF? |
| **Laktatschwellen-Fitness** | Pace bei Z4-HF, Dauer bis Drift | Wie lange hält er Schwellentempo? |
| **Schnelligkeit** | Beste Pace in kurzen Intervallen | Grundschnelligkeit vorhanden? |
| **Ausdauer** | Pace-Drift im langen Lauf (letzte 25% vs. erste 25%) | Hält die Pace über Distanz? |
| **Erholungsfähigkeit** | HRV-Recovery nach harten Einheiten, Tage bis TSB neutral | Wie schnell erholt sich der Körper? |
| **Kadenz-Effizienz** | Kadenz vs. Pace-Korrelation | Optimale Schrittfrequenz gefunden? |
| **Reaktion auf Intervalle** | VO2max-Trend nach Intervall-Wochen | Reagiert der Athlet auf Intervalle? |
| **Reaktion auf Volumen** | Aerobic Efficiency nach Volumen-Wochen | Reagiert er auf mehr Kilometer? |

### Profil-Format (data/athlete_profile.json)

```json
{
  "aktualisiert_am": "2026-05-23",
  "wochen_daten": 8,
  "staerken": ["aerobe_basis", "erholungsfaehigkeit"],
  "schwaechen": ["laktatschwelle", "ausdauer_drift"],
  "empfohlener_fokus": "schwellenarbeit",
  "reaktion_auf": {
    "intervalle": "stark",
    "volumen": "moderat",
    "tempo_laeufe": "noch_unklar"
  },
  "trends": {
    "aerobic_efficiency": "verbessernd",
    "vo2max": "stagnierend",
    "wochen_km": "steigend",
    "gewicht": "fallend"
  },
  "limitierender_faktor": "laktatschwelle",
  "naechster_durchbruch": "Wenn Schwellenpace um 10 sek/km sinkt, ist Sub-1:26 HM realistisch"
}
```

## Trainingstypen-Katalog

Der Coach wählt aus einem breiten Repertoire – nicht nur "leichter Lauf" und "Intervalle":

### Grundlagen-Einheiten (Zone 1–2)
| Typ | Beschreibung | Wann einsetzen |
|-----|-------------|----------------|
| **Lockerer Dauerlauf** | 30–60 min, rein nach HF (Z2), Pace egal | Standard-Grundlage |
| **Langer Lauf** | 60–120 min, Z2, gleichmäßig | Ausdauer aufbauen, Fettstoffwechsel |
| **Langer Lauf progressiv** | 90 min, erste 60 min Z2, letzte 30 min Z3 | Ausdauer + mentale Stärke |
| **Recovery-Lauf** | 20–30 min, Z1, sehr langsam | Nach harten Einheiten, aktive Erholung |
| **Nüchternlauf** | 40–60 min, Z2, morgens vor dem Frühstück | Fettstoffwechsel, Gewichtsmanagement |

### Schwellenarbeit (Zone 3–4)
| Typ | Beschreibung | Wann einsetzen |
|-----|-------------|----------------|
| **Tempodauerlauf** | 20–40 min am Stück in Z3-Z4 | Laktatschwelle anheben |
| **Cruise Intervals** | 3–5x 8 min Z4, 2 min Trab | Schwellenarbeit mit Erholung |
| **Schwellensteigerung** | 30 min, alle 10 min eine Zone höher (Z2→Z3→Z4) | Schwelle + Pacing lernen |
| **Tempo-Wechsel** | Abwechselnd 5 min Z3 / 5 min Z2, 40 min gesamt | Schwelle bei geringerer Belastung |

### Intervalle (Zone 4–5)
| Typ | Beschreibung | Wann einsetzen |
|-----|-------------|----------------|
| **Kurze Intervalle** | 8–12x 400m Z5, 200m Trab | Grundschnelligkeit, VO2max |
| **Mittlere Intervalle** | 5–8x 800m Z4-Z5, 400m Trab | VO2max, Laktatschwelle |
| **Lange Intervalle** | 4–6x 1000–1600m Z4, 400m Trab | Spezifische Ausdauer |
| **Pyramide** | 400-800-1200-1600-1200-800-400m | Variation, mentale Stärke |
| **Fahrtspiel (Fartlek)** | 40 min mit 6–8 Tempowechseln nach Gefühl | Lockerheit, Rhythmuswechsel |

### Spezial-Einheiten
| Typ | Beschreibung | Wann einsetzen |
|-----|-------------|----------------|
| **Steigerungsläufe** | 6–8x 100m Steigerung bis Sprint am Ende eines Z2-Laufs | Laufökonomie, neuromuskulär |
| **Hügelsprints** | 8–10x 30 sek bergauf maximal, Geh-Pause runter | Kraft, Schnelligkeit |
| **Bergintervalle** | 4–6x 3 min bergauf Z4, Trab runter | Kraft-Ausdauer |
| **Renntempo-Blöcke** | 2–3x 10 min in Ziel-Renntempo, 3 min Trab | Rennspezifisch, Pacing |
| **Negative Splits** | Lauf mit bewusst schnellerer zweiter Hälfte | Pacing, mentale Stärke |
| **Cut-Down-Lauf** | Jeder km 5–10 sek schneller als der vorherige | Progressive Belastung |

## Adaptive Entscheidungslogik

### Nach jedem Lauf: Was braucht der Athlet als nächstes?

```
1. ERHOLUNG PRÜFEN
   ├── TSB < -25 → STOP: Nur Recovery/Ruhe bis TSB > -15
   ├── TSB < -15 → Nur Z1-Z2 Einheiten
   ├── HRV-Trend fallend (>10ms unter Baseline) → Intensität reduzieren
   └── TSB > -10 → Alle Optionen offen

2. LIMITIERENDEN FAKTOR IDENTIFIZIEREN
   ├── Aerobic Efficiency stagniert → Mehr Z2-Volumen oder Steigerungsläufe
   ├── Pace bei Z4 stagniert → Schwellenarbeit (Cruise Intervals, Tempo)
   ├── Drift im langen Lauf > 15 sek/km → Längere Läufe, progressive Long Runs
   ├── VO2max stagniert → Kurze/mittlere Intervalle
   ├── Kadenz < 170 → Steigerungsläufe, Kadenz-Fokus-Läufe
   └── Alles verbessert sich → Weiter so, leichte Progression

3. TRAININGSREIZ WÄHLEN
   ├── Welcher Reiz hat in den letzten 4 Wochen GEFEHLT?
   │   (Variation sicherstellen – nie >2 Wochen gleicher Schwerpunkt)
   ├── Welcher Reiz hat beim Athleten die BESTE Reaktion gezeigt?
   │   (Aus athlete_profile.json → reaktion_auf)
   ├── Was passt zur aktuellen PHASE?
   │   (Aufbau: Volumen > Intensität, Spezifisch: Renntempo, Tapering: kurz+knackig)
   └── Was passt zum ZEITBUDGET des Tages?
       (Werktag max 60 min, Wochenende max 120 min)

4. WORKOUT KONKRETISIEREN
   ├── Typ aus Katalog wählen
   ├── Dauer/Distanz an aktuelles Niveau anpassen
   ├── Zielzonen aus config/athlete.json berechnen
   ├── Garmin-kompatibles Format erstellen (für Push)
   └── Begründung für den Athleten formulieren
```

### Beispiel-Entscheidungskette:

> Letzter Lauf: Langer Lauf, Pace-Drift +20 sek/km in den letzten 5 km.
> TSB: -8 (erholt genug). Letzte 3 Wochen: kein Schwellentraining.
> Profil: Reagiert stark auf Intervalle, Schwäche = Ausdauer-Drift.
>
> → Entscheidung: **Cruise Intervals** (4x 8 min Z4, 2 min Trab)
> → Begründung: "Dein langer Lauf zeigt Drift in den letzten km – das deutet auf eine Schwäche an der Laktatschwelle hin. Cruise Intervals heben deine Schwelle an, ohne dich zu überlasten. Du reagierst gut auf Intervallreize."

## Progression über Wochen

### Woche 1–4: Kennenlernen
- Verschiedene Reize setzen, Reaktion beobachten
- Baseline für alle Metriken etablieren
- Profil aufbauen

### Ab Woche 5: Adaptives Coaching
- Fokus auf limitierenden Faktor
- Reize gezielt setzen basierend auf Profil
- Alle 2 Wochen: Profil aktualisieren, Strategie anpassen

### Periodisierung (dynamisch, nicht starr)
- **Aufbau** (>12 Wochen vor Rennen): 70% Volumen-Fokus, 30% Intensität
- **Spezifisch** (4–12 Wochen): 50/50, Renntempo-Einheiten einbauen
- **Tapering** (<4 Wochen): Volumen -40%, Intensität beibehalten, nur kurze knackige Reize
- **Recovery-Blöcke**: Nicht starr alle 4 Wochen, sondern wenn TSB/HRV es erfordern

## Gewichtsmanagement-Integration

- Bei Gewichtsreduktionsziel: bevorzuge Nüchternläufe und lange Z2-Einheiten
- Berechne Pace/kg als zusätzliche Leistungsmetrik
- Warnung wenn Gewichtsverlust zu schnell (>0.5 kg/Woche) → Intensität reduzieren
- Fortschritt in Coach-Kommentar erwähnen

## Plan-Format (data/plan.json)

```json
{
  "erstellt_am": "2026-05-23",
  "gueltig_bis": "2026-05-30",
  "phase": "spezifisch",
  "wochen_km_ziel": 48,
  "fokus_diese_woche": "Laktatschwelle anheben",
  "begruendung": "VO2max stagniert seit 3 Wochen, Schwellenpace hat sich nicht verbessert. Cruise Intervals und ein progressiver Long Run sollen die Schwelle nach oben schieben.",
  "tage": [
    {
      "datum": "2026-05-24",
      "typ": "lockerer_dauerlauf",
      "beschreibung": "Lockerer Dauerlauf, rein nach Herzfrequenz",
      "dauer_min": 45,
      "distanz_km": 8,
      "ziel_zone": "Z2",
      "ziel_pace_bereich": "5:45-6:15 min/km",
      "garmin_workout_typ": "leichter_lauf",
      "coach_notiz": "Locker bleiben, Pace ist egal – nur HF zählt heute."
    },
    {
      "datum": "2026-05-25",
      "typ": "cruise_intervals",
      "beschreibung": "4x 8 min Schwellentempo, 2 min Trabpause",
      "dauer_min": 55,
      "distanz_km": 11,
      "ziel_zone": "Z4",
      "details": "15 min Einlaufen Z2 → 4x(8 min Z4 + 2 min Z1) → 10 min Auslaufen Z1",
      "garmin_workout_typ": "intervalle",
      "coach_notiz": "Fokus auf gleichmäßiges Tempo in den Intervallen. Nicht zu schnell starten!"
    },
    {
      "datum": "2026-05-27",
      "typ": "steigerungslaeufe",
      "beschreibung": "40 min Z2 + 6x 100m Steigerung",
      "dauer_min": 50,
      "distanz_km": 9,
      "ziel_zone": "Z2",
      "details": "40 min lockerer Dauerlauf Z2, dann 6x 100m Steigerung bis Sprinttempo, 100m Geh-Pause",
      "garmin_workout_typ": "leichter_lauf",
      "coach_notiz": "Die Steigerungen am Ende verbessern deine Laufökonomie. Locker und flüssig steigern."
    },
    {
      "datum": "2026-05-29",
      "typ": "langer_lauf_progressiv",
      "beschreibung": "90 min progressiv: 60 min Z2, 20 min Z3, 10 min Z4",
      "dauer_min": 90,
      "distanz_km": 16,
      "ziel_zone": "Z2-Z4",
      "details": "60 min Z2 → 20 min Z3 → 10 min Z4 (Renntempo)",
      "garmin_workout_typ": "langer_lauf",
      "coach_notiz": "Der progressive Aufbau simuliert die Rennbelastung. Die letzten 10 min in Renntempo geben dir Vertrauen."
    }
  ]
}
```

## Empfehlungen generieren

Für die nächsten 7 Tage werden ausgegeben:

- **Trainingseinheiten**: Typ, Dauer, Distanz, Zielzone, Pace-Bereich, Coach-Notiz
- **Wochen-Fokus**: Was ist das Ziel dieser Woche und warum?
- **Coach-Kommentar**: Einschätzung zum aktuellen Zustand (3–5 Sätze)
- **Begründung**: Warum genau diese Einheiten gewählt wurden
- **Warnungen**: Falls Übertraining droht, Muster erkannt werden, oder Anpassung nötig

## Report generieren

Nach der Analyse wird `scripts/generate_report.py` aufgerufen:

```bash
python scripts/generate_report.py
```

Dies aktualisiert `web/index.html` mit:

### Rückblick (8 Wochen):
- CTL/ATL/TSB-Kurve als Liniendiagramm
- Wochenkilometer als Balkendiagramm
- Aerobic Efficiency als Linienchart
- Intensitätsverteilung (Pie-Chart: Z1-Z2 vs. Z4-Z5)
- Letzte 5 Läufe: Kennzahlen-Tabelle

### Ausblick (7 Tage):
- Trainingsplan als Tabelle mit Datum, Typ, Dauer, Zone, Coach-Notiz
- Nächster Schlüssel-Workout hervorgehoben
- Wochen-Fokus und Begründung

### Coach-Einschätzung:
- Textblock mit aktueller Formanalyse
- Erkannte Stärken und Schwächen
- Empfehlung für Fokus der kommenden Woche
- Prognose Richtung Zielrennen

## Workflow nach jedem Lauf

Wenn der Nutzer sagt: *„Neuer Lauf heute, analysiere und aktualisiere alles."*

1. **garmin_data.md** ausführen: Neue Aktivitäten abrufen und speichern
2. **analyze.py** ausführen: CTL/ATL/TSB und Trends berechnen
3. **Profil aktualisieren**: `data/athlete_profile.json` mit neuen Erkenntnissen
4. **Adaptive Entscheidung**: Limitierenden Faktor identifizieren, Reiz wählen
5. **Plan anpassen**: `data/plan.json` mit begründeten Einheiten füllen
6. **Report generieren**: `scripts/generate_report.py` → `web/index.html`
7. **Zusammenfassung ausgeben**: Coach-Kommentar + nächste Einheit + Begründung
8. **Optional** (nur auf Anfrage): Nächsten Workout zu Garmin pushen

## Wichtig: Keine Wiederholung

- Nie zwei Wochen mit identischem Aufbau
- Trainingstypen rotieren (nicht jede Woche die gleichen Intervalle)
- Wenn ein Reiz 3+ Wochen keine Verbesserung zeigt → anderen Ansatz wählen
- Der Coach erklärt IMMER warum er eine bestimmte Einheit wählt

## Feature: Verletzungsprävention

Berechnet Risiko-Indikatoren und warnt frühzeitig.

### Metriken:

| Indikator | Formel | Warnschwelle |
|-----------|--------|--------------|
| **Monotonie** | Std.Abw. der täglichen Belastung / Durchschnitt (7 Tage) | > 2.0 |
| **Strain** | Wochen-Belastung × Monotonie | > 3000 |
| **ACWR** | ATL / CTL (Acute:Chronic Workload Ratio) | > 1.5 |
| **Volumensprung** | Wochen-km vs. 4-Wochen-Durchschnitt | > 30% |

### Warnungen:
- ACWR > 1.5 → "Belastungssprung zu groß. Volumen diese Woche reduzieren."
- Monotonie > 2.0 → "Training zu gleichförmig. Mehr Variation einbauen."
- 3+ Wochen ohne Ruhetag → "Regeneration fehlt. Ruhetag einplanen."
- Volumensprung > 30% → "Zu schnelle Steigerung. Max. 10% pro Woche."

### Integration:
- Wird bei jeder Analyse berechnet
- Erscheint als Warnung im Dashboard wenn Schwellen überschritten
- Coach passt Plan automatisch an wenn Risiko hoch

## Feature: Cardiac Drift (Pace-Dekopplung)

Misst wie stark die HF bei gleichbleibender Pace über die Laufdauer ansteigt.

### Berechnung:
- Vergleiche Durchschnitts-HF der ersten 50% vs. letzten 50% des Laufs
- Drift = (HF_zweite_Hälfte - HF_erste_Hälfte) / HF_erste_Hälfte × 100

### Bewertung:
| Drift | Bedeutung |
|-------|-----------|
| < 3% | Exzellent – starke aerobe Basis |
| 3-5% | Gut – normale Dekopplung |
| 5-10% | Moderat – Ausdauer ausbaufähig |
| > 10% | Hoch – aerobe Basis limitiert, mehr Z2-Volumen nötig |

### Trend:
- Wird für jeden Lauf > 40 min berechnet
- Sinkender Drift über Wochen = aerobe Fitness verbessert sich
- Im Dashboard als Trend-Linie darstellbar

## Feature: Lauf-Vergleich

Vergleiche zwei Läufe auf ähnlicher Strecke, um Fortschritt sichtbar zu machen.

### Matching-Kriterien (gleiche Strecke):
- Distanz innerhalb ±500m
- Höhenmeter innerhalb ±20%
- Idealerweise gleicher Name oder ähnlicher Startbereich

### Vergleichsmetriken:
| Metrik | Bedeutung |
|--------|-----------|
| Pace bei gleicher HF | Aerobe Verbesserung |
| HF bei gleicher Pace | Effizienz-Gewinn |
| Aerobic Efficiency | Gesamtbild Pace/HF |
| Pace-Drift | Ausdauer-Verbesserung |
| Kadenz | Lauftechnik-Entwicklung |

### Ausgabe:
- Tabellarischer Vergleich der beiden Läufe
- Prozentuale Veränderung pro Metrik
- Coach-Kommentar: Was hat sich verbessert, was nicht?
- Im Dashboard: Vergleichs-Karte mit Vorher/Nachher

## Feature: Rennprognose

Berechnet eine realistische Zielzeit für das Zielrennen basierend auf aktuellen Daten.

### Berechnungsgrundlage:
1. **Schwellenpace** (aus Z4-Läufen): Basis für Renntempo-Schätzung
2. **Aerobic Efficiency**: Wie effizient läuft der Athlet bei niedriger HF?
3. **Langstrecken-Drift**: Wie stark fällt die Pace über Distanz ab?
4. **Gewicht**: Jedes kg weniger ≈ 2-3 sek/km schneller
5. **Verbleibende Trainingswochen**: Wie viel Verbesserung ist noch realistisch?

### Formel (vereinfacht):
```
Renntempo = Schwellenpace × 1.05 + Drift-Korrektur + Gewichts-Korrektur
Zielzeit = Renntempo × Distanz
```

### Prognose-Verlauf:
- Wird bei jeder Analyse aktualisiert
- Gespeichert in `data/race_prognosis.json`
- Im Dashboard als Trend-Linie dargestellt
- Zeigt: "Wenn du so weitertrainierst, erreichst du X"

### Konfidenz-Level:
- **Hoch**: >8 Wochen Daten, stabile Trends, Langstrecken-Erfahrung
- **Mittel**: 4-8 Wochen Daten, Trends erkennbar
- **Niedrig**: <4 Wochen oder fehlende Langstrecken-Daten

## Feature: Erholungs-Tracking

Morgens (oder bei jeder Analyse) werden Recovery-Daten abgerufen und in die Trainingsempfehlung integriert.

### Datenquellen:
- HRV (Nacht-Messung) via `mcp_garmin_get_hrv_data`
- Ruhepuls via `mcp_garmin_get_rhr_day`
- Schlaf via `mcp_garmin_get_sleep_summary`
- Training Readiness via `mcp_garmin_get_training_readiness`
- Body Battery via `mcp_garmin_get_body_battery`

### Entscheidungsmatrix:

| Signal | Schwelle | Aktion |
|--------|----------|--------|
| HRV > 10ms unter 7-Tage-Schnitt | Kritisch | Nur Z1-Z2, keine Intensität |
| Training Readiness < 40 | Kritisch | Ruhetag empfehlen |
| Body Battery < 30 morgens | Warnung | Ruhetag oder nur Recovery-Lauf |
| Schlaf < 5h | Warnung | Einheit kürzen, keine Intensität |
| Ruhepuls > 5 bpm über Baseline | Warnung | Reduzierte Belastung |
| Alles normal | OK | Plan wie geplant ausführen |

### Integration in den Plan:
- Wenn Recovery-Daten schlecht → Plan wird automatisch angepasst
- Coach erklärt warum: "Dein HRV ist heute 12ms unter deinem Schnitt. Das deutet auf unvollständige Erholung hin. Heute nur lockerer Z2-Lauf statt der geplanten Intervalle."

## Feature: Gewichtsverlauf

Trackt das Gewicht über Zeit und korreliert es mit Trainingsvolumen.

### Datenquelle:
- `mcp_garmin_get_weigh_ins(start_date, end_date)` bei jeder Analyse
- Gespeichert in `data/weight_history.json`

### Metriken:
- Aktuelles Gewicht (7-Tage-Durchschnitt für Glättung)
- Veränderung pro Woche
- Trend-Richtung (fallend/stabil/steigend)
- Verbleibend bis Zielgewicht
- Pace/kg als Leistungsmetrik

### Warnungen:
- Gewichtsverlust > 0.7 kg/Woche → "Zu schnell, Verletzungsrisiko steigt"
- Gewichtszunahme trotz Training → "Kein Grund zur Sorge, Muskelaufbau möglich"
- Zielgewicht erreicht → "Ziel erreicht! Gewicht halten, Fokus auf Performance"

### Dashboard:
- Gewichtskurve als Linienchart (8 Wochen)
- Zielgewicht als horizontale Linie
- Korrelation mit Wochen-km (Doppelachse)

## Feature: Wochen-Zusammenfassung

Automatischer Rückblick am Ende jeder Woche.

### Inhalt:
```
Woche 21/2026 – Zusammenfassung
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Läufe: 3 | Gesamt: 28.4 km | Ø Pace: 5:35/km | Ø HF: 154 bpm
CTL: 16.7 (+1.2) | TSB: -12.4
Gewicht: 81.5 kg (-0.5 kg)
Intensität: 68% Z4-Z5 (Ziel: 20%) ⚠️

Highlight: Intervall-Training am 10.05. mit 3x1000m in 4:30
Problem: Immer noch zu viel Z4-Z5, zu wenig Z2
Nächste Woche: Fokus auf echte Z2-Läufe, HF unter 139 halten
```

### Speicherung:
- `data/weekly_summaries.json` – alle Wochen als Array
- Im Dashboard unter "Historie" als zusätzliche Timeline-Einträge

### Trigger:
- Automatisch jeden Sonntag bei Analyse
- Oder manuell: "Gib mir die Wochen-Zusammenfassung"
