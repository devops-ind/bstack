#!/usr/bin/env python3
"""
GitHub Client Module
=====================
This module handles Git and GitHub operations:
1. Clone repositories
2. Create branches
3. Commit and push changes
4. Create pull requests via GitHub API

Key Concepts:
- Temporary directories: Clone into temp folder for each run
- Authentication: Uses GitHub token for API calls
- Git commands: Uses subprocess to run git commands
"""

import subprocess
import tempfile
from pathlib import Path
from logger import get_logger
import requests


class GitHubClient:
    """
    Client for GitHub Git and API operations

    Methods:
    - clone_repository(): Clone a repo to temporary directory
    - create_branch(): Create and checkout a new branch
    - commit_and_push(): Commit changes and push to remote
    - create_pull_request(): Create PR via GitHub API
    """

    def __init__(self, config):
        """
        Initialize GitHub client

        Args:
            config: Config object with Git and GitHub settings
        """
        self.config = config
        self.log = get_logger(__name__)
        self.git_config = config.get_git_config()
        self.github_config = config.get_github_config()

    def clone_repository(self):
        """
        Clone repository to temporary directory

        Process:
        1. Create temporary directory
        2. Clone repository with --depth 1 (shallow clone for speed)
        3. Configure git user name and email

        Returns:
            Path: Path to cloned repository

        Raises:
            subprocess.CalledProcessError: If clone fails
        """
        self.log.info(f"Cloning repository: {self.git_config['repo_url']}")

        try:
            # Create temporary directory for clone
            temp_dir = tempfile.mkdtemp(prefix='yaml-config-')
            repo_path = Path(temp_dir)

            # Prepare repository URL with authentication
            repo_url = self.git_config['repo_url']

            # Insert GitHub token into URL for authentication
            if 'github.com' in repo_url and self.github_config.get('token'):
                # Format: https://oauth2:TOKEN@github.com/org/repo.git
                repo_url = repo_url.replace(
                    'https://github.com',
                    f"https://oauth2:{self.github_config['token']}@github.com"
                )

            # Clone repository
            self._run_git_command(
                ['git', 'clone', '--depth', '1', repo_url, str(repo_path)],
                cwd=temp_dir
            )

            # Configure git user name
            self._run_git_command(
                ['git', 'config', 'user.name', self.git_config['user_name']],
                cwd=str(repo_path)
            )

            # Configure git user email
            self._run_git_command(
                ['git', 'config', 'user.email', self.git_config['user_email']],
                cwd=str(repo_path)
            )

            self.log.info(f"Repository cloned to: {repo_path}")
            return repo_path

        except subprocess.CalledProcessError as e:
            self.log.error(f"Failed to clone repository: {e.stderr}")
            raise

    def create_branch(self, repo_path, branch_name):
        """
        Create new git branch

        Process:
        1. Fetch latest from origin
        2. Create new branch
        3. Checkout the new branch

        Args:
            repo_path (Path): Path to repository
            branch_name (str): Name for new branch

        Raises:
            subprocess.CalledProcessError: If git commands fail
        """
        self.log.info(f"Creating branch: {branch_name}")

        try:
            # Fetch latest from remote
            self._run_git_command(
                ['git', 'fetch', 'origin'],
                cwd=str(repo_path)
            )

            # Create and checkout new branch
            self._run_git_command(
                ['git', 'checkout', '-b', branch_name],
                cwd=str(repo_path)
            )

            self.log.info(f"Branch created: {branch_name}")

        except subprocess.CalledProcessError as e:
            self.log.error(f"Failed to create branch: {e.stderr}")
            raise

    def commit_and_push(self, repo_path, branch_name, files, message):
        """
        Commit changes and push to remote

        Process:
        1. Stage files (git add)
        2. Commit with message (git commit)
        3. Get commit SHA
        4. Push to origin (git push)

        Args:
            repo_path (Path): Path to repository
            branch_name (str): Branch name to push to
            files (list): List of file paths to commit
            message (str): Commit message

        Returns:
            dict: Commit information (SHA, branch, message)

        Raises:
            subprocess.CalledProcessError: If git commands fail
        """
        self.log.info(f"Committing changes: {message}")

        try:
            # Stage all specified files
            for file_path in files:
                self._run_git_command(
                    ['git', 'add', file_path],
                    cwd=str(repo_path)
                )

            # Commit with message
            self._run_git_command(
                ['git', 'commit', '-m', message],
                cwd=str(repo_path)
            )

            # Get commit SHA (short version)
            commit_sha = self._run_git_command(
                ['git', 'rev-parse', 'HEAD'],
                cwd=str(repo_path),
                capture=True
            ).strip()

            # Push branch to origin
            self._run_git_command(
                ['git', 'push', 'origin', branch_name],
                cwd=str(repo_path)
            )

            self.log.info(f"Changes pushed: {commit_sha}")

            return {
                'commit_sha': commit_sha,
                'branch_name': branch_name,
                'branch': branch_name,
                'message': message
            }

        except subprocess.CalledProcessError as e:
            self.log.error(f"Failed to commit/push: {e.stderr}")
            raise

    def create_pull_request(self, title, body, branch, labels=None):
        """
        Create pull request via GitHub API

        Process:
        1. Call GitHub API to create PR
        2. Optionally add labels

        Args:
            title (str): PR title
            body (str): PR description
            branch (str): Source branch name
            labels (list): Optional labels to add

        Returns:
            str: PR URL

        Raises:
            requests.exceptions.RequestException: If API call fails
        """
        self.log.info(f"Creating pull request: {title}")

        try:
            # Get credentials from config
            github_token = self.github_config['token']
            org = self.github_config['org']
            repo = self.github_config['repo']
            default_branch = self.git_config['default_branch']

            # GitHub API endpoint for creating PRs
            url = f"https://api.github.com/repos/{org}/{repo}/pulls"

            # Set up authentication header
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }

            # Prepare PR payload
            payload = {
                'title': title,
                'body': body,
                'head': branch,  # Source branch
                'base': default_branch,  # Target branch (usually 'main')
                'draft': False
            }

            # Send POST request to create PR
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            # Parse response
            pr_data = response.json()
            pr_number = pr_data['number']
            pr_url = pr_data['html_url']

            # Add labels if provided
            if labels:
                self._add_pr_labels(github_token, org, repo, pr_number, labels)

            self.log.info(f"PR created: {pr_url}")
            return pr_url

        except requests.exceptions.RequestException as e:
            self.log.error(f"Failed to create PR: {e}")
            raise

    def _add_pr_labels(self, token, org, repo, pr_number, labels):
        """
        Add labels to pull request

        Args:
            token (str): GitHub API token
            org (str): Organization name
            repo (str): Repository name
            pr_number (int): PR number
            labels (list): Labels to add
        """
        self.log.debug(f"Adding labels to PR: {labels}")

        try:
            # GitHub API endpoint for PR labels
            url = f"https://api.github.com/repos/{org}/{repo}/issues/{pr_number}/labels"

            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }

            # Send POST request to add labels
            response = requests.post(url, json=labels, headers=headers)
            response.raise_for_status()
            self.log.debug(f"Labels added: {labels}")

        except requests.exceptions.RequestException as e:
            # Don't fail if labels can't be added
            self.log.warning(f"Failed to add labels: {e}")

    def clone_and_prepare_branch(self, platform, app_variant, build_id):
        """
        Clone repository and prepare branch based on workflow configuration

        Supports two workflows:
        1. PR workflow (create_pr: true): Creates feature branch
        2. Direct commit (create_pr: false): Checks out target branch

        Args:
            platform (str): android, android_hw, or ios
            app_variant (str): agent, retail, wallet
            build_id (str): Build identifier

        Returns:
            dict: Repository info (clone_path, branch, create_pr)
        """
        # Clone repository
        clone_path = self.clone_repository()

        # Check workflow configuration
        create_pr = self.git_config.get('create_pr', True)

        if create_pr:
            # Create feature branch for PR workflow
            branch_name = f"browserstack-update/{platform}/{app_variant}/{build_id}"
            self.create_branch(clone_path, branch_name)
            self.log.info(f"Created feature branch: {branch_name}")
        else:
            # Checkout target branch for direct commit workflow
            branch_name = self.git_config.get('target_branch', 'main')
            self._checkout_existing_branch(clone_path, branch_name)
            self.log.info(f"Checked out target branch: {branch_name}")

        return {
            'clone_path': clone_path,
            'branch': branch_name,
            'create_pr': create_pr
        }

    def _checkout_existing_branch(self, repo_path, branch_name):
        """
        Checkout an existing branch and pull latest changes

        This is used for direct commit workflow.

        Args:
            repo_path (Path): Path to repository
            branch_name (str): Branch to checkout
        """
        self.log.info(f"Checking out existing branch: {branch_name}")

        try:
            # Fetch latest changes
            self._run_git_command(
                ['git', 'fetch', 'origin'],
                cwd=str(repo_path)
            )

            # Checkout the branch
            self._run_git_command(
                ['git', 'checkout', branch_name],
                cwd=str(repo_path)
            )

            # Pull latest changes
            self._run_git_command(
                ['git', 'pull', 'origin', branch_name],
                cwd=str(repo_path)
            )

            self.log.info(f"Branch checked out and updated: {branch_name}")

        except subprocess.CalledProcessError as e:
            self.log.error(f"Failed to checkout branch: {e.stderr}")
            raise

    def _run_git_command(self, cmd, cwd, capture=False):
        """
        Run git command using subprocess

        Args:
            cmd (list): Command to run (e.g., ['git', 'status'])
            cwd (str): Working directory
            capture (bool): If True, return stdout; if False, return result object

        Returns:
            result or str: Command result or stdout if capture=True

        Raises:
            subprocess.CalledProcessError: If command fails
        """
        self.log.debug(f"Running: {' '.join(cmd)}")

        try:
            # Run command
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,  # Return strings instead of bytes
                check=True  # Raise error if command fails
            )

            # Return stdout if capture requested, otherwise result
            if capture:
                return result.stdout

            return result

        except subprocess.CalledProcessError as e:
            # Log error and re-raise
            error_msg = f"Command failed: {' '.join(cmd)}\nError: {e.stderr}"
            self.log.error(error_msg)
            raise
