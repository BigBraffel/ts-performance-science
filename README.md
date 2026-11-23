# TS Performance Science

*Thesaurus Scientiae* – „Schatzkammer des Wissens“ für Training und Ernährung.

Eine sich selbst aktualisierende Website, die den Forschungsstand zu Trainings- und Ernährungswissenschaft auf Deutsch zusammenfasst. Sie stützt sich ausschließlich auf wissenschaftliche Quellen, bewertet sie kritisch und zitiert sie nach APA 7 (deutsche Fassung).

**Themen:** Training (u. a. Maximalkraft, Hypertrophie, Ausdauer, Regeneration, Schlaf, Verletzungsprävention), Ernährung (Makronährstoffe, Energiebilanz, Flüssigkeit, Timing) und über 20 Supplemente. Jedes Thema ist eine Datei in `data/topics/`; welche davon sichtbar sind, steht in `index.html` unter `NAV` und `AVAILABLE`.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `index.html` | Die komplette Website (Navigation, Darstellung, Diagramme). Keine externen Abhängigkeiten außer Schriftarten. |
| `data/topics/<thema>.json` | Inhalt je Thema: Ableitungen, Kernaussagen, Variablen mit Abbildungen, kritische Einordnung, Quellen, Forschungsverlauf, Änderungsprotokoll. |
| `data/screening/<thema>.json` | Screening-Register: jede PubMed-Arbeit zur Suchanfrage des Themas mit Entscheidung (A aufgenommen, X geprüft/nicht im Fokus, S/P/E/C/M/K regelbasiert). Bereits gesichtete Arbeiten werden nie erneut geprüft. |
| `data/kandidaten/<thema>.json` | Von der automatischen Abfrage gefundene neue oder geänderte Arbeiten, die inhaltlich bewertet werden müssen. `"bearbeitet": true`, sobald ausgewertet. |
| `tools/pubmed_update.py` | PubMed-Abgleich (`scan`, `set`, `init`). |
| `tools/scan_all.py` | Fragt alle Themen ab und legt die Kandidaten ab; startet danach `rueckzug.py`. |
| `tools/rueckzug.py` | Prüft alle zitierten Arbeiten auf Rückzug, Korrektur oder Bedenken (`data/kandidaten/_rueckzuege.json`). |
| `tools/pruefen.py` | Formale Prüfung der Daten (JSON, Quellenschlüssel, Abbildungen, Wirkungsübersicht) und Suche nach ungenutztem Code. |
| `manifest.webmanifest`, `sw.js`, `icon-*.png` | Installierbar als App und offline lesbar (nur GitHub Pages). |
| `docs/AUSWERTUNG.md` | Verbindliche Regeln für die inhaltliche Auswertung. |

## Automatischer Ablauf (alle 2 Wochen freitags, ab 20.11.2026)

1. **06:07 – PubMed-Abfrage (GitHub Actions, `pubmed-abfrage.yml`).** Neue und geänderte Arbeiten werden mit den Registern abgeglichen. Eindeutige Fälle werden per Titelregel kodiert, Übersichtsarbeiten landen in `data/kandidaten/`.
2. **11:23 – Inhaltliche Auswertung (Claude, geplante Aufgabe).** Abstracts lesen, aufnehmen oder ausschließen, Inhalte, Abbildungen und Forschungsverlauf aktualisieren, Änderungen hier speichern und die claude.ai-Fassung der Website aktualisieren.
3. **Bei jeder Änderung – Prüfung (`pruefen.yml`)** und **Veröffentlichung über GitHub Pages**.

Die Abfrage lässt sich jederzeit von Hand starten: *Actions → PubMed-Abfrage → Run workflow*.

## Lokal ansehen

```
python3 -m http.server 8000
```
Dann `http://localhost:8000` öffnen. Direkt als Datei geöffnet funktioniert die Seite nicht, weil die Themen nachgeladen werden.
