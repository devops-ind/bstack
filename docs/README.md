# Documentation

Complete documentation for the BrowserStack Uploader tool.

## Quick Navigation

### For Getting Started

If you're new to the project, start here:

1. **[SETUP.md](SETUP.md)** - Installation and initial configuration
   - System requirements
   - Step-by-step installation
   - Environment setup
   - Verification tests
   - Troubleshooting common setup issues

### For Daily Usage

When using the tool:

2. **[USAGE.md](USAGE.md)** - How to use the tool
   - Command-line interface
   - All parameters explained
   - 5 detailed usage examples
   - Output formats
   - Advanced patterns

### For Configuration

When customizing settings:

3. **[CONFIGURATION.md](CONFIGURATION.md)** - Complete configuration reference
   - All configuration options
   - Environment variables
   - Settings for each section (BrowserStack, Git, GitHub, Teams, Retry)
   - Tips for different scenarios (dev, prod, large apps)
   - Complete example configuration

### For Problem Solving

When something goes wrong:

4. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solutions to common issues
   - Installation problems
   - Configuration issues
   - Runtime errors
   - Upload failures
   - GitHub integration issues
   - Debug mode
   - When to contact support

## Documentation Structure

```
docs/
├── README.md                    # This file - navigation guide
├── SETUP.md                     # Installation & initial configuration
├── USAGE.md                     # How to use the tool
├── CONFIGURATION.md             # Configuration reference
└── TROUBLESHOOTING.md           # Solutions to common issues
```

## Learning Paths

### Path 1: Complete Beginner (New to the tool)

1. Start with [SETUP.md](SETUP.md)
   - Read Prerequisites section
   - Follow Installation step-by-step
   - Run Verification tests

2. Read [USAGE.md](USAGE.md)
   - Understand Quick Start examples
   - Try Example 1 (basic Android staging)

3. Refer to [CONFIGURATION.md](CONFIGURATION.md)
   - Understand what each setting does
   - Customize for your environment

4. Keep [TROUBLESHOOTING.md](TROUBLESHOOTING.md) handy for issues

### Path 2: Setting Up for Your Project

1. Check [SETUP.md](SETUP.md) Prerequisites section
   - Ensure you have BrowserStack account
   - Ensure you have GitHub account
   - Get your API credentials

2. Follow [SETUP.md](SETUP.md) Installation section
   - Clone repository
   - Create virtual environment
   - Install dependencies

3. Use [CONFIGURATION.md](CONFIGURATION.md) to configure
   - Set environment variables
   - Edit config.yaml with your values
   - Validate configuration

4. Test with [USAGE.md](USAGE.md) Quick Start
   - Run a test upload
   - Verify it works

### Path 3: Advanced Usage (For CI/CD Integration)

1. Read [USAGE.md](USAGE.md) Advanced Usage section
   - Understand parallel uploads
   - Learn retry logic
   - See logging options

2. Review [CONFIGURATION.md](CONFIGURATION.md)
   - Understand retry settings
   - Configure for production

3. See `examples/basic_example.py` for programmatic usage

4. Check Jenkins configuration in `jenkins/` directory

### Path 4: Troubleshooting (When Issues Occur)

