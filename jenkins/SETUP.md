# Jenkins Setup Guide

Complete guide to integrating BrowserStack Uploader with Jenkins CI/CD pipelines.

## Quick Start (30 Minutes)

If you're in a hurry, follow this quick setup:

### 1. DevOps Jenkins - Create Job (10 min)

1. Login to DevOps Jenkins
2. Create a new **Pipeline** job: `DevOps-BrowserStack-Upload`
3. Configure → Pipeline
4. Select "Pipeline script from SCM"
5. Set these values:
   - **Repository URL**: `https://github.com/your-org/devops-automation.git`
   - **Script Path**: `Jenkinsfile-DevOps-TriggerReady`
   - **Branch**: `main`
6. Click **Save**

### 2. DevOps Jenkins - Configure Credentials (5 min)

1. Go to **Manage Jenkins** → **Manage Credentials** → **Global**
2. Click **Add Credentials** for each:

| Credential | Type | ID | Value |
|-----------|------|-----|-------|
| BrowserStack User | Secret text | `browserstack-user` | Your BrowserStack username |
| BrowserStack Key | Secret text | `browserstack-access-key` | Your API key |
| GitHub Token | Secret text | `github-token` | Your GitHub token |
| Teams Webhook | Secret text | `teams-webhook-url` | Your Teams webhook (optional) |

### 3. App Build Job - Add Trigger (10 min)

1. Login to Dev Jenkins
2. Edit your App Build job
3. Go to **Post-build Actions**
4. Click **Add post-build action**
5. Select **Trigger parameterized build on other jobs**
6. Configure:
   - **Jenkins Instance URL**: `http://devops-jenkins.company.com:8080/`
   - **Job to build**: `DevOps-BrowserStack-Upload`
   - **Parameters**: (see APP_BUILD_JOB_SETUP.txt for details)
7. Click **Save**

### 4. Test (5 min)

1. Run your App Build job
2. After success, DevOps job should trigger automatically
3. Check DevOps Jenkins console for upload results

---

## Files in This Directory

| File | Purpose | Read Time |
|------|---------|-----------|
| [README.md](README.md) | Overview & features | 10 min |
| [SETUP.md](SETUP.md) | This file - quick setup | 30 min |
| APP_BUILD_JOB_SETUP.txt | How to configure App Build job | 15 min |
| JENKINS_CROSS_PIPELINE_SETUP.txt | Detailed cross-Jenkins setup | 20 min |
| JENKINS_INTEGRATION_SUMMARY.txt | Executive summary & architecture | 10 min |
| JENKINS_SETUP_FINAL.txt | Complete checklist & status | 15 min |
| Jenkinsfile-DevOps-TriggerReady | Production-ready pipeline | Reference |
| Jenkinsfile-Standard.groovy | Alternative pipeline | Reference |

---

## Detailed Setup by Deployment Model

### Model 1: Cross-Jenkins (Recommended)

**Setup**: App Build (Dev Jenkins) → BrowserStack Upload (DevOps Jenkins)

**When to use**:
- Separate Dev and DevOps Jenkins instances
- Want to decouple app builds from DevOps tasks
- Need different authentication/access

**Time**: 30-45 minutes

**Steps**:
1. Read: APP_BUILD_JOB_SETUP.txt
2. Read: JENKINS_CROSS_PIPELINE_SETUP.txt
3. Create DevOps Jenkins job
4. Configure credentials
5. Add trigger to App Build job
6. Test

**Files needed**:
- Jenkinsfile-DevOps-TriggerReady
- APP_BUILD_JOB_SETUP.txt
- JENKINS_CROSS_PIPELINE_SETUP.txt

### Model 2: Single Jenkins

**Setup**: App Build → BrowserStack Upload (same Jenkins)

**When to use**:
- Single Jenkins instance
- Simpler architecture
- Everything in one place

**Time**: 20-30 minutes

**Steps**:
1. Read: JENKINS_INTEGRATION_SUMMARY.txt
2. Create Pipeline job from Jenkinsfile-DevOps-TriggerReady
3. Configure credentials
4. Modify App Build job to trigger internally
5. Test

**Files needed**:
- Jenkinsfile-DevOps-TriggerReady
- JENKINS_INTEGRATION_SUMMARY.txt

---

## File Descriptions

### APP_BUILD_JOB_SETUP.txt

**What**: Step-by-step configuration for the App Build job

