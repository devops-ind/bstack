# BrowserStack Uploader - Class Diagram & Relationships

## 📊 UML Class Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Config                                  │
├─────────────────────────────────────────────────────────────────┤
│ - config_path: Path                                             │
│ - config: dict                                                  │
├─────────────────────────────────────────────────────────────────┤
│ + __init__(config_path: str)                                    │
│ + get(key: str, default=None): any                              │
│ + get_required(key: str): any                                   │
│ + get_browserstack_config(): dict                               │
│ + get_git_config(): dict                                        │
│ + get_github_config(): dict                                     │
│ + get_local_storage_config(): dict                              │
│ + get_teams_config(): dict                                      │
│ + get_yaml_config(): dict                                       │
│ + get_retry_config(): dict                                      │
│ - _substitute_env_vars(obj): any                                │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              │ uses
                              │
      ┌───────────────────────┴────────────────────────┐
      │                                                 │
      │                                                 │
┌─────┴─────────────────────────────┐    ┌────────────┴──────────────────────┐
│       LocalStorage                │    │    BrowserStackClient             │
├───────────────────────────────────┤    ├───────────────────────────────────┤
│ - config: Config                  │    │ - config: Config                  │
│ - log: Logger                     │    │ - log: Logger                     │
│ - storage_config: dict            │    │ - username: str                   │
│ - src_folder: str                 │    │ - access_key: str                 │
├───────────────────────────────────┤    │ - api_endpoint: str               │
│ + __init__(config, src_folder)    │    │ - upload_timeout: int             │
│ + construct_artifact_path(...): str│   │ - session: requests.Session       │
│ + validate_artifact(path): dict   │    ├───────────────────────────────────┤
│ - _get_valid_extensions(...): list│   │ + __init__(config: Config)        │
│ - _calculate_md5(path): str       │    │ + upload_app(...): dict           │
│ - _read_magic_bytes(path): bytes  │    │ + get_app_details(app_id): dict   │
│ - _validate_magic_bytes(...): None│    │ + delete_app(app_id): bool        │
└───────────────────────────────────┘    │ - _create_session(): Session      │
                                         └───────────────────────────────────┘
      │                                                 │
      │                                                 │
      │                                                 │
┌─────┴─────────────────────────────┐    ┌────────────┴──────────────────────┐
│       GitHubClient                │    │      YAMLUpdater                  │
├───────────────────────────────────┤    ├───────────────────────────────────┤
│ - config: Config                  │    │ - config: Config                  │
│ - log: Logger                     │    │ - log: Logger                     │
│ - git_config: dict                │    │ - repo_path: Path                 │
│ - github_config: dict             │    │ - yaml_config: dict               │
├───────────────────────────────────┤    ├───────────────────────────────────┤
│ + __init__(config: Config)        │    │ + __init__(config, repo_path)     │
│ + clone_repository(): Path        │    │ + get_current_app_id(...): str    │
│ + create_branch(path, name): None │    │ + update_app_id(...): list        │
│ + commit_and_push(...): dict      │    │ - _get_yaml_file_path(...): Path  │
│ + create_pull_request(...): str   │    │ - _get_shared_yaml_file_path(): Path│
│ + clone_and_prepare_branch(...): dict│ │ - _update_yaml_file(...): None    │
│ - _add_pr_labels(...): None       │    │ - _update_shared_yaml(...): None  │
│ - _run_git_command(...): result   │    │ - _write_yaml_file(...): None     │
└───────────────────────────────────┘    └───────────────────────────────────┘
      │
      │
      │
┌─────┴─────────────────────────────┐
│       TeamsNotifier               │
├───────────────────────────────────┤
│ - config: Config                  │
│ - log: Logger                     │
│ - webhook_url: str                │
├───────────────────────────────────┤
│ + __init__(config: Config)        │
│ + send_notification(...): bool    │
│ - _build_facts(...): list         │
│ - _create_adaptive_card(...): dict│
└───────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    BrowserStackUploader                         │
│                        (Orchestrator)                           │
├─────────────────────────────────────────────────────────────────┤
│ - config: Config                                                │
│ - logger: Logger                                                │
├─────────────────────────────────────────────────────────────────┤
│ + __init__(config_file: str, verbose: bool)                     │
│ + run(params: dict, output_file: str): dict                     │
│ - _generate_custom_id(params: dict): str                        │
│ - _write_output(output_file: str, result: dict): None           │
└─────────────────────────────────────────────────────────────────┘
      │
      │ creates and uses ▼
      │
      ├── LocalStorage
      ├── BrowserStackClient
      ├── GitHubClient
      ├── YAMLUpdater
      └── TeamsNotifier