1. Identify the problem type in [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - Installation Issues
   - Configuration Issues
   - Runtime Errors
   - Upload Failures
   - GitHub Integration Issues

2. Follow the Solution steps

3. Refer to related docs for more details

## Document Summaries

### SETUP.md

**What**: Installation and configuration guide
**Length**: ~360 lines
**Time to read**: 15-20 minutes
**Covers**:
- Python, Git, Pip requirements
- Creating accounts and getting credentials
- Step-by-step installation (clone, venv, pip, env vars)
- Configuration file setup
- 6 verification tests
- Troubleshooting for 6 common setup issues
- Security best practices

**Key sections**:
- Prerequisites
- Installation (4 steps)
- Configuration (6 sections)
- Verification (6 tests)

### USAGE.md

**What**: How to use the tool and its features
**Length**: ~500 lines
**Time to read**: 20-25 minutes
**Covers**:
- Command-line interface with all options
- Detailed parameter explanations
- 5 complete usage examples
- Output format (console and JSON)
- Exit codes
- Advanced patterns (batch, retry, parallel, logging)

**Key sections**:
- Quick Start (3 examples)
- CLI Reference
- Parameters (7 required, 3 optional)
- Usage Examples (5 examples)
- Output & Results
- Advanced Usage (4 patterns)

### CONFIGURATION.md

**What**: Complete configuration reference
**Length**: ~450 lines
**Time to read**: 20-25 minutes
**Covers**:
- How configuration works
- All 6 configuration sections explained
- Every setting with type, default, and examples
- Environment variable substitution
- How to find API credentials
- Settings tips for different scenarios
- Complete example configuration

**Key sections**:
- Configuration File overview
- BrowserStack Settings (4 parameters)
- Local Storage Settings (3 parameters)
- Git & GitHub Settings (8 parameters)
- Notifications Settings (3 parameters)
- Retry Logic Settings (3 parameters)
- Environment Variables reference table
- Complete example

### TROUBLESHOOTING.md

**What**: Solutions to common problems
**Length**: ~550 lines
**Time to read**: 20-30 minutes (search as needed)
**Covers**:
- 40+ common issues and solutions
- Installation problems (5 issues)
- Configuration problems (6 issues)
- Runtime errors (8 issues)
- Upload failures (7 issues)
- GitHub integration issues (3 issues)
- Debug mode and tools
- How to test components

**Key sections**:
- Installation Issues
- Configuration Issues
- Runtime Errors
- Upload Failures
- GitHub Integration Issues
- Debug Mode
- Getting Help

## Common Tasks

### Task: Install the tool

**See**: [SETUP.md](SETUP.md) - Installation section

```bash
git clone https://github.com/devops-ind/bstack.git
cd bstack
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Task: Configure for your environment

**See**: [SETUP.md](SETUP.md) - Configuration section and [CONFIGURATION.md](CONFIGURATION.md)

```bash
# Edit .env file with your credentials
nano .env

# Edit config.yaml with your settings
nano config/config.yaml
```

### Task: Upload an Android app

**See**: [USAGE.md](USAGE.md) - Usage Examples section, Example 1

```bash
python3 src/main.py \
  --platform android \
  --environment staging \
  --build-type Debug \
  --app-variant agent \
  --version 1.0.0 \
  --build-id jenkins-001 \
  --source-build-url https://jenkins.example.com/job/android/001
```

### Task: Upload an iOS app

**See**: [USAGE.md](USAGE.md) - Usage Examples section, Example 2

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

### Task: Fix a configuration error

**See**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Configuration Issues section

Common configuration issues:
- Environment variable not set
- Configuration file not found
- Invalid configuration format
- Invalid environment variable reference

### Task: Debug an upload failure

**See**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Upload Failures section

Steps:
1. Run with `--verbose` flag to see details
2. Check `logs/browserstack_uploader.log` for error
3. Find the matching issue in Upload Failures
4. Follow the solution steps

### Task: Integrate with Jenkins

**See**: `jenkins/` directory

- `jenkins/README.md` - Overview of Jenkins integration options
- `jenkins/SETUP.md` - How to set up each pipeline variant

### Task: Use in Python code

**See**: `examples/basic_example.py`

```python
from src.main import BrowserStackUploader

params = {
    'platform': 'android',
    'environment': 'staging',
    'build_type': 'Debug',
    'app_variant': 'agent',
    'version': '1.0.0',
    'build_id': 'jenkins-123',
    'source_build_url': 'https://jenkins.example.com/build/123'
}

uploader = BrowserStackUploader('config/config.yaml')
result = uploader.run(params)
```

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| Setup & Installation | [docs/SETUP.md](SETUP.md) | Getting started |
| Usage Guide | [docs/USAGE.md](USAGE.md) | How to use |
| Configuration Reference | [docs/CONFIGURATION.md](CONFIGURATION.md) | Settings |
| Troubleshooting | [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Problem solving |
| Examples | `examples/basic_example.py` | Code samples |
| Project README | `PROJECT_README.md` | Project overview |
| Tests | `tests/` | Unit tests |
| Source Code | `src/` | Implementation |

## Quick Reference

### Required Parameters

```bash
--platform {android, android_hw, ios}
--environment {production, staging}
--build-type {Debug, Release}
--app-variant {agent, retail, wallet}
--version X.Y.Z
--build-id BUILD_ID
--source-build-url URL
```

### Optional Parameters

```bash
--config-file PATH              # Default: config.yaml
--output-file PATH              # Save results to JSON
--verbose, -v                   # Enable debug logging
--help, -h                       # Show help
```

### Environment Variables

```bash
BROWSERSTACK_USER               # BrowserStack username
BROWSERSTACK_ACCESS_KEY         # BrowserStack API key
GITHUB_TOKEN                    # GitHub personal access token
TEAMS_WEBHOOK_URL               # Teams webhook URL (optional)
```

## Support Resources

### Online Resources

- **BrowserStack Docs**: https://www.browserstack.com/docs
- **GitHub Docs**: https://docs.github.com
- **Python Docs**: https://docs.python.org/3/

### Getting Help

1. **Read relevant documentation** - Start with the appropriate doc above
2. **Check Troubleshooting** - Look for your error in [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Enable verbose mode** - Run with `--verbose` for detailed output
4. **Check logs** - Review `logs/browserstack_uploader.log`
5. **Try debug commands** - Use commands in Debug Mode section
6. **Contact support** - If all else fails, contact BrowserStack or GitHub support

## Table of Contents

**This documentation includes**:

- 1 navigation guide (this README)
- 1 setup guide (~360 lines)
- 1 usage guide (~500 lines)
- 1 configuration reference (~450 lines)
- 1 troubleshooting guide (~550 lines)

**Total**: ~2,000 lines of comprehensive documentation

## Last Updated

Documentation last updated: November 2024

For the latest version and updates, check the project repository.

---

**Start here**: Decide which documentation you need based on what you're doing, then follow the links above.
