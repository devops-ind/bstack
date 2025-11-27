#!/usr/bin/env python3
"""
Simple BrowserStack Uploader - Beginner-Friendly Version
=========================================================
This is a simplified version using only FUNCTIONS (no classes).
Perfect for learning Python!

What this script does:
1. Reads app files (APK/IPA) from network storage
2. Uploads them to BrowserStack
3. Updates configuration files in Git
4. Creates a Pull Request
5. Sends a Teams notification

Usage:
    python3 simple_uploader.py \\
        --platform android \\
        --environment production \\
        --build-type Release \\
        --app-variant agent \\
        --build-id jenkins-123 \\
        --source-build-url https://jenkins.example.com/build/123
"""

import os
import sys
import json
import yaml
import hashlib
import argparse
import requests
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime


# =============================================================================
# 1. CONFIGURATION FUNCTIONS
# =============================================================================

def load_config(config_file='config/config.yaml'):
    """
    Load configuration from YAML file

    This reads the config file and replaces environment variables.
    For example: ${BROWSERSTACK_USER} becomes the actual username.

    Args:
        config_file (str): Path to config file

    Returns:
        dict: Configuration dictionary
    """
    print(f"📋 Loading configuration from {config_file}...")

    # Read the YAML file
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Replace environment variables
    config = replace_env_vars(config)

    print("✅ Configuration loaded successfully")
    return config


def replace_env_vars(obj):
    """
    Replace ${VAR_NAME} with actual environment variable values

    This function is recursive - it can handle nested dictionaries and lists.

    Args:
        obj: Can be dict, list, string, or other

    Returns:
        Object with environment variables replaced
    """
    if isinstance(obj, dict):
        # For dictionaries, process each key-value pair
        return {key: replace_env_vars(value) for key, value in obj.items()}

    elif isinstance(obj, list):
        # For lists, process each item
        return [replace_env_vars(item) for item in obj]

    elif isinstance(obj, str):
        # For strings, check if it's an environment variable
        if obj.startswith('${') and obj.endswith('}'):
            var_name = obj[2:-1]  # Remove ${ and }
            value = os.getenv(var_name)
            if value is None:
                raise ValueError(f"❌ Environment variable not set: {var_name}")
            return value
        return obj

    else:
        # For other types (numbers, booleans), return as-is
        return obj


# =============================================================================
# 2. FILE OPERATIONS
# =============================================================================

def build_artifact_path(config, platform, environment, build_type, app_variant, src_folder=None):
    """
    Build the full path to the artifact file

    This uses a template from config and replaces placeholders.
    Example template: "{base}/{platform}/{environment}/{build_type}/Android/enterprise/{app_variant}/build/app-{build_type_lower}.apk"

    Args:
        config (dict): Configuration dictionary
        platform (str): android, android_hw, or ios
        environment (str): production or staging
        build_type (str): Debug or Release
        app_variant (str): agent, retail, or wallet
        src_folder (str): Optional custom source folder

    Returns:
        str: Full path to artifact
    """
    print(f"🔍 Building artifact path for {platform}/{app_variant}/{environment}/{build_type}...")

    # Get the path template for this platform
    templates = config['local_storage']['path_templates']
    template = templates.get(platform)

    if not template:
        raise ValueError(f"❌ No path template for platform: {platform}")

    # Use custom folder or default base path
    if src_folder:
        base_path = src_folder
    else:
        base_path = config['local_storage']['artifact_base_path']

    # Replace all placeholders in the template
    artifact_path = template.format(
        base=base_path,
        platform=platform,
        environment=environment,
        build_type=build_type,
        build_type_lower=build_type.lower(),
        app_variant=app_variant
    )

    print(f"📁 Artifact path: {artifact_path}")
    return artifact_path


