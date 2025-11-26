#!/usr/bin/env python3
"""
BrowserStack Artifact Uploader - Main Entry Point
==================================================

This script orchestrates the complete workflow of:
1. Validating input parameters
2. Checking artifact files exist and are valid
3. Uploading to BrowserStack
4. Updating YAML configuration files
5. Creating Git commits and pull requests
6. Sending Teams notifications
7. Creating audit trails

Usage:
    python3 main.py \\
        --platform android \\
        --environment production \\
        --build-type Release \\
        --app-variant agent \\
        --version 1.2.0 \\
        --build-id jenkins-1234 \\
        --source-build-url https://jenkins.example.com/job/build/123 \\
        --src-folder "\\\\192.1.6.8\\Builds\\MobileApp\\Nightly_Builds\\mainline" \\
        --config-file ../config/config.yaml \\
        --verbose
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Import our modules
from config import Config
from logger import setup_logger
from local_storage import LocalStorage
from browserstack_client import BrowserStackClient
from yaml_updater import YAMLUpdater
from github_client import GitHubClient
from teams_notifier import TeamsNotifier
from utils import validate_parameters, create_audit_trail


class BrowserStackUploader:
    """
    Main orchestrator for the artifact upload workflow

    This class coordinates 9 workflow steps:
    1. Validate Parameters
    2. Validate & Read Artifact
    3. Upload to BrowserStack
    4. Clone YAML Repository
    5. Update YAML Files
    6. Git Commit & Push
    7. Create Pull Request
    8. Send Teams Notification
    9. Create Audit Trail
    """

    def __init__(self, config_file: str, verbose: bool = False):
        """
        Initialize uploader with configuration

        Args:
            config_file (str): Path to YAML config file
            verbose (bool): Enable verbose logging
        """
        # Load configuration
        self.config = Config(config_file)

        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        self.logger = setup_logger(log_level)
        self.logger.info("BrowserStack Uploader initialized")

    def run(self, params: Dict[str, str], output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the complete artifact upload workflow

        Args:
            params (dict): Parameters with keys:
                - platform: android, android_hw, ios
                - environment: production, staging
                - build_type: Debug, Release
                - app_variant: agent, retail, wallet
                - version: semantic version (X.Y.Z)
                - build_id: Jenkins build number
                - source_build_url: Jenkins build URL
                - src_folder: (optional) Custom source folder path for artifacts
            output_file (str): Optional JSON file for results

        Returns:
            dict: Workflow results
        """
        try:
            # Create result object
            result = {
                "status": "PENDING",
                "timestamp": datetime.utcnow().isoformat(),
                "params": params,
                "steps": {}
            }

            # =========================================================
            # STEP 1: Validate Parameters
            # =========================================================
            self.logger.info("=" * 70)
            self.logger.info("STEP 1: Validate Parameters")
            self.logger.info("=" * 70)

            validation_errors = validate_parameters(params)
            if validation_errors:
                self.logger.error(f"Parameter validation failed:")
                for error in validation_errors:
                    self.logger.error(f"  - {error}")

                result["status"] = "FAILED"
                result["error"] = "Parameter validation failed"
                result["details"] = validation_errors
                self._write_output(output_file, result)
                return result

            # Log validated parameters
            self.logger.info("Parameters validated successfully")
            self.logger.info(f"  Platform: {params['platform']}")
            self.logger.info(f"  Environment: {params['environment']}")
            self.logger.info(f"  Build Type: {params['build_type']}")
            self.logger.info(f"  App Variant: {params['app_variant']}")
            self.logger.info(f"  Version: {params['version']}")
            result["steps"]["validate"] = "SUCCESS"

            # =========================================================
            # STEP 2: Validate & Read Artifact
            # =========================================================
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 2: Validate & Read Artifact")
            self.logger.info("=" * 70)

            # Create storage manager with optional custom src_folder
            src_folder = params.get('src_folder')
            if src_folder:
                self.logger.info(f"Using custom source folder: {src_folder}")
            local_storage = LocalStorage(self.config, src_folder=src_folder)

            # Build artifact path from parameters
            artifact_path = local_storage.construct_artifact_path(
                platform=params['platform'],
                environment=params['environment'],
                build_type=params['build_type'],
                app_variant=params['app_variant']
            )

            # Validate artifact file
            artifact_info = local_storage.validate_artifact(artifact_path)

            self.logger.info(f"Artifact validated")
            self.logger.info(f"  Path: {artifact_info['path']}")
            self.logger.info(f"  Size: {artifact_info['size_mb']} MB")
            self.logger.info(f"  MD5: {artifact_info['md5']}")
            result["steps"]["artifact_validation"] = "SUCCESS"
            result["artifact"] = artifact_info

            # =========================================================
            # STEP 3: Upload to BrowserStack
            # =========================================================
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 3: Upload to BrowserStack")
            self.logger.info("=" * 70)

            # Create BrowserStack client
            bs_client = BrowserStackClient(self.config)

            # Upload app
            upload_result = bs_client.upload_app(
                artifact_path=artifact_info['path'],
                custom_id=self._generate_custom_id(params),
                app_variant=params['app_variant'],
                environment=params['environment']
            )

            self.logger.info(f"Upload successful")
            self.logger.info(f"  App ID: {upload_result['app_id']}")
            result["steps"]["browserstack_upload"] = "SUCCESS"
            result["browserstack"] = upload_result

            # =========================================================
            # STEP 4: Clone & Prepare YAML Repository
            # =========================================================
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 4: Clone & Prepare YAML Repository")
            self.logger.info("=" * 70)

            # Create GitHub client
            github = GitHubClient(self.config)

            # Clone repo and create branch
            repo_info = github.clone_and_prepare_branch(
                platform=params['platform'],
                app_variant=params['app_variant'],
                build_id=params['build_id']
            )

            self.logger.info(f"Repository prepared")
            self.logger.info(f"  Clone Path: {repo_info['clone_path']}")
            self.logger.info(f"  Branch: {repo_info['branch']}")
            result["steps"]["git_prepare"] = "SUCCESS"
            result["git"] = repo_info

            # Get old app ID before updating
            yaml_updater = YAMLUpdater(self.config, repo_info['clone_path'])
            old_app_id = yaml_updater.get_current_app_id(
                platform=params['platform'],
                app_variant=params['app_variant'],
                environment=params['environment'],
                build_type=params['build_type']
            )
            self.logger.info(f"  Old App ID: {old_app_id}")
            result["old_app_id"] = old_app_id

            # =========================================================
            # STEP 5: Update YAML Files
            # =========================================================
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 5: Update YAML Configuration")
            self.logger.info("=" * 70)

            yaml_files_updated = yaml_updater.update_app_id(
                platform=params['platform'],
                app_variant=params['app_variant'],
                environment=params['environment'],
                build_type=params['build_type'],
                new_app_id=upload_result['app_id'],
                version=params['version'],
                build_id=params['build_id']
            )

            self.logger.info(f"YAML files updated")
            for file_path in yaml_files_updated:
                self.logger.info(f"  - {file_path}")
            result["steps"]["yaml_update"] = "SUCCESS"
            result["yaml_files_updated"] = yaml_files_updated

            # =========================================================
            # STEP 6: Git Commit & Push
            # =========================================================
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 6: Git Commit & Push")
            self.logger.info("=" * 70)

            # Create commit message
            commit_message = (
                f"Update BrowserStack app ID for {params['platform']}/{params['app_variant']} "
                f"{params['environment']} {params['build_type']}\n\n"
                f"Build: {params['build_id']}\n"
                f"Version: {params['version']}"
            )

            # Commit and push
            commit_info = github.commit_and_push(
                repo_path=repo_info['clone_path'],
                branch_name=repo_info['branch'],
                files=yaml_files_updated,
                message=commit_message
            )

            self.logger.info(f"Changes committed and pushed")
            self.logger.info(f"  Commit SHA: {commit_info['commit_sha']}")
            self.logger.info(f"  Branch: {commit_info['branch_name']}")
            result["steps"]["git_commit"] = "SUCCESS"
            result["git"]["commit"] = commit_info

            # =========================================================
            # STEP 7: Create Pull Request
            # =========================================================
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 7: Create Pull Request")
            self.logger.info("=" * 70)

            # Create PR title
            pr_title = (
                f"[BrowserStack] Update {params['app_variant']}: "
                f"{params['platform']} {params['environment']} {params['build_type']}"
            )

            # Create PR body
            pr_body = f"""## BrowserStack App Update

### Build Information
- **Platform**: {params['platform']}
- **Application**: {params['app_variant']}
- **Environment**: {params['environment']}
- **Build Type**: {params['build_type']}
- **Version**: {params['version']}
- **Build ID**: {params['build_id']}

### App ID Change
- **Old App ID**: {old_app_id}
- **New App ID**: {upload_result['app_id']}

### Files Updated
"""
            for file_path in yaml_files_updated:
                pr_body += f"- {file_path}\n"

            pr_body += f"""
### Links
- [Source Build]({params['source_build_url']})
- [BrowserStack Dashboard](https://app-live.browserstack.com)

**Auto-generated by DevOps Automation**
"""

            # Create pull request
            pr_url = github.create_pull_request(
                title=pr_title,
                body=pr_body,
                branch=repo_info['branch'],
                labels=['browserstack', 'auto-generated']
            )

            # Parse PR number from URL for result
            pr_number = pr_url.split('/')[-1]

            pr_info = {
                'pr_url': pr_url,
                'pr_number': pr_number,
                'branch': repo_info['branch']
            }

            self.logger.info(f"Pull Request created")
            self.logger.info(f"  PR Number: #{pr_number}")
            self.logger.info(f"  PR URL: {pr_url}")
            result["steps"]["create_pr"] = "SUCCESS"
            result["pr"] = pr_info

            # =========================================================
            # STEP 8: Send Teams Notification
            # =========================================================
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 8: Send Teams Notification")
            self.logger.info("=" * 70)

            notifier = TeamsNotifier(self.config)
            notifier.send_notification(
                platform=params['platform'],
                app_variant=params['app_variant'],
                environment=params['environment'],
                build_type=params['build_type'],
                version=params['version'],
                old_app_id=old_app_id,
                new_app_id=upload_result['app_id'],
                pr_url=pr_url,
                source_build_url=params['source_build_url'],
                yaml_file=f"{params['platform']}/{params['app_variant']}.yml"
            )

            self.logger.info(f"Teams notification sent")
            result["steps"]["teams_notification"] = "SUCCESS"

            # =========================================================
            # STEP 9: Create Audit Trail
            # =========================================================
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 9: Create Audit Trail")
            self.logger.info("=" * 70)

            audit_file = create_audit_trail(
                params=params,
                artifact_info=artifact_info,
                upload_result=upload_result,
                old_app_id=old_app_id,
                pr_info=pr_info,
                yaml_files=yaml_files_updated
            )

            self.logger.info(f"Audit trail created")
            self.logger.info(f"  File: {audit_file}")
            result["steps"]["audit_trail"] = "SUCCESS"
            result["audit_file"] = audit_file

            # =========================================================
            # Final Success Result
            # =========================================================
            result["status"] = "SUCCESS"
            result["timestamp_end"] = datetime.utcnow().isoformat()

            self.logger.info("\n" + "=" * 70)
            self.logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 70)
            self.logger.info(f"PR: {pr_url}")
            self.logger.info(f"App ID: {upload_result['app_id']}")

            # Write output file if requested
            self._write_output(output_file, result)
            return result

        except Exception as e:
            # Handle errors
            self.logger.error(f"Workflow failed: {str(e)}", exc_info=True)
            result["status"] = "FAILED"
            result["error"] = str(e)
            result["timestamp_end"] = datetime.utcnow().isoformat()
            self._write_output(output_file, result)
            return result

    def _generate_custom_id(self, params: Dict[str, str]) -> str:
        """Generate custom ID for BrowserStack upload"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return (f"{params['platform']}-{params['app_variant']}-"
                f"{params['environment']}-{params['build_type']}-"
                f"{params['version']}-{timestamp}")

    def _write_output(self, output_file: Optional[str], result: Dict[str, Any]) -> None:
        """Write result to JSON output file if specified"""
        if output_file:
            try:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2)
                self.logger.info(f"Result written to: {output_file}")
            except Exception as e:
                self.logger.error(f"Failed to write output file: {e}")


def main():
    """Main entry point - parse arguments and run uploader"""
    parser = argparse.ArgumentParser(
        description="BrowserStack Artifact Uploader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py \\
    --platform android \\
    --environment production \\
    --build-type Release \\
    --app-variant agent \\
    --version 1.2.0 \\
    --build-id jenkins-1234 \\
    --source-build-url https://jenkins.example.com/job/build/123 \\
    --src-folder "\\\\192.1.6.8\\Builds\\MobileApp\\Nightly_Builds\\mainline" \\
    --config-file ../config/config.yaml \\
    --verbose
        """
    )

    # Add command-line arguments
    parser.add_argument('--platform', required=True,
                        choices=['android', 'android_hw', 'ios'],
                        help='Mobile platform')
    parser.add_argument('--environment', required=True,
                        choices=['production', 'staging'],
                        help='Target environment')
    parser.add_argument('--build-type', required=True,
                        choices=['Debug', 'Release'],
                        help='Build type/variant')
    parser.add_argument('--app-variant', required=True,
                        choices=['agent', 'retail', 'wallet'],
                        help='Application variant')
    parser.add_argument('--version', required=True,
                        help='Application version (semantic: X.Y.Z)')
    parser.add_argument('--build-id', required=True,
                        help='Build identifier (e.g., jenkins-1234)')
    parser.add_argument('--source-build-url', required=True,
                        help='Source build URL for reference')
    parser.add_argument('--src-folder', default=None,
                        help='Custom source folder path for artifacts (NFS location)')
    parser.add_argument('--config-file', default='config.yaml',
                        help='Configuration file path')
    parser.add_argument('--output-file', default=None,
                        help='Output JSON file for results')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')

    # Parse arguments
    args = parser.parse_args()

    # Create parameters dict
    params = {
        'platform': args.platform,
        'environment': args.environment,
        'build_type': args.build_type,
        'app_variant': args.app_variant,
        'version': args.version,
        'build_id': args.build_id,
        'source_build_url': args.source_build_url,
        'src_folder': args.src_folder
    }

    # Run uploader
    try:
        uploader = BrowserStackUploader(args.config_file, args.verbose)
        result = uploader.run(params, args.output_file)

        # Exit with appropriate code
        sys.exit(0 if result['status'] == 'SUCCESS' else 1)

    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
