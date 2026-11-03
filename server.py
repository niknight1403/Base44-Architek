"""Base44 Architek: dependency-free, local-first AI project workspace."""
from __future__ import annotations
import json
import os
import re
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = Path(os.getenv("ARCHITEK_WORKSPACE", str(ROOT / "workspace"))).resolve()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
HOST = os.getenv("ARCHITEK_HOST", "127.0.0.1")
PORT = int(os.getenv("ARCHITEK_PORT", "8765"))
MAX_BODY = 16_384

def slugify(name: str) -> str:
    name = re.sub(r"[^a-z0-9-]+", "-", name.lower().strip()).strip("-")
    if not name or len(name) > 64:
        raise ValueError("Projektname muss 1-64 gueltige Zeichen enthalten")
    return name

def template(prompt: str) -> str:
    return (
        "# Projektentwurf (Offline-Fallback)\n\n"
        "## Auftrag\n" + prompt + "\n\n"
        "## Umsetzung\n"
        "1. Anforderungen und Nutzerfluss beschreiben.\n"
        "2. Datenmodell und UI planen.\n"
        "3. Einen minimalen Prototyp implementieren.\n"
        "4. Tests, Sicherheit und Release pruefen.\n\n"
        "> Kein LLM erreichbar. Dies ist ein deterministischer Entwurf, keine generierte App.\n"
    )

def ask_local_model(prompt: str) -> tuple[str, str]:
    system = (
        "Du bist ein erfahrener Softwarearchitekt. Erstelle einen umsetzbaren "
        "deutschsprachigen Projektplan mit Architektur, Dateistruktur, Tests, "
        "Sicherheitsgrenzen und naechsten Schritten. Gib Markdown aus. "
        "Behaupte keine Implementierung oder Tests, die nicht stattgefunden haben."
    )
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "stream": False,
        "prompt": f"{system}\n\nNutzerauftrag:\n{prompt}",
        "options": {"temperature": 0.2, "num_predict": 1200}
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL + "/api/generate", data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.load(response)
        content = result.get("response", "")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Leere Modellantwort")
        return content, "ollama:" + OLLAMA_MODEL
    except (OSError, ValueError, json.JSONDecodeError, TimeoutError):
        return template(prompt), "offline-template"

def create_project(name: str, prompt: str) -> dict:
    if not isinstance(name, str) or not isinstance(prompt, str):
        raise ValueError("name und prompt muessen Text sein")
    slug = slugify(name)
    prompt = prompt.strip()
    if not 4 <= len(prompt) <= 8000:
        raise ValueError("Prompt muss zwischen 4 und 8000 Zeichen enthalten")
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    folder = (WORKSPACE / slug).resolve()
    if not folder.is_relative_to(WORKSPACE):
        raise ValueError("Ungueltiger Projektpfad")
    if folder.exists():
        raise FileExistsError("Projekt existiert bereits")
    plan, route = ask_local_model(prompt)
    folder.mkdir()
    (folder / "PLAN.md").write_text(plan, encoding="utf-8")
    metadata = {"name": name.strip(), "slug": slug, "route": route, "created_at": int(time.time()), "status": "draft"}
    (folder / "project.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return metadata

def list_projects() -> list[dict]:
    if not WORKSPACE.is_dir():
        return []
    projects = []
    for folder in sorted(WORKSPACE.iterdir()):
        if not folder.is_dir() or folder.is_symlink():
            continue
        meta = folder / "project.json"
        if meta.is_file() and not meta.is_symlink():
            try:
                projects.append(json.loads(meta.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
    return projects

class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: object):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/api/status":
            self.send_json(200, {"service": "base44-architek", "mode": "local-first", "model": OLLAMA_MODEL, "fallback": "offline-template"})
        elif self.path == "/api/projects":
            self.send_json(200, {"projects": list_projects()})
        elif self.path in ("/", "/index.html"):
            page = (ROOT / "web" / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(page)
        else:
            self.send_json(404, {"error": "Nicht gefunden"})

    def do_POST(self):
        if self.path != "/api/projects":
            return self.send_json(404, {"error": "Nicht gefunden"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                return self.send_json(413, {"error": "Ungueltige Groesse"})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("JSON Objekt erwartet")
            result = create_project(data.get("name"), data.get("prompt"))
            self.send_json(201, {"project": result})
        except (ValueError, TypeError) as e:
            self.send_json(400, {"error": str(e)})
        except FileExistsError as e:
            self.send_json(409, {"error": str(e)})

def main():
    print(f"Base44 Architek: http://{HOST}:{PORT} | Ollama: {OLLAMA_URL} | Modell: {OLLAMA_MODEL}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

if __name__ == "__main__":
    main()
