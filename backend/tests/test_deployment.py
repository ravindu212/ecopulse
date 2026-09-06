import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.index import app as vercel_app
from app.main import app as application_app


BACKEND_DIRECTORY = Path(__file__).resolve().parents[1]


def test_vercel_entrypoint_exposes_existing_app_and_routes():
    assert isinstance(vercel_app, FastAPI)
    assert vercel_app is application_app

    paths = set(vercel_app.openapi()["paths"])
    assert {
        "/health",
        "/api/v1/auth/login",
        "/api/v1/assessment",
        "/api/v1/actions",
        "/api/v1/challenges",
        "/api/v1/dashboard",
        "/api/v1/progress",
        "/api/v1/climate/overview",
    } <= paths
    assert not any(path.startswith("/api/api/") for path in paths)
    framework_paths = {getattr(route, "path", None) for route in vercel_app.routes}
    assert {"/docs", "/docs/oauth2-redirect", "/openapi.json", "/redoc"} <= (
        framework_paths
    )


def test_health_is_public_and_does_not_require_database_access():
    with TestClient(application_app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_vercel_rewrites_public_routes_to_the_single_entrypoint():
    config = json.loads((BACKEND_DIRECTORY / "vercel.json").read_text())
    rewrites = config["rewrites"]

    assert {rewrite["source"] for rewrite in rewrites} == {
        "/",
        "/health",
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
        "/openapi.json",
        "/api/v1/:path*",
    }
    assert all(rewrite["destination"] == "/api/index" for rewrite in rewrites)
    assert not any(rewrite["source"] == "/api/index" for rewrite in rewrites)
    assert "builds" not in config
    assert "functions" not in config
