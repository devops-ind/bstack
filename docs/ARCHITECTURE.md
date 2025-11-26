# BrowserStack Uploader - Architecture & Mind Map

## 🗺️ System Mind Map

```
BrowserStack Uploader System
│
├── 📋 ENTRY POINT
│   └── main.py
│       ├── BrowserStackUploader (Main Orchestrator)
│       └── main() function (CLI entry point)
│
├── ⚙️ CONFIGURATION & UTILITIES
│   ├── config.py
│   │   └── Config class
│   │       ├── Load YAML configuration
│   │       ├── Substitute environment variables
│   │       └── Provide typed config accessors
│   │
│   ├── logger.py
│   │   ├── ColoredFormatter class (colored console logs)
│   │   ├── setup_logger() function
│   │   └── get_logger() function
│   │
│   └── utils.py
│       ├── validate_parameters()
│       ├── create_audit_trail()
│       ├── is_valid_version()
│       ├── calculate_file_md5()
│       ├── format_bytes()
│       ├── sanitize_filename()
│       └── retry_with_backoff()
│
├── 💾 ARTIFACT MANAGEMENT
│   └── local_storage.py
│       └── LocalStorage class
│           ├── construct_artifact_path()
│           ├── validate_artifact()
│           ├── _calculate_md5()
│           ├── _read_magic_bytes()
│           └── _validate_magic_bytes()
│
├── ☁️ EXTERNAL SERVICE CLIENTS
│   ├── browserstack_client.py
│   │   └── BrowserStackClient class
│   │       ├── upload_app()
│   │       ├── get_app_details()
│   │       ├── delete_app()
│   │       └── _create_session()
│   │
│   ├── github_client.py
│   │   └── GitHubClient class
│   │       ├── clone_repository()
│   │       ├── create_branch()
│   │       ├── commit_and_push()
│   │       ├── create_pull_request()
│   │       ├── clone_and_prepare_branch()
│   │       ├── _add_pr_labels()
│   │       └── _run_git_command()
│   │
│   └── teams_notifier.py
│       └── TeamsNotifier class
│           ├── send_notification()
│           ├── _build_facts()
│           └── _create_adaptive_card()
│
├── 📝 CONFIGURATION FILES
│   └── yaml_updater.py
│       └── YAMLUpdater class
│           ├── get_current_app_id()
│           ├── update_app_id()
│           ├── _get_yaml_file_path()
│           ├── _get_shared_yaml_file_path()
│           ├── _update_yaml_file()
│           ├── _update_shared_yaml()
│           └── _write_yaml_file()
│
└── 🔧 JENKINS INTEGRATION
    ├── Jenkinsfile-DevOps-TriggerReady
    │   └── Triggered by Dev Jenkins app builds
    └── Jenkinsfile-Standard.groovy
        └── Manual or scheduled execution
```

## 🏗️ High-Level Architecture

### System Overview

The BrowserStack Uploader is an automation tool that:
1. **Reads** mobile app artifacts (APK/IPA) from NFS storage
2. **Uploads** them to BrowserStack for testing
3. **Updates** YAML configuration files in Git
4. **Creates** Pull Requests for code review
5. **Sends** Teams notifications to stakeholders

### Data Flow

```
┌─────────────────┐
│  Jenkins Job    │ (Triggers with parameters)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   main.py       │ (Entry point)
│ BrowserStack    │
│   Uploader      │
└────────┬────────┘
         │
         ├─► LocalStorage ────► NFS (Read APK/IPA)
         │
         ├─► BrowserStackClient ─► BrowserStack API (Upload)
         │
         ├─► GitHubClient ──────► GitHub (Clone, Commit, Push)
         │
         ├─► YAMLUpdater ───────► YAML Files (Update app IDs)
         │
         ├─► GitHubClient ──────► GitHub API (Create PR)
         │
         └─► TeamsNotifier ─────► MS Teams (Send notification)
```

## 📦 Class Relationships

### Dependency Graph

```
BrowserStackUploader (main.py)
    │
    ├── uses ──► Config (config.py)
    │              │
    │              └── loads ──► config.yaml
    │
    ├── uses ──► LocalStorage (local_storage.py)
    │              └── depends on ──► Config
    │
    ├── uses ──► BrowserStackClient (browserstack_client.py)
    │              └── depends on ──► Config
    │
    ├── uses ──► GitHubClient (github_client.py)
    │              └── depends on ──► Config
    │
    ├── uses ──► YAMLUpdater (yaml_updater.py)
    │              └── depends on ──► Config
    │
    └── uses ──► TeamsNotifier (teams_notifier.py)
                   └── depends on ──► Config

All classes use logger.py for logging
All classes can use utils.py for helper functions
```

## 🔄 Workflow Steps

The `BrowserStackUploader.run()` method orchestrates 9 steps:

