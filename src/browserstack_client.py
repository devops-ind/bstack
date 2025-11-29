#!/usr/bin/env python3
"""
BrowserStack API Client Module
===============================
This module handles all interactions with the BrowserStack API.
It uploads app files and manages the upload session.

Key Concepts:
- HTTP requests: Communicating with BrowserStack API
- File upload: Sending binary file data to server
- Retry logic: Automatically retrying on network failures
- Authentication: Using username and access key
"""

import requests
import time
import urllib3
from logger import get_logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BrowserStackClient:
    """
    Client for BrowserStack App Automate API

    This class handles:
    - Uploading app artifacts to BrowserStack
    - Retrieving app details
    - Deleting apps from BrowserStack
    """

    def __init__(self, config):
        """
        Initialize BrowserStack client

        Args:
            config: Config object with BrowserStack settings
        """
        self.config = config
        self.log = get_logger(__name__)

        # Get BrowserStack configuration
        bs_config = config.get_browserstack_config()

        # Store credentials
        self.username = bs_config['username']
        self.access_key = bs_config['access_key']
        self.api_endpoint = bs_config.get(
            'api_endpoint',
            'https://api-cloud.browserstack.com/app-automate/upload'
        )
        self.upload_timeout = bs_config.get('upload_timeout', 300)

        # SSL/TLS settings for corporate networks
        self.ssl_verify = bs_config.get('ssl_verify', True)
        self.ssl_ca_bundle = bs_config.get('ssl_ca_bundle', None)

        # Log SSL configuration
        if not self.ssl_verify:
            self.log.warning("⚠️  SSL certificate verification is DISABLED - this is a security risk!")
            # Suppress InsecureRequestWarning when SSL verification is disabled
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        elif self.ssl_ca_bundle:
            self.log.info(f"Using custom CA bundle: {self.ssl_ca_bundle}")

        # Create HTTP session with retry logic
        self.session = self._create_session()

    def _create_session(self):
        """
        Create HTTP session with automatic retry logic

        Retries are triggered when:
        - Server returns 429 (Rate Limited)
        - Server returns 500, 502, 503, 504 (Server Errors)
        - Network errors occur

        Uses exponential backoff: 1s -> 2s -> 4s -> etc.

        Returns:
            requests.Session: Configured session with retry strategy
        """
        # Create new session
        session = requests.Session()

        # Get retry configuration
        retry_config = self.config.get_retry_config()

        # Setup retry strategy
        retry_strategy = Retry(
            total=retry_config['max_attempts'],  # Max 3 attempts
            backoff_factor=retry_config['backoff_factor'],  # Exponential backoff
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these codes
            allowed_methods=['POST', 'GET']  # Retry these methods
        )

        # Create adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)

        # Mount adapter for both HTTP and HTTPS
        session.mount('https://', adapter)
        session.mount('http://', adapter)

        return session

    def upload_app(self, artifact_path, custom_id, app_variant=None, environment=None):
        """
        Upload app artifact to BrowserStack

        Process:
        1. Open app file in binary mode
        2. Send to BrowserStack API with authentication
        3. Parse response JSON
        4. Return app URL and metadata

        Args:
            artifact_path (str): Path to APK/IPA file
            custom_id (str): Custom identifier for this upload
            app_variant (str): App variant name (optional, for logging)
            environment (str): Environment name (optional, for logging)

        Returns:
            dict: Upload result with app_id, custom_id, timestamp, response

        Raises:
            requests.exceptions.Timeout: If upload takes too long
            requests.exceptions.RequestException: If HTTP request fails
            ValueError: If BrowserStack response is invalid
        """
        self.log.info(f"Uploading artifact to BrowserStack: {artifact_path}")

        try:
            # Open file in binary read mode
            with open(artifact_path, 'rb') as f:
                files = {'file': f}  # File data to upload
                data = {'custom_id': custom_id}  # Additional metadata

                # Log upload details
                self.log.debug(f"Custom ID: {custom_id}")
                self.log.debug(f"Endpoint: {self.api_endpoint}")
                if app_variant:
                    self.log.debug(f"App Variant: {app_variant}")
                if environment:
                    self.log.debug(f"Environment: {environment}")

                # Determine SSL verification settings
                # Priority: ssl_ca_bundle > ssl_verify
                if self.ssl_ca_bundle:
                    verify = self.ssl_ca_bundle  # Use custom CA bundle
                else:
                    verify = self.ssl_verify  # Use True/False

                # Send POST request to BrowserStack API
                response = self.session.post(
                    self.api_endpoint,
                    files=files,
                    data=data,
                    auth=(self.username, self.access_key),  # Basic auth
                    timeout=self.upload_timeout,  # 5 minute timeout
                    verify=verify  # SSL certificate verification
                )

                # Raise error if HTTP status is not 2xx
                response.raise_for_status()

                # Parse JSON response
                result = response.json()
                self.log.debug(f"Response: {result}")

                # Check if upload was successful (app_url should be in response)
                if 'app_url' not in result:
                    raise ValueError(
                        f"Invalid BrowserStack response: {result}"
                    )

                # Extract app URL (this is the app ID)
                app_id = result['app_url']
                self.log.info(f"Upload successful: {app_id}")

                # Return upload metadata
                return {
                    'app_id': app_id,
                    'app_url': app_id,  # Alias for compatibility
                    'custom_id': custom_id,
                    'timestamp': time.time(),
                    'response': result
                }

        except requests.exceptions.Timeout:
            # Handle timeout error
            self.log.error(f"Upload timeout after {self.upload_timeout} seconds")
            raise

        except requests.exceptions.RequestException as e:
            # Handle HTTP request errors
            self.log.error(f"Upload failed: {e}")
            raise

        except ValueError as e:
            # Handle invalid response
            self.log.error(f"Invalid response: {e}")
            raise

    def get_app_details(self, app_id):
        """
        Get details about an uploaded app

        Args:
            app_id (str): App URL from upload (e.g., bs://123456)

        Returns:
            dict: App details from BrowserStack

        Raises:
            Exception: If API call fails
        """
        self.log.debug(f"Fetching app details for: {app_id}")

        try:
            # Remove 'bs://' prefix if present
            if app_id.startswith('bs://'):
                app_id_clean = app_id.replace('bs://', '')
            else:
                app_id_clean = app_id

            # Build endpoint URL
            endpoint = f"{self.api_endpoint}/{app_id_clean}"

            # Determine SSL verification settings
            if self.ssl_ca_bundle:
                verify = self.ssl_ca_bundle
            else:
                verify = self.ssl_verify

            # Send GET request
            response = self.session.get(
                endpoint,
                auth=(self.username, self.access_key),
                timeout=30,
                verify=verify
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            self.log.error(f"Failed to fetch app details: {e}")
            raise

    def delete_app(self, app_id):
        """
        Delete app from BrowserStack

        Args:
            app_id (str): App URL to delete

        Returns:
            bool: True if deleted successfully

        Raises:
            Exception: If delete fails
        """
        self.log.info(f"Deleting app from BrowserStack: {app_id}")

        try:
            # Remove 'bs://' prefix if present
            if app_id.startswith('bs://'):
                app_id_clean = app_id.replace('bs://', '')
            else:
                app_id_clean = app_id

            # Build endpoint URL
            endpoint = f"{self.api_endpoint}/{app_id_clean}"

            # Determine SSL verification settings
            if self.ssl_ca_bundle:
                verify = self.ssl_ca_bundle
            else:
                verify = self.ssl_verify

            # Send DELETE request
            response = self.session.delete(
                endpoint,
                auth=(self.username, self.access_key),
                timeout=30,
                verify=verify
            )

            response.raise_for_status()
            self.log.info(f"App deleted: {app_id}")
            return True

        except Exception as e:
            self.log.error(f"Failed to delete app: {e}")
            raise
