#!/usr/bin/env python3
"""
Utility Functions Module
=========================
Common helper functions for:
- Parameter validation
- Audit trail creation
- File operations
- Data formatting
- Retry logic
"""

import json
import hashlib
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from logger import get_logger

logger = get_logger("Utils")


# ============================================================================
# PARAMETER VALIDATION
# ============================================================================

def validate_parameters(params: Dict[str, str]) -> List[str]:
    """
    Validate all input parameters

    Checks:
    - Required fields present
    - Enum values are valid (platform, environment, build_type, app_variant)
    - Version format is semantic (X.Y.Z)
    - URL format is valid (http/https)

    Args:
        params (dict): Parameter dictionary

    Returns:
        list: List of validation errors (empty if all valid)
    """
    errors = []

    # Check required fields
    required = ['platform', 'environment', 'build_type', 'app_variant',
                'version', 'build_id', 'source_build_url']
    for field in required:
        if field not in params or not params[field]:
            errors.append(f"Missing required parameter: {field}")

    # Validate platform
    valid_platforms = ['android', 'android_hw', 'ios']
    if 'platform' in params and params['platform'] not in valid_platforms:
        errors.append(f"Invalid platform: {params['platform']}. "
                     f"Must be one of {valid_platforms}")

    # Validate environment
    valid_environments = ['production', 'staging']
    if 'environment' in params and params['environment'] not in valid_environments:
        errors.append(f"Invalid environment: {params['environment']}. "
                     f"Must be one of {valid_environments}")

    # Validate build type
    valid_build_types = ['Debug', 'Release']
    if 'build_type' in params and params['build_type'] not in valid_build_types:
        errors.append(f"Invalid build_type: {params['build_type']}. "
                     f"Must be one of {valid_build_types}")

    # Validate app variant
    valid_variants = ['agent', 'retail', 'wallet']
    if 'app_variant' in params and params['app_variant'] not in valid_variants:
        errors.append(f"Invalid app_variant: {params['app_variant']}. "
                     f"Must be one of {valid_variants}")

    # Validate version format (semantic versioning)
    if 'version' in params:
        version = params['version']
        if not is_valid_version(version):
            errors.append(f"Invalid version format: {version}. "
                         f"Expected semantic version (e.g., 1.2.0 or 1.3.0-beta)")

    # Validate URL format
    if 'source_build_url' in params:
        url = params['source_build_url']
        if not url.startswith(('http://', 'https://')):
            errors.append(f"Invalid source_build_url: {url}. Must be HTTP(S) URL")

    return errors


def is_valid_version(version: str) -> bool:
    """
    Validate semantic version format

    Accepts: X.Y.Z or X.Y.Z-suffix
    Examples:
    - 1.0.0 ✓
    - 1.2.3-beta ✓
    - 1.2 ✗
    - 1.2.3.4 ✗

    Args:
        version (str): Version string to validate

    Returns:
        bool: True if valid semantic version, False otherwise
    """
    # Pattern: X.Y.Z or X.Y.Z-suffix
    pattern = r'^(\d+)\.(\d+)\.(\d+)(-[a-zA-Z0-9.]+)?$'
    return bool(re.match(pattern, version))


# ============================================================================
# AUDIT TRAIL CREATION
# ============================================================================

def create_audit_trail(params: Dict[str, str], artifact_info: Dict[str, Any],
                      upload_result: Dict[str, str], old_app_id: Optional[str],
                      pr_info: Dict[str, str], yaml_files: List[str]) -> str:
    """
    Create comprehensive audit trail JSON file

    This creates a record of:
    - Input parameters
    - Artifact metadata
    - BrowserStack upload results
    - Pull request information
    - YAML files updated

    Useful for compliance and debugging.

    Args:
        params (dict): Input parameters
        artifact_info (dict): Artifact file metadata
        upload_result (dict): BrowserStack upload result
        old_app_id (str): Previous app ID
        pr_info (dict): Pull request information
        yaml_files (list): YAML files that were updated

    Returns:
        str: Path to audit trail file
    """
    # Build audit data structure
    audit_data = {
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "parameters": params,
        "artifact": {
            "path": artifact_info.get('path'),
            "size": artifact_info.get('size'),
            "md5": artifact_info.get('md5'),
            "modified_time": artifact_info.get('modified_time')
        },
        "browserstack": {
            "old_app_id": old_app_id,
            "new_app_id": upload_result.get('app_id'),
            "app_url": upload_result.get('app_url'),
            "upload_timestamp": upload_result.get('timestamp')
        },
        "yaml_updates": {
            "files": yaml_files,
            "platform": params.get('platform'),
            "app_variant": params.get('app_variant')
        },
        "pull_request": {
            "number": pr_info.get('pr_number'),
            "url": pr_info.get('pr_url'),
            "branch": pr_info.get('branch')
        }
    }

    # Create audit file name
    platform = params.get('platform', 'unknown')
    app_variant = params.get('app_variant', 'unknown')
    build_id = params.get('build_id', 'unknown')

    audit_file = f"audit-trail-{platform}-{app_variant}-{build_id}.json"
    audit_path = Path(audit_file)

    # Write audit trail to file
    with open(audit_path, 'w') as f:
        json.dump(audit_data, f, indent=2)

    logger.info(f"Audit trail created: {audit_path}")
    return str(audit_path)


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def calculate_file_md5(file_path: Path) -> str:
    """
    Calculate MD5 checksum of file

    Reads file in chunks for memory efficiency with large files.

    Args:
        file_path (Path): Path to file

    Returns:
        str: MD5 hash in hexadecimal format
    """
    md5_hash = hashlib.md5()

    # Read file in 8KB chunks
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()


