/**
 * JobDSL Script for BrowserStack Uploader Multi-Branch Pipeline
 *
 * This script creates a multi-branch pipeline job that:
 * - Scans Git repository for branches
 * - Discovers Jenkinsfile in each branch
 * - Creates individual jobs for each branch
 * - Handles webhook triggers from Git
 * - Manages credentials securely
 *
 * Usage:
 * 1. Create a Jenkins Seed Job
 * 2. Configure it to process this DSL script
 * 3. Run the seed job to create the multi-branch pipeline
 */

// ==============================================================================
// CONFIGURATION - Modify these values for your environment
// ==============================================================================

def jobConfig = [
    // Job configuration
    jobName: 'browserstack-uploader',
    jobDisplayName: 'BrowserStack Artifact Uploader',
    jobDescription: '''
        Multi-branch pipeline for uploading mobile app artifacts to BrowserStack.

        Features:
        - Automatic branch discovery
        - Webhook-triggered builds
        - NFS artifact support
        - GitHub PR integration
        - Teams notifications

        Supported Platforms: Android, iOS, Huawei Android
        Supported Workflows: PR creation or direct commit
    ''',

    // Git repository configuration
    gitRepo: 'https://github.com/devops-ind/bstack.git',
    gitCredentialsId: 'github-credentials',  // Jenkins credential ID for Git access

    // Branch discovery
    branchInclude: '*',  // Include all branches (or use 'main develop feature/*')
    branchExclude: '',   // Exclude specific branches if needed

    // Jenkinsfile location
    jenkinsfilePath: 'jenkins/Jenkinsfile-DevOps-TriggerReady',  // Path to Jenkinsfile in repo

    // Build configuration
    buildDaysToKeep: 30,
    buildNumToKeep: 20,

    // Scan configuration
    scanInterval: '1 hour',  // How often to scan for new branches/changes
    scanWebhook: true,       // Enable webhook scanning

    // Credentials (Jenkins Credential IDs)
    credentials: [
        browserstackUser: 'browserstack-user',
        browserstackKey: 'browserstack-access-key',
        githubToken: 'github-token',
        teamsWebhook: 'teams-webhook-url'
    ],

    // Pipeline triggers
    enableWebhook: true,
    enableScheduled: false,  // Set to true for scheduled builds
    scheduleCron: 'H 2 * * *',  // Daily at 2 AM (if enableScheduled = true)

    // Folder organization (optional)
    folderName: 'Mobile-DevOps',  // Set to '' to create job at root level
    folderDisplayName: 'Mobile DevOps',
    folderDescription: 'Mobile application DevOps automation jobs'
]

// ==============================================================================
// FOLDER CREATION (Optional)
// ==============================================================================

if (jobConfig.folderName) {
    folder(jobConfig.folderName) {
        displayName(jobConfig.folderDisplayName)
        description(jobConfig.folderDescription)
    }
}

// ==============================================================================
// MULTI-BRANCH PIPELINE JOB DEFINITION
// ==============================================================================

def fullJobPath = jobConfig.folderName ? "${jobConfig.folderName}/${jobConfig.jobName}" : jobConfig.jobName

multibranchPipelineJob(fullJobPath) {

    // Display configuration
    displayName(jobConfig.jobDisplayName)
    description(jobConfig.jobDescription)

    // ==============================================================================
    // BRANCH SOURCES - Git Repository Configuration
    // ==============================================================================

    branchSources {
        git {
            id('bstack-repo')  // Unique identifier for this branch source
            remote(jobConfig.gitRepo)

            // Credentials for Git access (if private repo)
            if (jobConfig.gitCredentialsId) {
                credentialsId(jobConfig.gitCredentialsId)
            }

            // Branch discovery
            traits {
                // Discover branches
                gitBranchDiscovery()

                // Discover pull requests (optional)
                // gitHubPullRequestDiscovery {
                //     strategyId(1)  // Merge PR with current target branch
                // }

                // Branch filtering
                headWildcardFilter {
                    includes(jobConfig.branchInclude)
                    excludes(jobConfig.branchExclude)
                }

                // Clean checkout
                cleanBeforeCheckout()

                // Wipe workspace
                wipeWorkspace()
            }
        }
    }

    // ==============================================================================
    // BUILD CONFIGURATION
    // ==============================================================================

    // Discard old builds to save disk space
    orphanedItemStrategy {
        discardOldItems {
            daysToKeep(jobConfig.buildDaysToKeep)
            numToKeep(jobConfig.buildNumToKeep)
        }
    }

    // ==============================================================================
    // TRIGGERS - Webhook and Scheduled
    // ==============================================================================

    triggers {
        if (jobConfig.scanWebhook) {
            // Automatically scan for changes when webhook is triggered
            // Configure webhook in GitHub: Settings → Webhooks → Add webhook
            // URL: http://jenkins.example.com/github-webhook/
            periodic(1)  // Scan every 1 minute if webhook enabled
        } else {
            // Periodic scan for branches (less frequent)
            periodic(jobConfig.scanInterval)
        }
    }

    // ==============================================================================
    // FACTORY - Jenkinsfile Location
    // ==============================================================================

    factory {
        workflowBranchProjectFactory {
            scriptPath(jobConfig.jenkinsfilePath)
        }
    }

    // ==============================================================================
    // PROPERTIES - Additional Job Configuration
    // ==============================================================================

    configure { node ->
        // Add properties node for additional configuration
        def propertiesNode = node / 'properties'

        // Disable concurrent builds to prevent conflicts
        propertiesNode << 'org.jenkinsci.plugins.workflow.multibranch.DurabilityHintBranchProperty' {
            hint('PERFORMANCE_OPTIMIZED')
        }

        // Configure build triggers
        if (jobConfig.enableScheduled) {
            propertiesNode << 'org.jenkinsci.plugins.workflow.multibranch.PipelineTriggers' {
                triggers {
                    'hudson.triggers.TimerTrigger' {
                        spec(jobConfig.scheduleCron)
                    }
                }
            }
        }
    }
}

