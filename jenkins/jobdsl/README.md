# JobDSL Scripts for BrowserStack Uploader

This directory contains JobDSL scripts that automate the creation and configuration of Jenkins jobs for the BrowserStack Uploader pipeline.

## Overview

JobDSL (Job Domain Specific Language) is a Groovy-based DSL that allows you to define Jenkins jobs programmatically. Instead of manually clicking through the Jenkins UI to configure jobs, you can version-control your job configurations as code.

## Files

- **`browserstack-uploader-multibranch.groovy`** - Main JobDSL script that creates a multi-branch pipeline job

## What Gets Created

When you run the seed job with this DSL script, it creates:

1. **Multi-Branch Pipeline Job** - `browserstack-uploader`
   - Automatically discovers branches in your Git repository
   - Creates sub-jobs for each branch
   - Scans for Jenkinsfile in each branch
   - Handles webhook triggers from GitHub/GitLab

2. **Manual Upload Job** (optional) - `browserstack-manual-upload`
   - Simple freestyle job for quick manual testing
   - Easy-to-use parameter form
   - No need to understand pipeline syntax

3. **Pipeline View** (optional) - `Pipeline-View`
   - Visual representation of the pipeline
   - Shows build status across branches
   - Real-time updates

## Prerequisites

Before using JobDSL scripts, ensure:

1. **Job DSL Plugin** is installed in Jenkins
   - Go to: Manage Jenkins → Plugin Manager → Available
   - Search for "Job DSL"
   - Install and restart Jenkins

2. **Required Credentials** are configured in Jenkins:
   - `browserstack-user` - BrowserStack username
   - `browserstack-access-key` - BrowserStack API key
   - `github-token` - GitHub personal access token
   - `github-credentials` - Git credentials for cloning
   - `teams-webhook-url` - Microsoft Teams webhook URL (optional)

3. **Git Plugin** and **Pipeline Plugin** are installed

## Setup Instructions

### Step 1: Create a Seed Job

1. **Open Jenkins** and go to your Jenkins dashboard

2. **Create New Job**:
   - Click "New Item"
   - Enter name: `seed-job-browserstack-uploader`
   - Select "Freestyle project"
   - Click "OK"

3. **Configure Source Code Management**:
   - Select "Git"
   - Repository URL: `https://github.com/devops-ind/bstack.git`
   - Credentials: Select your Git credentials
   - Branch: `*/main` (or your default branch)

4. **Add Build Step**:
   - Click "Add build step" → "Process Job DSLs"
   - Select "Look on Filesystem"
   - DSL Scripts: `jenkins/jobdsl/browserstack-uploader-multibranch.groovy`

5. **Advanced Options** (expand "Advanced" in the DSL build step):
   - Action for removed jobs: `Delete`
   - Action for removed views: `Delete`
   - Check "Enable script security for Job DSL scripts" (if using sandboxed mode)

6. **Save** the seed job

### Step 2: Configure the DSL Script

Before running the seed job, review and customize the configuration in `browserstack-uploader-multibranch.groovy`:

```groovy
def jobConfig = [
    // Job configuration
    jobName: 'browserstack-uploader',  // Change job name if needed

    // Git repository
    gitRepo: 'https://github.com/devops-ind/bstack.git',  // Your repo URL
    gitCredentialsId: 'github-credentials',  // Your Git credentials ID

    // Jenkinsfile location
    jenkinsfilePath: 'jenkins/Jenkinsfile-DevOps-TriggerReady',  // Path to Jenkinsfile

    // Branch filtering
    branchInclude: '*',  // Which branches to include
    branchExclude: '',   // Which branches to exclude

    // Credentials
    credentials: [
        browserstackUser: 'browserstack-user',      // Your credential IDs
        browserstackKey: 'browserstack-access-key',
        githubToken: 'github-token',
        teamsWebhook: 'teams-webhook-url'
    ],

    // Folder organization
    folderName: 'Mobile-DevOps',  // Set to '' for root level
]
```

### Step 3: Run the Seed Job

1. Go to the seed job: `seed-job-browserstack-uploader`
2. Click "Build Now"
3. Wait for the build to complete
4. Check the console output for confirmation

You should see output like:
```
Created Jobs:
  ✓ Multi-branch Pipeline: Mobile-DevOps/browserstack-uploader
  ✓ Manual Upload Job: Mobile-DevOps/browserstack-manual-upload
  ✓ Pipeline View: Mobile-DevOps/Pipeline-View
```

### Step 4: Verify Job Creation

1. Go to Jenkins dashboard
2. Navigate to the folder (if you specified one): `Mobile-DevOps`
3. You should see:
   - `browserstack-uploader` (multi-branch pipeline)
   - `browserstack-manual-upload` (freestyle job)
   - `Pipeline-View` (build pipeline view)

### Step 5: Configure Webhook (Optional but Recommended)

