from __future__ import annotations

from typing import Any


def create_app(startup_session_file: str | None = None) -> Any:
    """Create the FastAPI application."""
    from .server import create_app as _create_app

    return _create_app(startup_session_file)


def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    session_file: str | None = None,
    reload: bool = False,
) -> None:
    """Start the uvicorn server (used as anytask-api entry point)."""
    try:
        import uvicorn
    except ImportError as exc:
        raise ImportError(
            "uvicorn is required to run the API server. "
            "Install it with: pip install 'anytask-scraper[api]'"
        ) from exc

    import argparse

    parser = argparse.ArgumentParser(prog="anytask-api", description="anytask-scraper HTTP API")
    parser.add_argument("--host", default=host, help=f"Bind host (default: {host})")
    parser.add_argument("--port", type=int, default=port, help=f"Bind port (default: {port})")
    parser.add_argument("--session-file", default=session_file, help="Session file to load")
    parser.add_argument("--reload", action="store_true", default=reload, help="Enable auto-reload")
    args = parser.parse_args()

    if args.reload:
        uvicorn.run(
            "anytask_scraper.api.server:create_app",
            factory=True,
            host=args.host,
            port=args.port,
            reload=True,
        )
    else:
        app = create_app(args.session_file)
        uvicorn.run(app, host=args.host, port=args.port)


__all__ = ["create_app", "run_server"]
