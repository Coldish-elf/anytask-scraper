from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from anytask_scraper.client import AnytaskClient

T = TypeVar("T")


class AppState:
    """Thread-safe container for a single AnytaskClient instance."""

    def __init__(self, startup_session_file: str | None = None) -> None:
        self._lock = threading.RLock()
        self._client: AnytaskClient | None = None
        if startup_session_file:
            self.load_session(startup_session_file)

    def login(self, username: str, password: str) -> None:
        """Create a new client and authenticate with credentials."""
        with self._lock:
            if self._client is not None:
                self._client.close()
            client = AnytaskClient(username=username, password=password)
            client.login()
            self._client = client

    def load_session(self, session_file: str) -> bool:
        """Load session cookies from file; returns True if loaded."""
        with self._lock:
            if self._client is None:
                self._client = AnytaskClient()
            return self._client.load_session(Path(session_file))

    def save_session(self, session_file: str) -> None:
        """Save current session cookies to file."""
        with self._lock:
            client = self._get_client_unsafe()
            client.save_session(Path(session_file))

    def logout(self) -> None:
        """Close and discard the client."""
        with self._lock:
            if self._client is not None:
                self._client.close()
                self._client = None

    def is_authenticated(self) -> bool:
        """Return True if a client is present and authenticated."""
        with self._lock:
            return self._client is not None and self._client._authenticated

    def get_username(self) -> str:
        """Return username of the current client, or empty string."""
        with self._lock:
            return self._client.username if self._client is not None else ""

    def _get_client_unsafe(self) -> AnytaskClient:
        """Return client without acquiring lock (caller must hold lock)."""
        if self._client is None:
            raise RuntimeError("Not authenticated. Call /auth/login or /auth/load-session first.")
        return self._client

    def get_client(self) -> AnytaskClient:
        """Return authenticated client or raise RuntimeError."""
        with self._lock:
            return self._get_client_unsafe()

    def with_client(self, fn: Callable[[AnytaskClient], T]) -> T:
        """Execute fn(client) while holding the lock."""
        with self._lock:
            client = self._get_client_unsafe()
            return fn(client)
