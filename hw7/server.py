"""MCP tools for generating and deploying an isolated nginx lab service."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import urllib.request
from fastmcp import FastMCP

mcp = FastMCP("Nginx Configuration Lab")
ROOT = Path(__file__).resolve().parent / ".generated"
IMAGE = "nginx:stable-alpine"
CONTAINER = "dwain-hw7-nginx"
PORT = 8087

def docker(*args: str) -> dict:
    """Run fixed Docker argument lists without a shell, with a time limit."""
    result = subprocess.run(["sudo", "-n", "docker", *args],
                            capture_output=True, text=True, timeout=120)
    return {"returncode": result.returncode, "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()}

def config_path() -> Path:
    """Return the single application-owned configuration path."""
    ROOT.mkdir(exist_ok=True)
    return ROOT / "nginx.conf"

def sandbox_args() -> list[str]:
    """Constrain the container to an unprivileged, read-only runtime."""
    return ["--read-only", "--user", "101:101", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges", "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
            "-v", str(config_path()) + ":/etc/nginx/nginx.conf:ro"]

@mcp.tool()
def generate_config(message: str = "Hello from Dwain HW7", server_name: str = "localhost") -> dict:
    """Generate nginx configuration from bounded text and a valid hostname."""
    if not re.fullmatch(r"[A-Za-z0-9 .,!?_-]{1,120}", message):
        raise ValueError("Message must be 1-120 simple text characters; config syntax is rejected.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}", server_name):
        raise ValueError("Invalid hostname.")
    text = f"""worker_processes 1;
pid /tmp/nginx.pid;
error_log /dev/stderr warn;
events {{ worker_connections 128; }}
http {{
    client_body_temp_path /tmp/client;
    proxy_temp_path /tmp/proxy;
    fastcgi_temp_path /tmp/fastcgi;
    uwsgi_temp_path /tmp/uwsgi;
    scgi_temp_path /tmp/scgi;
    access_log /dev/stdout;
    server {{
        listen 8080;
        server_name {server_name};
        default_type text/plain;
        add_header X-Content-Type-Options nosniff always;
        location = /health {{ return 200 "healthy"; }}
        location / {{ return 200 {json.dumps(message)}; }}
    }}
}}
"""
    config_path().write_text(text)
    return {"path": str(config_path()), "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "configuration": text}

@mcp.tool()
def validate_config() -> dict:
    """Check generated configuration with the real nginx syntax validator."""
    if not config_path().exists():
        raise ValueError("Generate a configuration first.")
    return docker("run", "--rm", *sandbox_args(), "--entrypoint", "nginx",
                  IMAGE, "-t", "-c", "/etc/nginx/nginx.conf")

@mcp.tool()
def deploy_config() -> dict:
    """Validate, then deploy only the named lab container on loopback port 8087."""
    check = validate_config()
    if check["returncode"]:
        return {"deployed": False, "validation": check}
    existing = docker("ps", "-a", "--filter", "name=^/" + CONTAINER + "$", "--format", "{{.Names}}")
    if existing["returncode"]:
        return {"deployed": False, "error": existing}
    if existing["stdout"]:
        return {"deployed": False, "error": "Lab container exists. Stop it before redeploying."}
    result = docker("run", "-d", "--name", CONTAINER, *sandbox_args(),
                    "-p", f"127.0.0.1:{PORT}:8080", "--entrypoint", "nginx",
                    IMAGE, "-g", "daemon off;")
    return {"deployed": result["returncode"] == 0, "url": f"http://127.0.0.1:{PORT}", **result}

@mcp.tool()
def service_status() -> dict:
    """Inspect the lab container and request its local health endpoint."""
    state = docker("ps", "-a", "--filter", "name=^/" + CONTAINER + "$",
                   "--format", "{{.Names}} {{.Status}} {{.Ports}}")
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=5) as response:
            state["health"] = {"status": response.status, "body": response.read(1024).decode()}
    except Exception as exc:
        state["health"] = {"error": str(exc)}
    return state

@mcp.tool()
def stop_service() -> dict:
    """Remove only this disposable lab container; retain its generated configuration."""
    return docker("rm", "-f", CONTAINER)

if __name__ == "__main__":
    mcp.run()
