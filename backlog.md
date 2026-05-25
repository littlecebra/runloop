# Backlog – Garmin Coach

## Legende

- **Priorität**: P1 (kritisch) → P5 (nice-to-have)
- **Aufwand**: S (klein, <2h) | M (mittel, 2-8h) | L (groß, >8h)
- **Status**: Offen | In Arbeit | Erledigt

---

## Dashboard & UI

### DASH-01: Heatmap-Kalender
**Priorität:** P3 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich auf einen Blick sehen, an welchen Tagen ich trainiert habe und wie intensiv, damit ich Konsistenz und Lücken sofort erkenne.

**Beschreibung:** GitHub-Contributions-Style Kalender. Jeder Tag des Jahres als kleines Kästchen. Farbe = Trainingsintensität (Training Load). Grau = kein Training, helles Lila = leicht, dunkles Lila = intensiv.

**Akzeptanzkriterien:**
- Zeigt mindestens 12 Wochen (idealerweise ganzes Jahr)
- Farbskala: Kein Training → Leicht → Moderat → Intensiv → Sehr intensiv
- Hover zeigt: Datum, km, Dauer, Training Load
- Responsive auf Mobile (horizontal scrollbar)

**Technische Hinweise:**
- Rein CSS Grid + JS, kein externes Library nötig
- Daten aus `data/history.json` (Datum + Training Load pro Tag)

---

### DASH-02: Pace-Zonen Stacked Bar
**Priorität:** P3 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich visuell sehen, wie sich meine Intensitätsverteilung pro Lauf über die letzten Wochen verändert, damit ich erkenne ob ich mich Richtung 80/20 bewege.

**Beschreibung:** Gestapeltes Balkendiagramm. Pro Lauf ein Balken. Farben = Zeit in Z1-Z5. Zeigt die letzten 10-15 Läufe nebeneinander.

**Akzeptanzkriterien:**
- Letzte 10-15 Läufe als Balken
- Farbkodierung: Z1 grün, Z2 hellgrün, Z3 gelb, Z4 orange, Z5 rot
- Legende mit Prozentangaben
- Hover zeigt exakte Minuten pro Zone

**Datenquelle:** `data/activities/*.json` → `herzfrequenz.zonen`

---

### DASH-03: "Was wäre wenn"-Simulator
**Priorität:** P4 | **Aufwand:** L | **Status:** Offen

**User Story:** Als Läufer möchte ich interaktiv simulieren können, wie sich Änderungen (mehr Volumen, Gewichtsverlust, andere Intensität) auf meine Rennprognose auswirken.

**Beschreibung:** Interaktives Widget mit Slidern:
- Wochen-km Slider (20-80 km)
- Gewicht Slider (aktuell → Ziel)
- Intensitätsverteilung Slider (Z2% vs Z4%)
- Trainingswochen bis Rennen

Output: Geschätzte Zielzeit-Veränderung in Echtzeit.

**Akzeptanzkriterien:**
- Slider-basierte Eingabe
- Echtzeit-Berechnung der Prognose-Änderung
- Zeigt Delta zur aktuellen Prognose
- Erklärungstext warum sich die Prognose ändert

---

### DASH-04: "Frag den Coach" Textfeld
**Priorität:** P5 | **Aufwand:** L | **Status:** Offen

**User Story:** Als Läufer möchte ich im Dashboard Fragen stellen können ("Kann ich morgen Wettkampf laufen?", "Soll ich bei Regen raus?") und kontextbezogene Antworten bekommen.

**Beschreibung:** Freies Textfeld im Dashboard. Fragen werden an Kiro weitergeleitet (oder lokal per LLM beantwortet). Kontext: Aktuelle Daten, Plan, Recovery-Status.

**Hinweis:** Braucht entweder Server-Backend oder Integration mit Kiro-Chat. Aktuell nicht ohne Server möglich.

---

### DASH-05: Lauf-Vergleich im Dashboard
**Priorität:** P3 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich zwei Läufe auf ähnlicher Strecke visuell gegenüberstellen, damit ich meinen Fortschritt objektiv sehe.

