from datetime import datetime, timedelta, timezone

import httpx
import pytest

from app.services.climate.cache import TTLCache
from app.services.climate.http_client import ProviderHttpClient, ProviderRequestError


class Clock:
    def __init__(self):
        self.now = datetime(2026, 9, 5, tzinfo=timezone.utc)

    def __call__(self):
        return self.now


def test_ttl_cache_keeps_expired_last_known_good_value():
    clock = Clock()
    cache = TTLCache[str](clock=clock)

    entry = cache.put("provider", "real data", ttl_seconds=60)

    assert entry.fetched_at == clock.now
    assert entry.expires_at == clock.now + timedelta(seconds=60)
    assert cache.get_fresh("provider").value == "real data"

    clock.now += timedelta(seconds=61)
    assert cache.get_fresh("provider") is None
    assert cache.get_last_known_good("provider").value == "real data"


def test_http_client_sets_user_agent_and_parses_json():
    def handler(request: httpx.Request):
        assert request.headers["user-agent"].startswith("EcoPulse/")
        return httpx.Response(200, json={"events": []})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = ProviderHttpClient(client=client).get_json("https://provider.test/events")
    assert result == {"events": []}


@pytest.mark.parametrize(
    "handler",
    [
        lambda request: httpx.Response(503, text="provider details"),
        lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("slow", request=request)),
    ],
)
def test_http_client_normalises_status_and_timeout_errors(handler):
    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(ProviderRequestError, match="Climate provider request failed"):
        ProviderHttpClient(client=client).get_text("https://provider.test/data")


def test_http_client_rejects_oversized_response():
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, content=b"12345"))
    )
    with pytest.raises(ProviderRequestError, match="size limit"):
        ProviderHttpClient(client=client, max_response_bytes=4).get_text(
            "https://provider.test/data"
        )


def test_http_client_rejects_invalid_json_without_leaking_payload():
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, text="secret bad data"))
    )
    with pytest.raises(ProviderRequestError, match="invalid data") as exc_info:
        ProviderHttpClient(client=client).get_json("https://provider.test/data")
    assert "secret bad data" not in str(exc_info.value)
