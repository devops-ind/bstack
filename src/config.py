#!/usr/bin/env python3
"""
Configuration Management Module
==================================
This module loads and manages settings from a YAML configuration file.
It also replaces environment variables like ${BROWSERSTACK_USER} with their actual values.

Key Concepts:
- Config class: Manages all application settings
- Environment variable substitution: Replaces ${VAR_NAME} with actual values
"""

import os
import yaml
from pathlib import Path


class Config:
    """
    Manages configuration loading and retrieval

    This class:
    1. Reads settings from a YAML file
    2. Replaces environment variable placeholders (${VAR_NAME})
    3. Provides methods to safely retrieve configuration values
    """

    def __init__(self, config_path='config.yaml'):
        """
        Load configuration from YAML file

        Args:
            config_path (str): Path to the YAML configuration file

        Raises:
            FileNotFoundError: If configuration file doesn't exist
        """
        # Convert string path to Path object
        self.config_path = Path(config_path)

        # Check if file exists
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        # Read YAML file
        with open(self.config_path, 'r') as f:
            raw_config = yaml.safe_load(f)

        # Replace environment variables in configuration
        self.config = self._substitute_env_vars(raw_config)

    def _substitute_env_vars(self, obj):
        """
        Recursively replace environment variable placeholders with actual values

        This function handles:
        - Dictionaries: processes all key-value pairs
        - Lists: processes all items
        - Strings: replaces ${VAR_NAME} with environment variable values

        Args:
            obj: Object to process (dict, list, string, or other)

        Returns:
            Object with environment variables replaced
        """
        if isinstance(obj, dict):
            # For dictionaries: process all key-value pairs
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            # For lists: process all items
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # For strings: replace ${VAR_NAME} with environment variable value
            if obj.startswith('${') and obj.endswith('}'):
                # Extract variable name (remove ${ and })
                var_name = obj[2:-1]

                # Get environment variable value
                value = os.getenv(var_name)

                # Raise error if environment variable not set
                if value is None:
                    raise ValueError(f"Environment variable not set: {var_name}")

                return value
            return obj
        else:
            # For other types: return as-is
            return obj

    def get(self, key, default=None):
        """
        Get configuration value using dot notation

        Examples:
            config.get('browserstack.username')
            config.get('git.repo_url', 'https://github.com/default/repo')

        Args:
            key (str): Configuration key using dot notation (e.g., 'section.subsection.key')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        # Split key by dots to navigate nested dictionaries
        keys = key.split('.')
        value = self.config

        # Navigate through each level
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_required(self, key):
        """
        Get required configuration value - raises error if missing

        Args:
            key (str): Configuration key

        Returns:
            Configuration value

        Raises:
            ValueError: If configuration key is missing
        """
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required configuration missing: {key}")
        return value

    def get_browserstack_config(self):
        """Get BrowserStack API configuration"""
        return {
            'username': self.get_required('browserstack.username'),
            'access_key': self.get_required('browserstack.access_key'),
            'api_endpoint': self.get('browserstack.api_endpoint'),
            'upload_timeout': self.get('browserstack.upload_timeout', 300)
        }

    def get_git_config(self):
        """Get Git repository configuration"""
        return {
            'repo_url': self.get_required('git.repo_url'),
            'default_branch': self.get('git.default_branch', 'main'),
            'user_name': self.get('git.user_name', 'DevOps Automation'),
            'user_email': self.get('git.user_email', 'devops@company.com'),
            'create_pr': self.get('git.create_pr', True)
        }

    def get_github_config(self):
        """Get GitHub API configuration"""
        return {
            'token': self.get_required('github.token'),
            'org': self.get_required('github.org'),
            'repo': self.get_required('github.repo')
        }

    def get_local_storage_config(self):
        """Get local artifact storage configuration"""
        return {
            'artifact_base_path': self.get_required('local_storage.artifact_base_path'),
            'path_templates': self.get_required('local_storage.path_templates'),
            'accepted_extensions': self.get_required('local_storage.accepted_extensions')
        }

    def get_teams_config(self):
        """Get Microsoft Teams notification configuration"""
        return {
            'webhook_url': self.get_required('notifications.teams.webhook_url'),
            'mention_qa': self.get('notifications.teams.mention_qa', True),
            'qa_group': self.get('notifications.teams.qa_group', 'QA Team')
        }

    def get_yaml_config(self):
        """Get YAML file structure configuration"""
        return {
            'shared_file': self.get('yaml_structure.shared_file', 'shared.yml'),
            'app_root_key': self.get('yaml_structure.app_root_key', 'apps'),
            'environment_levels': self.get('yaml_structure.environment_levels', ['environment', 'build_type'])
        }

    def get_retry_config(self):
        """Get retry strategy configuration"""
        return {
            'max_attempts': self.get('retry.max_attempts', 3),
            'initial_delay': self.get('retry.initial_delay', 2),
            'backoff_factor': self.get('retry.backoff_factor', 2)
        }