**Beschreibung:** Vergleichs-Karte mit zwei Läufen nebeneinander. Matching: Distanz ±500m, Höhenmeter ±20%. Zeigt Pace, HF, Effizienz, Drift als Vorher/Nachher.

**Akzeptanzkriterien:**
- Automatisches Matching ähnlicher Läufe
- Tabellarischer Vergleich mit Prozent-Veränderung
- Farbkodierung: Grün = verbessert, Rot = verschlechtert
- Coach-Kommentar zum Vergleich

**Datenquelle:** `data/activities/*.json` – Distanz, Höhenmeter, Pace, HF

---

### DASH-06: VO2max-Trend-Chart
**Priorität:** P4 | **Aufwand:** S | **Status:** Offen

**User Story:** Als Läufer möchte ich meinen VO2max-Trend über Zeit sehen, damit ich weiß ob mein Training die aerobe Kapazität verbessert.

**Beschreibung:** Linienchart mit VO2max-Werten über die letzten 8-12 Wochen.

**Datenquelle:** `mcp_garmin_get_vo2max_trend(start_date, end_date)`

---

### DASH-07: Export als PDF
**Priorität:** P5 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich mein Dashboard als PDF exportieren können, um es offline zu haben oder meinem Trainer zu zeigen.

**Technische Optionen:**
- `window.print()` mit Print-CSS
- html2canvas + jsPDF
- Puppeteer-Script (serverseitig)

---

## Trainingssteuerung

### TRAIN-01: Trainingsblock-Planung (Mesozyklus)
**Priorität:** P3 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich nicht nur 7 Tage, sondern 4-Wochen-Blöcke sehen, damit ich die Periodisierung verstehe.

**Beschreibung:** 4-Wochen-Mesozyklus-Logik:
- Woche 1: Einführung (70% Volumen)
- Woche 2: Aufbau (85%)
- Woche 3: Überlastung (100%)
- Woche 4: Recovery (60%)

**Akzeptanzkriterien:**
- 4-Wochen-Übersicht im Plan-Tab
- Aktuelle Woche hervorgehoben
- Volumen-Ziel pro Woche sichtbar
- Recovery-Woche automatisch erkannt und eingeplant

---

### TRAIN-02: Saisonale Meilenstein-Tests
**Priorität:** P2 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich alle 4-6 Wochen einen standardisierten Test absolvieren, damit ich meinen Fortschritt objektiv messen kann.

**Beschreibung:** Der Coach schlägt regelmäßig Tests vor und trackt die Ergebnisse:

1. **MAF-Test**: 5 km bei MAF-HF (180 - Alter) → Pace messen
   - Zeigt aerobe Entwicklung
   - Ziel: Pace wird bei gleicher HF schneller
   
2. **Laktat-Turn-Point-Test**: Steigerungslauf (alle 3 min +0.5 km/h schneller)
   - HF-Knick finden = Laktatschwelle
   - Zeigt Schwellenentwicklung

3. **Cooper-Test / 12-min-Test**: Maximale Distanz in 12 min
   - VO2max-Schätzung
   - Zeigt maximale aerobe Kapazität

**Akzeptanzkriterien:**
- Tests werden automatisch vorgeschlagen (alle 4-6 Wochen)
- Ergebnisse in `data/tests.json` gespeichert
- Trend-Visualisierung im Dashboard
- Coach-Kommentar: "Dein MAF-Test zeigt 9% Verbesserung in 6 Wochen"

**Garmin-Integration:**
- Test als Workout zu Garmin pushen
- Ergebnis nach dem Lauf automatisch auswerten

---

### TRAIN-03: Individuelle Zonen-Kalibrierung
**Priorität:** P2 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich, dass meine HF-Zonen auf meinen tatsächlichen Daten basieren und nicht nur auf einer Formel, damit die Trainingssteuerung präziser wird.

**Beschreibung:** Standard-Zonen (% HFmax) sind oft ungenau. Mit genug Laufdaten kann man:
- Ventilatorische Schwellen aus dem HF-Verlauf bei Steigerungsläufen schätzen
- Den HF-Knickpunkt (Deflection Point) aus Intervall-Daten ableiten
- Zonen automatisch anpassen wenn sich die Fitness ändert