def validate_artifact_file(artifact_path):
    """
    Validate that the artifact file exists and is valid

    Checks:
    - File exists
    - File is readable
    - File has correct extension
    - File signature (magic bytes) is correct

    Args:
        artifact_path (str): Path to artifact

    Returns:
        dict: File information (path, size, md5, etc.)
    """
    print(f"🔍 Validating artifact: {artifact_path}")

    path = Path(artifact_path)

    # Check 1: Does file exist?
    if not path.exists():
        raise FileNotFoundError(f"❌ Artifact not found: {artifact_path}")

    # Check 2: Is file readable?
    if not os.access(artifact_path, os.R_OK):
        raise PermissionError(f"❌ Cannot read artifact: {artifact_path}")

    # Check 3: Get file size
    file_size = path.stat().st_size
    file_size_mb = round(file_size / (1024 * 1024), 2)

    # Check 4: Validate file extension
    extension = path.suffix
    if extension not in ['.apk', '.aab', '.ipa']:
        raise ValueError(f"❌ Invalid file extension: {extension}")

    # Check 5: Check magic bytes (first 2 bytes should be 'PK' for APK/IPA)
    with open(artifact_path, 'rb') as f:
        magic_bytes = f.read(2)

    if magic_bytes != b'PK':
        raise ValueError(f"❌ Invalid file signature. Expected 'PK', got {magic_bytes}")

    # Check 6: Calculate MD5 checksum
    md5_hash = calculate_md5(artifact_path)

    artifact_info = {
        'path': artifact_path,
        'name': path.name,
        'size': file_size,
        'size_mb': file_size_mb,
        'md5': md5_hash,
        'extension': extension
    }

    print(f"✅ Artifact validated: {path.name} ({file_size_mb} MB)")
    return artifact_info


def calculate_md5(file_path):
    """
    Calculate MD5 checksum of a file

    Reads file in chunks for memory efficiency.

    Args:
        file_path (str): Path to file

    Returns:
        str: MD5 hash in hexadecimal
    """
    md5 = hashlib.md5()

    # Read file in 8KB chunks
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            md5.update(chunk)

    return md5.hexdigest()


# =============================================================================
# 3. BROWSERSTACK OPERATIONS
# =============================================================================

def upload_to_browserstack(config, artifact_path, custom_id):
    """
    Upload artifact to BrowserStack

    This sends the APK/IPA file to BrowserStack's API and gets back an app ID.

    Args:
        config (dict): Configuration dictionary
        artifact_path (str): Path to artifact file
        custom_id (str): Custom identifier for this upload

    Returns:
        dict: Upload result with app_id
    """
    print(f"☁️  Uploading to BrowserStack...")

    # Get BrowserStack credentials from config
    username = config['browserstack']['username']
    access_key = config['browserstack']['access_key']
    api_endpoint = config['browserstack']['api_endpoint']
    timeout = config['browserstack']['upload_timeout']

    try:
        # Open file in binary mode
        with open(artifact_path, 'rb') as f:
            # Prepare the upload
            files = {'file': f}
            data = {'custom_id': custom_id}

            # Send POST request to BrowserStack
            response = requests.post(
                api_endpoint,
                files=files,
                data=data,
                auth=(username, access_key),  # Basic authentication
                timeout=timeout
            )

            # Check if request was successful
            response.raise_for_status()

            # Parse the JSON response
            result = response.json()

            # Extract the app ID
            app_id = result['app_url']

            print(f"✅ Upload successful! App ID: {app_id}")

            return {
                'app_id': app_id,
                'app_url': app_id,
                'custom_id': custom_id,
                'timestamp': datetime.utcnow().isoformat()
            }

    except requests.exceptions.RequestException as e:
        print(f"❌ Upload failed: {e}")
        raise


# =============================================================================
# 4. GIT OPERATIONS
# =============================================================================

def clone_git_repo(config):
    """
    Clone the YAML configuration repository

    Clones to a temporary directory for safety.

    Args:
        config (dict): Configuration dictionary

    Returns:
        str: Path to cloned repository
    """
    print("📦 Cloning Git repository...")

    # Get Git settings from config
    repo_url = config['git']['repo_url']
    user_name = config['git']['user_name']
    user_email = config['git']['user_email']
    github_token = config['github']['token']

    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='yaml-config-')
    repo_path = Path(temp_dir)

    # Add GitHub token to URL for authentication
    if 'github.com' in repo_url:
        repo_url = repo_url.replace(
            'https://github.com',
            f'https://oauth2:{github_token}@github.com'
        )

    try:
        # Clone the repository
        run_command(['git', 'clone', '--depth', '1', repo_url, str(repo_path)])

        # Configure git user
        run_command(['git', 'config', 'user.name', user_name], cwd=str(repo_path))
        run_command(['git', 'config', 'user.email', user_email], cwd=str(repo_path))

        print(f"✅ Repository cloned to: {repo_path}")
        return str(repo_path)

    except subprocess.CalledProcessError as e:
        print(f"❌ Git clone failed: {e}")
        raise