```

## 🔗 Detailed Class Relationships

### 1. Config (Foundation Class)

**Dependencies**: None (it's the foundation)

**Dependents**: All other classes

**Relationship Type**: Dependency Injection

```python
# All classes receive Config in constructor
class BrowserStackClient:
    def __init__(self, config: Config):
        self.config = config
```

**Why**: Centralized configuration management, easy testing

---

### 2. LocalStorage

**Dependencies**:
- Config (injected)
- logger (imported)

**Methods Explained**:

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| `construct_artifact_path()` | platform, environment, build_type, app_variant | str (file path) | Build full path to artifact |
| `validate_artifact()` | artifact_path | dict (metadata) | Validate and get file info |
| `_calculate_md5()` | file_path | str (checksum) | Calculate MD5 hash |
| `_validate_magic_bytes()` | extension, magic_bytes | None | Verify file type |

**Data Flow**:
```
Parameters → construct_artifact_path() → File Path
    ↓
File Path → validate_artifact() → Artifact Info Dict
```

---

### 3. BrowserStackClient

**Dependencies**:
- Config (injected)
- logger (imported)
- requests library

**Methods Explained**:

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| `upload_app()` | artifact_path, custom_id | dict (upload result) | Upload to BrowserStack |
| `get_app_details()` | app_id | dict (app details) | Get app information |
| `delete_app()` | app_id | bool | Delete app from BS |

**Data Flow**:
```
Artifact Path → upload_app() → HTTP POST → BrowserStack API
    ↓
BrowserStack Response → Parse JSON → Return app_id
```

**Retry Logic**:
```
Attempt 1 → Fail → Wait 2s
Attempt 2 → Fail → Wait 4s
Attempt 3 → Fail → Wait 8s
Attempt 4 → Success or Give Up
```

---

### 4. GitHubClient

**Dependencies**:
- Config (injected)
- logger (imported)
- subprocess (for git commands)
- requests (for GitHub API)

**Methods Explained**:

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| `clone_repository()` | None | Path (clone location) | Clone Git repo to temp dir |
| `create_branch()` | repo_path, branch_name | None | Create new Git branch |
| `commit_and_push()` | repo_path, branch, files, message | dict (commit info) | Commit and push changes |
| `create_pull_request()` | title, body, branch, labels | str (PR URL) | Create GitHub PR |

**Data Flow**:
```
clone_repository()
    ↓
Create Temp Dir → git clone → Configure Git User → Return Path
    ↓
create_branch()
    ↓
git fetch → git checkout -b → Create Branch
    ↓
commit_and_push()
    ↓
git add → git commit → git push → Return Commit SHA
    ↓
create_pull_request()
    ↓
GitHub API POST → Create PR → Return PR URL
```

---

### 5. YAMLUpdater

**Dependencies**:
- Config (injected)
- logger (imported)
- yaml library
- pathlib

**Methods Explained**:

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| `get_current_app_id()` | platform, app_variant, env, build_type | str (app_id) | Read current app ID from YAML |
| `update_app_id()` | platform, variant, env, build_type, new_id, version, build_id | list (files updated) | Update YAML with new app ID |

**YAML Navigation**:
```yaml
# File structure:
apps:
  agent:                    ← app_variant
    production:             ← environment
      Release:              ← build_type
        app_id: bs://...    ← target
        version: 1.2.3
        build_id: jenkins-123
```

**Data Flow**:
```
Parameters → Construct Path to YAML File
    ↓
Read YAML → Parse to Dict
    ↓
Navigate: dict['apps'][variant][env][build_type]
    ↓
Update app_id
    ↓
