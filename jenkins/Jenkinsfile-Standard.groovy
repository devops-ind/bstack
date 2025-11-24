pipeline {
    agent {
        // Use standard Docker agent instead of Kubernetes
        docker {
            image 'python:3.11-slim'
            args '-v /shared:/shared:ro -v /var/run/docker.sock:/var/run/docker.sock'
            reuseNode true
        }
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    parameters {
        choice(
            name: 'PLATFORM',
            choices: ['android', 'android_hw', 'ios'],
            description: 'Mobile platform'
        )
        choice(
            name: 'ENVIRONMENT',
            choices: ['production', 'staging'],
            description: 'Target environment'
        )
        choice(
            name: 'BUILD_TYPE',
            choices: ['Debug', 'Release'],
            description: 'Build type'
        )
        choice(
            name: 'APP_VARIANT',
            choices: ['agent', 'retail', 'wallet'],
            description: 'Application variant'
        )
        string(
            name: 'VERSION',
            defaultValue: '1.0.0',
            description: 'Application version (semantic: X.Y.Z)'
        )
        string(
            name: 'BUILD_ID',
            defaultValue: '${BUILD_NUMBER}',
            description: 'Build identifier'
        )
        string(
            name: 'SOURCE_BUILD_URL',
            defaultValue: '${BUILD_URL}',
            description: 'Source build URL'
        )
    }

    environment {
        // Credentials (set in Jenkins Credentials Manager)
        BROWSERSTACK_USER = credentials('browserstack-user')
        BROWSERSTACK_ACCESS_KEY = credentials('browserstack-access-key')
        GITHUB_TOKEN = credentials('github-token')
        TEAMS_WEBHOOK_URL = credentials('teams-webhook-url')
        
        // Paths
        DEVOPS_REPO = '/tmp/devops-browserstack-automation'
        WORKSPACE_ROOT = "${WORKSPACE}"
        ARTIFACT_BASE = '/shared/mobileapp/builds/mainline'
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    echo "════════════════════════════════════════════"
                    echo "BrowserStack Artifact Upload Automation"
                    echo "════════════════════════════════════════════"
                    echo ""
                    echo "Parameters:"
                    echo "  Platform:      ${params.PLATFORM}"
                    echo "  Environment:   ${params.ENVIRONMENT}"
                    echo "  Build Type:    ${params.BUILD_TYPE}"
                    echo "  App Variant:   ${params.APP_VARIANT}"
                    echo "  Version:       ${params.VERSION}"
                    echo "  Build ID:      ${params.BUILD_ID}"
                    echo "  Source Build:  ${params.SOURCE_BUILD_URL}"
                    echo ""
                    echo "Workspace: ${WORKSPACE_ROOT}"
                    echo "Build: ${BUILD_NUMBER}"
                }
            }
        }

        stage('Checkout DevOps Scripts') {
            steps {
                script {
                    sh '''
                        echo "Checking out DevOps scripts..."
                        rm -rf ${DEVOPS_REPO}
                        mkdir -p ${DEVOPS_REPO}
                        cd ${DEVOPS_REPO}
                        
                        # Clone the DevOps automation scripts
                        git clone https://github.com/your-org/devops-browserstack-automation.git .
                        
                        echo "✓ DevOps scripts checked out"
                        echo ""
                        echo "Contents:"
                        ls -la
                    '''
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh '''
                        echo "Installing Python dependencies..."
                        cd ${DEVOPS_REPO}
                        
                        # Upgrade pip
                        pip install --no-cache-dir -q --upgrade pip
                        
                        # Install dependencies
                        pip install --no-cache-dir -q -r requirements.txt
                        
                        # Verify installations
                        echo "✓ Verifying installations..."
                        python3 -c "import yaml; import requests; import git; print('✓ All dependencies installed successfully')"
                        
                        echo ""
                        python3 --version
                        pip list | grep -E "PyYAML|requests|GitPython"
                    '''
                }
            }
        }

        stage('Validate Parameters') {
            steps {
                script {
                    sh '''
                        echo "Validating parameters..."
                        cd ${DEVOPS_REPO}
                        
                        # Validation using Python script
                        python3 << 'EOF'
from utils import validate_parameters

params = {
    'platform': '${params.PLATFORM}',
    'environment': '${params.ENVIRONMENT}',
    'build_type': '${params.BUILD_TYPE}',
    'app_variant': '${params.APP_VARIANT}',
    'version': '${params.VERSION}',
    'build_id': '${params.BUILD_ID}',
    'source_build_url': '${params.SOURCE_BUILD_URL}'
}

print("\nParameter Validation:")
print("─" * 50)
for key, value in params.items():
    print(f"  {key:20} : {value}")
print("─" * 50)

errors = validate_parameters(params)
if errors:
    print("\n❌ Parameter validation FAILED:")
    for error in errors:
        print(f"  • {error}")
    exit(1)
else:
    print("\n✓ All parameters validated successfully")
EOF
                    '''
                }
            }
        }

        stage('Setup Configuration') {
            steps {
                script {
                    sh '''
                        echo "Setting up configuration..."
                        cd ${DEVOPS_REPO}
                        
                        # Verify config file exists
                        if [ ! -f config.yaml ]; then
                            echo "❌ config.yaml not found!"
                            exit 1
                        fi
                        
                        echo "✓ config.yaml found"
                        
                        # Export credentials as environment variables for config substitution
                        export BROWSERSTACK_USER="${BROWSERSTACK_USER}"
                        export BROWSERSTACK_ACCESS_KEY="${BROWSERSTACK_ACCESS_KEY}"
                        export GITHUB_TOKEN="${GITHUB_TOKEN}"
                        export TEAMS_WEBHOOK_URL="${TEAMS_WEBHOOK_URL}"
                        
                        # Verify paths
                        echo ""
                        echo "Verifying artifact paths..."
                        
                        ARTIFACT_PATH="${ARTIFACT_BASE}/${params.PLATFORM}/${params.ENVIRONMENT}/${params.BUILD_TYPE}"
                        
                        if [ ! -d "$ARTIFACT_PATH" ]; then
                            echo "⚠ Artifact directory doesn't exist yet: $ARTIFACT_PATH"
                            echo "  This is OK during first test"
                        else
                            echo "✓ Artifact directory exists: $ARTIFACT_PATH"
                            echo "  Contents:"
                            find "$ARTIFACT_PATH" -type f | head -5
                        fi
                    '''
                }
            }
        }

        stage('Execute Upload') {
            steps {
                script {
                    sh '''
                        echo ""
                        echo "════════════════════════════════════════════"
                        echo "Executing BrowserStack Upload"
                        echo "════════════════════════════════════════════"
                        echo ""
                        
                        cd ${DEVOPS_REPO}
                        
                        # Export credentials for config substitution
                        export BROWSERSTACK_USER="${BROWSERSTACK_USER}"
                        export BROWSERSTACK_ACCESS_KEY="${BROWSERSTACK_ACCESS_KEY}"
                        export GITHUB_TOKEN="${GITHUB_TOKEN}"
                        export TEAMS_WEBHOOK_URL="${TEAMS_WEBHOOK_URL}"
                        
                        # Run the uploader with all parameters
                        python3 browserstack-uploader.py \\
                          --platform "${params.PLATFORM}" \\
                          --environment "${params.ENVIRONMENT}" \\
                          --build-type "${params.BUILD_TYPE}" \\
                          --app-variant "${params.APP_VARIANT}" \\
                          --version "${params.VERSION}" \\
                          --build-id "${params.BUILD_ID}" \\
                          --source-build-url "${params.SOURCE_BUILD_URL}" \\
                          --config-file config.yaml \\
                          --output-file ${WORKSPACE_ROOT}/upload-result.json \\
                          --verbose
                        
                        RESULT=$?
                        
                        if [ $RESULT -ne 0 ]; then
                            echo ""
                            echo "❌ Upload failed with exit code: $RESULT"
                            exit 1
                        fi
                        
                        echo ""
                        echo "✓ Upload completed successfully"
                    '''
                }
            }
        }

        stage('Archive Results') {
            steps {
                script {
                    sh '''
                        echo ""
                        echo "════════════════════════════════════════════"
                        echo "Archiving Results"
                        echo "════════════════════════════════════════════"
                        echo ""
                        
                        cd ${DEVOPS_REPO}
                        
                        # Copy results to workspace
                        echo "Copying result files..."
                        cp ${WORKSPACE_ROOT}/upload-result.json ${WORKSPACE_ROOT}/ 2>/dev/null || true
                        
                        # Copy audit trail files
                        AUDIT_FILES=$(find . -name "audit-trail-*.json" -type f)
                        if [ -n "$AUDIT_FILES" ]; then
                            cp audit-trail-*.json ${WORKSPACE_ROOT}/ 2>/dev/null || true
                            echo "✓ Audit trail files copied"
                        fi
                        
                        # Display results
                        echo ""
                        if [ -f ${WORKSPACE_ROOT}/upload-result.json ]; then
                            echo "════════════════════════════════════════════"
                            echo "Upload Results"
                            echo "════════════════════════════════════════════"
                            python3 -m json.tool < ${WORKSPACE_ROOT}/upload-result.json | head -50
                            
                            # Extract key information
                            echo ""
                            echo "════════════════════════════════════════════"
                            echo "Summary"
                            echo "════════════════════════════════════════════"
                            python3 << 'SUMMARY'
import json

with open('${WORKSPACE_ROOT}/upload-result.json', 'r') as f:
    result = json.load(f)

print(f"Status:    {result.get('status')}")

if result.get('status') == 'SUCCESS':
    print(f"App ID:    {result.get('browserstack', {}).get('app_id', 'N/A')}")
    print(f"PR:        {result.get('pr', {}).get('pr_url', 'N/A')}")
    yaml_file = f"{result.get('params', {}).get('platform')}/{result.get('params', {}).get('app_variant')}.yml"
    print(f"YAML File: {yaml_file}")
else:
    print(f"Error:     {result.get('error', 'Unknown error')}")
    if 'details' in result:
        for detail in result.get('details', []):
            print(f"  - {detail}")
SUMMARY
                        fi
                    '''
                }
                
                // Archive artifacts for Jenkins
                archiveArtifacts artifacts: 'upload-result.json,audit-trail-*.json',
                                 allowEmptyArchive: true,
                                 onlyIfSuccessful: false
            }
        }
    }

    post {
        always {
            script {
                echo "Cleaning up..."
                
                // Clean up workspace in Docker container
                sh '''
                    echo "Removing temporary files..."
                    rm -rf ${DEVOPS_REPO}
                    
                    # Keep result files in workspace
                    ls -lh ${WORKSPACE_ROOT}/*.json 2>/dev/null | awk '{print $9}' || echo "No result files found"
                '''
            }
        }

        success {
            script {
                echo "✅ BrowserStack upload completed successfully"
                
                // Parse result JSON to extract key information
                sh '''
                    if [ -f ${WORKSPACE_ROOT}/upload-result.json ]; then
                        python3 << 'EXTRACT'
import json
import os

result_file = '${WORKSPACE_ROOT}/upload-result.json'

with open(result_file, 'r') as f:
    result = json.load(f)

if result.get('status') == 'SUCCESS':
    # Extract key information
    app_id = result.get('browserstack', {}).get('app_id', 'N/A')
    pr_url = result.get('pr', {}).get('pr_url', 'N/A')
    pr_number = result.get('pr', {}).get('pr_number', 'N/A')
    yaml_file = f"{result.get('params', {}).get('platform')}/{result.get('params', {}).get('app_variant')}.yml"
    
    # Write to Jenkins environment file for use in other steps
    with open('${WORKSPACE_ROOT}/build-info.env', 'w') as f:
        f.write(f"APP_ID={app_id}\\n")
        f.write(f"PR_URL={pr_url}\\n")
        f.write(f"PR_NUMBER={pr_number}\\n")
        f.write(f"YAML_FILE={yaml_file}\\n")
    
    print(f"Build info exported to build-info.env")
EXTRACT
                    fi
                '''
                
                // Update build description
                script {
                    try {
                        def result = readJSON file: "${WORKSPACE}/upload-result.json"
                        if (result.status == 'SUCCESS') {
                            def appId = result.browserstack?.app_id ?: "N/A"
                            def prUrl = result.pr?.pr_url ?: "N/A"
                            def yamlFile = "${result.params?.platform}/${result.params?.app_variant}.yml"
                            
                            currentBuild.description = """
Platform: ${params.PLATFORM}<br/>
App: ${params.APP_VARIANT}<br/>
Version: ${params.VERSION}<br/>
YAML File: <code>${yamlFile}</code><br/>
App ID: <code>${appId}</code><br/>
<a href="${prUrl}">View Pull Request</a>
"""
                        }
                    } catch (Exception e) {
                        echo "Warning: Could not update build description: ${e.message}"
                    }
                }
            }
        }

        failure {
            script {
                echo "❌ BrowserStack upload failed"
                
                // Try to extract error details
                sh '''
                    if [ -f ${WORKSPACE_ROOT}/upload-result.json ]; then
                        echo ""
                        echo "Error Details:"
                        echo "─────────────────────────────────────────────"
                        python3 -m json.tool < ${WORKSPACE_ROOT}/upload-result.json | grep -A 20 "error"
                    fi
                '''
                
                // Update build description with error
                script {
                    try {
                        def result = readJSON file: "${WORKSPACE}/upload-result.json"
                        currentBuild.description = """
<span style="color: red;"><b>FAILED</b></span><br/>
Platform: ${params.PLATFORM}<br/>
App: ${params.APP_VARIANT}<br/>
Error: ${result.error ?: 'Unknown error'}
"""
                    } catch (Exception e) {
                        echo "Warning: Could not update build description: ${e.message}"
                    }
                }
                
                // Send email notification
                emailext(
                    subject: "❌ BrowserStack Upload Failed - ${params.PLATFORM}/${params.APP_VARIANT}",
                    body: """
                    <h2>BrowserStack Upload Failed</h2>
                    <p><b>Build:</b> <a href="${BUILD_URL}">${BUILD_NUMBER}</a></p>
                    <p><b>Status:</b> FAILED</p>
                    <hr/>
                    <p><b>Parameters:</b></p>
                    <ul>
                        <li>Platform: ${params.PLATFORM}</li>
                        <li>App: ${params.APP_VARIANT}</li>
                        <li>Environment: ${params.ENVIRONMENT}</li>
                        <li>Build Type: ${params.BUILD_TYPE}</li>
                        <li>Version: ${params.VERSION}</li>
                    </ul>
                    <hr/>
                    <p>Please check the build logs for details:</p>
                    <p><a href="${BUILD_URL}console">${BUILD_URL}console</a></p>
                    """,
                    mimeType: 'text/html',
                    to: '${DEFAULT_RECIPIENTS}',
                    recipientProviders: [
                        developers(),
                        requestor(),
                        brokenBuildSuspects()
                    ]
                )
            }
        }

        unstable {
            script {
                echo "⚠ Build is unstable"
            }
        }

        cleanup {
            script {
                // Final cleanup
                cleanWs(
                    deleteDirs: true,
                    patterns: [[pattern: '/tmp/devops-browserstack-automation', type: 'INCLUDE']]
                )
            }
        }
    }
}
