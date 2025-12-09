"""Utility functions for the backend server."""

import socket
import sys
import tempfile
from pathlib import Path
from typing import Optional


def get_free_port() -> int:
    """
    Bind to port 0 to get OS-assigned ephemeral port.

    Returns:
        int: The port number assigned by the OS
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        return port
    finally:
        sock.close()


def announce_port(port: int) -> None:
    """
    Print port to stdout in parseable format for Rust to capture.

    Args:
        port: The port number to announce
    """
    print(f"SERVER_PORT={port}", flush=True)
    sys.stdout.flush()  # Critical: Force immediate stdout flush


def get_temp_pdf_dir() -> Path:
    """
    Get or create a temporary directory for PDF files.

    Returns:
        Path: The temporary directory path
    """
    temp_dir = Path(tempfile.gettempdir()) / "nsaanbiedingen_pdfs"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def cleanup_temp_files(max_age_hours: int = 24) -> None:
    """
    Clean up temporary PDF files older than max_age_hours.

    Args:
        max_age_hours: Maximum age of files to keep (in hours)
    """
    import time

    temp_dir = get_temp_pdf_dir()
    if not temp_dir.exists():
        return

    now = time.time()
    max_age_seconds = max_age_hours * 3600

    for pdf_file in temp_dir.glob("*.pdf"):
        if (now - pdf_file.stat().st_mtime) > max_age_seconds:
            try:
                pdf_file.unlink()
                print(f"Cleaned up old PDF: {pdf_file.name}")
            except Exception as e:
                print(f"Failed to clean up {pdf_file.name}: {e}")
