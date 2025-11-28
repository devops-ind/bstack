# JobDSL Quick Start Guide

Get your BrowserStack uploader multi-branch pipeline running in 5 minutes!

## 🚀 Fast Track Setup

### Prerequisites Checklist

- [ ] Jenkins installed and running
- [ ] Job DSL plugin installed
- [ ] Pipeline plugin installed
- [ ] Git plugin installed
- [ ] Access to create jobs in Jenkins

### Option 1: Freestyle Seed Job (Easiest)

**Step 1: Create Seed Job** (2 minutes)

1. Jenkins Dashboard → "New Item"
2. Name: `seed-browserstack-uploader`
3. Type: "Freestyle project"
4. Click "OK"

**Step 2: Configure Git Source** (1 minute)

1. Source Code Management → Git
   - Repository URL: `https://github.com/devops-ind/bstack.git`
   - Branch: `*/main`
   - Credentials: (select your Git credentials)

**Step 3: Add DSL Build Step** (1 minute)

1. Build → Add build step → "Process Job DSLs"
2. Select: "Look on Filesystem"
3. DSL Scripts: `jenkins/jobdsl/browserstack-uploader-multibranch.groovy`
4. Advanced:
   - Removed jobs: `Delete`
   - Removed views: `Delete`

**Step 4: Run Seed Job** (1 minute)

1. Click "Save"
2. Click "Build Now"
3. Wait for build to complete (green checkmark)

**Done!** ✅ Your multi-branch pipeline is created.

---

### Option 2: Pipeline Seed Job (Alternative)

**Step 1: Create Pipeline Job** (2 minutes)

1. Jenkins Dashboard → "New Item"
2. Name: `seed-browserstack-uploader`
3. Type: "Pipeline"
4. Click "OK"

**Step 2: Configure Pipeline from SCM** (2 minutes)

1. Pipeline section:
   - Definition: "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: `https://github.com/devops-ind/bstack.git`
   - Branch: `*/main`
   - Script Path: `jenkins/jobdsl/Jenkinsfile-Seed`

**Step 3: Run Seed Job** (1 minute)

1. Click "Save"
2. Click "Build Now"
3. Check console output for success message

**Done!** ✅ Your multi-branch pipeline is created.

---

## 🔐 Configure Credentials (Required)

After creating jobs, configure these credentials:

### Step 1: Open Credentials Manager

Jenkins → Manage Jenkins → Manage Credentials → System → Global credentials → Add Credentials

### Step 2: Add Required Credentials

| Credential ID | Type | Description | Example Value |
|--------------|------|-------------|---------------|
| `browserstack-user` | Secret text | BrowserStack username | `your_username` |
| `browserstack-access-key` | Secret text | BrowserStack API key | `abcdef123456` |
| `github-token` | Secret text | GitHub PAT | `ghp_xxxxxxxxxxxx` |
| `github-credentials` | Username/Password or SSH | Git clone access | (depends on your setup) |
| `teams-webhook-url` | Secret text | Teams webhook (optional) | `https://outlook.office.com/webhook/...` |

### How to Add Each Credential:

1. Click "Add Credentials"
2. Kind: Select "Secret text" (or appropriate type)
3. Scope: "Global"
4. Secret: Paste your secret value
5. ID: Enter the exact ID from table above
6. Description: Optional description
7. Click "OK"

**Repeat for all credentials.**

---

## 🔄 Initial Setup (One-Time)

### Step 1: Scan Repository

1. Go to: `Mobile-DevOps/browserstack-uploader`
2. Click "Scan Repository Now"
3. Wait for scan to complete
4. Branches will appear in the job view

### Step 2: Configure Webhook (Optional)

For automatic builds on Git push:

**In GitHub:**
1. Repository → Settings → Webhooks → Add webhook
2. Payload URL: `http://your-jenkins.com/github-webhook/`
3. Content type: `application/json`
4. Events: "Just the push event"
5. Active: ✅ Checked
6. Click "Add webhook"

**Test Webhook:**
- Make a small change and push to Git
- Check GitHub webhook delivery logs
- Check Jenkins for triggered build

---

## ✅ Verify Setup

### Check 1: Jobs Created

Navigate to Jenkins Dashboard. You should see:

```
Mobile-DevOps/
├── browserstack-uploader (multi-branch pipeline)
├── browserstack-manual-upload (freestyle job)
└── Pipeline-View (build pipeline view)
```

### Check 2: Branches Discovered