**Ablauf:**
1. Sammle Daten aus Steigerungsläufen und Intervallen
2. Identifiziere den HF-Punkt wo die Pace-HF-Linearität bricht
3. Setze diesen als individuelle Schwelle
4. Berechne Zonen relativ zu dieser Schwelle (nicht zu HFmax)

**Output:** "Deine Z2-Obergrenze liegt laut Daten bei 142 bpm, nicht bei 139 wie berechnet. Zonen werden angepasst."

**Voraussetzung:** Mindestens 2-3 Steigerungsläufe oder Intervall-Einheiten in den Daten.

---

### TRAIN-04: Belastungs-Dosis per TRIMP
**Priorität:** P3 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich eine genauere Belastungsberechnung als Garmins "Training Load", die meine individuelle HF-Kurve berücksichtigt.

**Beschreibung:** Banister TRIMP (Training Impulse) nutzt die exakte HF-Verteilung:
- Gewichtet Zeit in höheren Zonen exponentiell stärker
- Berücksichtigt individuelle HFmax und Ruhepuls
- Genauer als einfaches "Dauer × Durchschnitts-HF"

**Formel:** TRIMP = Dauer (min) × ΔHF-Ratio × e^(1.92 × ΔHF-Ratio)
- ΔHF-Ratio = (HF_avg - HF_ruhe) / (HF_max - HF_ruhe)

**Datenquelle:** HF-Zonen-Daten aus `data/activities/*.json` (bereits vorhanden)

---

### TRAIN-05: Aerobic Decoupling (präzise Version)
**Priorität:** P1 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich wissen, ab welcher Distanz/Dauer meine aerobe Kapazität nicht mehr ausreicht, damit ich meine Long Runs optimal dosiere.

**Beschreibung:** Vergleiche das Verhältnis Pace:HF in der ersten vs. zweiten Hälfte eines Laufs.

**Berechnung:**
- Efficiency Factor (EF) = Pace / HF für erste und zweite Hälfte
- Decoupling = (EF_erste_Hälfte - EF_zweite_Hälfte) / EF_erste_Hälfte × 100

**Bewertung:**
| Decoupling | Bedeutung |
|-----------|-----------|
| < 5% | Aerob gut trainiert für diese Distanz |
| 5-10% | Grenzbereich – Distanz fordert dich |
| > 10% | Distanz überfordert aktuelle aerobe Kapazität |

**Konsequenz für den Coach:**
- "Du kannst 10 km aerob gut bewältigen, aber bei 15 km entkoppelt es >10%. Dein Long Run sollte aktuell bei 12 km bleiben und langsam gesteigert werden."

**Datenquelle:** Braucht Split-Daten (erste/zweite Hälfte). Aus `mcp_garmin_get_activity_splits` ableitbar wenn genug Laps vorhanden, oder aus der Gesamtdauer approximierbar.

---

### TRAIN-06: HF-Recovery-Analyse nach Intervallen
**Priorität:** P2 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich wissen, wie schnell sich meine HF nach harten Intervallen erholt, weil das einer der besten Fitness-Indikatoren ist.

**Beschreibung:** Nach jedem Intervall-Training:
- Wie schnell fällt die HF nach Belastungsende?
- HF-Drop in 60 Sekunden nach dem letzten Intervall
- Trend über Wochen tracken

**Interpretation:**
- HF-Drop > 30 bpm in 60s = exzellente Fitness
- HF-Drop 20-30 bpm = gut
- HF-Drop < 20 bpm = Erholung eingeschränkt oder Fitness ausbaufähig

**Vergleich über Zeit:** "Vor 4 Wochen brauchtest du 90 Sek um von 175 auf 140 zu fallen. Jetzt nur noch 55 Sek."

**Datenquelle:** `recovery_hr_bpm` ist bereits in den Activity-Daten vorhanden (Garmin misst das). Für detailliertere Analyse: Split-Daten bei Intervall-Läufen.

---

### TRAIN-07: Hitze-/Kälte-Anpassung
**Priorität:** P3 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich, dass der Coach die Temperatur berücksichtigt, damit ich bei Hitze nicht frustriert bin weil meine Pace "schlecht" ist.