// ==============================================================================
// ADDITIONAL HELPER JOBS (Optional)
// ==============================================================================

/**
 * Create a freestyle job to test BrowserStack uploader manually
 * This provides a simple UI for developers to trigger uploads
 */
if (jobConfig.folderName) {
    freeStyleJob("${jobConfig.folderName}/browserstack-manual-upload") {
        displayName('BrowserStack Manual Upload (Quick Test)')
        description('Quick manual upload job for testing BrowserStack uploader')

        parameters {
            choiceParam('PLATFORM', ['android', 'android_hw', 'ios'], 'Mobile platform')
            choiceParam('ENVIRONMENT', ['staging', 'production'], 'Target environment')
            choiceParam('BUILD_TYPE', ['Debug', 'Release'], 'Build type')
            choiceParam('APP_VARIANT', ['agent', 'retail', 'wallet'], 'Application variant')
            stringParam('BUILD_ID', '', 'Build identifier (e.g., jenkins-1234)')
            stringParam('SOURCE_BUILD_URL', '', 'Source build URL for reference')
            stringParam('srcFolder', '', 'NFS location where APK/IPA artifacts are stored (optional)')
        }

        wrappers {
            credentialsBinding {
                string('BROWSERSTACK_USER', jobConfig.credentials.browserstackUser)
                string('BROWSERSTACK_ACCESS_KEY', jobConfig.credentials.browserstackKey)
                string('GITHUB_TOKEN', jobConfig.credentials.githubToken)
                string('TEAMS_WEBHOOK_URL', jobConfig.credentials.teamsWebhook)
            }
        }

        steps {
            shell('''#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║     BrowserStack Manual Upload - Quick Test           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Clone or update repo
if [ -d "bstack" ]; then
    cd bstack
    git pull origin main
else
    git clone https://github.com/devops-ind/bstack.git
    cd bstack
fi

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Build command
CMD="python3 src/main.py \
    --platform \\"${PLATFORM}\\" \
    --environment \\"${ENVIRONMENT}\\" \
    --build-type \\"${BUILD_TYPE}\\" \
    --app-variant \\"${APP_VARIANT}\\" \
    --build-id \\"${BUILD_ID}\\" \
    --source-build-url \\"${SOURCE_BUILD_URL}\\""

# Add src-folder if provided
if [ -n "${srcFolder}" ]; then
    CMD="$CMD --src-folder \\"${srcFolder}\\""
fi

# Add config and output
CMD="$CMD --config-file config/config.yaml \
    --output-file ../upload-result.json \
    --verbose"

# Execute
echo "🚀 Running upload..."
eval $CMD

echo ""
echo "✅ Upload completed successfully!"
''')
        }

        publishers {
            archiveArtifacts {
                pattern('upload-result.json')
                allowEmpty(true)
            }
        }
    }
}

/**
 * Create a pipeline view for better visualization
 */
if (jobConfig.folderName) {
    buildPipelineView("${jobConfig.folderName}/Pipeline-View") {
        displayName('BrowserStack Pipeline View')
        description('Visual pipeline view of BrowserStack upload workflow')
        filterBuildQueue()
        filterExecutors()
        title('BrowserStack Upload Pipeline')
        selectedJob("${jobConfig.folderName}/${jobConfig.jobName}")
        showPipelineParameters()
        refreshFrequency(5)
    }
}

// ==============================================================================
// LOGGING AND VALIDATION
// ==============================================================================

println """
╔════════════════════════════════════════════════════════════════════════════╗
║                    JobDSL Script Execution Complete                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Created Jobs:
  ✓ Multi-branch Pipeline: ${fullJobPath}
  ${jobConfig.folderName ? "✓ Manual Upload Job: ${jobConfig.folderName}/browserstack-manual-upload" : ''}
  ${jobConfig.folderName ? "✓ Pipeline View: ${jobConfig.folderName}/Pipeline-View" : ''}

Configuration:
  • Git Repository: ${jobConfig.gitRepo}
  • Jenkinsfile Path: ${jobConfig.jenkinsfilePath}
  • Branch Filter: ${jobConfig.branchInclude}
  • Webhook Enabled: ${jobConfig.enableWebhook}
  • Builds to Keep: ${jobConfig.buildNumToKeep}

Next Steps:
  1. Configure GitHub webhook (if not already done):
     URL: http://your-jenkins.com/github-webhook/

  2. Add Jenkins credentials (if not already done):
     - ${jobConfig.credentials.browserstackUser}
     - ${jobConfig.credentials.browserstackKey}
     - ${jobConfig.credentials.githubToken}
     - ${jobConfig.credentials.teamsWebhook}

  3. Trigger initial scan of repository:
     Jenkins UI → ${fullJobPath} → Scan Repository Now

  4. Test the pipeline:
     Navigate to job → Select branch → Build with Parameters

For documentation, see: jenkins/README.md
════════════════════════════════════════════════════════════════════════════
"""
