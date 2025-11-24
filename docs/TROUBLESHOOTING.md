# Troubleshooting Guide

Solutions to common issues when using the BrowserStack Uploader.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Issues](#configuration-issues)
3. [Runtime Errors](#runtime-errors)
4. [Upload Failures](#upload-failures)
5. [GitHub Integration Issues](#github-integration-issues)
6. [Debug Mode](#debug-mode)
7. [Getting Help](#getting-help)

## Installation Issues

### Issue: "No module named 'yaml'"

**Symptom**:
```
ModuleNotFoundError: No module named 'yaml'
```

**Cause**: PyYAML package not installed

**Solution**:
```bash
pip install PyYAML
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "No module named 'requests'"

**Symptom**:
```
ModuleNotFoundError: No module named 'requests'
```

**Cause**: requests package not installed

**Solution**:
```bash
pip install requests
```

### Issue: Python version incompatible

**Symptom**:
```
Error: This project requires Python 3.11 or higher
```

**Cause**: Running with Python 3.10 or older

**Solution**:
```bash
# Check your Python version
python3 --version

# If less than 3.11, upgrade Python
# On macOS:
brew install python@3.11
```

### Issue: Virtual environment not activating

**Symptom**:
Command prompt doesn't show `(venv)` prefix

**Solution**:
```bash
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify it's activated
which python  # Should show path inside venv directory
```

### Issue: Permission denied on script

**Symptom**:
```
bash: ./src/main.py: Permission denied
```

**Solution**:
```bash
# Make script executable
chmod +x src/main.py

# Or run with python3 explicitly
python3 src/main.py --help
```

## Configuration Issues

### Issue: "Environment variable not set"

**Symptom**:
```
Error: BROWSERSTACK_USER environment variable not set
Error: GITHUB_TOKEN environment variable not set
```

**Cause**: Environment variables not loaded

**Solution**:
```bash
# Create .env file with your credentials
cat > .env << 'EOF'
export BROWSERSTACK_USER="your_username"
export BROWSERSTACK_ACCESS_KEY="your_access_key"
export GITHUB_TOKEN="your_token"
export TEAMS_WEBHOOK_URL="your_webhook_url"
EOF

# Load the variables
source .env

# Verify they're loaded
echo $BROWSERSTACK_USER
```

### Issue: "Configuration file not found"

**Symptom**:
```
Error: Configuration file not found: config/config.yaml
```

**Cause**: config.yaml missing from config/ directory

**Solution**:
```bash
# Check if config directory exists
ls -la config/

# If missing, create it
mkdir -p config

# Copy config.yaml from project root
cp config.yaml config/config.yaml

# Or use custom path
python3 src/main.py ... --config-file /path/to/config.yaml
```

### Issue: "Invalid configuration format"

**Symptom**:
```
Error: Invalid YAML format in config file
```

**Cause**: YAML syntax error (indentation, missing quotes, etc.)

**Solution**:
1. Open the config file in a text editor
2. Check for YAML syntax errors:
   - Use consistent indentation (spaces, not tabs)
   - Quote strings with special characters
   - Check colon placement (space after colons)

Example of correct YAML:
```yaml
browserstack:
  username: "${BROWSERSTACK_USER}"
  access_key: "${BROWSERSTACK_ACCESS_KEY}"
```

### Issue: "Invalid environment variable reference"

**Symptom**:
```
Error: Failed to resolve environment variable: BROWSERSTACK_USER
```

**Cause**: Referenced environment variable not set

**Solution**:
```bash
# Check if the variable is set
echo $BROWSERSTACK_USER

# If empty, set it
export BROWSERSTACK_USER="your_username"

# Or use absolute value in config (not recommended)
username: "your_username"  # Instead of "${BROWSERSTACK_USER}"
```

## Runtime Errors

### Issue: "Invalid platform specified"

**Symptom**:
```
Error: Platform must be one of: android, android_hw, ios
```

**Cause**: Wrong platform value provided

**Solution**:
```bash
# Use only valid platforms
python3 src/main.py \
  --platform android \    # Valid: android, android_hw, ios
  --environment staging
```

**Valid values**:
- `android` - Standard Android
- `android_hw` - Huawei Android
- `ios` - Apple iOS

### Issue: "Invalid environment specified"

**Symptom**:
```
Error: Environment must be one of: production, staging
```

**Cause**: Wrong environment value

**Solution**:
```bash
# Use only valid environments
python3 src/main.py \
  --environment staging \  # Valid: staging, production
  ...
```

### Issue: "Invalid build type"

**Symptom**:
```
Error: Build type must be one of: Debug, Release
```

**Cause**: Wrong build type (case-sensitive)

**Solution**:
```bash
# Use correct case (capital D or R)
python3 src/main.py \
  --build-type Debug \    # or Release (NOT debug or release)
  ...
```

### Issue: "Invalid version format"

**Symptom**:
```
Error: Version must follow semantic versioning (X.Y.Z)
```

**Cause**: Version format incorrect

**Solution**:
```bash
# Valid format: X.Y.Z (with optional suffix)
python3 src/main.py \
  --version 1.0.0 \               # Correct
  --version 1.2.3-alpha \         # Also correct (pre-release)
  --version 1.2 \                 # Wrong! Need 3 parts
  --version 1.2.3.4 \             # Wrong! Too many parts
  ...
```

### Issue: "Invalid URL format"

**Symptom**:
```
Error: Source build URL must be a valid HTTP(S) URL
```

**Cause**: URL format incorrect

**Solution**:
```bash
# Use valid HTTP or HTTPS URLs
python3 src/main.py \
  --source-build-url "https://jenkins.example.com/build/123" \
  --source-build-url "http://example.com/artifact" \
  ...
```

## Upload Failures

### Issue: "Artifact file not found"

**Symptom**:
```
Error: Artifact not found at: /path/to/app.apk
```

**Cause**: APK/IPA file doesn't exist at expected location

**Solution**:
1. Check the artifact path in your config:
   ```bash
   # Show what path is being looked for
   python3 src/main.py ... --verbose
   ```

2. Verify file exists:
   ```bash
   ls -lh /path/to/app.apk
   ```

3. Check path template in config/config.yaml:
   ```yaml
   path_templates:
     android: "{base}/{platform}/{environment}/{build_type}/android/app.apk"
   ```

4. Verify artifact_base_path:
   ```yaml
   artifact_base_path: "/shared/builds"  # Must exist and be readable
   ```

### Issue: "Invalid file type"

**Symptom**:
```
Error: File extension not accepted for platform
```

**Cause**: Wrong file type for platform

**Solution**:
```bash
# Verify file extension matches platform
# For Android: use .apk or .aab
# For iOS: use .ipa

# Check accepted extensions in config:
cat config/config.yaml | grep -A 3 "accepted_extensions"
```

### Issue: "File validation failed (magic bytes)"

**Symptom**:
```
Error: File validation failed - not a valid APK/IPA file
```

**Cause**: File is corrupted or wrong format

**Solution**:
```bash
# Check file size (should be more than 1 MB typically)
ls -lh /path/to/app.apk

# Verify it's a valid archive
file /path/to/app.apk  # Should say "Zip archive data"

# Re-download or rebuild the artifact
```

### Issue: "BrowserStack upload timeout"

**Symptom**:
```
Error: Upload timeout - exceeded 300 seconds
```

**Cause**: File upload taking too long (network or file size issue)

**Solution**:
```bash
# Option 1: Increase timeout in config
# Edit config/config.yaml:
browserstack:
  upload_timeout: 600  # Increase from 300 to 600 seconds

# Option 2: Check network connectivity
ping api-cloud.browserstack.com

# Option 3: Check file size
ls -lh /path/to/app.apk  # Large files take longer

# Option 4: Retry with verbose logging
python3 src/main.py ... --verbose
```

### Issue: "BrowserStack API authentication failed"

**Symptom**:
```
Error: BrowserStack authentication failed (401 Unauthorized)
```

**Cause**: Invalid BrowserStack credentials

**Solution**:
```bash
# Verify credentials are set
echo $BROWSERSTACK_USER
echo $BROWSERSTACK_ACCESS_KEY

# Check credentials are correct (get from BrowserStack Settings → API Key)

# Test credentials with curl
curl -X POST \
  -u "username:access_key" \
  -F "file=@/path/to/app.apk" \
  https://api-cloud.browserstack.com/app-automate/upload

# If curl works, the issue is in the tool configuration
```

### Issue: "BrowserStack API rate limited"

**Symptom**:
```
Error: BrowserStack API rate limit exceeded (429)
```

**Cause**: Too many requests to BrowserStack API

**Solution**:
```bash
# Wait a few minutes before retrying
sleep 60

# Or configure exponential backoff in config/config.yaml:
retry:
  max_attempts: 5
  initial_delay: 5
  backoff_factor: 2  # Will wait 5, 10, 20, 40 seconds between retries

# Retry the upload
python3 src/main.py ...
```

### Issue: "BrowserStack server error"

**Symptom**:
```
Error: BrowserStack API error (500 Internal Server Error)
```

**Cause**: BrowserStack server temporarily down

**Solution**:
```bash
# Wait and retry - the tool has automatic retry logic
python3 src/main.py ... --verbose

# Check BrowserStack status page
# https://status.browserstack.com

# If persistent, contact BrowserStack support
```

## GitHub Integration Issues

### Issue: "GitHub authentication failed"

**Symptom**:
```
Error: GitHub authentication failed (401 Unauthorized)
```

**Cause**: Invalid GitHub token

**Solution**:
```bash
# Verify token is set
echo $GITHUB_TOKEN

# Generate new token:
# 1. Log in to GitHub
# 2. Settings → Developer settings → Personal access tokens
# 3. Click "Generate new token"
# 4. Select scopes: repo, workflow
# 5. Copy token and update .env

# Verify token works
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user

# Should show your GitHub user info (not an error)
```

### Issue: "Git repository not found"

**Symptom**:
```
Error: Failed to clone repository
fatal: repository not found
```

**Cause**: Repository URL incorrect or no access

**Solution**:
```bash
# Check repository URL in config/config.yaml
cat config/config.yaml | grep "repo_url"

# Verify repository exists
git clone <repo_url>

# If private repo, check GitHub token has repo scope
```

### Issue: "Cannot create pull request"

**Symptom**:
```
Error: Failed to create pull request
```

**Cause**: Various GitHub API issues

**Solution**:
```bash
# Check GitHub token has 'repo' scope:
# 1. Log in to GitHub
# 2. Settings → Developer settings → Personal access tokens
# 3. Click on your token
# 4. Verify 'repo' is checked under Scopes

# Check branch exists
git ls-remote <repo_url> <branch_name>

# Try creating PR manually first to test
# Then check tool logs for specific error
python3 src/main.py ... --verbose
```

### Issue: "Merge conflicts in YAML files"

**Symptom**:
```
Error: Failed to push branch due to merge conflicts
```

**Cause**: Another PR modified the same YAML files

**Solution**:
```bash
# The tool uses per-app-variant files to minimize conflicts
# Example structure:
# - android/agent.yml (only for agent variant)
# - android/retail.yml (only for retail variant)
# - shared.yml (metadata only)

# If still getting conflicts:
# 1. Manually resolve in the YAML configs repo
# 2. Re-run the tool

# Or configure different merge strategy in git config
```

## Debug Mode

### Enable Verbose Logging

Run the tool in verbose mode to get detailed logging:

```bash
python3 src/main.py \
  --platform android \
  --environment staging \
  --build-type Debug \
  --app-variant agent \
  --version 1.0.0 \
  --build-id jenkins-123 \
  --source-build-url https://jenkins.example.com/build/123 \
  --verbose
```

Output will show:
- All configuration values
- Step-by-step progress
- Detailed error messages
- API request/response details

### Check Log Files

Logs are saved to `logs/` directory:

```bash
# List all logs
ls -lh logs/

# View latest log
tail -f logs/browserstack_uploader.log

# Search for errors
grep ERROR logs/browserstack_uploader.log

# Search for specific build
grep "jenkins-123" logs/browserstack_uploader.log
```

### Generate Output File

Save results to JSON for analysis:

```bash
python3 src/main.py \
  ... \
  --output-file debug_result.json

# View results
cat debug_result.json | python3 -m json.tool
```

### Test Individual Components

Test configuration loading:
```bash
python3 -c "from src.config import Config; Config('config/config.yaml'); print('✅ Config OK')"
```

Test artifact validation:
```bash
python3 -c "
from src.local_storage import LocalStorage
from src.config import Config
config = Config('config/config.yaml')
storage = LocalStorage(config)
# Will validate artifact exists and is valid
"
```

Test BrowserStack connection:
```bash
python3 -c "
from src.browserstack_client import BrowserStackClient
from src.config import Config
config = Config('config/config.yaml')
client = BrowserStackClient(config)
print('✅ BrowserStack connection OK')
"
```

## Getting Help

### Useful Commands

```bash
# Show help
python3 src/main.py --help

# Run with verbose output
python3 src/main.py ... --verbose

# Save results for analysis
python3 src/main.py ... --output-file result.json

# Check logs
tail -f logs/browserstack_uploader.log

# Validate configuration
python3 -c "from src.config import Config; Config('config/config.yaml'); print('✅ Valid')"
```

### Common Commands for Debugging

```bash
# List artifact directories
ls -la /shared/builds/

# Check BrowserStack API connectivity
curl -X GET https://api-cloud.browserstack.com/app-automate/upload -u "user:key"

# Check GitHub token validity
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Check YAML syntax
python3 -m yaml < config/config.yaml

# List recent builds
find /shared/builds -type f -name "*.apk" -mtime -1
```

### When to Contact Support

Contact BrowserStack or GitHub support if you've verified:
1. Configuration is correct (validate with tool)
2. Credentials are valid (test with curl)
3. Files exist and are readable
4. Network connectivity is working
5. Using latest tool version

---

**Still stuck?** Check [SETUP.md](SETUP.md) or [CONFIGURATION.md](CONFIGURATION.md) for more details.
