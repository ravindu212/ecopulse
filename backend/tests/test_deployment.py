from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.index import app as vercel_app
from app.main import app as application_app


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
    assert any(
        getattr(route, "path", None) == "/docs" for route in vercel_app.routes
    )


def test_health_is_public_and_does_not_require_database_access():
    with TestClient(application_app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