To enable automatic builds on Git push:

1. **In GitHub/GitLab**:
   - Go to: Repository → Settings → Webhooks
   - Add webhook URL: `http://your-jenkins.com/github-webhook/`
   - Content type: `application/json`
   - Events: Select "Just the push event"
   - Click "Add webhook"

2. **In Jenkins**:
   - The multi-branch job will automatically detect webhook triggers
   - No additional configuration needed in Jenkins

### Step 6: Initial Branch Scan

1. Open the multi-branch pipeline job
2. Click "Scan Repository Now"
3. Jenkins will:
   - Scan all branches in your Git repository
   - Look for the Jenkinsfile in each branch
   - Create sub-jobs for branches containing the Jenkinsfile
   - Display discovered branches in the job view

## Usage

### Running a Build

**Option 1: Via Multi-Branch Pipeline** (Recommended)

1. Go to `Mobile-DevOps/browserstack-uploader`
2. Select a branch (e.g., `main`)
3. Click "Build with Parameters"
4. Fill in the parameters:
   - Platform: `android`, `ios`, or `android_hw`
   - Environment: `staging` or `production`
   - Build Type: `Debug` or `Release`
   - App Variant: `agent`, `retail`, or `wallet`
   - Build ID: e.g., `jenkins-1234`
   - Source Build URL: e.g., `https://jenkins.example.com/job/build/123`
   - srcFolder: NFS location (optional)
5. Click "Build"

**Option 2: Via Manual Upload Job** (Quick Testing)

1. Go to `Mobile-DevOps/browserstack-manual-upload`
2. Click "Build with Parameters"
3. Fill in parameters (same as above)
4. Click "Build"

**Option 3: Via Git Push** (Automatic)

1. Push changes to your Git repository
2. Webhook triggers Jenkins
3. Build starts automatically
4. Parameters can be set via commit message or default values

### Triggering from Another Job

You can trigger the BrowserStack upload from another Jenkins job (e.g., from an app build job):

```groovy
// In your app build Jenkinsfile
stage('Upload to BrowserStack') {
    steps {
        build job: 'Mobile-DevOps/browserstack-uploader/main',
              parameters: [
                  string(name: 'PLATFORM', value: 'android'),
                  string(name: 'ENVIRONMENT', value: 'staging'),
                  string(name: 'BUILD_TYPE', value: 'Release'),
                  string(name: 'APP_VARIANT', value: 'agent'),
                  string(name: 'BUILD_ID', value: "${BUILD_ID}"),
                  string(name: 'SOURCE_BUILD_URL', value: "${BUILD_URL}"),
                  string(name: 'srcFolder', value: '\\\\192.1.6.8\\Builds\\MobileApp\\Nightly_Builds\\mainline')
              ],
              wait: true  // Wait for completion
    }
}
```

### Via REST API

```bash
curl -X POST \
  -u "username:api-token" \
  "http://jenkins.example.com/job/Mobile-DevOps/job/browserstack-uploader/job/main/buildWithParameters" \
  -d "PLATFORM=android" \
  -d "ENVIRONMENT=staging" \
  -d "BUILD_TYPE=Release" \
  -d "APP_VARIANT=agent" \
  -d "BUILD_ID=jenkins-1234" \
  -d "SOURCE_BUILD_URL=https://jenkins.example.com/job/build/123" \
  -d "srcFolder=\\\\192.1.6.8\\Builds\\MobileApp\\Nightly_Builds\\mainline"
```

## Configuration Options

### Branch Filtering

Control which branches trigger builds:

```groovy
// Include only main and develop branches
branchInclude: 'main develop'

// Include all feature branches
branchInclude: 'main develop feature/*'

// Include all branches
branchInclude: '*'

// Exclude specific branches
branchExclude: 'experimental/* temp/*'
```

### Build Retention

Control how many builds to keep:

```groovy
buildDaysToKeep: 30,  // Keep builds for 30 days
buildNumToKeep: 20,   // Keep last 20 builds
```

### Scan Interval

Control how often Jenkins scans for changes:

```groovy
// Scan every 1 hour
scanInterval: '1 hour'

// Scan every 15 minutes
scanInterval: '15 minutes'

// Scan every day
scanInterval: '1 day'

// Immediate (with webhook)
scanWebhook: true
```

### Folder Organization

Organize jobs in folders:

```groovy
// Create job in folder
folderName: 'Mobile-DevOps'

// Create job at root level
folderName: ''
```

## Updating Jobs

When you need to update job configuration:

1. **Modify the DSL script** in Git
   - Edit `jenkins/jobdsl/browserstack-uploader-multibranch.groovy`
   - Commit and push changes

2. **Re-run the seed job**
   - Go to: `seed-job-browserstack-uploader`
   - Click "Build Now"
   - Jenkins will update existing jobs with new configuration

3. **Verify changes**
   - Check the updated jobs
   - Verify configuration matches your changes

