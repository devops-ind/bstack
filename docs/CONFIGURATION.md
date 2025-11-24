# Configuration Reference

Complete reference guide for configuring the BrowserStack Uploader tool.

## Table of Contents

1. [Configuration File](#configuration-file)
2. [BrowserStack Settings](#browserstack-settings)
3. [Local Storage Settings](#local-storage-settings)
4. [Git & GitHub Settings](#git--github-settings)
5. [Notifications Settings](#notifications-settings)
6. [Retry Logic Settings](#retry-logic-settings)
7. [Environment Variables](#environment-variables)
8. [Complete Example](#complete-example)

## Configuration File

### Location

The configuration file is typically located at:
```
config/config.yaml
```

### Format

The configuration uses YAML format with the following structure:

```yaml
browserstack:
  # BrowserStack API settings
  ...

local_storage:
  # Local artifact storage settings
  ...

git:
  # Git repository settings
  ...

github:
  # GitHub API settings
  ...

notifications:
  # Notification settings
  ...

retry:
  # Retry logic settings
  ...
```

### Environment Variable Substitution

Configuration values support environment variable substitution using `${VAR_NAME}` syntax:

```yaml
browserstack:
  username: ${BROWSERSTACK_USER}           # Will use BROWSERSTACK_USER env var
  access_key: ${BROWSERSTACK_ACCESS_KEY}   # Will use BROWSERSTACK_ACCESS_KEY env var
```

**Important**: Environment variables are substituted at runtime. Make sure they are set before running the tool.

## BrowserStack Settings

### Configuration

```yaml
browserstack:
  username: "${BROWSERSTACK_USER}"
  access_key: "${BROWSERSTACK_ACCESS_KEY}"
  api_endpoint: "https://api-cloud.browserstack.com/app-automate/upload"
  upload_timeout: 300
```

### Parameters

#### `username` (Required)

Your BrowserStack account username.

- **Type**: String
- **Default**: None (must be set)
- **Source**: Environment variable `BROWSERSTACK_USER`
- **Example**:
  ```yaml
  username: "john_doe"
  ```

**How to find it**:
1. Log in to BrowserStack (https://www.browserstack.com)
2. Go to Settings → API Key
3. Your username is displayed under "Username"

#### `access_key` (Required)

Your BrowserStack account access key (API key).

- **Type**: String
- **Default**: None (must be set)
- **Source**: Environment variable `BROWSERSTACK_ACCESS_KEY`
- **Example**:
  ```yaml
  access_key: "abc123xyz789..."
  ```

**How to find it**:
1. Log in to BrowserStack
2. Go to Settings → API Key
3. Copy the "Access Key" value
4. Store securely in `.env` file, never commit to git

#### `api_endpoint` (Optional)

BrowserStack's API endpoint for app uploads.

- **Type**: URL
- **Default**: `"https://api-cloud.browserstack.com/app-automate/upload"`
- **Example**:
  ```yaml
  api_endpoint: "https://api-cloud.browserstack.com/app-automate/upload"
  ```

**Note**: Usually, you don't need to change this unless BrowserStack updates their API.

#### `upload_timeout` (Optional)

Maximum time (in seconds) to wait for a single app upload.

- **Type**: Integer
- **Default**: `300` (5 minutes)
- **Range**: 30-900 seconds recommended
- **Example**:
  ```yaml
  upload_timeout: 300
  ```

**Guide**:
- **Small apps (< 50 MB)**: 60-120 seconds
- **Medium apps (50-100 MB)**: 180-300 seconds
- **Large apps (> 100 MB)**: 300-600 seconds

## Local Storage Settings

### Configuration

```yaml
local_storage:
  artifact_base_path: "/shared/builds"

  path_templates:
    android: "{base}/{platform}/{environment}/{build_type}/android/app.apk"
    android_hw: "{base}/{platform}/{environment}/{build_type}/android/app.apk"
    ios: "{base}/{platform}/{environment}/{build_type}/ios/app.ipa"

  accepted_extensions:
    android: [".apk", ".aab"]
    ios: [".ipa"]
```

### Parameters

#### `artifact_base_path` (Required)

Base directory where all build artifacts are stored.

- **Type**: Path (string)
- **Default**: None (must be set)
- **Example**:
  ```yaml
  artifact_base_path: "/shared/builds"
  ```

**Setup**:
1. Create the base directory on your system
2. Set appropriate permissions so the script can read artifacts
3. Ensure the directory structure matches your `path_templates`

#### `path_templates` (Required)

Template paths for locating artifacts by platform.

- **Type**: Object with platform keys
- **Platforms**: `android`, `android_hw`, `ios`

**Template Variables**:
- `{base}` - Replaced with `artifact_base_path`
- `{platform}` - The platform (android, ios, etc.)
- `{environment}` - staging or production
- `{build_type}` - Debug or Release
- `{app_variant}` - agent, retail, or wallet

**Example**:
```yaml
path_templates:
  android: "{base}/{platform}/{environment}/{build_type}/android/app.apk"
  android_hw: "{base}/{platform}/{environment}/{build_type}/android/app.apk"
  ios: "{base}/{platform}/{environment}/{build_type}/ios/app.ipa"
```

**Resulting Paths**:
For a Debug build on Android staging:
```
/shared/builds/android/staging/Debug/android/app.apk
```

For a Release build on iOS production:
```
/shared/builds/ios/production/Release/ios/app.ipa
```

#### `accepted_extensions` (Required)

File extensions accepted for each platform.

- **Type**: Object with platform keys containing array of extensions
- **Android extensions**: `.apk` (app), `.aab` (app bundle)
- **iOS extensions**: `.ipa` (app)

**Example**:
```yaml
accepted_extensions:
  android: [".apk", ".aab"]
  ios: [".ipa"]
```

**Validation**:
The tool checks file extensions to ensure artifacts are correct type before uploading.

## Git & GitHub Settings

### Configuration

```yaml
git:
  repo_url: "https://github.com/your-org/yaml-configs.git"
  default_branch: "main"
  user_name: "DevOps Automation"
  user_email: "devops@company.com"
  create_pr: true

github:
  token: "${GITHUB_TOKEN}"
  org: "your-organization"
  repo: "yaml-configs"
```

### Git Parameters

#### `repo_url` (Required)

URL to the Git repository containing YAML configuration files.

- **Type**: URL (HTTPS recommended)
- **Example**:
  ```yaml
  repo_url: "https://github.com/devops-ind/yaml-configs.git"
  ```

**Format**: Use HTTPS format (not SSH) for better compatibility.

#### `default_branch` (Optional)

The default branch to create PRs against.

- **Type**: String
- **Default**: `"main"`
- **Example**:
  ```yaml
  default_branch: "main"
  ```

**Common values**: `main`, `master`, `develop`

#### `user_name` (Optional)

Git user name for commits created by the automation.

- **Type**: String
- **Default**: `"DevOps Automation"`
- **Example**:
  ```yaml
  user_name: "CI/CD Bot"
  ```

#### `user_email` (Optional)

Git user email for commits created by the automation.

- **Type**: Email address
- **Default**: `"devops@company.com"`
- **Example**:
  ```yaml
  user_email: "automation@company.com"
  ```

#### `create_pr` (Optional)

Whether to create a Pull Request after pushing changes.

- **Type**: Boolean
- **Default**: `true`
- **Values**: `true` or `false`
- **Example**:
  ```yaml
  create_pr: true
  ```

### GitHub Parameters

#### `token` (Required)

GitHub personal access token for API authentication.

- **Type**: String (token)
- **Source**: Environment variable `GITHUB_TOKEN`
- **Example**:
  ```yaml
  token: "${GITHUB_TOKEN}"
  ```

**How to create**:
1. Log in to GitHub
2. Go to Settings → Developer settings → Personal access tokens
3. Click "Generate new token"
4. Select scopes: `repo`, `workflow`
5. Copy the token and store in `.env` file

**Security**: Never commit the actual token to git. Use environment variables.

#### `org` (Required)

GitHub organization name.

- **Type**: String
- **Example**:
  ```yaml
  org: "devops-ind"
  ```

#### `repo` (Required)

GitHub repository name (within the organization).

- **Type**: String
- **Example**:
  ```yaml
  repo: "yaml-configs"
  ```

## Notifications Settings

### Configuration

```yaml
notifications:
  teams:
    webhook_url: "${TEAMS_WEBHOOK_URL}"
    mention_qa: true
    qa_group: "QA Team"
```

### Parameters

#### `webhook_url` (Optional)

Microsoft Teams webhook URL for notifications.

- **Type**: URL (Teams webhook)
- **Default**: None (notifications disabled if not set)
- **Source**: Environment variable `TEAMS_WEBHOOK_URL`
- **Example**:
  ```yaml
  webhook_url: "${TEAMS_WEBHOOK_URL}"
  ```

**How to create**:
1. In Teams, go to your channel
2. Click "..." (More options) → Connectors
3. Search for "Incoming Webhook"
4. Click Configure
5. Enter a name and optionally upload an image
6. Click Create
7. Copy the webhook URL and store in `.env` file

#### `mention_qa` (Optional)

Whether to mention QA team in notifications.

- **Type**: Boolean
- **Default**: `false`
- **Example**:
  ```yaml
  mention_qa: true
  ```

#### `qa_group` (Optional)

Name of the QA group to mention.

- **Type**: String
- **Default**: `"QA Team"`
- **Example**:
  ```yaml
  qa_group: "QA Team"
  ```

**Note**: Only used if `mention_qa` is true.

## Retry Logic Settings

### Configuration

```yaml
retry:
  max_attempts: 3
  initial_delay: 2
  backoff_factor: 2
```

### Parameters

#### `max_attempts` (Optional)

Maximum number of retry attempts for API calls.

- **Type**: Integer
- **Default**: `3`
- **Range**: 1-10 recommended
- **Example**:
  ```yaml
  max_attempts: 3
  ```

**How it works**:
- First attempt: immediately
- Second attempt: after initial_delay seconds
- Third attempt: after initial_delay * backoff_factor seconds
- And so on...

#### `initial_delay` (Optional)

Initial delay in seconds before first retry.

- **Type**: Integer (seconds)
- **Default**: `2`
- **Range**: 1-10 recommended
- **Example**:
  ```yaml
  initial_delay: 2
  ```

#### `backoff_factor` (Optional)

Multiplier for delay between retries (exponential backoff).

- **Type**: Integer or Float
- **Default**: `2`
- **Example**:
  ```yaml
  backoff_factor: 2
  ```

**Backoff Schedule Example** (with initial_delay=2, backoff_factor=2):
- Attempt 1: immediate (0s delay)
- Attempt 2: after 2 seconds
- Attempt 3: after 4 seconds (2 * 2)
- Attempt 4: after 8 seconds (4 * 2)

## Environment Variables

The tool uses the following environment variables (should be set in `.env` file):

| Variable | Required | Example | Source |
|----------|----------|---------|--------|
| `BROWSERSTACK_USER` | Yes | `john_doe` | BrowserStack Settings → API Key |
| `BROWSERSTACK_ACCESS_KEY` | Yes | `abc123xyz...` | BrowserStack Settings → API Key |
| `GITHUB_TOKEN` | Yes | `ghp_abc123...` | GitHub Settings → Developer settings → Personal access tokens |
| `TEAMS_WEBHOOK_URL` | No | `https://outlook.webhook.office.com/...` | Teams Channel → Connectors → Incoming Webhook |

### Setting Environment Variables

Create a `.env` file in the project root:

```bash
cat > .env << 'EOF'
export BROWSERSTACK_USER="your_username"
export BROWSERSTACK_ACCESS_KEY="your_access_key"
export GITHUB_TOKEN="your_token"
export TEAMS_WEBHOOK_URL="your_webhook_url"
EOF
```

Load the variables:

```bash
source .env
```

Verify they're set:

```bash
echo $BROWSERSTACK_USER
echo $GITHUB_TOKEN
```

## Complete Example

Here's a complete, working configuration file:

```yaml
# BrowserStack API Configuration
browserstack:
  username: "${BROWSERSTACK_USER}"
  access_key: "${BROWSERSTACK_ACCESS_KEY}"
  api_endpoint: "https://api-cloud.browserstack.com/app-automate/upload"
  upload_timeout: 300

# Local Storage Configuration
local_storage:
  artifact_base_path: "/shared/builds"

  path_templates:
    android: "{base}/{platform}/{environment}/{build_type}/android/app.apk"
    android_hw: "{base}/{platform}/{environment}/{build_type}/android/app.apk"
    ios: "{base}/{platform}/{environment}/{build_type}/ios/app.ipa"

  accepted_extensions:
    android: [".apk", ".aab"]
    ios: [".ipa"]

# Git Configuration
git:
  repo_url: "https://github.com/devops-ind/yaml-configs.git"
  default_branch: "main"
  user_name: "DevOps Automation"
  user_email: "devops@company.com"
  create_pr: true

# GitHub Configuration
github:
  token: "${GITHUB_TOKEN}"
  org: "devops-ind"
  repo: "yaml-configs"

# Notifications Configuration
notifications:
  teams:
    webhook_url: "${TEAMS_WEBHOOK_URL}"
    mention_qa: true
    qa_group: "QA Team"

# Retry Logic Configuration
retry:
  max_attempts: 3
  initial_delay: 2
  backoff_factor: 2
```

## Configuration Tips

### For Development

Use relaxed settings for faster iterations:

```yaml
retry:
  max_attempts: 1          # Don't retry in development
  initial_delay: 0
  backoff_factor: 1

browserstack:
  upload_timeout: 120      # 2 minutes should be enough for testing
```

### For Production

Use conservative settings for reliability:

```yaml
retry:
  max_attempts: 5          # Retry up to 5 times
  initial_delay: 5
  backoff_factor: 2

browserstack:
  upload_timeout: 600      # 10 minutes timeout
```

### For Large Apps

If you're uploading large app bundles (> 100 MB):

```yaml
browserstack:
  upload_timeout: 900      # 15 minutes

retry:
  max_attempts: 5
  initial_delay: 10
  backoff_factor: 2
```

## Validation

After editing the configuration file, you can validate it:

```bash
# Check configuration loads without errors
python3 -c "from src.config import Config; Config('config/config.yaml'); print('✅ Config is valid')"
```

## Getting Help

- **Configuration questions**: See [SETUP.md](SETUP.md)
- **Usage examples**: See [USAGE.md](USAGE.md)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Project structure**: See [README.md](README.md)

---

**Configuration is critical!** Take time to set it up correctly.
