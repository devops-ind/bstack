# BrowserStack Uploader - Beginner's Guide

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [What This System Does](#what-this-system-does)
3. [Core Concepts](#core-concepts)
4. [Class-by-Class Breakdown](#class-by-class-breakdown)
5. [Step-by-Step Workflow](#step-by-step-workflow)
6. [Configuration Explained](#configuration-explained)
7. [Common Scenarios](#common-scenarios)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Introduction

This system automates the process of uploading mobile app builds (Android APK files and iOS IPA files) to BrowserStack, a cloud testing platform. It then updates configuration files and notifies the team.

### Why do we need this?

When developers build a new version of a mobile app, testers need access to it on BrowserStack to run tests. Instead of manually:
1. Finding the app file on the network
2. Uploading it to BrowserStack
3. Updating configuration files
4. Notifying the team

This system does all of that automatically!

---

## 🚀 What This System Does

### The Big Picture

```
1. FIND APP → 2. UPLOAD → 3. UPDATE CONFIGS → 4. CREATE PR → 5. NOTIFY TEAM
```

### Detailed Flow

1. **Find the App File**: Locates the APK or IPA file on the network drive (NFS)
2. **Validate the File**: Checks that the file is valid and readable
3. **Upload to BrowserStack**: Sends the file to BrowserStack's cloud
4. **Get App ID**: BrowserStack gives us a unique ID (like `bs://abc123...`)
5. **Clone Git Repository**: Downloads the configuration repository
6. **Update YAML Files**: Replaces old app ID with new one
7. **Commit Changes**: Saves the changes to Git
8. **Create Pull Request**: Opens a PR on GitHub for review
9. **Send Notification**: Posts a message to Microsoft Teams
10. **Create Audit Trail**: Records everything that happened

---

## 🧠 Core Concepts

### 1. Classes and Objects

Think of a **class** as a blueprint and an **object** as the actual thing built from that blueprint.

```python
# Class = Blueprint for a car
class Car:
    def __init__(self, color):
        self.color = color

    def drive(self):
        print(f"Driving the {self.color} car!")

# Object = Actual car built from blueprint
my_car = Car("red")
my_car.drive()  # Prints: "Driving the red car!"
```

### 2. Dependency Injection

Instead of creating objects inside a class, we "inject" (pass) them in:

```python
# ❌ Bad: Creates dependency inside
class BrowserStackClient:
    def __init__(self):
        self.config = Config('config.yaml')  # Hard to test!

# ✅ Good: Dependency injected
class BrowserStackClient:
    def __init__(self, config):
        self.config = config  # Easy to test with mock config!
```

### 3. Configuration Management

All settings are stored in one YAML file instead of scattered throughout the code:

```yaml
browserstack:
  username: ${BROWSERSTACK_USER}  # From environment variable
  access_key: ${BROWSERSTACK_ACCESS_KEY}

local_storage:
  artifact_base_path: "/shared/mobileapp/builds"
```

### 4. Logging

Instead of using `print()`, we use a logger that:
- Adds timestamps
- Shows log levels (DEBUG, INFO, WARNING, ERROR)
- Can save to files
- Adds colors for readability

```python
# ❌ Bad
print("Starting upload...")

# ✅ Good
logger.info("Starting upload...")
# Output: [2025-01-15 10:30:45] INFO    main: Starting upload...
```

---

## 📚 Class-by-Class Breakdown

### 1. Config (`config.py`)

**Purpose**: Manages all application settings

**What it does**:
- Reads `config.yaml` file
- Replaces `${VARIABLE_NAME}` with actual environment variable values
- Provides methods to get specific configuration sections

**Key Methods**:
```python
config = Config('config/config.yaml')

# Get any value using dot notation
username = config.get('browserstack.username')

# Get required value (raises error if missing)
api_key = config.get_required('browserstack.access_key')

# Get typed config sections
bs_config = config.get_browserstack_config()
git_config = config.get_git_config()
```

**Example**:
```python
# config.yaml contains:
# browserstack:
#   username: ${BROWSERSTACK_USER}

# Environment has:
# BROWSERSTACK_USER=john@example.com

config = Config('config.yaml')
username = config.get('browserstack.username')
print(username)  # Prints: john@example.com
```

**Why it's useful**: All settings in one place, easy to change without modifying code.

---

### 2. Logger (`logger.py`)

**Purpose**: Provides colored, formatted logging

**What it does**:
- Creates colored console output
- Can also write to log files
- Adds timestamps automatically

**Key Components**:

1. **ColoredFormatter**: Adds ANSI color codes
   - Green = INFO
   - Yellow = WARNING
   - Red = ERROR

2. **setup_logger()**: Configures the logger
3. **get_logger(name)**: Gets a logger for a specific module

**Example**:
```python
from logger import setup_logger, get_logger

# Setup in main
setup_logger(log_level=logging.INFO)

# Get logger in any module
log = get_logger(__name__)
log.info("✅ This is green!")
log.warning("⚠️ This is yellow!")
log.error("❌ This is red!")
```

---

### 3. Utils (`utils.py`)

**Purpose**: Helper functions used across the application

**Key Functions**:

#### validate_parameters(params)
Checks that all required parameters are present and valid.

```python
params = {
    'platform': 'android',
    'environment': 'production',
    'build_type': 'Release',
    # ... more params
}

errors = validate_parameters(params)
if errors:
    print("Validation failed:", errors)
```

#### create_audit_trail(...)
Creates a JSON file recording what happened.

```python
audit_file = create_audit_trail(
    params=params,
    artifact_info=artifact_info,
    upload_result=upload_result,
    # ... more data
)
# Creates: audit-trail-android-agent-jenkins-123.json
```

#### is_valid_version(version)
Checks if version follows semantic versioning (X.Y.Z).

```python
is_valid_version("1.2.3")        # True
is_valid_version("1.2.3-beta")   # True
is_valid_version("1.2")          # False
is_valid_version("1.2.3.4")      # False
```

#### retry_with_backoff(func, max_attempts=3)
Retries a function with increasing delays if it fails.

```python
def upload_file():
    # Might fail due to network
    requests.post(url, data=data)

# Automatically retries: wait 2s, 4s, 8s between attempts
retry_with_backoff(upload_file, max_attempts=3)
```

---

### 4. LocalStorage (`local_storage.py`)

**Purpose**: Manages reading and validating app artifact files

**What it does**:
- Constructs file paths based on parameters
- Validates files (exists, readable, correct type)
- Calculates MD5 checksums
- Verifies file signatures (magic bytes)

**Key Methods**:

#### __init__(config, src_folder=None)
```python
storage = LocalStorage(config, src_folder="\\\\192.1.6.8\\Builds")
```

#### construct_artifact_path(platform, environment, build_type, app_variant)
Builds the full path to the artifact file.

```python
path = storage.construct_artifact_path(
    platform='android',
    environment='production',
    build_type='Release',
    app_variant='agent'
)
# Returns: \\192.1.6.8\Builds\...\agent\build\app-release.apk
```

#### validate_artifact(artifact_path)
Validates the file and returns metadata.

```python
info = storage.validate_artifact('/path/to/app.apk')
# Returns:
# {
#     'path': '/path/to/app.apk',
#     'name': 'app.apk',
#     'size': 52428800,
#     'size_mb': 50.0,
#     'md5': 'abc123...',
#     'extension': '.apk'
# }
```

**How it validates**:
1. ✅ File exists?
2. ✅ File is readable?
3. ✅ Extension is valid (.apk, .ipa, .aab)?
4. ✅ Magic bytes match file type? (APK/IPA start with 'PK')
5. ✅ Calculate MD5 checksum

**Magic Bytes Explained**:
Every file type has a unique signature in its first few bytes:
- APK/IPA files start with `PK` (they're ZIP files)
- PNG files start with `89 50 4E 47`
- JPEG files start with `FF D8 FF`

---

### 5. BrowserStackClient (`browserstack_client.py`)

**Purpose**: Handles all communication with BrowserStack API

**What it does**:
- Uploads app files to BrowserStack
- Gets app details
- Deletes apps
- Handles authentication
- Implements retry logic

**Key Methods**:

#### upload_app(artifact_path, custom_id, ...)
Uploads an app file to BrowserStack.

```python
client = BrowserStackClient(config)

result = client.upload_app(
    artifact_path='/path/to/app.apk',
    custom_id='android-agent-prod-20250115',
    app_variant='agent',
    environment='production'
)

# Returns:
# {
#     'app_id': 'bs://abc123...',
#     'app_url': 'bs://abc123...',
#     'custom_id': 'android-agent-prod-20250115',
#     'timestamp': 1234567890.0
# }
```

**How upload works**:
1. Opens file in binary mode
2. Creates HTTP POST request with:
   - File data
   - Custom ID
   - Authentication (username + access key)
3. Sends to BrowserStack API
4. Parses JSON response
5. Extracts app ID (like `bs://abc123...`)

**Retry Strategy**:
Automatically retries on:
- Network errors
- Rate limiting (HTTP 429)
- Server errors (HTTP 500, 502, 503, 504)

Uses exponential backoff: 1s → 2s → 4s → 8s

---

### 6. GitHubClient (`github_client.py`)

**Purpose**: Manages Git and GitHub operations

**What it does**:
- Clones repositories
- Creates branches
- Commits and pushes changes
- Creates pull requests via API

**Key Methods**:

#### clone_repository()
Clones a Git repo to a temporary directory.

```python
client = GitHubClient(config)
repo_path = client.clone_repository()
# Returns: Path('/tmp/yaml-config-abc123')
```

**What happens**:
1. Creates temporary directory
2. Runs `git clone --depth 1 <url>`
3. Configures git user name and email
4. Returns path to cloned repo

#### create_branch(repo_path, branch_name)
Creates a new Git branch.

```python
client.create_branch(
    repo_path=repo_path,
    branch_name='browserstack-update/android/agent/build-123'
)
```

**What happens**:
1. `git fetch origin`
2. `git checkout -b browserstack-update/...`

#### commit_and_push(repo_path, branch_name, files, message)
Commits files and pushes to GitHub.

```python
commit_info = client.commit_and_push(
    repo_path=repo_path,
    branch_name='feature-branch',
    files=['config.yml', 'shared.yml'],
    message='Update BrowserStack app ID'
)

# Returns:
# {
#     'commit_sha': 'abc123...',
#     'branch_name': 'feature-branch',
#     'message': 'Update BrowserStack app ID'
# }
```

**What happens**:
1. `git add <files>`
2. `git commit -m <message>`
3. `git rev-parse HEAD` (get commit SHA)
4. `git push origin <branch>`

#### create_pull_request(title, body, branch, labels=[])
Creates a PR using GitHub API.

```python
pr_url = client.create_pull_request(
    title='[BrowserStack] Update agent: android production Release',
    body='## Details\n- Updated app ID\n- Build: 123',
    branch='feature-branch',
    labels=['browserstack', 'auto-generated']
)
# Returns: 'https://github.com/org/repo/pull/456'
```

**What happens**:
1. Calls GitHub API: `POST /repos/{org}/{repo}/pulls`
2. Authenticates with token
3. Creates PR from feature branch to main
4. Optionally adds labels
5. Returns PR URL

---

### 7. YAMLUpdater (`yaml_updater.py`)

**Purpose**: Updates YAML configuration files with new app IDs

**What it does**:
- Reads existing YAML files
- Updates app IDs in nested structures
- Writes files back safely
- Updates both app-specific and shared metadata files

**Key Methods**:

#### get_current_app_id(platform, app_variant, environment, build_type)
Retrieves the current app ID from YAML.

```python
updater = YAMLUpdater(config, repo_path)

old_id = updater.get_current_app_id(
    platform='android',
    app_variant='agent',
    environment='production',
    build_type='Release'
)
# Returns: 'bs://old123...' or 'NOT_SET'
```

#### update_app_id(platform, app_variant, environment, build_type, new_app_id, version, build_id)
Updates app ID in YAML files.

```python
files_updated = updater.update_app_id(
    platform='android',
    app_variant='agent',
    environment='production',
    build_type='Release',
    new_app_id='bs://new456...',
    version='1.2.3',
    build_id='jenkins-123'
)

# Returns: ['browserstack_ag_Android.yml', 'shared.yml']
```

**YAML Structure**:
```yaml
apps:
  agent:
    production:
      Release:
        app_id: bs://abc123...
        app_url: bs://abc123...
        build_id: jenkins-123
        version: 1.2.3
        updated_at: 2025-01-15T10:30:00Z
```

**What it updates**:
1. **App-specific file**: `browserstack_ag_Android.yml`
   - Updates the app_id
   - Adds metadata (version, build_id, timestamp)

2. **Shared metadata file**: `shared.yml`
   - Records what was updated
   - Tracks update history

---

### 8. TeamsNotifier (`teams_notifier.py`)

**Purpose**: Sends formatted notifications to Microsoft Teams

**What it does**:
- Creates adaptive card messages
- Posts to Teams webhook
- Includes all relevant information

**Key Methods**:

#### send_notification(platform, app_variant, environment, ...)
Sends a Teams notification.

```python
notifier = TeamsNotifier(config)

success = notifier.send_notification(
    platform='android',
    app_variant='agent',
    environment='production',
    build_type='Release',
    version='1.2.3',
    old_app_id='bs://old123...',
    new_app_id='bs://new456...',
    pr_url='https://github.com/org/repo/pull/123',
    source_build_url='https://jenkins.example.com/build/456',
    yaml_file='browserstack_ag_Android.yml'
)
```

**Message Format** (Adaptive Card):
```
🤖 BrowserStack Update - agent
PRODUCTION | Release

Platform:     android
Application:  agent
Environment:  production
Build Type:   Release
Version:      1.2.3
Old App ID:   bs://old123...
New App ID:   bs://new456...
Updated At:   2025-01-15T10:30:00Z

[View Pull Request] [Source Build]
```

---

### 9. BrowserStackUploader (`main.py`)

**Purpose**: Main orchestrator that coordinates the entire workflow

**What it does**:
- Receives parameters from command line or Jenkins
- Executes all 9 steps in sequence
- Handles errors and logging
- Creates results and audit trails

**Key Methods**:

#### run(params, output_file=None)
Executes the complete workflow.

```python
uploader = BrowserStackUploader('config/config.yaml', verbose=True)

result = uploader.run(
    params={
        'platform': 'android',
        'environment': 'production',
        'build_type': 'Release',
        'app_variant': 'agent',
        'build_id': 'jenkins-123',
        'source_build_url': 'https://...',
        'src_folder': '\\\\192.1.6.8\\...'
    },
    output_file='upload-result.json'
)

# Returns:
# {
#     'status': 'SUCCESS',
#     'timestamp': '2025-01-15T10:30:00Z',
#     'params': {...},
#     'steps': {
#         'validate': 'SUCCESS',
#         'artifact_validation': 'SUCCESS',
#         'browserstack_upload': 'SUCCESS',
#         ...
#     },
#     'browserstack': {...},
#     'pr': {...}
# }
```

---

## 🔄 Step-by-Step Workflow

Let's walk through what happens when you run the uploader:

### Step 1: Validate Parameters

```python
# Checks all required parameters
validation_errors = validate_parameters(params)
if validation_errors:
    raise ValueError(f"Invalid parameters: {validation_errors}")
```

**Validates**:
- ✅ Platform is 'android', 'android_hw', or 'ios'
- ✅ Environment is 'production' or 'staging'
- ✅ Build type is 'Debug' or 'Release'
- ✅ App variant is 'agent', 'retail', or 'wallet'
- ✅ URLs start with http:// or https://

### Step 2: Validate & Read Artifact

```python
# Create storage manager
storage = LocalStorage(config, src_folder=params['src_folder'])

# Build artifact path
artifact_path = storage.construct_artifact_path(
    platform='android',
    environment='production',
    build_type='Release',
    app_variant='agent'
)
# Path: \\192.1.6.8\...\agent\build\app-release.apk

# Validate file
artifact_info = storage.validate_artifact(artifact_path)
```

### Step 3: Upload to BrowserStack

```python
# Create BrowserStack client
bs_client = BrowserStackClient(config)

# Generate custom ID
custom_id = "android-agent-production-Release-20250115103000"

# Upload
upload_result = bs_client.upload_app(
    artifact_path=artifact_info['path'],
    custom_id=custom_id
)
# Result: {'app_id': 'bs://abc123...', ...}
```

### Step 4: Clone & Prepare YAML Repository

```python
# Create GitHub client
github = GitHubClient(config)

# Clone and create branch
repo_info = github.clone_and_prepare_branch(
    platform='android',
    app_variant='agent',
    build_id='jenkins-123'
)
# Result: {
#     'clone_path': '/tmp/yaml-config-xyz',
#     'branch': 'browserstack-update/android/agent/jenkins-123'
# }
```

### Step 5: Update YAML Files

```python
# Create YAML updater
yaml_updater = YAMLUpdater(config, repo_info['clone_path'])

# Get old app ID
old_app_id = yaml_updater.get_current_app_id(
    platform='android',
    app_variant='agent',
    environment='production',
    build_type='Release'
)

# Update with new app ID
files_updated = yaml_updater.update_app_id(
    platform='android',
    app_variant='agent',
    environment='production',
    build_type='Release',
    new_app_id='bs://abc123...',
    version='1.2.3',
    build_id='jenkins-123'
)
# Result: ['browserstack_ag_Android.yml', 'shared.yml']
```

### Step 6: Git Commit & Push

```python
# Create commit message
message = """Update BrowserStack app ID for android/agent production Release

Build: jenkins-123
Version: 1.2.3"""

# Commit and push
commit_info = github.commit_and_push(
    repo_path=repo_info['clone_path'],
    branch_name=repo_info['branch'],
    files=files_updated,
    message=message
)
```

### Step 7: Create Pull Request

```python
# Create PR
pr_url = github.create_pull_request(
    title='[BrowserStack] Update agent: android production Release',
    body="""
## BrowserStack App Update

### Build Information
- Platform: android
- Application: agent
- Environment: production
- Build Type: Release
- Build ID: jenkins-123

### App ID Change
- Old: bs://old123...
- New: bs://abc123...

### Files Updated
- browserstack_ag_Android.yml
- shared.yml
    """,
    branch=repo_info['branch'],
    labels=['browserstack', 'auto-generated']
)
# Result: 'https://github.com/org/repo/pull/456'
```

### Step 8: Send Teams Notification

```python
# Send Teams notification
notifier = TeamsNotifier(config)
notifier.send_notification(
    platform='android',
    app_variant='agent',
    environment='production',
    build_type='Release',
    version='1.2.3',
    old_app_id=old_app_id,
    new_app_id='bs://abc123...',
    pr_url=pr_url,
    source_build_url=params['source_build_url'],
    yaml_file='browserstack_ag_Android.yml'
)
```

### Step 9: Create Audit Trail

```python
# Create audit trail
audit_file = create_audit_trail(
    params=params,
    artifact_info=artifact_info,
    upload_result=upload_result,
    old_app_id=old_app_id,
    pr_info={'pr_url': pr_url, 'pr_number': '456'},
    yaml_files=files_updated
)
# Creates: audit-trail-android-agent-jenkins-123.json
```

---

## ⚙️ Configuration Explained

### config.yaml Structure

```yaml
# BrowserStack API Settings
browserstack:
  username: ${BROWSERSTACK_USER}      # From environment variable
  access_key: ${BROWSERSTACK_ACCESS_KEY}
  api_endpoint: "https://api-cloud.browserstack.com/app-automate/upload"
  upload_timeout: 300  # 5 minutes

# Where to find app files
local_storage:
  artifact_base_path: "/shared/mobileapp/builds/mainline"

  # Path templates use placeholders
  path_templates:
    android: "{base}/{platform}/{environment}/{build_type}/Android/enterprise/{app_variant}/build/app-{build_type_lower}.apk"
    ios: "{base}/{platform}/{environment}/{build_type}/Ios/enterprise/{app_variant}/App.ipa"

  # Valid file extensions
  accepted_extensions:
    android: [".apk", ".aab"]
    ios: [".ipa"]

# Git repository settings
git:
  repo_url: "https://github.com/org/yaml-configs.git"
  default_branch: "main"
  user_name: "DevOps Automation"
  user_email: "devops@company.com"

# GitHub API settings
github:
  token: ${GITHUB_TOKEN}
  org: "your-org"
  repo: "yaml-configs"

# Teams notification settings
notifications:
  teams:
    webhook_url: ${TEAMS_WEBHOOK_URL}

# YAML file structure
yaml_structure:
  yaml_files:
    android:
      agent: "browserstack_ag_Android.yml"
      retail: "browserstack_re_Android.yml"
    ios:
      agent: "browserstackiOS_ag.yml"
  shared_file: "shared.yml"

# Retry settings
retry:
  max_attempts: 3
  initial_delay: 2        # seconds
  backoff_factor: 2       # multiply delay by this
```

### Path Template Placeholders

When constructing artifact paths, these placeholders are replaced:

- `{base}`: Base path or custom `src_folder`
- `{platform}`: android, android_hw, or ios
- `{environment}`: production or staging
- `{build_type}`: Debug or Release
- `{build_type_lower}`: debug or release (lowercase)
- `{app_variant}`: agent, retail, or wallet

**Example**:
```python
template = "{base}/{platform}/{environment}/{build_type}/Android/enterprise/{app_variant}/build/app-{build_type_lower}.apk"

# With values:
# base = "\\192.1.6.8\Builds"
# platform = "android"
# environment = "production"
# build_type = "Release"
# app_variant = "agent"

# Result:
# \\192.1.6.8\Builds\android\production\Release\Android\enterprise\agent\build\app-release.apk
```

---

## 🎬 Common Scenarios

### Scenario 1: Upload APK from Default Location

```bash
python3 src/main.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --build-id jenkins-123 \
  --source-build-url https://jenkins.example.com/job/build/123 \
  --config-file config/config.yaml
```

Uses `artifact_base_path` from config.

### Scenario 2: Upload from Custom NFS Location

```bash
python3 src/main.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --build-id jenkins-123 \
  --source-build-url https://jenkins.example.com/job/build/123 \
  --src-folder "\\192.1.6.8\Builds\MobileApp\Nightly_Builds\mainline" \
  --config-file config/config.yaml
```

Overrides base path with `--src-folder`.

### Scenario 3: Upload iOS IPA

```bash
python3 src/main.py \
  --platform ios \
  --environment staging \
  --build-type Debug \
  --app-variant retail \
  --build-id jenkins-456 \
  --source-build-url https://jenkins.example.com/job/build/456 \
  --config-file config/config.yaml
```

Uses iOS path template and validates .ipa file.

### Scenario 4: Debug Mode with Verbose Logging

```bash
python3 src/main.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --build-id jenkins-123 \
  --source-build-url https://jenkins.example.com/job/build/123 \
  --config-file config/config.yaml \
  --verbose
```

Shows DEBUG level logs for troubleshooting.

---

## 🔧 Troubleshooting

### Problem: "Artifact not found"

**Cause**: File doesn't exist at expected path

**Solution**:
1. Check `construct_artifact_path()` output
2. Verify NFS mount is accessible
3. Check `src_folder` parameter if using custom path
4. Verify path template in config matches actual structure

### Problem: "Invalid BrowserStack response"

**Cause**: Upload failed or API returned error

**Solution**:
1. Check BrowserStack credentials
2. Verify internet connectivity
3. Check artifact file is valid (not corrupted)
4. Review BrowserStack dashboard for quota/limits

### Problem: "Git push failed"

**Cause**: Authentication or network issue

**Solution**:
1. Verify `GITHUB_TOKEN` environment variable
2. Check token has push permissions
3. Verify repository URL is correct
4. Check branch name doesn't already exist

### Problem: "YAML update failed"

**Cause**: File structure mismatch

**Solution**:
1. Check `yaml_structure.yaml_files` mapping
2. Verify YAML file exists in repository
3. Review file structure (should match expected nesting)
4. Check file permissions

### Problem: "Teams notification not sent"

**Cause**: Webhook URL invalid or Teams service down

**Solution**:
1. Verify `TEAMS_WEBHOOK_URL` environment variable
2. Test webhook manually with curl
3. Check Teams channel permissions
4. This is non-critical, workflow continues anyway

---

## 📖 Learning Path

### For Complete Beginners

1. **Start with**: `logger.py` and `utils.py`
   - Learn about logging
   - Understand helper functions

2. **Then**: `config.py`
   - Learn configuration management
   - Understand environment variables

3. **Next**: `local_storage.py`
   - Learn file operations
   - Understand path construction

4. **After that**: Individual clients
   - `browserstack_client.py`: Learn HTTP APIs
   - `github_client.py`: Learn Git operations
   - `yaml_updater.py`: Learn YAML manipulation

5. **Finally**: `main.py`
   - See how everything fits together
   - Understand the orchestration pattern

### Key Programming Concepts You'll Learn

1. **Object-Oriented Programming**: Classes and objects
2. **Dependency Injection**: Passing dependencies via constructor
3. **Error Handling**: Try/except blocks, raising exceptions
4. **HTTP APIs**: Making REST API calls
5. **File I/O**: Reading, writing, validating files
6. **Git Operations**: Cloning, committing, pushing
7. **Configuration Management**: YAML, environment variables
8. **Logging**: Structured logging vs print statements
9. **Retry Logic**: Exponential backoff for resilience
10. **Subprocess**: Running shell commands from Python

---

## 🎓 Summary

This BrowserStack Uploader is a **real-world automation system** that demonstrates:

- **Clean Architecture**: Separation of concerns
- **Dependency Injection**: Testable, modular code
- **Error Handling**: Robust, resilient operation
- **Configuration Management**: Flexible, environment-aware
- **API Integration**: BrowserStack, GitHub, Teams
- **Git Automation**: Clone, commit, push, PR creation
- **Audit Trails**: Compliance and debugging

By understanding this codebase, you'll learn patterns and practices used in professional software development.

Happy coding! 🚀
