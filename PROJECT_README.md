# BrowserStack Artifact Uploader - Organized Project Guide

A beginner-friendly Python automation system for uploading mobile apps to BrowserStack.

## 🎯 What This Project Does

Automates uploading mobile app builds (APK, IPA) to BrowserStack with these steps:

1. **Validate** parameters (platform, version, etc.)
2. **Check** that artifact files exist and are valid
3. **Upload** to BrowserStack API (with automatic retries)
4. **Clone** YAML configuration repository
5. **Update** YAML files with new app IDs
6. **Commit** changes to git
7. **Create** pull request on GitHub (for review)
8. **Notify** team via Microsoft Teams (with rich card)
9. **Log** everything in audit trail (for compliance)

**Result**: What takes 2+ hours manually now takes 5-10 minutes! ⚡

## 📁 New Project Structure

```
bstack/
├── src/                          # Python source code
│   ├── main.py                   # Entry point - START HERE
│   ├── config.py                 # Configuration loading
│   ├── logger.py                 # Colored logging
│   ├── local_storage.py          # Artifact validation
│   ├── browserstack_client.py    # BrowserStack API calls
│   ├── yaml_updater.py           # Updates YAML files
│   ├── github_client.py          # Git/GitHub operations
│   ├── teams_notifier.py         # Teams notifications
│   └── utils.py                  # Helper functions
│
├── config/                       # Configuration
│   └── config.yaml               # Settings (credentials, paths)
│
├── jenkins/                      # CI/CD Pipeline files
│   ├── Jenkinsfile               # Kubernetes variant
│   ├── Jenkinsfile-Docker        # Docker variant (easy to use)
│   └── Jenkinsfile-Shell         # Shell script variant
│
├── docs/                         # Documentation
│   ├── SETUP.md                  # Installation guide
│   ├── CONFIGURATION.md          # Config file guide
│   ├── USAGE.md                  # How to run
│   └── TROUBLESHOOTING.md        # Common issues
│
├── examples/                     # Learning examples
│   ├── basic_example.py          # Simple usage
│   └── advanced_example.py       # Advanced features
│
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore patterns
└── PROJECT_README.md             # This file
```

## 🚀 Quick Start (5 Minutes)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export BROWSERSTACK_USER="your_username"
export BROWSERSTACK_ACCESS_KEY="your_key"
export GITHUB_TOKEN="your_token"
export TEAMS_WEBHOOK_URL="https://..."
```

### 3. Edit Configuration
```bash
# Edit file with your settings
nano config/config.yaml
```

### 4. Run
```bash
python3 src/main.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --version 1.2.0 \
  --build-id jenkins-1234 \
  --source-build-url https://jenkins.example.com/build/123 \
  --config-file config/config.yaml \
  --verbose
```

## 📚 Understanding the Code (For Beginners)

### Key Concept: Modules

Each Python file (`*.py`) is a **module** that does one job:

| Module | What It Does | Good For Learning |
|--------|-------------|-------------------|
| `config.py` | Loads YAML config & replaces `${VAR}` | File reading, environment variables |
| `logger.py` | Colored console logging | Decorators, formatting |
| `local_storage.py` | Validates artifact files (APK/IPA) | File operations, checksums |
| `browserstack_client.py` | Calls BrowserStack API | HTTP requests, JSON, error handling |
| `github_client.py` | Git commands & GitHub API | Subprocess, API calls |
| `yaml_updater.py` | Reads/writes YAML files | YAML parsing, nested dicts |
| `teams_notifier.py` | Sends Teams notifications | HTTP POST, JSON structures |
| `utils.py` | Helper functions | Validation, retry logic |
| `main.py` | Orchestrates everything | Control flow, error handling |

### Learning Paths

**Path 1: File Operations** (Start here if you like working with files)
1. Read `src/config.py` - Loading YAML files
2. Read `src/local_storage.py` - Validating files, calculating MD5
3. Read `src/yaml_updater.py` - Reading/writing YAML

**Path 2: API Integration** (Start here if you like web services)
1. Read `src/browserstack_client.py` - HTTP uploads
2. Read `src/github_client.py` - Git + API calls
3. Read `src/teams_notifier.py` - Webhook POSTs

**Path 3: Main Flow** (Start here if you want to understand everything)
1. Read `src/main.py` - The orchestrator (9 workflow steps)
2. Read all other modules to see how they fit together

## 🔧 Configuration Explained

The `config/config.yaml` file has 6 main sections:

```yaml
# 1. BrowserStack credentials and API settings
browserstack:
  username: ${BROWSERSTACK_USER}      # From environment variable
  access_key: ${BROWSERSTACK_ACCESS_KEY}
  api_endpoint: "https://api-cloud.browserstack.com/..."
  upload_timeout: 300                 # 5 minutes

# 2. Where to find artifact files
local_storage:
  artifact_base_path: "/shared/builds/mainline"
  path_templates:
    android: "{base}/{platform}/{environment}/{build_type}/app.apk"
    ios: "{base}/{platform}/{environment}/{build_type}/app.ipa"
  accepted_extensions:
    android: [".apk", ".aab"]
    ios: [".ipa"]

# 3. Git repository settings
git:
  repo_url: "https://github.com/org/yaml-configs.git"
  default_branch: "main"
  user_name: "DevOps Automation"
  user_email: "devops@company.com"

# 4. GitHub API settings
github:
  token: ${GITHUB_TOKEN}
  org: "your-organization"
  repo: "yaml-configs"