Write YAML → Return Files Updated
```

---

### 6. TeamsNotifier

**Dependencies**:
- Config (injected)
- logger (imported)
- requests (for webhook)
- datetime

**Methods Explained**:

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| `send_notification()` | platform, variant, env, build_type, version, old_id, new_id, pr_url, source_url, yaml_file | bool | Send Teams message |
| `_build_facts()` | All notification parameters | list (facts array) | Build message facts |
| `_create_adaptive_card()` | All notification parameters | dict (card JSON) | Create Teams card |

**Data Flow**:
```
Parameters → _build_facts() → Facts List
    ↓
Facts + Parameters → _create_adaptive_card() → Adaptive Card JSON
    ↓
Card JSON → HTTP POST → Teams Webhook → Send Message
```

---

### 7. BrowserStackUploader (Main Orchestrator)

**Dependencies**:
- Config (created internally)
- ALL other classes (created as needed)
- logger (imported)
- utils (imported)

**Methods Explained**:

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| `run()` | params dict, output_file | result dict | Execute full workflow |
| `_generate_custom_id()` | params dict | str (custom ID) | Generate unique identifier |
| `_write_output()` | output_file, result | None | Write JSON result file |

**Workflow**:
```python
def run(params, output_file):
    # STEP 1: Validate
    validate_parameters(params)

    # STEP 2: Read Artifact
    storage = LocalStorage(config, params['src_folder'])
    artifact_info = storage.validate_artifact(artifact_path)

    # STEP 3: Upload
    bs_client = BrowserStackClient(config)
    upload_result = bs_client.upload_app(artifact_path, custom_id)

    # STEP 4: Clone Repo
    github = GitHubClient(config)
    repo_info = github.clone_and_prepare_branch(platform, variant, build_id)

    # STEP 5: Update YAML
    yaml_updater = YAMLUpdater(config, repo_info['clone_path'])
    files_updated = yaml_updater.update_app_id(...)

    # STEP 6: Commit & Push
    commit_info = github.commit_and_push(repo_path, branch, files, message)

    # STEP 7: Create PR
    pr_url = github.create_pull_request(title, body, branch, labels)

    # STEP 8: Send Notification
    notifier = TeamsNotifier(config)
    notifier.send_notification(...)

    # STEP 9: Audit Trail
    audit_file = create_audit_trail(...)

    return result
```

---

## 🎯 Design Patterns Used

### 1. Dependency Injection Pattern

**What**: Pass dependencies via constructor instead of creating them inside

**Example**:
```python
# ❌ Bad: Hard-coded dependency
class BrowserStackClient:
    def __init__(self):
        self.config = Config('config.yaml')  # Hard to test!

# ✅ Good: Injected dependency
class BrowserStackClient:
    def __init__(self, config):
        self.config = config  # Easy to test with mock!
```

**Benefits**:
- Easy to test (pass mock objects)
- Flexible (different configs for different environments)
- Clear dependencies (constructor shows what's needed)

---

### 2. Orchestrator Pattern

**What**: One class coordinates multiple workers

**Example**:
```python
class BrowserStackUploader:  # Orchestrator
    def run(self, params):
        # Coordinates these workers:
        storage = LocalStorage(config)
        bs_client = BrowserStackClient(config)
        github = GitHubClient(config)
        yaml_updater = YAMLUpdater(config)
        notifier = TeamsNotifier(config)

        # Orchestrates the workflow
        artifact = storage.validate_artifact(...)
        result = bs_client.upload_app(...)
        # ... etc
```

**Benefits**:
- Clear workflow
- Separation of concerns
- Easy to modify workflow

---

### 3. Client Pattern

**What**: Separate client classes for each external service

**Example**:
```python
# Each service has its own client
BrowserStackClient  → Talks to BrowserStack API
GitHubClient       → Talks to GitHub API & Git
TeamsNotifier      → Talks to Teams Webhook
```

**Benefits**:
- Encapsulation (API details hidden)
- Reusability (use clients anywhere)
- Easy to mock for testing

---

### 4. Configuration Pattern

**What**: Centralize all settings in one place

**Example**:
```python
# One Config class for all settings
config = Config('config.yaml')

