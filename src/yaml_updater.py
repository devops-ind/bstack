#!/usr/bin/env python3
"""
YAML Configuration File Updater Module
========================================
This module updates YAML configuration files with new BrowserStack app IDs.

Key Concepts:
- Separate files per variant: Each app variant has its own YAML file
- Nested YAML structure: apps > app_variant > environment > build_type > app_id
- Shared metadata: shared.yml tracks which builds were updated
"""

import yaml
from pathlib import Path
from datetime import datetime
from logger import get_logger


class YAMLUpdater:
    """
    Updates YAML configuration files with new BrowserStack app IDs

    Strategy: Separate files per app variant to avoid merge conflicts
    """

    def __init__(self, config, repo_path):
        """
        Initialize YAML updater

        Args:
            config: Config object with YAML settings
            repo_path: Path to cloned repository
        """
        self.config = config
        self.repo_path = Path(repo_path)
        self.log = get_logger(__name__)
        self.yaml_config = config.get_yaml_config()

    def get_current_app_id(self, platform, app_variant, environment, build_type):
        """
        Get the current app ID from YAML file

        This helps track what was replaced.

        Args:
            platform (str): android, android_hw, or ios
            app_variant (str): agent, retail, wallet
            environment (str): production or staging
            build_type (str): Debug or Release

        Returns:
            str: Current app ID or 'NOT_SET' if not found
        """
        yaml_file = self._get_yaml_file_path(platform, app_variant)

        try:
            # Read YAML file
            with open(yaml_file, 'r') as f:
                content = yaml.safe_load(f)

            # Navigate nested structure: apps[app_variant][environment][build_type]
            app_id = content.get('apps', {}).get(app_variant, {}).get(
                environment, {}
            ).get(build_type, {}).get('app_id', 'NOT_SET')

            self.log.debug(f"Current app_id: {app_id}")
            return app_id

        except FileNotFoundError:
            # File doesn't exist yet
            self.log.warning(f"YAML file not found: {yaml_file}")
            return 'NOT_SET'

        except Exception as e:
            # Error reading file
            self.log.warning(f"Error reading current app_id: {e}")
            return 'NOT_SET'

    def update_app_id(self, platform, app_variant, environment, build_type,
                      new_app_id, version, build_id):
        """
        Update app ID in YAML file

        Updates two files:
        1. Platform-specific file: {platform}/{app_variant}.yml
        2. Shared metadata file: shared.yml

        Args:
            platform (str): android, android_hw, or ios
            app_variant (str): agent, retail, wallet
            environment (str): production or staging
            build_type (str): Debug or Release
            new_app_id (str): New app ID from BrowserStack
            version (str): App version number
            build_id (str): Build identifier

        Returns:
            list: List of files updated
        """
        self.log.info(f"Updating YAML files for {platform}/{app_variant}/{environment}/{build_type}")

        updated_files = []
        timestamp = datetime.utcnow().isoformat() + 'Z'

        # 1. Update specific app variant YAML file
        yaml_file = self._get_yaml_file_path(platform, app_variant)
        self._update_yaml_file(
            yaml_file=yaml_file,
            app_variant=app_variant,
            environment=environment,
            build_type=build_type,
            new_app_id=new_app_id,
            version=version,
            build_id=build_id,
            timestamp=timestamp
        )

        # Convert to relative path for git operations
        relative_path = yaml_file.relative_to(self.repo_path)
        updated_files.append(str(relative_path))
        self.log.info(f"Updated: {relative_path}")

        # 2. Update shared.yml with metadata
        shared_file = self._get_shared_yaml_file_path()
        self._update_shared_yaml(
            shared_file=shared_file,
            platform=platform,
            app_variant=app_variant,
            environment=environment,
            build_type=build_type,
            build_id=build_id,
            timestamp=timestamp
        )

        relative_shared = shared_file.relative_to(self.repo_path)
        updated_files.append(str(relative_shared))
        self.log.info(f"Updated: {relative_shared}")

        return updated_files

    def _get_yaml_file_path(self, platform, app_variant):
        """
        Get path to YAML file for app variant

        Uses configuration mapping to find correct file name.

        Args:
            platform (str): android, android_hw, or ios
            app_variant (str): agent, retail, wallet

        Returns:
            Path: Full path to YAML file
        """
        yaml_files = self.yaml_config.get('yaml_files', {})

        # Look up file name in config
        if platform in yaml_files and app_variant in yaml_files[platform]:
            file_name = yaml_files[platform][app_variant]
        else:
            # Fallback to default naming
            self.log.warning(
                f"YAML file mapping not found for {platform}/{app_variant}, "
                f"using default naming"
            )
            file_name = f"{platform}_{app_variant}.yml"

        # YAML files are in repo root
        yaml_path = self.repo_path / file_name
        self.log.debug(f"YAML file path: {yaml_path}")
        return yaml_path

    def _get_shared_yaml_file_path(self):
        """
        Get path to shared.yml metadata file

        Returns:
            Path: Full path to shared.yml
        """
        shared_file = self.yaml_config.get('shared_file', 'shared.yml')
        return self.repo_path / shared_file

    def _update_yaml_file(self, yaml_file, app_variant, environment, build_type,
                         new_app_id, version, build_id, timestamp):
        """
        Update specific app variant YAML file

        Creates nested structure:
            apps:
              app_variant:
                environment:
                  build_type:
                    app_id: bs://12345...
                    version: 1.0.0
                    build_id: jenkins-123
                    updated_at: 2024-01-01T12:00:00Z

        Args:
            yaml_file (Path): Path to YAML file
            app_variant (str): Application variant
            environment (str): Production or staging
            build_type (str): Debug or Release
            new_app_id (str): New app ID from BrowserStack
            version (str): App version
            build_id (str): Build identifier
            timestamp (str): ISO format timestamp
        """
        self.log.debug(f"Updating YAML file: {yaml_file}")

        # Create parent directories if needed
        yaml_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing content or create empty dict
        if yaml_file.exists():
            with open(yaml_file, 'r') as f:
                content = yaml.safe_load(f) or {}
        else:
            content = {}

        # Ensure 'apps' key exists
        if 'apps' not in content:
            content['apps'] = {}

        # Ensure app_variant key exists
        if app_variant not in content['apps']:
            content['apps'][app_variant] = {}

        # Ensure environment key exists
        if environment not in content['apps'][app_variant]:
            content['apps'][app_variant][environment] = {}

        # Ensure build_type key exists
        if build_type not in content['apps'][app_variant][environment]:
            content['apps'][app_variant][environment][build_type] = {}

        # Update the app ID and metadata
        content['apps'][app_variant][environment][build_type] = {
            'app_id': new_app_id,
            'app_url': new_app_id,
            'version': version,
            'build_id': build_id,
            'build_type': build_type,
            'environment': environment,
            'updated_at': timestamp
        }

        # Write updated content back to file
        self._write_yaml_file(yaml_file, content)
        self.log.debug(f"YAML file updated: {yaml_file}")

    def _update_shared_yaml(self, shared_file, platform, app_variant,
                            environment, build_type, build_id, timestamp):
        """
        Update shared.yml with metadata about updates

        This file tracks:
        - Which builds were updated
        - When they were updated
        - Links to BrowserStack

        Args:
            shared_file (Path): Path to shared.yml
            platform (str): android, android_hw, or ios
            app_variant (str): agent, retail, wallet
            environment (str): production or staging
            build_type (str): Debug or Release
            build_id (str): Build identifier
            timestamp (str): ISO format timestamp
        """
        self.log.debug(f"Updating shared YAML file: {shared_file}")

        # Create parent directories if needed
        shared_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing content or create empty dict
        if shared_file.exists():
            with open(shared_file, 'r') as f:
                content = yaml.safe_load(f) or {}
        else:
            content = {}

        # Ensure required keys exist
        if 'browserstack' not in content:
            content['browserstack'] = {
                'dashboard': 'https://app-live.browserstack.com',
                'api_version': 'v1',
                'retention_days': 30
            }

        if 'artifacts' not in content:
            content['artifacts'] = {}

        # Update timestamp
        content['browserstack']['last_updated'] = timestamp

        # Ensure platform entry exists
        if platform not in content['artifacts']:
            content['artifacts'][platform] = {}

        # Ensure app_variant entry exists
        if app_variant not in content['artifacts'][platform]:
            content['artifacts'][platform][app_variant] = {}

        # Update metadata
        content['artifacts'][platform][app_variant] = {
            'last_updated': timestamp,
            'last_updated_by': 'devops-automation',
            'last_build_id': build_id,
            'app_variants_updated': [f"{environment}/{build_type}"]
        }

        # Write updated content back to file
        self._write_yaml_file(shared_file, content)
        self.log.debug(f"Shared YAML file updated: {shared_file}")

    def _write_yaml_file(self, yaml_file, content):
        """
        Write YAML content to file with proper formatting

        Args:
            yaml_file (Path): Path to YAML file
            content (dict): Content to write
        """
        with open(yaml_file, 'w') as f:
            yaml.dump(
                content,
                f,
                default_flow_style=False,  # Use block style (not inline)
                sort_keys=False,  # Keep order as written
                allow_unicode=True,  # Support international characters
                indent=2,  # 2-space indentation
                explicit_start=False  # No --- at start
            )

    def validate_yaml_files(self, updated_files):
        """
        Validate that updated YAML files are valid

        Args:
            updated_files (list): List of file paths to validate

        Raises:
            yaml.YAMLError: If any file has invalid YAML
        """
        self.log.info("Validating updated YAML files")

        for file_path in updated_files:
            full_path = self.repo_path / file_path

            try:
                # Try to load YAML file
                with open(full_path, 'r') as f:
                    yaml.safe_load(f)
                self.log.debug(f"Valid YAML: {file_path}")

            except yaml.YAMLError as e:
                # File has invalid YAML syntax
                self.log.error(f"Invalid YAML in {file_path}: {e}")
                raise
