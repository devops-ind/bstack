# Code Examples

This directory contains practical examples of how to use the BrowserStack Uploader.

## Quick Start

### Run Basic Example
```bash
python3 examples/basic_example.py
```

## Available Examples

### 1. basic_example.py

Demonstrates the most common use cases:

- **example_basic_upload()** - Simple artifact upload
- **example_with_output_file()** - Save results to JSON
- **example_parameter_validation()** - Validate input parameters
- **example_config_loading()** - Load and access configuration

### How to Use

```python
from src.main import BrowserStackUploader

# Define upload parameters
params = {
    'platform': 'android',
    'environment': 'staging',
    'build_type': 'Debug',
    'app_variant': 'agent',
    'version': '1.0.0',
    'build_id': 'jenkins-123',
    'source_build_url': 'https://jenkins.example.com/build/123'
}

# Initialize uploader
uploader = BrowserStackUploader('config/config.yaml', verbose=True)

# Run the upload
result = uploader.run(params)

# Check result
if result['status'] == 'SUCCESS':
    print(f"App uploaded! ID: {result['browserstack']['app_id']}")
else:
    print(f"Upload failed: {result['error']}")
```

## Common Patterns

### Pattern 1: Simple Upload
```python
from src.main import BrowserStackUploader

params = {
    'platform': 'android',
    'environment': 'production',
    'build_type': 'Release',
    'app_variant': 'agent',
    'version': '1.2.0',
    'build_id': 'jenkins-456',
    'source_build_url': 'https://jenkins.example.com/build/456'
}

uploader = BrowserStackUploader('config/config.yaml')
result = uploader.run(params)
```

### Pattern 2: With Error Handling
```python
from src.main import BrowserStackUploader

try:
    params = {...}
    uploader = BrowserStackUploader('config/config.yaml', verbose=True)
    result = uploader.run(params)

    if result['status'] == 'SUCCESS':
        print("Upload successful!")
        print(f"App ID: {result['browserstack']['app_id']}")
    else:
        print(f"Upload failed: {result['error']}")

except Exception as e:
    print(f"Error: {e}")
```

### Pattern 3: Batch Processing
```python
from src.main import BrowserStackUploader

builds = [
    {'platform': 'android', 'app_variant': 'agent', ...},
    {'platform': 'android', 'app_variant': 'retail', ...},
    {'platform': 'ios', 'app_variant': 'agent', ...},
]

uploader = BrowserStackUploader('config/config.yaml')

for build in builds:
    result = uploader.run(build)
    print(f"{build['app_variant']}: {result['status']}")
```

### Pattern 4: Validate Before Upload
```python
from src.main import BrowserStackUploader
from src.utils import validate_parameters

params = {...}

# Validate first
errors = validate_parameters(params)
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    # Safe to upload
    uploader = BrowserStackUploader('config/config.yaml')
    result = uploader.run(params)
```

## Prerequisites

Before running examples:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   export BROWSERSTACK_USER="your_username"
   export BROWSERSTACK_ACCESS_KEY="your_access_key"
   export GITHUB_TOKEN="your_github_token"
   export TEAMS_WEBHOOK_URL="your_webhook_url"
   ```

3. **Configure settings**
   Edit `config/config.yaml` with your actual values

4. **Verify setup**
   ```bash
   python3 src/main.py --help
   ```

## Learning Path

If you're learning the codebase, follow this order:

1. **Read the examples** in this directory
2. **Understand the flow** by reading `src/main.py`
3. **Study individual modules**:
   - `src/config.py` - Configuration management
   - `src/logger.py` - Logging setup
   - `src/local_storage.py` - Artifact validation
   - `src/browserstack_client.py` - API integration
   - `src/github_client.py` - Git operations
   - `src/yaml_updater.py` - Configuration updates
   - `src/teams_notifier.py` - Notifications
   - `src/utils.py` - Helper functions

4. **Look at test examples** in `tests/` directory

## Creating Your Own Examples

When creating new examples:

1. **Use clear naming**: `example_feature_name.py`
2. **Add docstrings**: Explain what the example does
3. **Include error handling**: Show proper error handling
4. **Add comments**: Explain key concepts
5. **Test thoroughly**: Make sure it works before committing

## Troubleshooting

### "Config file not found"
```bash
# Make sure you're in the correct directory
cd /path/to/bstack

# Check config file exists
ls config/config.yaml

# If not, copy from root
cp config.yaml config/config.yaml
```

### "Environment variable not set"
```bash
# Set the missing variable
export BROWSERSTACK_USER="your_username"

# Verify it's set
echo $BROWSERSTACK_USER
```

### "ModuleNotFoundError"
```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# Check you're running from project root
pwd  # Should be /path/to/bstack
```

## More Help

- See `GETTING_STARTED.md` for setup instructions
- See `PROJECT_README.md` for complete project guide
- See `tests/` directory for unit test examples
- See inline comments in `src/` files for code explanations

---

**Happy Learning!** 🚀

Feel free to modify these examples and create your own!
