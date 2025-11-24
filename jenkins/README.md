# Jenkins Integration

Guide to integrating the BrowserStack Uploader with Jenkins pipelines.

## Overview

The BrowserStack Uploader can be integrated into Jenkins CI/CD pipelines using Declarative Pipelines (Jenkinsfile). This directory contains pipeline configurations and setup guides.

## Quick Start

Choose your deployment environment:

1. **Kubernetes** - Modern cloud-native deployments
2. **Docker** - Container-based deployments
3. **Shell** - Traditional server deployments

Each variant has its own Jenkinsfile optimized for that environment.

## Available Pipeline Variants

### 1. Kubernetes Pipeline (Recommended for Cloud)

**File**: `Jenkinsfile-kubernetes`

**When to use**:
- Running Jenkins on Kubernetes cluster
- Need cloud-native deployment
- Want automatic pod scaling
- Prefer container-based agents

**Features**:
- Runs in Kubernetes pod
- Dynamic agent provisioning
- Container isolation
- Resource limits

**Setup**: See [SETUP.md](SETUP.md) - Kubernetes section

### 2. Docker Pipeline (Recommended for Container)

**File**: `Jenkinsfile-docker`

**When to use**:
- Running Jenkins with Docker
- Need consistent build environment
- Want dependency isolation
- Docker daemon available

**Features**:
- Builds within Docker container
- Predefined Docker image
- Consistent environment
- Easy to reproduce

**Setup**: See [SETUP.md](SETUP.md) - Docker section

### 3. Shell Pipeline (Simple/Traditional)

**File**: `Jenkinsfile-shell`

**When to use**:
- Simple setup needed
- Running on traditional Jenkins server
- Want minimal dependencies
- Testing/development

**Features**:
- Direct shell execution
- No containers needed
- Simplest configuration
- Best for small deployments

**Setup**: See [SETUP.md](SETUP.md) - Shell section

## Pipeline Workflow

All variants follow this workflow:

```
1. Clone Repository
   ↓
2. Setup Environment
   ↓
3. Install Dependencies
   ↓
4. Validate Configuration
   ↓
5. Run Upload
   ↓
6. Archive Results
   ↓
7. Notify Results
```

## Common Pipeline Steps

### Step 1: Clone Repository

```groovy
stage('Checkout') {
    steps {
        checkout scm
    }
}
```

### Step 2: Setup Environment

Load credentials and environment variables:

```groovy
stage('Setup') {
    steps {
        withCredentials([
            string(credentialsId: 'browserstack-user', variable: 'BROWSERSTACK_USER'),
            string(credentialsId: 'browserstack-key', variable: 'BROWSERSTACK_ACCESS_KEY'),
            string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')
        ]) {
            sh 'echo "Environment ready"'
        }
    }
}
```

### Step 3: Install Dependencies

```groovy
stage('Install Dependencies') {
    steps {
        sh '''
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        '''
    }
}
```

### Step 4: Validate Configuration

```groovy
stage('Validate') {
    steps {
        sh '''
            source venv/bin/activate
            python3 -c "from src.config import Config; Config('config/config.yaml'); print('✅ Config valid')"
        '''
    }
}
```

### Step 5: Run Upload

```groovy
stage('Upload') {
    steps {
        sh '''
            source venv/bin/activate
            python3 src/main.py \
                --platform ${PLATFORM} \
                --environment ${ENVIRONMENT} \
                --build-type ${BUILD_TYPE} \
                --app-variant ${APP_VARIANT} \
                --version ${VERSION} \
                --build-id ${BUILD_ID} \
                --source-build-url ${BUILD_URL} \
                --output-file result.json \
                --verbose
        '''
    }
}
```

### Step 6: Archive Results

```groovy
stage('Archive') {
    steps {
        archiveArtifacts artifacts: 'result.json'
        archiveArtifacts artifacts: 'logs/**/*'
    }
}
```

### Step 7: Notify Results

```groovy
stage('Notify') {
    steps {
        script {
            def result = readJSON file: 'result.json'
            if (result.status == 'SUCCESS') {
                echo "✅ Upload successful!"
                echo "App ID: ${result.browserstack.app_id}"
            } else {
                echo "❌ Upload failed!"
                currentBuild.result = 'FAILURE'
            }
        }
    }
}
```

