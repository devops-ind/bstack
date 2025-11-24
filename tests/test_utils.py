"""
Unit tests for the utils module

Tests parameter validation, version checking, and helper functions.
"""

import pytest


class TestVersionValidation:
    """Test semantic version validation"""

    def test_valid_semantic_version(self):
        """Test that valid semantic versions are accepted"""
        from src.utils import is_valid_version

        # Test valid versions
        assert is_valid_version('1.0.0') is True
        assert is_valid_version('2.5.10') is True
        assert is_valid_version('0.0.1') is True

    def test_valid_version_with_suffix(self):
        """Test that versions with suffixes are accepted"""
        from src.utils import is_valid_version

        # Test versions with pre-release suffixes
        assert is_valid_version('1.0.0-beta') is True
        assert is_valid_version('1.0.0-alpha.1') is True
        assert is_valid_version('1.0.0-rc1') is True

    def test_invalid_version_format(self):
        """Test that invalid versions are rejected"""
        from src.utils import is_valid_version

        # Test invalid formats
        assert is_valid_version('1.0') is False
        assert is_valid_version('1') is False
        assert is_valid_version('version1.0.0') is False
        assert is_valid_version('1.0.0.0') is False


class TestParameterValidation:
    """Test input parameter validation"""

    def test_valid_platform_values(self):
        """Test valid platform values"""
        valid_platforms = ['android', 'android_hw', 'ios']

        for platform in valid_platforms:
            assert platform in valid_platforms

    def test_valid_environment_values(self):
        """Test valid environment values"""
        valid_environments = ['production', 'staging']

        for env in valid_environments:
            assert env in valid_environments

    def test_valid_build_types(self):
        """Test valid build type values"""
        valid_build_types = ['Debug', 'Release']

        for build_type in valid_build_types:
            assert build_type in valid_build_types

    def test_valid_app_variants(self):
        """Test valid app variant values"""
        valid_variants = ['agent', 'retail', 'wallet']

        for variant in valid_variants:
            assert variant in valid_variants


class TestFileOperations:
    """Test file operation helper functions"""

    def test_format_bytes_kb(self):
        """Test byte formatting for KB"""
        from src.utils import format_bytes

        # 1024 bytes = 1 KB
        result = format_bytes(1024)
        assert 'KB' in result

    def test_format_bytes_mb(self):
        """Test byte formatting for MB"""
        from src.utils import format_bytes

        # 1048576 bytes = 1 MB
        result = format_bytes(1048576)
        assert 'MB' in result

    def test_format_bytes_gb(self):
        """Test byte formatting for GB"""
        from src.utils import format_bytes

        # 1073741824 bytes = 1 GB
        result = format_bytes(1073741824)
        assert 'GB' in result

    def test_sanitize_filename(self):
        """Test filename sanitization"""
        from src.utils import sanitize_filename

        # Test with special characters
        result = sanitize_filename('file@name#123.txt')
        assert '@' not in result
        assert '#' not in result
        assert 'file' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