Open `Mobile-DevOps/browserstack-uploader`. You should see:
- List of branches (e.g., main, develop, feature/*)
- Status indicator for each branch
- Last build time

### Check 3: Credentials Configured

Manage Jenkins → Manage Credentials → System → Global credentials

You should see all 5 credentials listed.

---

## 🧪 Test Your Setup

### Test 1: Manual Build

1. Go to: `Mobile-DevOps/browserstack-manual-upload`
2. Click "Build with Parameters"
3. Fill in:
   - Platform: `android`
   - Environment: `staging`
   - Build Type: `Debug`
   - App Variant: `agent`
   - Build ID: `test-001`
   - Source Build URL: `http://test.com`
   - srcFolder: (leave empty for now)
4. Click "Build"
5. Check console output

**Expected:** Build completes successfully or fails with clear error message

### Test 2: Multi-Branch Build

1. Go to: `Mobile-DevOps/browserstack-uploader`
2. Select branch: `main`
3. Click "Build with Parameters"
4. Fill in parameters (same as Test 1)
5. Click "Build"
6. Check console output

**Expected:** Pipeline executes all stages

### Test 3: Webhook Trigger

1. Make a small change to any file in Git
2. Commit and push
3. Check Jenkins within 1-2 minutes
4. Build should start automatically

**Expected:** Build triggered by Git push

---

## 📊 Common Workflows

### Workflow 1: Nightly Builds

Automatically upload artifacts every night:

1. Edit `jenkins/jobdsl/browserstack-uploader-multibranch.groovy`:
   ```groovy
   enableScheduled: true,
   scheduleCron: 'H 2 * * *',  // 2 AM daily
   ```

2. Re-run seed job to apply changes

### Workflow 2: Trigger from App Build

Trigger BrowserStack upload after app build completes:

In your app build Jenkinsfile:
```groovy
post {
    success {
        build job: 'Mobile-DevOps/browserstack-uploader/main',
              parameters: [
                  string(name: 'PLATFORM', value: 'android'),
                  string(name: 'ENVIRONMENT', value: 'staging'),
                  // ... other parameters
              ],
              wait: false  // Don't wait for completion
    }
}
```

### Workflow 3: Batch Upload Multiple Variants

Upload multiple app variants in sequence:

Create a new pipeline job that calls the uploader multiple times:
```groovy
['agent', 'retail', 'wallet'].each { variant ->
    build job: 'Mobile-DevOps/browserstack-uploader/main',
          parameters: [
              string(name: 'APP_VARIANT', value: variant),
              // ... other parameters
          ]
}
```

---

## 🔧 Customization

### Change Job Name

Edit `browserstack-uploader-multibranch.groovy`:
```groovy
jobName: 'my-custom-name',  // Change this
```

Re-run seed job.

### Change Folder Location

Edit `browserstack-uploader-multibranch.groovy`:
```groovy
folderName: 'My-Folder',  // Change this, or set to '' for root
```

Re-run seed job.

### Change Jenkinsfile Location

Edit `browserstack-uploader-multibranch.groovy`:
```groovy
jenkinsfilePath: 'path/to/my/Jenkinsfile',  // Change this
```

Re-run seed job.

### Filter Branches

Edit `browserstack-uploader-multibranch.groovy`:
```groovy
branchInclude: 'main develop feature/*',  // Only these branches
branchExclude: 'experimental/*',          // Exclude these
```

Re-run seed job.

---

## ❌ Troubleshooting

### Error: "Script security approval required"

**Solution:**
1. Manage Jenkins → In-process Script Approval
2. Find pending approval
3. Click "Approve"
4. Re-run seed job

### Error: "No such DSL method: multibranchPipelineJob"

**Solution:**
1. Install Job DSL plugin
2. Manage Jenkins → Plugin Manager → Available
3. Search "Job DSL"
4. Install and restart Jenkins

### Error: "Unable to clone repository"

**Solution:**
1. Check Git URL is correct
2. Verify credentials are configured
3. Test network connectivity
4. Check Jenkins has Git installed

### Error: "Credentials not found"

**Solution:**
1. Verify credential ID matches exactly
2. Check credentials are in "Global" scope
3. Verify credential type is correct
4. Re-create credential if needed

### Builds Not Triggered by Webhook

**Solution:**
1. Check webhook URL format: `http://jenkins.com/github-webhook/`
2. Verify webhook is active in GitHub
3. Check GitHub webhook delivery logs
4. Ensure Jenkins is accessible from internet

---

## 📚 Additional Resources

- **Detailed Guide**: [README.md](README.md)
- **Jenkins Integration**: [../README.md](../README.md)
- **JobDSL Plugin Docs**: https://plugins.jenkins.io/job-dsl/
- **Multi-Branch Pipeline**: https://plugins.jenkins.io/workflow-multibranch/

---

## 🎯 Success Checklist

After following this guide, you should have:

- [x] Seed job created and run successfully
- [x] Multi-branch pipeline job exists
- [x] Manual upload job exists
- [x] All credentials configured
- [x] Branches discovered
- [x] Webhook configured (optional)
- [x] Test build completed successfully

## 🎉 You're Done!

Your BrowserStack uploader multi-branch pipeline is ready to use!

**Next Steps:**
1. Integrate with your app build pipelines
2. Set up scheduled builds if needed
3. Monitor builds and optimize as needed

**Need Help?**
- Check [README.md](README.md) for detailed documentation
- Review console output for error details
- Check Jenkins system logs

---

*Time to complete: ~5 minutes* ⏱️