# 5. Microsoft Teams webhook
notifications:
  teams:
    webhook_url: ${TEAMS_WEBHOOK_URL}
    mention_qa: true
    qa_group: "QA Team"

# 6. Retry strategy (how many times to retry on failure)
retry:
  max_attempts: 3
  initial_delay: 2          # seconds
  backoff_factor: 2         # multiply delay each attempt
```

## 🎓 Learning Examples

### Example 1: Load Configuration
```python
from config import Config

# Load from YAML
config = Config('config/config.yaml')

# Get values (with dot notation)
username = config.get('browserstack.username')
timeout = config.get('browserstack.upload_timeout', 300)

# Get required values (raises error if missing)
token = config.get_required('github.token')
```

### Example 2: Validate Artifact
```python
from local_storage import LocalStorage

storage = LocalStorage(config)

# Build path from parameters
path = storage.construct_artifact_path(
    platform='android',
    environment='production',
    build_type='Release',
    app_variant='agent'
)

# Validate the artifact
artifact = storage.validate_artifact(path)
print(f"Size: {artifact['size_mb']} MB")
print(f"MD5: {artifact['md5']}")
```

### Example 3: Upload to BrowserStack
```python
from browserstack_client import BrowserStackClient

client = BrowserStackClient(config)

# Upload app with automatic retry
result = client.upload_app(
    artifact_path='/path/to/app.apk',
    custom_id='my-build-123'
)

print(f"App ID: {result['app_id']}")
```

## 📖 Detailed Documentation

See the `docs/` folder for:
- **SETUP.md** - Installation & environment setup
- **CONFIGURATION.md** - All config options explained
- **USAGE.md** - How to run, all parameters
- **TROUBLESHOOTING.md** - Common errors & solutions

## 🐛 Common Issues & Solutions

### Issue: "Artifact not found"
**Solution**: Check that the artifact path is correct in `config.yaml`
```bash
ls -la /shared/builds/mainline/android/production/...
```

### Issue: "Invalid BrowserStack response"
**Solution**: Verify credentials are set correctly
```bash
echo $BROWSERSTACK_USER
echo $BROWSERSTACK_ACCESS_KEY
```

### Issue: "Failed to create PR"
**Solution**: Check GitHub token has repo access
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

More solutions in `docs/TROUBLESHOOTING.md`

## 🧪 Testing (When You Make Changes)

```bash
# Run tests
python3 -m pytest tests/

# Run with verbose output
python3 -m pytest tests/ -v

# Test one module
python3 -m pytest tests/test_config.py
```

## 🔄 Workflow Diagram

```
START
  ↓
[User provides 7 parameters]
  ↓
[1] main.py validates parameters
  ↓
[2] local_storage.py checks artifact file
  ↓
[3] browserstack_client.py uploads to BrowserStack
  ↓
[4] github_client.py clones config repository
  ↓
[5] yaml_updater.py updates app IDs in YAML
  ↓
[6] github_client.py commits & pushes
  ↓
[7] github_client.py creates pull request
  ↓
[8] teams_notifier.py sends notification
  ↓
[9] utils.py creates audit trail JSON
  ↓
SUCCESS or FAILED
  ↓
END
```

## 💡 Code Quality Features

✅ **Well-Documented**
- Every function has a docstring
- Inline comments explain "why"
- Type hints show parameter types

✅ **Error Handling**
- Try/except blocks catch errors
- Meaningful error messages
- Retries on network failures

✅ **Logging**
- Colored console output
- Info, Warning, Error levels
- Log files for debugging

✅ **Security**
- No hardcoded credentials
- Environment variables for secrets
- Audit trails for compliance

## 🚀 Next Steps

1. **Read** `src/main.py` to understand the 9 workflow steps
2. **Read** one other module that interests you
3. **Review** `config/config.yaml` and customize for your needs
4. **Test** locally: `python3 src/main.py --help`
5. **Try** a test run (if you have test artifacts)
6. **Integrate** with Jenkins (see `docs/`)

## 📝 File Summary

After reorganization:

| Old Location | New Location | Change |
|-------------|-------------|--------|
| `*.py` (8 files) | `src/*.py` | Organized + simplified with comments |
| `config.yaml` | `config/config.yaml` | Moved to config directory |
| Jenkinsfiles (7) | `jenkins/` | Consolidated & organized |
| Docs (10+) | `docs/` | Reorganized for clarity |
| Root clutter (40+ files) | Removed | Cleaned up |

## ✨ Key Improvements Made

1. **Structure**: Files organized into logical directories
2. **Documentation**: Every function documented for learners
3. **Simplification**: Code simplified with clear variable names
4. **Comments**: Inline comments explain the "why"
5. **Examples**: Example code for learning
6. **Configuration**: Cleaner config structure
7. **Gitignore**: Proper file exclusions
8. **Readability**: Better formatted code

## 🤝 Contributing

When modifying code:
1. Add docstrings to new functions
2. Include type hints
3. Add inline comments for complex logic
4. Follow Python style guide (PEP 8)
5. Test your changes

## 📞 Support Resources

- 📖 Check `docs/` folder for detailed guides
- 🔍 See `examples/` for code examples
- ❌ Read `docs/TROUBLESHOOTING.md` for common issues
- 💬 Check inline comments in `src/` modules

---

**Happy Learning! This project is designed to teach Python concepts while solving a real-world problem.** 🎓

Start by reading `src/main.py` to see the big picture, then dive into the module you're most interested in!