**Beschreibung:** HF reagiert stark auf Temperatur. Pro 5°C über 15°C steigt die HF um ~5 bpm bei gleicher Pace. Das bedeutet:
- Bei 30°C ist deine Z2-Pace ~20-30 sek/km langsamer als bei 15°C
- Das ist NORMAL und kein Leistungsabfall

**Features:**
- Pace-Korrektur basierend auf Temperatur (aus Wetterdaten der Aktivität)
- "Heute 32°C: Deine Z2-Pace ist ~30 sek/km langsamer als bei 15°C. Das ist normal."
- Temperatur-bereinigte Aerobic Efficiency (faire Vergleiche über Jahreszeiten)
- Akklimatisierungs-Tracking: Wie gut passt sich dein Körper über Tage an Hitze an?

**Datenquelle:** Wetterdaten sind bereits in `data/activities/*.json` → `wetter.temperatur_fahrenheit`

---

### TRAIN-08: Pacing-Strategie-Analyse
**Priorität:** P3 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich wissen, ob ich meine Läufe gut einteile oder zu schnell starte, damit ich im Rennen die optimale Strategie fahre.

**Beschreibung:** Für jeden Lauf analysieren:
- **Positive Splits**: Erste Hälfte schneller als zweite (zu schnell gestartet)
- **Negative Splits**: Zweite Hälfte schneller (gut eingeteilt)
- **Even Splits**: Gleichmäßig (ideal für Rennen)

**Optimale Strategie berechnen:**
- Basierend auf individuellem Drift-Profil
- "Bei deinem Drift-Profil solltest du den HM mit 4:15/km starten und auf 4:05/km steigern"
- Warnung wenn Startpace zu aggressiv für aktuelle Fitness

**Datenquelle:** Split-Daten aus `mcp_garmin_get_activity_splits`

---

### TRAIN-09: Leistungskurve (Critical Pace)
**Priorität:** P3 | **Aufwand:** L | **Status:** Offen

**User Story:** Als Läufer möchte ich mein Stärke-Profil kennen (Sprinter vs. Ausdauer-Typ), damit der Coach die richtigen Reize setzt.

**Beschreibung:** Aus allen Läufen eine Leistungskurve berechnen:
- Beste Pace über: 1 min, 5 min, 10 min, 20 min, 60 min
- Zeigt: Wo liegt das Stärke-Profil?
- Trend: Verschiebt sich die Kurve nach links (schneller) oder rechts (ausdauernder)?

**Berechnung:**
- Für jede Dauer: Beste durchgehende Pace aus allen Aktivitäten
- Critical Pace = Asymptote der Kurve (theoretisch unendlich haltbare Pace)
- D' = Anaerobe Kapazität (Fläche über Critical Pace)

**Visualisierung:** Kurve mit Dauer auf X-Achse (log), Pace auf Y-Achse. Vergleich: Aktuell vs. vor 4 Wochen.

---

### TRAIN-10: Wettkampf-Simulation
**Priorität:** P4 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich vor dem Rennen testen ob mein Ziel realistisch ist, ohne einen vollen Wettkampf zu laufen.

**Beschreibung:** Vor dem Rennen einen Simulations-Lauf vorschlagen:
- "Lauf 10 km in Renntempo. Basierend auf deiner HF-Reaktion und dem Drift sage ich dir, ob Sub-1:26 realistisch ist."
- Analyse: HF bei Renntempo, Drift über 10 km, Recovery danach
- Prognose anpassen basierend auf Simulation

---

## Infrastruktur & Technik

### TECH-01: Umstieg auf React + shadcn/ui
**Priorität:** P4 | **Aufwand:** L | **Status:** Offen

**User Story:** Als Entwickler möchte ich ein modernes Frontend-Framework nutzen, damit das Dashboard interaktiver wird und Config-Editing direkt möglich ist.

**Vorteile:**
- Radix-Primitives, Tooltips, Dialogs, Tabs als fertige Komponenten
- Recharts für Charts (besser als Chart.js für React)
- Server-Actions für Config-Editing direkt im Dashboard
- Hot-Reload bei Entwicklung
- Bessere Interaktivität (Slider, Drag&Drop, Echtzeit-Updates)