def create_git_branch(repo_path, branch_name):
    """
    Create a new Git branch

    Args:
        repo_path (str): Path to repository
        branch_name (str): Name for new branch
    """
    print(f"🌿 Creating branch: {branch_name}")

    try:
        # Fetch latest changes
        run_command(['git', 'fetch', 'origin'], cwd=repo_path)

        # Create and checkout new branch
        run_command(['git', 'checkout', '-b', branch_name], cwd=repo_path)

        print(f"✅ Branch created: {branch_name}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Branch creation failed: {e}")
        raise


def commit_and_push(repo_path, branch_name, files, message):
    """
    Commit changes and push to remote

    Args:
        repo_path (str): Path to repository
        branch_name (str): Branch to push to
        files (list): List of files to commit
        message (str): Commit message

    Returns:
        str: Commit SHA
    """
    print("💾 Committing and pushing changes...")

    try:
        # Stage files
        for file_path in files:
            run_command(['git', 'add', file_path], cwd=repo_path)

        # Commit
        run_command(['git', 'commit', '-m', message], cwd=repo_path)

        # Get commit SHA
        result = run_command(['git', 'rev-parse', 'HEAD'], cwd=repo_path, capture=True)
        commit_sha = result.stdout.strip()

        # Push to remote
        run_command(['git', 'push', 'origin', branch_name], cwd=repo_path)

        print(f"✅ Changes pushed! Commit: {commit_sha[:8]}")
        return commit_sha

    except subprocess.CalledProcessError as e:
        print(f"❌ Git commit/push failed: {e}")
        raise


def run_command(cmd, cwd=None, capture=False):
    """
    Run a shell command

    This is a helper function to run git commands.

    Args:
        cmd (list): Command to run (e.g., ['git', 'status'])
        cwd (str): Working directory
        capture (bool): Whether to capture output

    Returns:
        CompletedProcess or None
    """
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True
    )

    if capture:
        return result
    return None


# =============================================================================
# 5. YAML FILE OPERATIONS
# =============================================================================

def update_yaml_files(config, repo_path, platform, app_variant, environment, build_type, new_app_id, version, build_id):
    """
    Update YAML configuration files with new app ID

    This updates two files:
    1. App-specific file (e.g., browserstack_ag_Android.yml)
    2. Shared metadata file (shared.yml)

    Args:
        config (dict): Configuration dictionary
        repo_path (str): Path to repository
        platform (str): android, android_hw, or ios
        app_variant (str): agent, retail, or wallet
        environment (str): production or staging
        build_type (str): Debug or Release
        new_app_id (str): New BrowserStack app ID
        version (str): App version (optional)
        build_id (str): Build identifier

    Returns:
        list: List of files updated
    """
    print("📝 Updating YAML files...")

    repo = Path(repo_path)
    files_updated = []
    timestamp = datetime.utcnow().isoformat() + 'Z'

    # 1. Update app-specific YAML file
    yaml_filename = get_yaml_filename(config, platform, app_variant)
    yaml_file = repo / yaml_filename

    # Read existing content or create new
    if yaml_file.exists():
        with open(yaml_file, 'r') as f:
            content = yaml.safe_load(f) or {}
    else:
        content = {}

    # Ensure nested structure exists
    if 'apps' not in content:
        content['apps'] = {}
    if app_variant not in content['apps']:
        content['apps'][app_variant] = {}
    if environment not in content['apps'][app_variant]:
        content['apps'][app_variant][environment] = {}

    # Update the app ID and metadata
    app_data = {
        'app_id': new_app_id,
        'app_url': new_app_id,
        'build_id': build_id,
        'build_type': build_type,
        'environment': environment,
        'updated_at': timestamp
    }

    # Add version if provided
    if version:
        app_data['version'] = version

    content['apps'][app_variant][environment][build_type] = app_data

    # Write file back
    with open(yaml_file, 'w') as f:
        yaml.dump(content, f, default_flow_style=False, sort_keys=False)

    files_updated.append(yaml_filename)
    print(f"✅ Updated: {yaml_filename}")

    # 2. Update shared.yml
    shared_file = repo / 'shared.yml'

    if shared_file.exists():
        with open(shared_file, 'r') as f:
            shared_content = yaml.safe_load(f) or {}
    else:
        shared_content = {}

    # Add update record
    if 'updates' not in shared_content:
        shared_content['updates'] = []

    shared_content['updates'].append({
        'platform': platform,
        'app_variant': app_variant,
        'environment': environment,
        'build_type': build_type,
        'build_id': build_id,
        'timestamp': timestamp
    })

    # Write shared file
    with open(shared_file, 'w') as f:
        yaml.dump(shared_content, f, default_flow_style=False, sort_keys=False)

    files_updated.append('shared.yml')
    print(f"✅ Updated: shared.yml")

    return files_updated