**Note**: JobDSL will update existing jobs, not create duplicates.

## Troubleshooting

### Seed Job Fails with "Script Security" Error

**Problem**: JobDSL script is blocked by script security

**Solution**:
1. Go to: Manage Jenkins → In-process Script Approval
2. Find the pending approval
3. Click "Approve"
4. Re-run the seed job

### Jobs Not Created

**Problem**: Seed job completes but no jobs appear

**Solution**:
1. Check seed job console output for errors
2. Verify DSL script syntax is correct
3. Check Jenkins logs: Manage Jenkins → System Log
4. Ensure Job DSL plugin is installed

### Git Credentials Not Working

**Problem**: Cannot clone repository

**Solution**:
1. Verify credential ID matches exactly: `github-credentials`
2. Test credentials: Jenkins → Credentials → Test connection
3. Ensure credential type is correct (Username/Password or SSH key)

### Webhook Not Triggering Builds

**Problem**: Git push doesn't trigger build

**Solution**:
1. Verify webhook URL is correct: `http://jenkins.com/github-webhook/`
2. Check GitHub webhook delivery logs
3. Ensure Jenkins is accessible from internet (or use GitHub Apps)
4. Check Jenkins system log for webhook events

### Branch Not Discovered

**Problem**: Branch exists but doesn't appear in Jenkins

**Solution**:
1. Check branch filter: `branchInclude` and `branchExclude`
2. Verify Jenkinsfile exists at correct path in branch
3. Click "Scan Repository Now" to force scan
4. Check Jenkins console output for scan results

### Parameters Not Showing

**Problem**: "Build with Parameters" shows no parameters

**Solution**:
1. Parameters are defined in Jenkinsfile, not DSL script
2. Verify Jenkinsfile has `parameters` block
3. Run build once to initialize parameters
4. Refresh page after first build

## Advanced Configuration

### Multiple Jenkinsfiles

To create jobs for multiple Jenkinsfiles:

```groovy
// Job for standard workflow
multibranchPipelineJob('browserstack-standard') {
    factory {
        workflowBranchProjectFactory {
            scriptPath('jenkins/Jenkinsfile-Standard.groovy')
        }
    }
}

// Job for trigger-ready workflow
multibranchPipelineJob('browserstack-trigger-ready') {
    factory {
        workflowBranchProjectFactory {
            scriptPath('jenkins/Jenkinsfile-DevOps-TriggerReady')
        }
    }
}
```

### Pull Request Discovery

To build pull requests automatically:

```groovy
traits {
    gitBranchDiscovery()

    // Enable PR discovery
    gitHubPullRequestDiscovery {
        strategyId(1)  // Merge PR with target branch
    }
}
```

### Custom Build Parameters

Add custom parameters in your Jenkinsfile:

```groovy
parameters {
    string(name: 'CUSTOM_PARAM', defaultValue: 'value', description: 'Custom parameter')
}
```

## Security Best Practices

1. **Never hardcode secrets** in DSL scripts
   - Use Jenkins Credentials plugin
   - Reference credentials by ID only

2. **Use script security**
   - Enable script security in Jenkins
   - Review and approve scripts

3. **Limit seed job access**
   - Only trusted users should run seed jobs
   - Seed jobs can create/modify any job

4. **Version control DSL scripts**
   - Keep DSL scripts in Git
   - Review changes via pull requests

## Related Documentation

- [Jenkins README](../README.md) - Jenkins integration overview
- [Jenkinsfile-DevOps-TriggerReady](../Jenkinsfile-DevOps-TriggerReady) - Main Jenkinsfile
- [Job DSL Plugin Documentation](https://plugins.jenkins.io/job-dsl/)
- [Multi-Branch Pipeline Plugin](https://plugins.jenkins.io/workflow-multibranch/)

## Example Workflow

Complete workflow from setup to production:

```bash
# 1. Install Job DSL plugin in Jenkins

# 2. Create Jenkins credentials

# 3. Create seed job in Jenkins UI

# 4. Commit DSL script to Git
git add jenkins/jobdsl/browserstack-uploader-multibranch.groovy
git commit -m "Add JobDSL for BrowserStack uploader"
git push

# 5. Run seed job
# (via Jenkins UI)

# 6. Configure webhook in GitHub
# (via GitHub Settings)

# 7. Scan repository
# (via Jenkins UI: "Scan Repository Now")

# 8. Make a code change and push
git commit -m "Update config"
git push

# 9. Jenkins automatically triggers build via webhook

# 10. View results in Jenkins
```

## Support

For issues with JobDSL:
1. Check [Troubleshooting](#troubleshooting) section above
2. Review Job DSL plugin documentation
3. Check Jenkins system logs
4. Validate DSL syntax using Job DSL Playground

---

**Ready to automate your Jenkins jobs?** Follow the [Setup Instructions](#setup-instructions) above to get started!