## Pipeline Parameters

Most pipelines accept these parameters:

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `PLATFORM` | Choice | android, ios | Mobile platform |
| `ENVIRONMENT` | Choice | staging, production | Target environment |
| `BUILD_TYPE` | Choice | Debug, Release | Build type |
| `APP_VARIANT` | Choice | agent, retail, wallet | App variant |
| `VERSION` | String | 1.0.0 | App version |
| `BUILD_ID` | String | jenkins-123 | Build identifier |

## Credentials Management

Pipelines use Jenkins credentials to securely manage secrets:

### Setting Up Credentials

1. In Jenkins, go to **Manage Jenkins** → **Manage Credentials**
2. Select **System** → **Global credentials**
3. Click **Add Credentials**

Create these credentials:

| Credential | Type | ID | Value |
|-----------|------|-----|-------|
| BrowserStack User | Secret text | browserstack-user | Your BrowserStack username |
| BrowserStack Key | Secret text | browserstack-key | Your BrowserStack API key |
| GitHub Token | Secret text | github-token | Your GitHub personal access token |
| Teams Webhook | Secret text | teams-webhook-url | Your Teams webhook URL (optional) |

### Using Credentials in Pipeline

```groovy
withCredentials([
    string(credentialsId: 'browserstack-user', variable: 'BROWSERSTACK_USER'),
    string(credentialsId: 'browserstack-key', variable: 'BROWSERSTACK_ACCESS_KEY'),
    string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')
]) {
    // Credentials available as environment variables
    sh 'python3 src/main.py ...'
}
```

## Environment Variables

Available in pipeline:

```groovy
// Jenkins built-in variables
${BUILD_ID}         // Jenkins build ID (e.g., 123)
${BUILD_URL}        // Full URL to the build
${WORKSPACE}        // Jenkins workspace directory
${GIT_BRANCH}       // Git branch name
${GIT_COMMIT}       // Git commit hash

// Custom variables (set in pipeline)
${PLATFORM}         // android, ios, android_hw
${ENVIRONMENT}      // staging, production
${BUILD_TYPE}       // Debug, Release
${APP_VARIANT}      // agent, retail, wallet
${VERSION}          // Semantic version (1.0.0)
```

## Triggering Pipelines

### Manually

1. Click **Build with Parameters** in Jenkins UI
2. Fill in parameter values
3. Click **Build**

### Via Git Webhook

Automatically trigger on push to branch:

1. In your Git repository settings
2. Add webhook pointing to: `http://jenkins.example.com/github-webhook/`
3. Select events: Push events
4. Pipeline will trigger on push

### Via API

```bash
curl -X POST \
  -u "username:password" \
  "http://jenkins.example.com/job/bstack-uploader/buildWithParameters" \
  -d "PLATFORM=android&ENVIRONMENT=staging&BUILD_TYPE=Debug&..."
```

### Scheduled (Cron)

In Jenkinsfile:

```groovy
triggers {
    cron('H 2 * * *')  // Run daily at 2 AM
}
```

## Pipeline Examples

### Example 1: Android Staging Upload

Parameters:
- PLATFORM: `android`
- ENVIRONMENT: `staging`
- BUILD_TYPE: `Debug`
- APP_VARIANT: `agent`
- VERSION: `1.0.0`

### Example 2: iOS Production Release

Parameters:
- PLATFORM: `ios`
- ENVIRONMENT: `production`
- BUILD_TYPE: `Release`
- APP_VARIANT: `retail`
- VERSION: `2.0.0`

### Example 3: Batch Upload

Modify pipeline to loop through multiple variants:

```groovy
stage('Batch Upload') {
    steps {
        script {
            def variants = ['agent', 'retail', 'wallet']
            for (variant in variants) {
                sh """
                    python3 src/main.py \
                        --platform android \
                        --environment production \
                        --build-type Release \
                        --app-variant ${variant} \
                        --version ${VERSION} \
                        --build-id jenkins-\${BUILD_ID} \
                        --source-build-url ${BUILD_URL}
                """
            }
        }
    }
}
```

## Monitoring & Logging

### View Build Logs

1. Open Jenkins job
2. Click on build number
3. Click **Console Output**
4. Search for specific text

### Archive Logs

Pipelines automatically archive:
- `result.json` - Upload results
- `logs/` directory - Application logs