def get_yaml_filename(config, platform, app_variant):
    """
    Get the YAML filename for a platform/variant combination

    Args:
        config (dict): Configuration dictionary
        platform (str): android, android_hw, or ios
        app_variant (str): agent, retail, or wallet

    Returns:
        str: Filename (e.g., 'browserstack_ag_Android.yml')
    """
    yaml_files = config['yaml_structure']['yaml_files']

    # Map full variant names to abbreviations
    variant_map = {
        'agent': 'ag',
        'retail': 're',
        'wallet': 'ag'  # Default to ag
    }

    variant_key = variant_map.get(app_variant, app_variant)

    if platform in yaml_files and variant_key in yaml_files[platform]:
        return yaml_files[platform][variant_key]
    else:
        # Fallback
        return f"{platform}_{app_variant}.yml"


# =============================================================================
# 6. GITHUB API OPERATIONS
# =============================================================================

def create_pull_request(config, title, body, branch):
    """
    Create a Pull Request on GitHub

    Uses GitHub's REST API to create a PR.

    Args:
        config (dict): Configuration dictionary
        title (str): PR title
        body (str): PR description
        branch (str): Source branch name

    Returns:
        str: PR URL
    """
    print("🔀 Creating Pull Request...")

    # Get GitHub settings
    github_token = config['github']['token']
    org = config['github']['org']
    repo = config['github']['repo']
    default_branch = config['git']['default_branch']

    # GitHub API endpoint
    url = f"https://api.github.com/repos/{org}/{repo}/pulls"

    # Prepare headers
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Prepare payload
    payload = {
        'title': title,
        'body': body,
        'head': branch,
        'base': default_branch,
        'draft': False
    }

    try:
        # Send POST request
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # Parse response
        pr_data = response.json()
        pr_url = pr_data['html_url']
        pr_number = pr_data['number']

        print(f"✅ Pull Request created: #{pr_number}")
        print(f"🔗 URL: {pr_url}")

        return pr_url

    except requests.exceptions.RequestException as e:
        print(f"❌ PR creation failed: {e}")
        raise


# =============================================================================
# 7. TEAMS NOTIFICATION
# =============================================================================

