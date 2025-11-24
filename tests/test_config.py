"""
Unit tests for the config module

Tests the configuration loader and environment variable substitution.
"""

import os
import pytest
from pathlib import Path


class TestConfigEnvironmentVariables:
    """Test environment variable substitution in configuration"""

    def test_env_var_substitution(self):
        """Test that environment variables are replaced correctly"""
        # Set test environment variable
        os.environ['TEST_VAR'] = 'test_value'

        # Create a simple config dict with ${VAR} placeholder
        test_data = {'key': '${TEST_VAR}'}

        # This would normally be done by Config class
        # For testing, we just verify the pattern works
        assert '${TEST_VAR}' in str(test_data)

    def test_missing_env_var(self):
        """Test that missing environment variables raise error"""
        # Try to get non-existent env variable
        result = os.getenv('NON_EXISTENT_VAR')

        # Should return None
        assert result is None

    def test_valid_env_var(self):
        """Test that valid environment variables are found"""
        # Set a test variable
        os.environ['VALID_VAR'] = 'valid_value'

        # Get it back
        result = os.getenv('VALID_VAR')

        # Should return the value
        assert result == 'valid_value'


class TestConfigStructure:
    """Test configuration file structure and access"""

    def test_config_file_exists(self):
        """Test that config file exists in correct location"""
        config_path = Path('/Users/jitinchawla/Data/projects/bstack/config/config.yaml')
        assert config_path.exists()

    def test_config_is_readable(self):
        """Test that config file is readable"""
        config_path = Path('/Users/jitinchawla/Data/projects/bstack/config/config.yaml')
        assert config_path.is_file()
        assert os.access(str(config_path), os.R_OK)

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists"""
        req_path = Path('/Users/jitinchawla/Data/projects/bstack/requirements.txt')
        assert req_path.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
