import logging
from typing import Any

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class ProviderRequestError(RuntimeError):
    """Safe provider failure raised without response payloads or secrets."""


class ProviderHttpClient:
    def __init__(
        self,
        client: httpx.Client | None = None,
        timeout_seconds: float = settings.climate_http_timeout_seconds,
        max_response_bytes: int = settings.climate_http_max_response_bytes,
    ):
        self._client = client
        self._timeout = timeout_seconds
        self._max_response_bytes = max_response_bytes
        self._headers = {
            "User-Agent": "EcoPulse/0.1 climate-data service",
            "Accept": "application/json,text/csv,text/plain;q=0.9",
        }

    def _request(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        try:
            if self._client is not None:
                response = self._client.get(
                    url,
                    params=params,
                    headers=self._headers,
                    timeout=self._timeout,
                    follow_redirects=True,
                )
            else:
                with httpx.Client(
                    headers=self._headers,
                    timeout=self._timeout,
                    follow_redirects=True,
                ) as client:
                    response = client.get(url, params=params)

            response.raise_for_status()
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self._max_response_bytes:
                raise ProviderRequestError("Provider response exceeded the size limit")
            if len(response.content) > self._max_response_bytes:
                raise ProviderRequestError("Provider response exceeded the size limit")
            return response
        except ProviderRequestError:
            raise
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Climate provider request failed for %s: %s", url, type(exc).__name__)
            raise ProviderRequestError("Climate provider request failed") from exc

    def get_text(self, url: str, params: dict[str, Any] | None = None) -> str:
        return self._request(url, params).text

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        try:
            return self._request(url, params).json()
        except ValueError as exc:
            logger.warning("Climate provider returned invalid JSON for %s", url)
            raise ProviderRequestError("Climate provider returned invalid data") from exc