```
Step 1: Validate Parameters
    ↓
Step 2: Validate & Read Artifact
    ↓
Step 3: Upload to BrowserStack
    ↓
Step 4: Clone & Prepare YAML Repository
    ↓
Step 5: Update YAML Files
    ↓
Step 6: Git Commit & Push
    ↓
Step 7: Create Pull Request
    ↓
Step 8: Send Teams Notification
    ↓
Step 9: Create Audit Trail
```

## 🎯 Core Design Patterns

### 1. **Configuration Management Pattern**
- Single `Config` class manages all settings
- Environment variables injected at runtime
- Typed accessors for different config sections

### 2. **Client Pattern**
- Separate client classes for each external service
- Each client encapsulates API communication
- Clients are stateless and reusable

### 3. **Orchestrator Pattern**
- `BrowserStackUploader` coordinates workflow
- Delegates specific tasks to specialized classes
- Maintains high-level workflow logic

### 4. **Dependency Injection**
- All classes receive `Config` via constructor
- Easy to test with mock configurations
- Clear dependencies

## 📊 Key Data Structures

### Parameters Dictionary
```python
params = {
    'platform': 'android',        # android, android_hw, ios
    'environment': 'production',  # production, staging
    'build_type': 'Release',      # Debug, Release
    'app_variant': 'agent',       # agent, retail, wallet
    'build_id': 'jenkins-1234',
    'source_build_url': 'https://...',
    'src_folder': '\\\\192.1.6.8\\...',  # Optional NFS path
    'version': '1.2.3'            # Optional version
}
```

### Artifact Info Dictionary
```python
artifact_info = {
    'path': '/path/to/app.apk',
    'name': 'app.apk',
    'size': 52428800,        # bytes
    'size_mb': 50.0,         # megabytes
    'md5': 'abc123...',
    'mtime': 1234567890.0,   # timestamp
    'extension': '.apk'
}
```

### Upload Result Dictionary
```python
upload_result = {
    'app_id': 'bs://abc123...',
    'app_url': 'bs://abc123...',
    'custom_id': 'android-agent-production-...',
    'timestamp': 1234567890.0,
    'response': {...}  # Full BrowserStack response
}
```

## 🔐 Configuration Structure

The system uses a YAML configuration file (`config/config.yaml`) with these sections:

- **browserstack**: API credentials and endpoints
- **local_storage**: Artifact paths and templates
- **git**: Repository settings
- **github**: API credentials
- **notifications.teams**: Teams webhook settings
- **yaml_structure**: YAML file mappings
- **logging**: Log levels and outputs
- **retry**: Retry strategy configuration

## 🚀 Entry Points

### 1. Command Line
```bash
python3 src/main.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --build-id jenkins-1234 \
  --source-build-url https://... \
  --src-folder "\\192.1.6.8\..." \
  --config-file config/config.yaml
```

### 2. Jenkins Pipeline
- `jenkins/Jenkinsfile-DevOps-TriggerReady`: Triggered by app builds
- `jenkins/Jenkinsfile-Standard.groovy`: Manual/scheduled runs

## 📝 File Organization

```
bstack/
├── config/
│   └── config.yaml           # Main configuration
├── src/
│   ├── main.py              # Entry point & orchestrator
│   ├── config.py            # Configuration management
│   ├── logger.py            # Logging setup
│   ├── utils.py             # Helper functions
│   ├── local_storage.py     # Artifact management
│   ├── browserstack_client.py  # BrowserStack API
│   ├── github_client.py     # Git & GitHub operations
│   ├── yaml_updater.py      # YAML file updates
│   └── teams_notifier.py    # Teams notifications
├── jenkins/
│   ├── Jenkinsfile-DevOps-TriggerReady
│   └── Jenkinsfile-Standard.groovy
├── tests/
│   └── (test files)
├── examples/
│   └── (example files)
└── docs/
    ├── ARCHITECTURE.md      # This file
    └── BEGINNER_GUIDE.md    # Detailed guide
```

## 🔍 Key Technical Concepts

### 1. NFS Path Handling
- Artifacts stored on network file shares
- Custom `srcFolder` parameter allows dynamic paths
- Path templates support platform-specific structures

### 2. Git Workflow
- Clone to temporary directory
- Create feature branch
- Update files, commit, push
- Create PR via GitHub API
- Cleanup temporary directory

### 3. YAML Updates
- Platform-specific YAML files
- Shared metadata file
- Nested structure: `apps[variant][env][build_type]`

### 4. Error Handling
- Comprehensive validation
- Retry logic with exponential backoff
- Detailed logging at each step
- Audit trail for compliance

## 📚 Further Reading

For detailed explanations of each component, see:
- [BEGINNER_GUIDE.md](./BEGINNER_GUIDE.md) - Step-by-step explanations
- [README.md](../README.md) - Setup and usage guide
- [JENKINS_INTEGRATION.md](./JENKINS_INTEGRATION.md) - Jenkins setup
