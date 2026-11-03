# Base44 Architek — Local-First KI-Projektstudio

Ein kostenlos nutzbarer **Startpunkt** zur KI-gestützten Planung von Softwareprojekten. Die Anwendung nutzt bevorzugt ein lokal betriebenes Ollama-Modell. Ist es nicht erreichbar, erstellt sie einen einfachen deterministischen Offline-Projektentwurf. **Sie baut, testet oder veröffentlicht noch keine vollständigen Apps automatisch.**

## Voraussetzungen

- Python 3.11+ (keine pip-Abhängigkeiten)
- Optional: [Ollama](https://ollama.com/) und ein lokal heruntergeladenes Modell (z. B. `qwen2.5-coder:1.5b`)
- Für Ollama: genügend Arbeitsspeicher; der Modell-Download benötigt Internet und freien Speicher.

## Start

```bash
git clone https://github.com/niknight1403/Base44-Architek.git
cd Base44-Architek
# optional mit installierter Ollama-CLI:
ollama pull qwen2.5-coder:1.5b
ollama serve
# in einem zweiten Terminal:
python server.py
```

Danach **http://127.0.0.1:8765** im Browser öffnen. Ohne Ollama funktioniert die App im Vorlagenmodus.

## Einstellungen (Umgebungsvariablen)

| Variable | Standard | Bedeutung |
| --- | --- | --- |
| `ARCHITEK_HOST` | `127.0.0.1` | Bind-Adresse (nur lokal empfohlen) |
| `ARCHITEK_PORT` | `8765` | HTTP-Port |
| `ARCHITEK_WORKSPACE` | `./workspace` | Projektordner |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | lokale Ollama-API |
| `OLLAMA_MODEL` | `qwen2.5-coder:1.5b` | verfügbares lokales Modell |

Beispiel Linux/macOS: `OLLAMA_MODEL=codellama:7b python server.py`. Bei Windows PowerShell: `$env:OLLAMA_MODEL="codellama:7b"; python server.py`.

## Funktionen

- Mobile-freundliche deutschsprachige Weboberfläche
- Lokale Projektanlage mit validiertem Projektnamen
- Erzeugung von `workspace/<slug>/PLAN.md` und `project.json`
- Kostenloses Ollama-Backend, ohne benötigten Cloud-API-Key
- Offline-Vorlagenmodus bei Modellfehlern, keine falschen Erfolgsbehauptungen
- Standardbibliothek statt kostenpflichtiger Build-Dienste
- GitHub-Actions-Checks (innerhalb der jeweils geltenden GitHub-Gratislimits)

## Tests

```bash
python -m unittest discover -s tests -v
python -m py_compile server.py
```

## Sicherheit und Kosten

Der Dienst bindet standardmäßig an `127.0.0.1`. **Nicht ohne Authentifizierung und TLS öffentlich ins Internet stellen.** Keine geheimen Tokens in Prompts ablegen. Das Projekt legt Entwürfe lokal ab; es führt keinen generierten Code aus.

Es gibt keine eingebauten Zahlungen oder kostenpflichtigen KI-APIs. Hardware, Energie, Datenverkehr und etwaige Hosting-/CI-Limits bleiben zu berücksichtigen.

## Nächste Ausbaustufen

1. Freigegebene und geprüfte Codegenerierung in isolierten Projektordnern
2. Automatische Tests und sichere Build-Runner mit Zeit-/Ressourcenlimits
3. Modellauswahl und Health-Checks für mehrere lokale Provider
4. Reproduzierbare Web-/Android-Builds und Release-Nachweise
5. Queue, Agentenrollen und Projektstatus für längere Entwicklungsprozesse

## Status

Dies ist ein **funktionsorientiertes MVP-Grundgerüst**, keine fertige Base44-Alternative und kein autonomer APK-Generator.