Access from Jenkins UI:
1. Open build
2. Click **Artifacts**
3. Download archived files

### Monitoring Dashboard

Set up Jenkins monitoring to track:
- Build success/failure rate
- Upload duration
- Error trends

## Best Practices

### 1. Use Parameters

Make pipelines flexible with parameters:

```groovy
properties([
    parameters([
        choice(name: 'PLATFORM', choices: ['android', 'ios', 'android_hw']),
        choice(name: 'ENVIRONMENT', choices: ['staging', 'production']),
        choice(name: 'BUILD_TYPE', choices: ['Debug', 'Release']),
        choice(name: 'APP_VARIANT', choices: ['agent', 'retail', 'wallet']),
        string(name: 'VERSION', defaultValue: '1.0.0'),
    ])
])
```

### 2. Validate Early

Check configuration before running upload:

```groovy
stage('Validate') {
    steps {
        sh 'python3 -c "from src.config import Config; Config(...)"'
    }
}
```

### 3. Use Credentials Plugin

Store secrets securely, never hardcode:

```groovy
// ✅ Good
withCredentials([string(credentialsId: 'token', variable: 'TOKEN')]) {
    sh 'echo $TOKEN'  // Secret is masked in logs
}

// ❌ Bad - Don't do this!
sh 'export TOKEN=abc123xyz; ...'  // Visible in logs
```

### 4. Archive Results

Save artifacts for post-build analysis:

```groovy
stage('Archive') {
    steps {
        archiveArtifacts artifacts: '**/*.json,logs/**/*'
    }
}
```

### 5. Handle Failures Gracefully

Use try-catch or post sections:

```groovy
post {
    failure {
        sh 'cat logs/browserstack_uploader.log'
        // Notify team of failure
    }
    success {
        // Notify team of success
    }
    always {
        // Cleanup
        sh 'rm -rf venv'
    }
}
```

### 6. Use Timeouts

Prevent hanging builds:

```groovy
options {
    timeout(time: 30, unit: 'MINUTES')
}
```

## Troubleshooting

### Pipeline Fails to Start

**Check**:
1. Jenkins credentials are set up
2. Pipeline file exists in repository
3. Jenkins has Python installed
4. Workspace has permissions

### Upload Fails in Pipeline

**Check**:
1. Credentials are accessible in pipeline
2. Configuration file is in workspace
3. Artifact file exists at expected path
4. Network connectivity to BrowserStack

**Debug**:
```bash
# Add verbose logging to pipeline
--verbose

# Check logs
cat logs/browserstack_uploader.log
```

### Out of Memory

**If seeing memory errors**:
1. Reduce container/pod memory usage
2. Increase Jenkins agent memory
3. Process smaller apps per build

## Related Documentation

- [SETUP.md](SETUP.md) - How to set up each variant
- [docs/SETUP.md](../docs/SETUP.md) - General project setup
- [docs/USAGE.md](../docs/USAGE.md) - Tool usage reference
- [docs/CONFIGURATION.md](../docs/CONFIGURATION.md) - Configuration reference
- [examples/](../examples/) - Code examples

## Next Steps

1. **Choose your variant**: Kubernetes, Docker, or Shell
2. **Follow setup guide**: See [SETUP.md](SETUP.md)
3. **Configure credentials**: Set up in Jenkins
4. **Create pipeline job**: Copy Jenkinsfile to your repo
5. **Test it**: Run a manual build
6. **Monitor**: Check logs and results

## Quick Reference

### Parameter Templates

**Android Staging**:
```
PLATFORM=android ENVIRONMENT=staging BUILD_TYPE=Debug APP_VARIANT=agent VERSION=1.0.0
```

**iOS Production**:
```
PLATFORM=ios ENVIRONMENT=production BUILD_TYPE=Release APP_VARIANT=retail VERSION=2.0.0
```

**Huawei Android**:
```
PLATFORM=android_hw ENVIRONMENT=staging BUILD_TYPE=Release APP_VARIANT=wallet VERSION=1.5.0
```

## Support

For issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Enable verbose logging (`--verbose`)
3. Check logs in `logs/` directory
4. See related [docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)

---

**Ready to integrate with Jenkins?** See [SETUP.md](SETUP.md) for your chosen variant.
