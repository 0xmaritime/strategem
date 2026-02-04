"""Strategem Core - I/O Utilities (Mechanical Only)"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from .primitives import generate_id


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    """
    Load JSON file (mechanical only).

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON data as dict, or None if file doesn't exist
    """
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise IOError(f"Failed to load JSON from {path}: {e}")


def save_json(data: Any, path: Path) -> None:
    """
    Save data to JSON file (mechanical only).

    Args:
        data: Data to serialize
        path: Path to save file
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_text(path: Path) -> str:
    """
    Load text file (mechanical only).

    Args:
        path: Path to text file

    Returns:
        File contents as string
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except IOError as e:
        raise IOError(f"Failed to load text from {path}: {e}")


def save_text(content: str, path: Path) -> None:
    """
    Save content to text file (mechanical only).

    Args:
        content: Text content to save
        path: Path to save file
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def ensure_directory(path: Path) -> None:
    """
    Ensure directory exists (mechanical only).

    Args:
        path: Directory path to ensure
    """
    path.mkdir(parents=True, exist_ok=True)


def list_files(
    directory: Path, pattern: str = "*", recursive: bool = False
) -> list[Path]:
    """
    List files in directory (mechanical only).

    Args:
        directory: Directory to search
        pattern: File pattern to match
        recursive: Whether to search recursively

    Returns:
        List of matching file paths
    """
    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


def delete_file(path: Path) -> None:
    """
    Delete file if exists (mechanical only).

    Args:
        path: File path to delete
    """
    if path.exists():
        path.unlink()


def generate_storage_path(
    base_dir: Path,
    prefix: str,
    extension: str = ".json",
) -> Path:
    """
    Generate unique storage path (mechanical only).

    Args:
        base_dir: Base directory for storage
        prefix: Filename prefix
        extension: File extension

    Returns:
        Unique file path
    """
    return base_dir / f"{prefix}_{generate_id()}{extension}"