# Different sections
bs_config = config.get_browserstack_config()
git_config = config.get_git_config()
teams_config = config.get_teams_config()
```

**Benefits**:
- Single source of truth
- Easy to change settings
- Environment-specific configs

---

## 📦 Module Dependencies

```
main.py
    ├── depends on → config.py
    ├── depends on → logger.py
    ├── depends on → utils.py
    ├── depends on → local_storage.py
    ├── depends on → browserstack_client.py
    ├── depends on → github_client.py
    ├── depends on → yaml_updater.py
    └── depends on → teams_notifier.py

local_storage.py
    ├── depends on → config.py
    └── depends on → logger.py

browserstack_client.py
    ├── depends on → config.py
    └── depends on → logger.py

github_client.py
    ├── depends on → config.py
    └── depends on → logger.py

yaml_updater.py
    ├── depends on → config.py
    └── depends on → logger.py

teams_notifier.py
    ├── depends on → config.py
    └── depends on → logger.py

utils.py
    └── depends on → logger.py

logger.py
    └── depends on → (none - foundation)

config.py
    └── depends on → (none - foundation)
```

---

## 🔄 Object Lifecycle

### During Execution

```python
# 1. Config is created first
config = Config('config/config.yaml')

# 2. Logger is set up
logger = setup_logger(log_level)

# 3. Main orchestrator is created
uploader = BrowserStackUploader(config_file, verbose)
    # Inside: config is loaded again (or passed)

# 4. For each workflow step, clients are created:
storage = LocalStorage(config, src_folder)        # Step 2
bs_client = BrowserStackClient(config)            # Step 3
github = GitHubClient(config)                     # Step 4
yaml_updater = YAMLUpdater(config, repo_path)     # Step 5
notifier = TeamsNotifier(config)                  # Step 8

# 5. After workflow completes, objects are destroyed
# Temporary directories are cleaned up
# Connections are closed
```

---

## 📊 Data Flow Through Classes

```
┌──────────────────┐
│  Command Line    │
│  or Jenkins      │
└────────┬─────────┘
         │ params dict
         ▼
┌──────────────────────────────┐
│  BrowserStackUploader.run()  │
└────────┬─────────────────────┘
         │
         ├─► LocalStorage.construct_artifact_path(params)
         │       └─► returns: artifact_path (str)
         │
         ├─► LocalStorage.validate_artifact(artifact_path)
         │       └─► returns: artifact_info (dict)
         │
         ├─► BrowserStackClient.upload_app(artifact_path, custom_id)
         │       └─► returns: upload_result (dict with app_id)
         │
         ├─► GitHubClient.clone_and_prepare_branch(platform, variant, build_id)
         │       └─► returns: repo_info (dict with clone_path, branch)
         │
         ├─► YAMLUpdater.get_current_app_id(platform, variant, env, build_type)
         │       └─► returns: old_app_id (str)
         │
         ├─► YAMLUpdater.update_app_id(platform, variant, env, build_type, new_app_id, ...)
         │       └─► returns: files_updated (list)
         │
         ├─► GitHubClient.commit_and_push(repo_path, branch, files, message)
         │       └─► returns: commit_info (dict)
         │
         ├─► GitHubClient.create_pull_request(title, body, branch, labels)
         │       └─► returns: pr_url (str)
         │
         ├─► TeamsNotifier.send_notification(platform, variant, env, ...)
         │       └─► returns: success (bool)
         │
         └─► utils.create_audit_trail(params, artifact_info, upload_result, ...)
                 └─► returns: audit_file (str)
```

---

## 🎓 Summary

This architecture demonstrates:

1. **Separation of Concerns**: Each class has one responsibility
2. **Dependency Injection**: Dependencies passed via constructors
3. **Orchestration**: Main class coordinates workflow
4. **Client Pattern**: Separate clients for external services
5. **Configuration Management**: Centralized settings
6. **Error Handling**: Try/except at each step
7. **Logging**: Comprehensive logging throughout
8. **Modularity**: Can replace/test components independently

The system is **production-ready**, **maintainable**, and **testable**.