def send_teams_notification(config, platform, app_variant, environment, build_type, version, old_app_id, new_app_id, pr_url, source_build_url):
    """
    Send notification to Microsoft Teams

    Posts a formatted message card to Teams webhook.

    Args:
        config (dict): Configuration dictionary
        platform (str): android, android_hw, or ios
        app_variant (str): agent, retail, or wallet
        environment (str): production or staging
        build_type (str): Debug or Release
        version (str): App version (optional)
        old_app_id (str): Previous app ID
        new_app_id (str): New app ID
        pr_url (str): Pull Request URL
        source_build_url (str): Source build URL
    """
    print("📢 Sending Teams notification...")

    # Get webhook URL
    webhook_url = config['notifications']['teams']['webhook_url']

    # Choose emoji based on platform
    platform_emoji = {
        'android': '🤖',
        'android_hw': '📱',
        'ios': '🍎'
    }.get(platform, '📱')

    # Build facts list
    facts = [
        {'name': 'Platform:', 'value': f'`{platform}`'},
        {'name': 'Application:', 'value': f'`{app_variant}`'},
        {'name': 'Environment:', 'value': f'`{environment}`'},
        {'name': 'Build Type:', 'value': f'`{build_type}`'}
    ]

    if version:
        facts.append({'name': 'Version:', 'value': f'`{version}`'})

    facts.extend([
        {'name': 'Old App ID:', 'value': f'`{old_app_id}`'},
        {'name': 'New App ID:', 'value': f'`{new_app_id}`'},
        {'name': 'Updated At:', 'value': datetime.utcnow().isoformat() + 'Z'}
    ])

    # Create Teams card
    card = {
        '@type': 'MessageCard',
        '@context': 'https://schema.org/extensions',
        'summary': f'BrowserStack Update - {platform}/{app_variant}',
        'themeColor': '0078D4',
        'sections': [{
            'activityTitle': f'{platform_emoji} BrowserStack Update - {app_variant}',
            'activitySubtitle': f'{environment.upper()} | {build_type}',
            'facts': facts
        }],
        'potentialAction': [
            {
                '@type': 'OpenUri',
                'name': 'View Pull Request',
                'targets': [{'os': 'default', 'uri': pr_url}]
            },
            {
                '@type': 'OpenUri',
                'name': 'Source Build',
                'targets': [{'os': 'default', 'uri': source_build_url}]
            }
        ]
    }

    try:
        # Send to Teams
        response = requests.post(webhook_url, json=card, timeout=10)
        response.raise_for_status()

        print("✅ Teams notification sent!")

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Teams notification failed (non-critical): {e}")


# =============================================================================
# 8. MAIN WORKFLOW
# =============================================================================

