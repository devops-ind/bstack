// Jenkinsfile for Standard Docker Setup
// Alternative pipeline for simpler Docker-based deployments
// Can be triggered by App Build Pipeline or manually with parameters
//
// This Jenkinsfile orchestrates the BrowserStack uploader which:
// 1. Validates input parameters
// 2. Checks artifact files exist and are valid
// 3. Uploads artifacts to BrowserStack
// 4. Updates YAML configuration files in Git
// 5. Creates pull requests in GitHub
// 6. Sends Teams notifications
// 7. Creates audit trails

pipeline {
    agent {
        // Use standard Docker agent (no special features needed)
        docker {
            image 'python:3.11-slim'
            args '-v /shared:/shared:ro'
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
        string(
            name: 'srcFolder',
            defaultValue: '',
            description: 'NFS location where APK/IPA artifacts are stored (e.g., \\\\192.1.6.8\\Builds\\MobileApp\\Nightly_Builds\\mainline)'
        )
    }

    environment {
        // Credentials (configure in Jenkins Credentials Manager)
        BROWSERSTACK_USER = credentials('browserstack-user')
        BROWSERSTACK_ACCESS_KEY = credentials('browserstack-access-key')
        GITHUB_TOKEN = credentials('github-token')
        TEAMS_WEBHOOK_URL = credentials('teams-webhook-url')

        // Paths
        DEVOPS_REPO = "${WORKSPACE}/bstack"
        CONFIG_FILE = "${WORKSPACE}/bstack/config/config.yaml"
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    echo "════════════════════════════════════════════════════════"
                    echo "BrowserStack Artifact Upload Automation"
                    echo "════════════════════════════════════════════════════════"
                    echo ""
                    echo "📋 Parameters:"
                    echo "   Platform:      ${params.PLATFORM}"
                    echo "   Environment:   ${params.ENVIRONMENT}"
                    echo "   Build Type:    ${params.BUILD_TYPE}"
                    echo "   App Variant:   ${params.APP_VARIANT}"
                    echo "   Version:       ${params.VERSION}"
                    echo "   Build ID:      ${params.BUILD_ID}"
                    echo "   Source Build:  ${params.SOURCE_BUILD_URL}"
                    if (params.srcFolder) {
                        echo "   Source Folder: ${params.srcFolder}"
                    }
                    echo ""
                }
            }
        }

        stage('Checkout Repository') {
            steps {
                script {
                    echo "📦 STAGE: Checkout Repository"
                    echo "════════════════════════════════════════════════════════"

                    sh '''
                        # Clone or update the bstack repository
                        if [ -d "${DEVOPS_REPO}/.git" ]; then
                            echo "Updating existing repository..."
                            cd ${DEVOPS_REPO}
                            git fetch origin
                            git checkout main
                            git pull origin main
                        else
                            echo "Cloning bstack repository..."
                            rm -rf ${DEVOPS_REPO}
                            mkdir -p ${DEVOPS_REPO}
                            git clone https://github.com/devops-ind/bstack.git ${DEVOPS_REPO}
                        fi

                        echo "✅ Repository ready"
                        echo ""
                        echo "Repository structure:"
                        ls -la ${DEVOPS_REPO} | head -20
                    '''
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    echo "🐍 STAGE: Install Dependencies"
                    echo "════════════════════════════════════════════════════════"

                    sh '''
                        cd ${DEVOPS_REPO}

                        # Create virtual environment
                        python3 -m venv venv
                        source venv/bin/activate

                        # Upgrade pip and install dependencies
                        pip install --upgrade pip > /dev/null 2>&1
                        pip install -r requirements.txt

                        # Verify installations
                        echo "✅ Verifying installations..."
                        python3 -c "
import yaml
import requests
print('✅ All required packages installed:')
print('   - PyYAML')
print('   - requests')
print('   - GitPython')
                        "
                        echo ""
                        python3 --version
                    '''
                }
            }
        }

        stage('Validate Configuration') {
            steps {
                script {
                    echo "⚙️  STAGE: Validate Configuration"
                    echo "════════════════════════════════════════════════════════"

                    sh '''
                        cd ${DEVOPS_REPO}
                        source venv/bin/activate

                        # Validate configuration file
                        python3 -c "
import sys
sys.path.insert(0, 'src')
from config import Config

try:
    config = Config('config/config.yaml')
    print('✅ Configuration file is valid')
    print('')
    print('BrowserStack API timeout: ' + str(config.get('browserstack.upload_timeout')) + ' seconds')
except Exception as e:
    print('❌ Configuration error: ' + str(e))
    sys.exit(1)
                        "

                        # Verify all required modules
                        echo ""
                        echo "✅ Verifying modules..."
                        python3 -c "
import sys
sys.path.insert(0, 'src')
from main import BrowserStackUploader
from config import Config
from logger import setup_logger
from local_storage import LocalStorage
from browserstack_client import BrowserStackClient
from github_client import GitHubClient
from yaml_updater import YAMLUpdater
from teams_notifier import TeamsNotifier
from utils import validate_parameters
print('✅ All modules imported successfully')
                        "
                    '''
                }
            }
        }

        stage('Validate Parameters') {
            steps {
                script {
                    echo "✔️  STAGE: Validate Parameters"
                    echo "════════════════════════════════════════════════════════"

                    sh '''
                        cd ${DEVOPS_REPO}
                        source venv/bin/activate

                        python3 -c "
import sys
sys.path.insert(0, 'src')
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

print('Parameter Validation:')
print('─' * 50)
for key, value in params.items():
    print(f'  {key:20} : {value}')
print('─' * 50)

errors = validate_parameters(params)
if errors:
    print('❌ Parameter validation FAILED:')
    for error in errors:
        print(f'  • {error}')
    sys.exit(1)
else:
    print('')
    print('✅ All parameters validated successfully')
                        "
                    '''
                }
            }
        }

        stage('Execute Upload') {
            steps {
                script {
                    echo "📤 STAGE: Execute BrowserStack Upload"
                    echo "════════════════════════════════════════════════════════"

                    sh '''
                        cd ${DEVOPS_REPO}
                        source venv/bin/activate

                        # Build command with optional src-folder parameter
                        CMD="python3 src/main.py \
                            --platform \"${PLATFORM}\" \
                            --environment \"${ENVIRONMENT}\" \
                            --build-type \"${BUILD_TYPE}\" \
                            --app-variant \"${APP_VARIANT}\" \
                            --version \"${VERSION}\" \
                            --build-id \"${BUILD_ID}\" \
                            --source-build-url \"${SOURCE_BUILD_URL}\""

                        # Add src-folder if provided
                        if [ -n "${srcFolder}" ]; then
                            CMD="$CMD --src-folder \"${srcFolder}\""
                        fi

                        # Add remaining arguments
                        CMD="$CMD --config-file config/config.yaml \
                            --output-file ${WORKSPACE}/upload-result.json \
                            --verbose"

                        # Run the uploader with all parameters
                        eval $CMD

                        RESULT=$?

                        if [ $RESULT -ne 0 ]; then
                            echo ""
                            echo "❌ Upload failed with exit code: $RESULT"
                            exit 1
                        fi

                        echo ""
                        echo "✅ Upload completed successfully"
                    '''
                }
            }
        }

        stage('Archive Results') {
            steps {
                script {
                    echo "📁 STAGE: Archive Results"
                    echo "════════════════════════════════════════════════════════"

                    sh '''
                        cd ${DEVOPS_REPO}

                        # Archive upload results
                        if [ -f ${WORKSPACE}/upload-result.json ]; then
                            echo "Archiving upload results..."
                            mkdir -p ${WORKSPACE}/artifacts
                            cp ${WORKSPACE}/upload-result.json ${WORKSPACE}/artifacts/

                            # Also copy audit trails if they exist
                            find logs -name "audit-trail-*.json" -exec cp {} ${WORKSPACE}/artifacts/ \; 2>/dev/null || true

                            echo "✅ Results archived"
                        fi
                    '''

                    // Archive artifacts in Jenkins
                    archiveArtifacts artifacts: 'artifacts/**/*.json',
                                     allowEmptyArchive: true,
                                     fingerprint: true
                }
            }
        }

        stage('Generate Report') {
            steps {
                script {
                    echo "📊 STAGE: Generate Report"
                    echo "════════════════════════════════════════════════════════"

                    sh '''
                        if [ -f ${WORKSPACE}/upload-result.json ]; then
                            python3 << 'EOF'
import json

try:
    with open('${WORKSPACE}/upload-result.json') as f:
        result = json.load(f)

    print("")
    print("╔════════════════════════════════════════════════════════╗")
    print("║              UPLOAD RESULT SUMMARY                     ║")
    print("╚════════════════════════════════════════════════════════╝")
    print("")

    print(f"Status:         {result.get('status', 'N/A')}")
    print(f"Platform:       {result.get('platform', 'N/A')}")
    print(f"Environment:    {result.get('environment', 'N/A')}")
    print(f"App Variant:    {result.get('app_variant', 'N/A')}")
    print(f"Version:        {result.get('version', 'N/A')}")

    if 'browserstack' in result:
        bs = result['browserstack']
        print(f"App ID:         {bs.get('app_id', 'N/A')}")
        print(f"App URL:        {bs.get('app_url', 'N/A')}")

    if 'pr' in result and 'pr_url' in result['pr']:
        print(f"PR URL:         {result['pr']['pr_url']}")

    print("")

except Exception as e:
    print(f"Error reading results: {e}")
    exit(1)
EOF
                        fi
                    '''
                }
            }
        }
    }

    post {
        success {
            script {
                echo ""
                echo "✅ Pipeline completed successfully"
                echo ""
                echo "Next steps:"
                echo "  1. Check the generated PR in GitHub"
                echo "  2. Verify artifact uploaded to BrowserStack"
                echo "  3. Review Teams notification (if configured)"
            }
        }

        failure {
            script {
                echo ""
                echo "❌ Pipeline failed"
                echo ""
                echo "Troubleshooting:"
                echo "  1. Check console output above for errors"
                echo "  2. Review configuration in config/config.yaml"
                echo "  3. Verify credentials are set in Jenkins Credentials Manager"
                echo "  4. Check logs in ${WORKSPACE}/bstack/logs"
            }
        }

        always {
            // Cleanup virtual environment to save space
            sh '''
                echo "Cleaning up..."
                if [ -d "${DEVOPS_REPO}/venv" ]; then
                    rm -rf ${DEVOPS_REPO}/venv
                fi
            '''
        }
    }
}
