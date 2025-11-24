#!/usr/bin/env python3
"""
Basic Example: Simple BrowserStack Uploader Usage

This example shows how to use the BrowserStack Uploader in its simplest form.

Prerequisites:
    1. Install dependencies: pip install -r requirements.txt
    2. Set environment variables:
       - BROWSERSTACK_USER
       - BROWSERSTACK_ACCESS_KEY
       - GITHUB_TOKEN
       - TEAMS_WEBHOOK_URL
    3. Edit config.yaml with your settings
"""

import sys
from pathlib import Path

# Add src directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.main import BrowserStackUploader


def example_basic_upload():
    """
    Basic example: Upload an artifact to BrowserStack

    This is the simplest way to use the uploader.
    """
    print("=" * 70)
    print("BASIC EXAMPLE: BrowserStack Artifact Upload")
    print("=" * 70)

    # Define parameters for the upload
    params = {
        'platform': 'android',                    # Mobile platform
        'environment': 'staging',                 # Target environment
        'build_type': 'Debug',                    # Debug or Release
        'app_variant': 'agent',                   # Which app variant
        'version': '1.0.0',                       # Version number
        'build_id': 'example-build-001',          # Build identifier
        'source_build_url': 'https://example.com/build/001'  # Build URL
    }

    # Initialize the uploader
    # Make sure config.yaml exists in the config/ directory
    config_file = 'config/config.yaml'
    uploader = BrowserStackUploader(config_file, verbose=True)

    # Run the upload process
    result = uploader.run(params)

    # Print results
    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)
    print(f"Status: {result['status']}")

    if result['status'] == 'SUCCESS':
        print(f"App ID: {result['browserstack']['app_id']}")
        print(f"Pull Request: {result['pr']['pr_url']}")
        print("\nUpload successful! ✅")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        print("\nUpload failed! ❌")

    return result


def example_with_output_file():
    """
    Example: Save upload results to a JSON file

    This is useful when you need to process the results programmatically.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: Save Results to JSON File")
    print("=" * 70)

    params = {
        'platform': 'ios',
        'environment': 'production',
        'build_type': 'Release',
        'app_variant': 'retail',
        'version': '2.0.0',
        'build_id': 'example-build-002',
        'source_build_url': 'https://example.com/build/002'
    }

    # Initialize uploader
    uploader = BrowserStackUploader('config/config.yaml', verbose=False)

    # Run with output file
    output_file = 'upload_result.json'
    result = uploader.run(params, output_file=output_file)

    print(f"Results saved to: {output_file}")
    print(f"Status: {result['status']}")

    return result


def example_parameter_validation():
    """
    Example: Validate parameters before uploading

    Shows how to validate parameters without actually uploading.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: Parameter Validation")
    print("=" * 70)

    from src.utils import validate_parameters

    # Valid parameters
    valid_params = {
        'platform': 'android',
        'environment': 'staging',
        'build_type': 'Release',
        'app_variant': 'wallet',
        'version': '1.5.0',
        'build_id': 'example-build-003',
        'source_build_url': 'https://example.com/build/003'
    }

    # Validate
    errors = validate_parameters(valid_params)

    if not errors:
        print("✅ Parameters are valid!")
    else:
        print("❌ Parameter errors:")
        for error in errors:
            print(f"  - {error}")

    # Invalid parameters example
    print("\n--- Testing with invalid parameters ---")

    invalid_params = {
        'platform': 'windows',              # Invalid platform
        'environment': 'test',              # Invalid environment
        'build_type': 'Debug',
        'app_variant': 'unknown',           # Invalid variant
        'version': '1.2',                   # Invalid version format
        'build_id': 'test-build',
        'source_build_url': 'not-a-url'    # Invalid URL
    }

    errors = validate_parameters(invalid_params)

    if errors:
        print("❌ Found validation errors:")
        for error in errors:
            print(f"  - {error}")


def example_config_loading():
    """
    Example: Load and access configuration

    Shows how to work with the configuration system.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: Configuration Loading")
    print("=" * 70)

    from src.config import Config

    try:
        # Load configuration
        config = Config('config/config.yaml')
        print("✅ Configuration loaded successfully!")

        # Get specific values
        print("\nConfiguration values:")
        print(f"  BrowserStack API timeout: {config.get('browserstack.upload_timeout')} seconds")
        print(f"  Default git branch: {config.get('git.default_branch')}")
        print(f"  Max retry attempts: {config.get('retry.max_attempts')}")

    except FileNotFoundError:
        print("❌ Configuration file not found!")
        print("   Make sure config/config.yaml exists")


if __name__ == '__main__':
    """
    Run examples

    Choose which example to run by uncommenting the function call.
    """

    # Example 1: Basic upload
    # example_basic_upload()

    # Example 2: Save results to file
    # example_with_output_file()

    # Example 3: Parameter validation
    example_parameter_validation()

    # Example 4: Configuration loading
    example_config_loading()

    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)
