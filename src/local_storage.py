#!/usr/bin/env python3
"""
Local Storage Management Module
================================
This module handles:
1. Finding mobile app artifacts (APK, IPA files) on the local filesystem
2. Validating artifact files (checking they exist, are readable, etc.)
3. Calculating file checksums (MD5) for integrity verification
4. Verifying file type using magic bytes (file signatures)

Key Concepts:
- Path templates: Dynamic path construction based on platform/environment/variant
- Artifact validation: Multi-step verification (exists, readable, valid extension, magic bytes)
- Magic bytes: First few bytes of a file that identify its type
"""

import os
import hashlib
from pathlib import Path
from logger import get_logger


class LocalStorage:
    """
    Manages local artifact storage operations

    Methods:
    - construct_artifact_path(): Build file path from configuration
    - validate_artifact(): Verify file is valid and return metadata
    """

    def __init__(self, config, src_folder=None):
        """
        Initialize storage manager with configuration

        Args:
            config: Config object with storage settings
            src_folder: Optional custom source folder path (overrides config)
        """
        self.config = config
        self.log = get_logger(__name__)
        self.storage_config = config.get_local_storage_config()
        self.src_folder = src_folder

    def construct_artifact_path(self, platform, environment, build_type, app_variant):
        """
        Construct the full path to an artifact file

        This function takes configuration templates like:
            "/shared/builds/{platform}/{environment}/{build_type}/{app_variant}/app.apk"

        And replaces placeholders with actual values.

        Args:
            platform (str): Mobile platform (android, android_hw, ios)
            environment (str): Environment (production, staging)
            build_type (str): Build type (Debug, Release)
            app_variant (str): App variant (agent, retail, wallet)

        Returns:
            str: Full path to artifact file

        Raises:
            ValueError: If platform not configured
        """
        self.log.info(f"Constructing artifact path for {platform}/{app_variant}/{environment}/{build_type}")

        # Get path template for this platform from config
        templates = self.storage_config.get('path_templates', {})
        template = templates.get(platform)

        if not template:
            raise ValueError(f"No path template configured for platform: {platform}")

        # Use custom src_folder if provided, otherwise use config's artifact_base_path
        base_path = self.src_folder if self.src_folder else self.storage_config.get('artifact_base_path')

        # Replace placeholders in template
        artifact_path = template.format(
            base=base_path,
            platform=platform,
            environment=environment,
            build_type=build_type,
            build_type_lower=build_type.lower(),
            app_variant=app_variant
        )

        self.log.debug(f"Constructed path: {artifact_path}")
        return artifact_path

    def validate_artifact(self, artifact_path):
        """
        Validate that artifact file exists and is valid

        Validation steps:
        1. Check file exists
        2. Check file is readable
        3. Check file extension is allowed
        4. Check file signature (magic bytes)
        5. Calculate MD5 checksum

        Args:
            artifact_path (str): Path to artifact file

        Returns:
            dict: Artifact metadata including size, MD5, extension, etc.

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file not readable
            ValueError: If file format invalid
        """
        self.log.info(f"Validating artifact: {artifact_path}")

        path = Path(artifact_path)

        # Step 1: Check file exists
        if not path.exists():
            raise FileNotFoundError(f"Artifact not found: {artifact_path}")

        # Step 2: Check file is readable
        if not os.access(artifact_path, os.R_OK):
            raise PermissionError(f"Artifact is not readable: {artifact_path}")

        # Step 3: Get file size and modification time
        file_size = path.stat().st_size
        file_mtime = path.stat().st_mtime

        # Step 4: Validate file extension
        valid_extensions = self._get_valid_extensions_for_file(artifact_path)
        if path.suffix not in valid_extensions:
            raise ValueError(
                f"Invalid artifact extension: {path.suffix}. "
                f"Valid: {valid_extensions}"
            )

        # Step 5: Calculate MD5 checksum
        md5_checksum = self._calculate_md5(artifact_path)

        # Step 6: Validate magic bytes (file signature)
        magic_bytes = self._read_magic_bytes(artifact_path)
        self._validate_magic_bytes(path.suffix, magic_bytes)

        # Build artifact info dictionary
        artifact_info = {
            'path': artifact_path,
            'name': path.name,
            'size': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2),
            'md5': md5_checksum,
            'mtime': file_mtime,
            'extension': path.suffix
        }

        self.log.info(f"Artifact validated: {path.name} ({artifact_info['size_mb']}MB)")
        return artifact_info

    def _get_valid_extensions_for_file(self, artifact_path):
        """
        Get list of valid file extensions for a platform

        Args:
            artifact_path (str): Path to determine platform from

        Returns:
            list: Valid extensions (e.g., ['.apk', '.aab'])
        """
        # Determine platform from path
        if 'ios' in artifact_path:
            platform = 'ios'
        elif 'android_hw' in artifact_path or 'huawei' in artifact_path:
            platform = 'android_hw'
        else:
            platform = 'android'

        # Get valid extensions from config
        extensions = self.storage_config.get('accepted_extensions', {}).get(platform, [])
        return extensions

    def _calculate_md5(self, file_path, chunk_size=8192):
        """
        Calculate MD5 checksum of file

        We read file in chunks to handle large files efficiently.

        Args:
            file_path (str): Path to file
            chunk_size (int): Size of chunks to read (8KB default)

        Returns:
            str: MD5 hash in hexadecimal format
        """
        # Create MD5 hash object
        md5 = hashlib.md5()

        # Read file in chunks and update hash
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                md5.update(chunk)

        # Return hexadecimal digest
        return md5.hexdigest()

    def _read_magic_bytes(self, file_path, num_bytes=4):
        """
        Read first few bytes of file

        These bytes contain the file signature/magic bytes that identify file type.

        Args:
            file_path (str): Path to file
            num_bytes (int): Number of bytes to read

        Returns:
            bytes: First bytes of file
        """
        with open(file_path, 'rb') as f:
            return f.read(num_bytes)

    def _validate_magic_bytes(self, extension, magic_bytes):
        """
        Validate file type using magic bytes (file signature)

        Magic bytes are first few bytes of a file that identify its type:
        - APK/AAB files: Start with 'PK' (ZIP archives)
        - IPA files: Start with 'PK' (ZIP archives)

        Args:
            extension (str): File extension (e.g., '.apk')
            magic_bytes (bytes): First bytes of file

        Raises:
            ValueError: If magic bytes don't match expected file type
        """
        # APK and AAB files are ZIP archives (start with 'PK')
        if extension in ['.apk', '.aab']:
            if magic_bytes[:2] != b'PK':
                raise ValueError(
                    f"Invalid {extension} file: "
                    f"Expected ZIP signature (PK), got {magic_bytes[:2]}"
                )

        # IPA files are also ZIP archives
        elif extension == '.ipa':
            if magic_bytes[:2] != b'PK':
                raise ValueError(
                    f"Invalid .ipa file: "
                    f"Expected ZIP signature (PK), got {magic_bytes[:2]}"
                )

        self.log.debug(f"Magic bytes validated for {extension}")
