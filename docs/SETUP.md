# Setup & Installation Guide

Complete step-by-step guide to install and configure the BrowserStack Uploader.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
  ```bash
  python3 --version
  ```

- **Git**: Version control system
  ```bash
  git --version
  ```

- **Pip**: Python package manager (comes with Python)
  ```bash
  pip --version
  ```

### Required Accounts & Credentials

Before starting, you'll need:

1. **BrowserStack Account**
   - Sign up at: https://browserstack.com
   - Get your API credentials from Settings → API Key
   - You'll need: username and access key

2. **GitHub Account**
   - Sign up at: https://github.com
   - Create a personal access token: Settings → Developer settings → Personal access tokens
   - Required scopes: `repo`, `workflow`

3. **Microsoft Teams** (optional, for notifications)
   - Get webhook URL from Teams channel
   - Integrations → Connectors → Incoming Webhook

## Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/devops-ind/bstack.git

# Navigate to project directory
cd bstack
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

Installed packages:
- `PyYAML>=6.0` - YAML file handling
- `requests>=2.28.0` - HTTP requests for APIs
- `GitPython>=3.1.30` - Git operations (optional, uses subprocess)

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cat > .env << 'EOF'
export BROWSERSTACK_USER="your_browserstack_username"
export BROWSERSTACK_ACCESS_KEY="your_browserstack_access_key"
export GITHUB_TOKEN="your_github_personal_access_token"
export TEAMS_WEBHOOK_URL="your_teams_webhook_url"
EOF
```

Load the environment variables:

```bash
# On macOS/Linux:
source .env

# On Windows (use set instead):
set /p BROWSERSTACK_USER=<.env
```

Verify they're loaded:

```bash
echo $BROWSERSTACK_USER
echo $GITHUB_TOKEN
```

## Configuration

### Step 1: Edit Configuration File

```bash
# Open configuration file
nano config/config.yaml
```

### Step 2: Configure BrowserStack

```yaml
browserstack:
  username: ${BROWSERSTACK_USER}           # From environment variable
  access_key: ${BROWSERSTACK_ACCESS_KEY}   # From environment variable
  api_endpoint: "https://api-cloud.browserstack.com/app-automate/upload"
  upload_timeout: 300                      # 5 minutes
```

### Step 3: Configure Local Storage Paths

```yaml
local_storage:
  artifact_base_path: "/path/to/artifacts"  # Where your APK/IPA files are stored

  path_templates:
    android: "{base}/{platform}/{environment}/{build_type}/android/app.apk"
    android_hw: "{base}/{platform}/{environment}/{build_type}/android/app.apk"
    ios: "{base}/{platform}/{environment}/{build_type}/ios/app.ipa"

  accepted_extensions:
    android: [".apk", ".aab"]
    ios: [".ipa"]
```

### Step 4: Configure Git/GitHub

```yaml
git:
  repo_url: "https://github.com/your-org/yaml-configs.git"
  default_branch: "main"
  user_name: "DevOps Automation"
  user_email: "devops@company.com"
  create_pr: true

github:
  token: ${GITHUB_TOKEN}
  org: "your-organization"
  repo: "yaml-configs"
```

### Step 5: Configure Teams Webhook (Optional)

```yaml
notifications:
  teams:
    webhook_url: ${TEAMS_WEBHOOK_URL}
    mention_qa: true
    qa_group: "QA Team"
```

### Step 6: Configure Retry Logic

```yaml
retry:
  max_attempts: 3
  initial_delay: 2      # seconds
  backoff_factor: 2     # multiply delay each attempt
```

## Verification

### Test 1: Check Python Installation

```bash
python3 --version
# Expected: Python 3.11.x or higher
```

### Test 2: Check Dependencies

```bash
pip list | grep -E 'PyYAML|requests|GitPython'
# Should see all three packages installed
```

### Test 3: Check Environment Variables

```bash
# Verify all variables are set
echo "BROWSERSTACK_USER: $BROWSERSTACK_USER"
echo "GITHUB_TOKEN: $GITHUB_TOKEN"
echo "TEAMS_WEBHOOK_URL: $TEAMS_WEBHOOK_URL"
```

### Test 4: Test Tool Help

```bash
python3 src/main.py --help
```

Expected output: Shows all available command-line options

### Test 5: Test Configuration Loading

```bash
python3 -c "from src.config import Config; c = Config('config/config.yaml'); print('✅ Config loaded successfully')"
```

### Test 6: Run Tests

```bash
# Install pytest if not already installed
pip install pytest

# Run tests
pytest tests/ -v
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'yaml'"

**Solution:**
```bash
pip install PyYAML
```

### Issue: "Environment variable not set"

**Solution:**
```bash
# Load environment variables
source .env

# Verify
echo $BROWSERSTACK_USER
```

### Issue: "Configuration file not found"

**Solution:**
```bash
# Make sure config.yaml exists
ls config/config.yaml

# If missing, copy from root
cp config.yaml config/config.yaml
```

### Issue: "Permission denied" when running script

**Solution:**
```bash
# Make script executable
chmod +x src/main.py

# Or run with python3
python3 src/main.py --help
```

### Issue: "git command not found"

**Solution:**
```bash
# Install git
# On macOS:
brew install git

# On Ubuntu/Debian:
sudo apt-get install git

# On Windows:
Download from https://git-scm.com/download/win
```

### Issue: Virtual environment not activating

**Solution:**
```bash
# Create new virtual environment
rm -rf venv
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate      # Windows
```

## Next Steps

1. **Read the getting started guide**
   ```bash
   cat GETTING_STARTED.md
   ```

2. **Try a test run**
   ```bash
   python3 src/main.py --help
   ```

3. **Run the examples**
   ```bash
   python3 examples/basic_example.py
   ```

4. **Check the project README**
   ```bash
   cat PROJECT_README.md
   ```

## Security Best Practices

1. **Never commit `.env` file**
   - Add `.env` to `.gitignore` (already done)

2. **Keep credentials secure**
   - Use environment variables, not hardcoded values
   - Rotate tokens regularly

3. **Limit token permissions**
   - GitHub: Only grant necessary scopes
   - BrowserStack: Use read-only keys where possible

4. **Monitor for leaks**
   - If you accidentally expose credentials, regenerate them immediately
   - GitHub has automatic secret scanning

## Getting Help

- **Setup issues**: See [Troubleshooting](#troubleshooting) section
- **Configuration questions**: See [Configuration](#configuration) section
- **General questions**: Check `PROJECT_README.md`
- **Code examples**: See `examples/` directory
- **Unit tests**: See `tests/` directory

---

**You're all set!** Your BrowserStack Uploader is now installed and configured. 🎉

Next step: Run the tool or check out the examples!
