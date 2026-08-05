"""Checksum utilities for downloaded files."""

from __future__ import annotations

import hashlib
import zlib
from pathlib import Path


def _read_chunks(path: Path, chunk_size: int = 1024 * 1024):
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            yield chunk


def calculate_sha256(path: Path | str) -> str:
    """Calculate SHA256 checksum for a file."""
    digest = hashlib.sha256()
    for chunk in _read_chunks(Path(path)):
        digest.update(chunk)
    return digest.hexdigest()


def calculate_md5(path: Path | str) -> str:
    """Calculate MD5 checksum for a file."""
    digest = hashlib.md5()
    for chunk in _read_chunks(Path(path)):
        digest.update(chunk)
    return digest.hexdigest()


def calculate_crc32(path: Path | str) -> str:
    """Calculate CRC32 checksum for a file."""
    checksum = 0
    for chunk in _read_chunks(Path(path)):
        checksum = zlib.crc32(chunk, checksum)
    return f"{checksum & 0xFFFFFFFF:08x}"

