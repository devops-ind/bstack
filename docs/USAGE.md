# Usage Guide

Complete guide on how to use the BrowserStack Uploader tool.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Command-Line Interface](#command-line-interface)
3. [Parameters Explained](#parameters-explained)
4. [Usage Examples](#usage-examples)
5. [Output & Results](#output--results)
6. [Advanced Usage](#advanced-usage)

## Quick Start

### Minimal Usage

```bash
python3 src/main.py \
  --platform android \
  --environment staging \
  --build-type Debug \
  --app-variant agent \
  --version 1.0.0 \
  --build-id jenkins-123 \
  --source-build-url https://jenkins.example.com/build/123
```

### With Configuration File

```bash
python3 src/main.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --version 1.2.0 \
  --build-id jenkins-456 \
  --source-build-url https://jenkins.example.com/build/456 \
  --config-file config/config.yaml
```

### With Verbose Output

```bash
python3 src/main.py \
  --platform android \
  --environment staging \
  --build-type Debug \
  --app-variant agent \
  --version 1.0.0 \
  --build-id jenkins-789 \
  --source-build-url https://jenkins.example.com/build/789 \
  --verbose
```

## Command-Line Interface

### Help

```bash
python3 src/main.py --help
```

Shows all available options and usage examples.

### Basic Syntax

```bash
python3 src/main.py [OPTIONS]
```

### All Options

```
--platform {android, android_hw, ios}    (required)
--environment {production, staging}       (required)
--build-type {Debug, Release}            (required)
--app-variant {agent, retail, wallet}    (required)
--version VERSION_STRING                  (required)
--build-id BUILD_ID                       (required)
--source-build-url BUILD_URL              (required)
--config-file PATH                        (default: config.yaml)
--output-file PATH                        (optional)
--verbose / -v                            (optional flag)
--help / -h                               (show help)
```

## Parameters Explained

### Required Parameters

#### --platform

Mobile platform to upload for.

**Valid values:**
- `android` - Google Play Android
- `android_hw` - Huawei Android devices
- `ios` - Apple iOS

**Example:**
```bash
--platform android
```

#### --environment

Target deployment environment.

**Valid values:**
- `production` - Production environment (real users)
- `staging` - Staging environment (testing before production)

**Example:**
```bash
--environment production
```

#### --build-type

Type of build being uploaded.

**Valid values:**
- `Debug` - Debug build (with debugging symbols)
- `Release` - Release build (optimized, obfuscated)

**Example:**
```bash
--build-type Release
```

#### --app-variant

Which application variant to upload.

**Valid values:**
- `agent` - Agent application
- `retail` - Retail/Customer application
- `wallet` - Wallet/Payment application

**Example:**
```bash
--app-variant agent
```

#### --version

Application version using semantic versioning.

**Format:**
- `X.Y.Z` - Standard (e.g., `1.2.0`)
- `X.Y.Z-suffix` - With pre-release (e.g., `1.2.0-beta`)

**Examples:**
```bash
--version 1.0.0
--version 2.3.1-alpha
--version 1.5.0-rc1
```

#### --build-id

Unique identifier for this build (usually from CI/CD).

**Format:** Any alphanumeric string

**Examples:**
```bash
--build-id jenkins-123
--build-id github-actions-456
--build-id pipeline-789
```

#### --source-build-url

URL to the source build in your CI/CD system.

**Format:** Valid HTTP or HTTPS URL

**Examples:**
```bash
--source-build-url https://jenkins.company.com/job/android-build/123
--source-build-url https://github.com/org/repo/actions/runs/456
```

### Optional Parameters

#### --config-file

Path to configuration file.

**Default:** `config.yaml`

**Example:**
```bash
--config-file /path/to/custom/config.yaml
```

#### --output-file

Save results to JSON file.

**Default:** No output file (results only in console)

**Example:**
```bash
--output-file result.json
```

#### --verbose / -v

Enable verbose logging (debug mode).

**Example:**
```bash
--verbose
# or
-v
```

## Usage Examples

### Example 1: Android Staging Debug Build

```bash
python3 src/main.py \
  --platform android \
  --environment staging \
  --build-type Debug \
  --app-variant agent \
  --version 1.0.0 \
  --build-id jenkins-001 \
  --source-build-url https://jenkins.example.com/job/android/001 \
  --verbose
```

### Example 2: iOS Production Release Build

```bash
python3 src/main.py \
  --platform ios \
  --environment production \
  --build-type Release \
  --app-variant retail \
  --version 2.0.0 \
  --build-id jenkins-002 \
  --source-build-url https://jenkins.example.com/job/ios/002
```

### Example 3: Huawei Android with Output File

```bash
python3 src/main.py \
  --platform android_hw \
  --environment staging \
  --build-type Release \
  --app-variant wallet \
  --version 1.5.0 \
  --build-id jenkins-003 \
  --source-build-url https://jenkins.example.com/job/huawei/003 \
  --output-file upload_result.json \
  --config-file config/config.yaml
```

### Example 4: Multiple Uploads (Batch)

```bash
#!/bin/bash

# Upload multiple builds
for variant in agent retail wallet; do
  echo "Uploading $variant..."
  python3 src/main.py \
    --platform android \
    --environment production \
    --build-type Release \
    --app-variant $variant \
    --version 1.0.0 \
    --build-id jenkins-batch-$(date +%s) \
    --source-build-url https://jenkins.example.com/build

  echo "✅ $variant uploaded"
  sleep 5  # Wait 5 seconds between uploads
done
```

### Example 5: With Environment Variables

```bash
# Set environment-specific variables
export BUILD_VERSION="1.2.3"
export BUILD_ID="jenkins-$(date +%Y%m%d-%H%M%S)"
export BUILD_URL="https://jenkins.company.com/job/build/123"

# Use in command
python3 src/main.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --version $BUILD_VERSION \
  --build-id $BUILD_ID \
  --source-build-url $BUILD_URL
```

## Output & Results

### Console Output

The tool prints detailed progress for each step:

```
======================================================================
STEP 1: Validate Parameters
======================================================================
[2024-01-01 12:00:00] INFO     BrowserStackUploader: Parameters validated successfully
  Platform: android
  Environment: production
  ...

======================================================================
STEP 2: Validate & Read Artifact
======================================================================
[2024-01-01 12:00:01] INFO     LocalStorage: Artifact validated
  Path: /shared/builds/app.apk
  Size: 45.32 MB
  MD5: abc123def456...

... (more steps) ...

======================================================================
✅ WORKFLOW COMPLETED SUCCESSFULLY
======================================================================
PR: https://github.com/org/repo/pull/42
App ID: bs://123456...
```

### Output File (JSON)

When using `--output-file`, results are saved as JSON:

```json
{
  "status": "SUCCESS",
  "timestamp": "2024-01-01T12:00:00...",
  "params": {
    "platform": "android",
    "version": "1.0.0",
    ...
  },
  "steps": {
    "validate": "SUCCESS",
    "artifact_validation": "SUCCESS",
    "browserstack_upload": "SUCCESS",
    ...
  },
  "browserstack": {
    "app_id": "bs://123456...",
    "app_url": "bs://123456...",
    ...
  },
  "pr": {
    "pr_number": "42",
    "pr_url": "https://github.com/org/repo/pull/42",
    ...
  },
  "yaml_files_updated": [
    "android/agent.yml",
    "shared.yml"
  ],
  "audit_file": "audit-trail-android-agent-jenkins-123.json"
}
```

### Exit Codes

- `0` - Success
- `1` - Failure (check error messages)

Use in scripts:

```bash
python3 src/main.py --platform android ...
if [ $? -eq 0 ]; then
  echo "Upload successful!"
else
  echo "Upload failed!"
  exit 1
fi
```

## Advanced Usage

### Conditional Uploads

```bash
# Only upload if version changed
CURRENT_VERSION=$(cat version.txt)
NEW_VERSION="1.2.0"

if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
  python3 src/main.py \
    --platform android \
    --environment production \
    --build-type Release \
    --app-variant agent \
    --version $NEW_VERSION \
    --build-id jenkins-$(date +%s) \
    --source-build-url https://jenkins.example.com/build
  echo $NEW_VERSION > version.txt
else
  echo "Version unchanged, skipping upload"
fi
```

### Retry on Failure

```bash
# Retry up to 3 times on failure
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  python3 src/main.py \
    --platform android \
    --environment staging \
    --build-type Debug \
    --app-variant agent \
    --version 1.0.0 \
    --build-id jenkins-123 \
    --source-build-url https://jenkins.example.com/build/123 \
    --output-file result.json

  if [ $? -eq 0 ]; then
    echo "✅ Upload successful!"
    break
  fi

  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
    echo "⚠️  Retrying... (attempt $RETRY_COUNT)"
    sleep 10
  fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "❌ Upload failed after $MAX_RETRIES attempts"
  exit 1
fi
```

### Parallel Uploads

```bash
# Upload multiple variants in parallel
for variant in agent retail wallet; do
  python3 src/main.py \
    --platform android \
    --environment production \
    --build-type Release \
    --app-variant $variant \
    --version 1.0.0 \
    --build-id jenkins-123 \
    --source-build-url https://jenkins.example.com/build/123 \
    --output-file result-$variant.json &
done

# Wait for all background jobs
wait

# Check results
for variant in agent retail wallet; do
  if grep -q '"status": "SUCCESS"' result-$variant.json; then
    echo "✅ $variant uploaded successfully"
  else
    echo "❌ $variant upload failed"
  fi
done
```

### Logging to File

```bash
# Capture all output to file
python3 src/main.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --version 1.0.0 \
  --build-id jenkins-123 \
  --source-build-url https://jenkins.example.com/build/123 \
  --verbose 2>&1 | tee upload_$(date +%Y%m%d_%H%M%S).log
```

---

**Need help?** Check the examples in `examples/` directory or see `SETUP.md` for configuration help.
