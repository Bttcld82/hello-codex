"""Entrypoint for running the Flask development server."""
from __future__ import annotations

from app_flask import create_app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
