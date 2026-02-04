"""Strategem Core - Mechanical Primitives"""

from .llm import LLMInferenceClient, LLMError
from .config import config, Config
from .io import (
    load_json,
    save_json,
    load_text,
    save_text,
    ensure_directory,
    list_files,
    delete_file,
    generate_storage_path,
)
from .primitives import (
    ConfidenceLevel,
    FrameworkName,
    ExecutionStatus,
    ContentType,
    generate_id,
    get_timestamp,
    create_uuid,
    validate_json_structure,
    V1_VERSION,
    V2_VERSION,
)
from .utils import (
    setup_logging,
    truncate_string,
    safe_get_nested,
    merge_dicts,
    chunks,
    format_duration,
    format_timestamp,
)

__all__ = [
    # LLM
    "LLMInferenceClient",
    "LLMError",
    # Config
    "config",
    "Config",
    # I/O
    "load_json",
    "save_json",
    "load_text",
    "save_text",
    "ensure_directory",
    "list_files",
    "delete_file",
    "generate_storage_path",
    # Primitives
    "ConfidenceLevel",
    "FrameworkName",
    "ExecutionStatus",
    "ContentType",
    "generate_id",
    "get_timestamp",
    "create_uuid",
    "validate_json_structure",
    "V1_VERSION",
    "V2_VERSION",
    # Utils
    "setup_logging",
    "truncate_string",
    "safe_get_nested",
    "merge_dicts",
    "chunks",
    "format_duration",
    "format_timestamp",
]