def get_file_type(file_path: Path) -> Optional[str]:
    """
    Detect file type from magic bytes

    Magic bytes are first few bytes that identify file type:
    - PK = ZIP archive (APK, AAB, IPA)
    - CAFEBABE or FEEDFACE = Mach-O binary (iOS)

    Args:
        file_path (Path): Path to file

    Returns:
        str: File type ('apk', 'ipa', 'aab') or None if unknown
    """
    magic_bytes = {
        b'PK': 'apk',  # ZIP-based formats
        b'\xca\xfe\xba\xbe': 'mach-o',  # Mach-O (iOS)
        b'\xfe\xed\xfa\xce': 'mach-o',  # Mach-O (iOS)
        b'\xce\xfa\xed\xfe': 'mach-o',  # Mach-O (iOS)
    }

    try:
        # Read first 4 bytes
        with open(file_path, 'rb') as f:
            header = f.read(4)

        # Check against known magic bytes
        for magic, ftype in magic_bytes.items():
            if header.startswith(magic):
                # For APK, also check extension
                if ftype == 'apk' and file_path.suffix.lower() == '.apk':
                    return 'apk'
                elif ftype == 'mach-o' and file_path.suffix.lower() == '.ipa':
                    return 'ipa'

        # Fallback to extension
        ext = file_path.suffix.lower().lstrip('.')
        if ext in ['apk', 'ipa', 'aab']:
            return ext

        return None

    except Exception as e:
        logger.error(f"Error detecting file type: {e}")
        return None


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable format

    Examples:
    - 1024 → "1.00 KB"
    - 1048576 → "1.00 MB"
    - 1073741824 → "1.00 GB"

    Args:
        bytes_value (int): Number of bytes

    Returns:
        str: Formatted string (e.g., "10.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe use

    Removes special characters, keeps only:
    - Alphanumeric (A-Z, a-z, 0-9)
    - Dash (-)
    - Underscore (_)
    - Dot (.)

    Args:
        filename (str): Original filename

    Returns:
        str: Sanitized filename
    """
    # Replace special characters with underscore
    sanitized = re.sub(r'[^\w\-.]', '_', filename)
    return sanitized


# ============================================================================
# RETRY LOGIC
# ============================================================================

def retry_with_backoff(func, max_attempts: int = 3, initial_delay: float = 2,
                       backoff_factor: float = 2):
    """
    Execute function with exponential backoff retry

    Retries on any exception with exponential backoff:
    - Attempt 1: Wait 2 seconds
    - Attempt 2: Wait 4 seconds
    - Attempt 3: Wait 8 seconds

    Args:
        func: Function to execute
        max_attempts (int): Maximum number of attempts (default 3)
        initial_delay (float): Initial delay in seconds (default 2)
        backoff_factor (float): Backoff multiplier (default 2)

    Returns:
        Function result

    Raises:
        Last exception if all attempts fail
    """
    last_exception = None
    delay = initial_delay

    # Try up to max_attempts times
    for attempt in range(1, max_attempts + 1):
        try:
            return func()

        except Exception as e:
            # Save exception
            last_exception = e

            if attempt < max_attempts:
                # Calculate next delay
                logger.warning(f"Attempt {attempt} failed: {e}. "
                              f"Retrying in {delay}s...")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                # Last attempt failed
                logger.error(f"All {max_attempts} attempts failed")

    # Raise the last exception
    raise last_exception
