#!/usr/bin/env python3
"""
Microsoft Teams Notification Module
====================================
This module sends formatted notifications to Microsoft Teams.
Notifications include build details and links to PR and BrowserStack dashboard.

Key Concepts:
- Adaptive cards: Rich message format for Teams
- Webhook URL: Teams channel webhook for posting messages
- Mention groups: Optionally mention QA team in notification
"""

import requests
from datetime import datetime
from logger import get_logger


class TeamsNotifier:
    """
    Sends Microsoft Teams notifications for BrowserStack uploads

    Uses Teams Adaptive Cards for rich formatting.
    """

    def __init__(self, config):
        """
        Initialize Teams notifier

        Args:
            config: Config object with Teams settings
        """
        self.config = config
        self.log = get_logger("TeamsNotifier")

        # Get Teams webhook URL
        try:
            teams_config = config.get_teams_config()
            self.webhook_url = teams_config.get('webhook_url')
        except:
            self.webhook_url = None

        if not self.webhook_url:
            self.log.warning("Teams webhook URL not configured")

    def send_notification(self, platform, app_variant, environment, build_type,
                         version, old_app_id, new_app_id, pr_url, source_build_url,
                         yaml_file):
        """
        Send Teams notification about BrowserStack update

        Args:
            platform (str): Android/iOS platform
            app_variant (str): App variant (agent, retail, wallet)
            environment (str): Production/staging
            build_type (str): Debug/Release
            version (str): App version
            old_app_id (str): Previous app ID
            new_app_id (str): New app ID
            pr_url (str): Pull request URL
            source_build_url (str): Source build URL
            yaml_file (str): YAML file path

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.webhook_url:
            self.log.warning("Skipping Teams notification - webhook not configured")
            return False

        try:
            # Create formatted message
            card = self._create_adaptive_card(
                platform=platform,
                app_variant=app_variant,
                environment=environment,
                build_type=build_type,
                version=version,
                old_app_id=old_app_id,
                new_app_id=new_app_id,
                pr_url=pr_url,
                source_build_url=source_build_url,
                yaml_file=yaml_file
            )

            # Send to Teams webhook
            response = requests.post(
                self.webhook_url,
                json=card,
                timeout=10
            )

            # Check if successful
            if response.status_code == 200:
                self.log.info("Teams notification sent successfully")
                return True
            else:
                self.log.error(f"Teams notification failed: {response.status_code}")
                self.log.error(f"Response: {response.text}")
                return False

        except Exception as e:
            self.log.error(f"Failed to send Teams notification: {e}")
            return False

    def _create_adaptive_card(self, platform, app_variant, environment, build_type,
                             version, old_app_id, new_app_id, pr_url, source_build_url,
                             yaml_file):
        """
        Create Teams Adaptive Card message

        This creates a formatted card with:
        - Title and subtitle
        - Key information fields
        - Action buttons with links

        Args:
            platform, app_variant, environment, build_type, version: Build info
            old_app_id, new_app_id: App ID change info
            pr_url, source_build_url: Important URLs
            yaml_file: Updated YAML file path

        Returns:
            dict: Adaptive Card JSON structure
        """
        timestamp = datetime.utcnow().isoformat() + 'Z'

        # Choose emoji based on platform
        platform_emoji = {
            'android': '🤖',
            'android_hw': '📱',
            'ios': '🍎'
        }.get(platform, '📱')

        # Create Adaptive Card
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"BrowserStack Update - {platform}/{app_variant}/{environment}/{build_type}",
            "themeColor": "0078D4",  # Microsoft blue
            "sections": [
                {
                    "activityTitle": f"{platform_emoji} BrowserStack Update - {app_variant}",
                    "activitySubtitle": f"{environment.upper()} | {build_type}",
                    "facts": [
                        {
                            "name": "Platform:",
                            "value": f"`{platform}`"
                        },
                        {
                            "name": "Application:",
                            "value": f"`{app_variant}`"
                        },
                        {
                            "name": "Environment:",
                            "value": f"`{environment}`"
                        },
                        {
                            "name": "Build Type:",
                            "value": f"`{build_type}`"
                        },
                        {
                            "name": "Version:",
                            "value": f"`{version}`"
                        },
                        {
                            "name": "YAML File:",
                            "value": f"`{yaml_file}`"
                        },
                        {
                            "name": "Old App ID:",
                            "value": f"`{old_app_id if old_app_id else 'N/A'}`"
                        },
                        {
                            "name": "New App ID:",
                            "value": f"```{new_app_id}```"
                        },
                        {
                            "name": "Updated At:",
                            "value": timestamp
                        }
                    ]
                }
            ],
            # Action buttons at bottom of card
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View Pull Request",
                    "targets": [
                        {
                            "os": "default",
                            "uri": pr_url
                        }
                    ]
                },
                {
                    "@type": "OpenUri",
                    "name": "Source Build",
                    "targets": [
                        {
                            "os": "default",
                            "uri": source_build_url
                        }
                    ]
                },
                {
                    "@type": "OpenUri",
                    "name": "BrowserStack Dashboard",
                    "targets": [
                        {
                            "os": "default",
                            "uri": "https://app-live.browserstack.com"
                        }
                    ]
                }
            ]
        }

        # Add QA team mention if configured
        try:
            teams_config = self.config.get_teams_config()
            if teams_config.get('mention_qa'):
                qa_group = teams_config.get('qa_group', 'QA Team')
                card["sections"][0]["text"] = f"cc: @{qa_group}"
        except:
            pass

        return card