**Contains**:
- Parameter definitions (5 choice parameters)
- Post-build action setup
- Trigger configuration
- Copy-paste ready values
- Common issues & quick fixes

**Use when**: Setting up the source job that triggers uploads

**Key sections**:
- Step 1: Open App Build Job Configuration
- Step 2: Add Build Parameters
- Step 3: Add Post-Build Action
- Step 4: Configure Trigger
- Step 5: Test
- Troubleshooting

### JENKINS_CROSS_PIPELINE_SETUP.txt

**What**: Comprehensive cross-Jenkins pipeline integration

**Contains**:
- Architecture overview
- Detailed setup instructions (3 methods)
- Parameter flow diagrams
- Network & security setup
- Testing procedures
- Comprehensive troubleshooting
- Security considerations

**Use when**: Setting up cross-Jenkins communication

**Best for**: Understanding the full architecture

**Key sections**:
- Overview
- Quick Setup (30 min)
- Detailed Setup for App Build Job
- Detailed Setup for DevOps Pipeline
- Parameter Flow
- Error Handling
- Network Configuration
- Testing Procedures

### JENKINS_INTEGRATION_SUMMARY.txt

**What**: Executive overview and quick reference

**Contains**:
- Architecture diagram
- Parameter flow visualization
- Feature summary
- 7-stage pipeline overview
- Testing checklist
- Deployment checklist
- Quick 20-minute setup for advanced users

**Use when**: Need quick overview or want checklist

**Best for**: Quick reference and project overview

### JENKINS_SETUP_FINAL.txt

**What**: Complete setup status and verification checklist

**Contains**:
- What was delivered
- What it enables (architecture diagram)
- 7-parameter flow explanation
- 7-stage pipeline breakdown
- Key features overview
- 30-minute setup guide
- Testing checklist
- Security considerations
- Common issues & quick fixes
- Verification checklist

**Use when**: Complete verification or understanding current status

**Best for**: Verification and ensuring nothing is missed

### Jenkinsfile-DevOps-TriggerReady

**What**: Production-ready Declarative Pipeline

**Features**:
- 7 comprehensive stages
- Docker agent with Python 3.11
- Credentials integration
- Parameter handling
- Error handling and logging
- Artifact archiving
- Result reporting

**Modify**:
- Line 131: Change Git repo URL to your devops repo
- Line 73: Change artifact base path if needed
- Credential IDs (lines 66-69) if different from default

**Use in**: DevOps Jenkins job

### Jenkinsfile-Standard.groovy

**What**: Alternative pipeline for standard Docker setups

**Differences**:
- Simpler configuration
- Standard Docker agent
- Fewer dependencies
- Good for simple setups

**When to use**: If Jenkinsfile-DevOps-TriggerReady doesn't work for your setup

---

## Common Parameters Across All Pipelines

All Jenkinsfile variants accept these 7 parameters:

```groovy
PLATFORM          // Choice: android, android_hw, ios
ENVIRONMENT       // Choice: staging, production
BUILD_TYPE        // Choice: Debug, Release
APP_VARIANT       // Choice: agent, retail, wallet
VERSION           // String: Semantic version (1.0.0)
BUILD_ID          // String: Unique build identifier
SOURCE_BUILD_URL  // String: URL to source build
```

These are automatically passed from App Build job to DevOps job.

---

## Step-by-Step: Cross-Jenkins Setup

### For DevOps Jenkins

**Step 1**: Create Pipeline Job
```
Name: DevOps-BrowserStack-Upload
Type: Pipeline
```

**Step 2**: Configure Pipeline
```
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/your-org/devops-automation.git
Branch: main
Script Path: Jenkinsfile-DevOps-TriggerReady
```

**Step 3**: Add Global Credentials
```
Credential 1:
  Type: Secret text
  ID: browserstack-user
  Value: <your browserstack username>

Credential 2:
  Type: Secret text
  ID: browserstack-access-key
  Value: <your browserstack access key>

Credential 3:
  Type: Secret text
  ID: github-token
  Value: <your github token>

Credential 4:
  Type: Secret text
  ID: teams-webhook-url
  Value: <your teams webhook>
```

**Step 4**: Save and Test
```
Run "Build with Parameters"
Fill in test values
Verify successful execution
Check artifacts archived
```

### For App Build Job (Dev Jenkins)

**Step 1**: Add Parameters
```
Add 5 Choice Parameters:
  - PLATFORM (android, android_hw, ios)
  - ENVIRONMENT (staging, production)
  - BUILD_TYPE (Debug, Release)
  - APP_VARIANT (agent, retail, wallet)
  - VERSION (1.0.0)
```