def run_upload_workflow(params, config_file='config/config.yaml'):
    """
    Execute the complete upload workflow

    This is the main function that coordinates all steps.

    Args:
        params (dict): Parameters dictionary
        config_file (str): Path to config file

    Returns:
        dict: Result dictionary
    """
    print("\n" + "="*70)
    print("🚀 BrowserStack Uploader - Simple Version")
    print("="*70 + "\n")

    try:
        # STEP 1: Load Configuration
        print("📋 STEP 1: Load Configuration")
        print("-" * 70)
        config = load_config(config_file)
        print()

        # STEP 2: Build & Validate Artifact Path
        print("📦 STEP 2: Build & Validate Artifact")
        print("-" * 70)
        artifact_path = build_artifact_path(
            config,
            params['platform'],
            params['environment'],
            params['build_type'],
            params['app_variant'],
            params.get('src_folder')
        )

        artifact_info = validate_artifact_file(artifact_path)
        print()

        # STEP 3: Upload to BrowserStack
        print("☁️  STEP 3: Upload to BrowserStack")
        print("-" * 70)
        custom_id = f"{params['platform']}-{params['app_variant']}-{params['environment']}-{params['build_type']}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        upload_result = upload_to_browserstack(config, artifact_path, custom_id)
        print()

        # STEP 4: Clone Repository
        print("📦 STEP 4: Clone Git Repository")
        print("-" * 70)
        repo_path = clone_git_repo(config)
        print()

        # STEP 5: Create Branch
        print("🌿 STEP 5: Create Git Branch")
        print("-" * 70)
        branch_name = f"browserstack-update/{params['platform']}/{params['app_variant']}/{params['build_id']}"
        create_git_branch(repo_path, branch_name)
        print()

        # STEP 6: Update YAML Files
        print("📝 STEP 6: Update YAML Files")
        print("-" * 70)
        files_updated = update_yaml_files(
            config,
            repo_path,
            params['platform'],
            params['app_variant'],
            params['environment'],
            params['build_type'],
            upload_result['app_id'],
            params.get('version'),
            params['build_id']
        )
        print()

        # STEP 7: Commit & Push
        print("💾 STEP 7: Commit & Push Changes")
        print("-" * 70)
        commit_message = f"Update BrowserStack app ID for {params['platform']}/{params['app_variant']} {params['environment']} {params['build_type']}\n\nBuild: {params['build_id']}"
        if params.get('version'):
            commit_message += f"\nVersion: {params['version']}"

        commit_sha = commit_and_push(repo_path, branch_name, files_updated, commit_message)
        print()

        # STEP 8: Create Pull Request
        print("🔀 STEP 8: Create Pull Request")
        print("-" * 70)
        pr_title = f"[BrowserStack] Update {params['app_variant']}: {params['platform']} {params['environment']} {params['build_type']}"

        pr_body = f"""## BrowserStack App Update

### Build Information
- **Platform**: {params['platform']}
- **Application**: {params['app_variant']}
- **Environment**: {params['environment']}
- **Build Type**: {params['build_type']}
- **Build ID**: {params['build_id']}"""

        if params.get('version'):
            pr_body += f"\n- **Version**: {params['version']}"

        pr_body += f"""

### App ID Change
- **New App ID**: {upload_result['app_id']}

### Files Updated
"""
        for file in files_updated:
            pr_body += f"- {file}\n"

        pr_body += f"""
### Links
- [Source Build]({params['source_build_url']})
- [BrowserStack Dashboard](https://app-live.browserstack.com)

**Auto-generated by Simple Uploader**
"""

        pr_url = create_pull_request(config, pr_title, pr_body, branch_name)
        print()

        # STEP 9: Send Teams Notification
        print("📢 STEP 9: Send Teams Notification")
        print("-" * 70)
        send_teams_notification(
            config,
            params['platform'],
            params['app_variant'],
            params['environment'],
            params['build_type'],
            params.get('version'),
            'NOT_SET',  # We don't read old ID in simple version
            upload_result['app_id'],
            pr_url,
            params['source_build_url']
        )
        print()

        # SUCCESS!
        print("="*70)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"📱 App ID: {upload_result['app_id']}")
        print(f"🔗 PR URL: {pr_url}")
        print("="*70 + "\n")

        return {
            'status': 'SUCCESS',
            'app_id': upload_result['app_id'],
            'pr_url': pr_url,
            'commit_sha': commit_sha
        }

    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ WORKFLOW FAILED: {str(e)}")
        print("="*70 + "\n")
        raise


# =============================================================================
# 9. COMMAND LINE INTERFACE
# =============================================================================

def main():
    """
    Main entry point for command line usage
    """
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='Simple BrowserStack Uploader (Functions Only)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Add arguments
    parser.add_argument('--platform', required=True,
                        choices=['android', 'android_hw', 'ios'],
                        help='Mobile platform')
    parser.add_argument('--environment', required=True,
                        choices=['production', 'staging'],
                        help='Target environment')
    parser.add_argument('--build-type', required=True,
                        choices=['Debug', 'Release'],
                        help='Build type')
    parser.add_argument('--app-variant', required=True,
                        choices=['agent', 'retail', 'wallet'],
                        help='Application variant')
    parser.add_argument('--build-id', required=True,
                        help='Build identifier')
    parser.add_argument('--source-build-url', required=True,
                        help='Source build URL')
    parser.add_argument('--version', default=None,
                        help='Application version (optional)')
    parser.add_argument('--src-folder', default=None,
                        help='Custom source folder (NFS path)')
    parser.add_argument('--config-file', default='config/config.yaml',
                        help='Configuration file path')

    # Parse arguments
    args = parser.parse_args()

    # Build parameters dictionary
    params = {
        'platform': args.platform,
        'environment': args.environment,
        'build_type': args.build_type,
        'app_variant': args.app_variant,
        'build_id': args.build_id,
        'source_build_url': args.source_build_url,
        'version': args.version,
        'src_folder': args.src_folder
    }

    # Run the workflow
    try:
        result = run_upload_workflow(params, args.config_file)
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