**Nachteile:**
- Braucht Node.js + Build-Step
- Report-Generator müsste JSON liefern statt HTML
- Komplexere Infrastruktur

**Alternative:** Next.js mit App Router + shadcn/ui + Recharts

---

### TECH-02: Lokaler Dev-Server (Flask/FastAPI)
**Priorität:** P4 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Nutzer möchte ich die Config direkt im Dashboard editieren können, ohne Dateien manuell zu bearbeiten.

**Beschreibung:** Minimaler Python-Server:
- GET `/api/config` → athlete.json lesen
- POST `/api/config` → athlete.json schreiben
- GET `/api/data/analysis` → analysis.json
- POST `/api/analyze` → analyze.py ausführen

**Technologie:** Flask oder FastAPI, `pip install flask` als einzige Dependency.

---

### TECH-03: Config-Validierung (JSON Schema)
**Priorität:** P4 | **Aufwand:** S | **Status:** Offen

**User Story:** Als Nutzer möchte ich bei fehlerhaften Config-Werten eine klare Fehlermeldung bekommen, statt dass das System still fehlschlägt.

**Beschreibung:** JSON-Schema für `athlete.json`:
- HFmax: 120-220 (Pflicht)
- Ruhepuls: 30-100 (Pflicht)
- Lauftage: 1-7
- Gewicht: 40-200 kg
- Coach-Typ: enum der erlaubten Werte

Validierung beim Start von `analyze.py` und `generate_report.py`.

---

### TECH-04: Multi-Sport Support
**Priorität:** P5 | **Aufwand:** L | **Status:** Offen

**User Story:** Als Triathlet oder Cross-Trainer möchte ich auch Radfahren und Schwimmen einbeziehen, damit mein Gesamtbild vollständig ist.

**Beschreibung:** Aktuell nur Laufen. Erweiterung auf:
- Radfahren (eigene Zonen, eigene Metriken)
- Schwimmen (SWOLF, Pace/100m)
- Cross-Training-Effekt auf Lauf-Fitness

---

### TECH-05: Schuh-/Gear-Tracking
**Priorität:** P4 | **Aufwand:** S | **Status:** Offen

**User Story:** Als Läufer möchte ich wissen, wie viele Kilometer meine Schuhe haben, damit ich sie rechtzeitig ersetze und Verletzungen vermeide.

**Beschreibung:**
- Kilometer pro Schuh aus Garmin Gear-Daten tracken
- Warnung bei >600-800 km (Dämpfung nachlässt)
- Im Dashboard anzeigen: "Deine Nike Pegasus: 523 km – noch ~150 km bis zum Wechsel"

**Datenquelle:** `mcp_garmin_get_gear()` + `mcp_garmin_get_activity_gear(activity_id)`

---

### TECH-06: Wetter-Integration in Planung
**Priorität:** P4 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich, dass der Coach die Wettervorhersage berücksichtigt, damit ich bei extremen Bedingungen angepasste Empfehlungen bekomme.

**Beschreibung:**
- Wettervorhersage für geplante Lauftage abrufen
- Bei >30°C: Pace-Vorgabe anpassen, frühen Morgen empfehlen
- Bei Gewitter: Lauf verschieben
- Bei Kälte <0°C: Aufwärmzeit verlängern

---

## Analyse & Intelligenz

### AI-01: Aerobic Decoupling (präzise)
**Priorität:** P1 | **Aufwand:** M | **Status:** Offen

*Siehe TRAIN-05 – hier als Top-Priorität markiert weil es der wichtigste fehlende Fitness-Indikator ist.*

---

### AI-02: MAF-Test Tracking
**Priorität:** P2 | **Aufwand:** S | **Status:** Offen

**User Story:** Als Läufer möchte ich regelmäßig einen standardisierten Test machen und den Fortschritt sehen.

**Beschreibung:** Alle 4-6 Wochen:
1. Coach schlägt MAF-Test vor: "5 km bei HF 142 bpm – so schnell wie möglich"
2. Workout wird zu Garmin gepusht
3. Nach dem Lauf: Ergebnis automatisch auswerten
4. Trend visualisieren: "5:48/km → 5:22/km in 8 Wochen = 7.5% Verbesserung"