**Step 2**: Add Post-Build Trigger
```
Post-build Actions → Add post-build action
Select: "Trigger parameterized build on other jobs"

Configure:
  Jenkins Instance URL: http://devops-jenkins.company.com:8080/
  Job to build: DevOps-BrowserStack-Upload

  Parameters:
    PLATFORM=${PLATFORM}
    ENVIRONMENT=${ENVIRONMENT}
    BUILD_TYPE=${BUILD_TYPE}
    APP_VARIANT=${APP_VARIANT}
    VERSION=${VERSION}
    BUILD_ID=${BUILD_NUMBER}
    SOURCE_BUILD_URL=${BUILD_URL}
```

**Step 3**: Test
```
Run app build job
Check if DevOps job triggers
Verify parameters passed correctly
Check final results
```

---

## Troubleshooting Quick Links

### Setup Issues
- See: JENKINS_CROSS_PIPELINE_SETUP.txt → Troubleshooting section
- See: APP_BUILD_JOB_SETUP.txt → Common Issues

### Parameter Issues
- See: JENKINS_INTEGRATION_SUMMARY.txt → Parameter Flow
- See: Jenkinsfile-DevOps-TriggerReady → lines 88-104

### Cross-Jenkins Communication
- See: JENKINS_CROSS_PIPELINE_SETUP.txt → Network Configuration
- See: JENKINS_INTEGRATION_SUMMARY.txt → Troubleshooting

### Pipeline Execution Issues
- Check console output in Jenkins
- Enable `--verbose` flag in Jenkinsfile
- See: jenkins/README.md → Troubleshooting

---

## Testing Your Setup

### Test 1: Manual Pipeline Trigger

```
1. Go to DevOps Jenkins
2. Navigate to "DevOps-BrowserStack-Upload"
3. Click "Build with Parameters"
4. Fill in test values:
   PLATFORM=android
   ENVIRONMENT=staging
   BUILD_TYPE=Debug
   APP_VARIANT=agent
   VERSION=1.0.0
5. Click "Build"
6. Watch console for success
7. Check artifacts archived
```

### Test 2: Cross-Jenkins Trigger

```
1. Go to Dev Jenkins
2. Run your App Build job
3. In console, should see: "Triggering job..."
4. Go to DevOps Jenkins
5. Check queue for new "DevOps-BrowserStack-Upload" build
6. Verify parameters in console
7. Wait for completion
8. Check BrowserStack for uploaded app
```

### Test 3: Full Workflow

```
1. Ensure all files are in place
2. Verify credentials are configured
3. Run full build from Dev Jenkins
4. Monitor entire pipeline
5. Check:
   - App uploaded to BrowserStack
   - YAML files updated
   - GitHub PR created
   - Teams notification sent
   - Audit trail created
```

---

## Next Steps

1. **Choose your setup**: Cross-Jenkins or Single Jenkins
2. **Read the relevant file**:
   - Cross-Jenkins: JENKINS_CROSS_PIPELINE_SETUP.txt
   - Single Jenkins: JENKINS_INTEGRATION_SUMMARY.txt
3. **Create the DevOps Jenkins job** (10 min)
4. **Configure credentials** (5 min)
5. **Add trigger to App Build job** (10 min)
6. **Test manually** (5 min)
7. **Test with real build** (5 min)

---

## Support Resources

**In this directory**:
- README.md - Overview and features
- APP_BUILD_JOB_SETUP.txt - App Build job configuration
- JENKINS_CROSS_PIPELINE_SETUP.txt - Detailed setup guide
- JENKINS_INTEGRATION_SUMMARY.txt - Executive overview

**In parent directories**:
- docs/SETUP.md - General project setup
- docs/USAGE.md - Tool usage
- docs/CONFIGURATION.md - Configuration reference
- docs/TROUBLESHOOTING.md - General troubleshooting

---

## Key Takeaways

✅ **Quick Setup**: 30 minutes from start to first test

✅ **Production Ready**: Jenkinsfile-DevOps-TriggerReady is tested

✅ **Secure**: Credentials stored in Jenkins, no hardcoding

✅ **Automated**: Entire workflow automated after trigger

✅ **Monitored**: Detailed logging and result archiving

✅ **Flexible**: Works with cross-Jenkins or single Jenkins

---

For detailed information, see the appropriate file above based on your setup needs.