**Warum wichtig:** Objektiver, reproduzierbarer Fortschritts-Nachweis. Besonders wertvoll in der Z2-Phase wo sich "nichts zu tun scheint".

---

### AI-03: Individuelle Zonen-Kalibrierung
**Priorität:** P2 | **Aufwand:** M | **Status:** Offen

*Siehe TRAIN-03 – hier als hohe Priorität weil falsche Zonen das gesamte Training verfälschen.*

---

### AI-04: Verletzungsprävention (erweitert)
**Priorität:** P2 | **Aufwand:** M | **Status:** Offen

**User Story:** Als Läufer möchte ich frühzeitig gewarnt werden wenn mein Verletzungsrisiko steigt, damit ich rechtzeitig gegensteuern kann.

**Beschreibung:** Über die bereits implementierten Basis-Metriken (ACWR, Monotonie) hinaus:
- **Ermüdungs-Erkennung im Lauf**: Wenn Kadenz fällt und Bodenkontaktzeit steigt bei gleicher Pace → Technik bricht ein
- **Asymmetrie-Warnung**: Wenn verfügbar (nur mit HRM-Pro)
- **Schlaf-Defizit-Akkumulation**: Mehrere Nächte <6h → erhöhtes Risiko
- **Volumen-Sprung nach Pause**: Nach >7 Tagen Pause nicht sofort volles Volumen

**Hinweis:** Bodenkontaktzeit und Kadenz sind auch mit einfachem Brustgurt NICHT verfügbar. Diese Metriken kommen nur von der Uhr selbst (Beschleunigungssensor). Prüfen ob Garmin diese Daten über die API liefert.

---

### AI-05: Pacing-Strategie für Zielrennen
**Priorität:** P3 | **Aufwand:** M | **Status:** Offen

*Siehe TRAIN-08 – Berechnung der optimalen Pacing-Strategie basierend auf individuellem Drift-Profil.*

---

## Hinweise zur Hardware

### Was der einfache Brustgurt liefert:
- Herzfrequenz (sehr genau, R-R-Intervalle)
- HRV (aus R-R-Intervallen ableitbar)
- Kein Running Power
- Keine Running Dynamics (GCT, Vertikale Oszillation, L/R-Balance)
- Keine Schrittlänge vom Gurt (kommt von der Uhr)

### Was die Garmin-Uhr liefert (ohne HRM-Pro):
- Pace, Distanz, Höhenmeter
- Kadenz (Schrittfrequenz)
- Schrittlänge (geschätzt)
- Training Effect, Training Load
- VO2max-Schätzung
- Body Battery, Stress, Schlaf
- Wetter zum Zeitpunkt der Aktivität

### Features die HRM-Pro/Run BRAUCHEN (nicht umsetzbar):
- ~~Running Dynamics (GCT, Vertikale Oszillation, L/R-Balance)~~
- ~~Running Power vom Brustgurt~~
- ~~Lauftechnik-Score basierend auf Dynamics~~
- ~~Ermüdungs-Erkennung via GCT-Anstieg~~
- ~~Pace-Power-Korrelation~~
- ~~Effizienz-Index (Pace pro Watt)~~

---

## Frontend-Optionen (Referenz)

### Option A: Statisches HTML (aktuell)
- Kein Build-Step, kein Server nötig
- `generate_report.py` schreibt direkt HTML
- Config-Editing nur über Texteditor oder Setup-Wizard (Download)
- Offline-fähig

### Option B: React + shadcn/ui + Next.js
- Modernes UI mit Komponenten-Bibliothek
- Config-Editing direkt im Dashboard (API-Routes)
- Hot-Reload, bessere Interaktivität
- Braucht Node.js, Build-Step, ggf. lokalen Server
- Charts via Recharts statt Chart.js

### Option C: Python + Flask/FastAPI (Minimal-Server)
- Statisches HTML bleibt, aber kleiner Server für Config-Editing
- POST-Endpoint zum Speichern von athlete.json
- Geringster Umbau-Aufwand
- `pip install flask` als einzige Dependency
