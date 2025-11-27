# Simple BrowserStack Uploader - Learning Guide

## 📚 Overview

This is a **beginner-friendly version** of the BrowserStack Uploader that uses **only functions** (no classes). It's perfect for learning Python!

**File**: `simple_uploader.py` (single file, ~650 lines)

## 🎯 What You'll Learn

By studying this code, you'll learn:
- ✅ How to organize code with functions
- ✅ How to read/write YAML files
- ✅ How to make HTTP API calls
- ✅ How to work with Git from Python
- ✅ How to handle errors properly
- ✅ How to validate input data
- ✅ How to calculate file checksums
- ✅ How to work with command-line arguments

## 🏗️ Code Structure

The script is organized into **9 sections**:

```
1. Configuration Functions      (load_config, replace_env_vars)
2. File Operations              (build_artifact_path, validate_artifact_file)
3. BrowserStack Operations      (upload_to_browserstack)
4. Git Operations               (clone_git_repo, create_git_branch, commit_and_push)
5. YAML File Operations         (update_yaml_files)
6. GitHub API Operations        (create_pull_request)
7. Teams Notification           (send_teams_notification)
8. Main Workflow                (run_upload_workflow)
9. Command Line Interface       (main)
```

## 📖 Function-by-Function Walkthrough

### 1. Configuration Functions

#### `load_config(config_file)`
**What it does**: Reads the YAML configuration file

```python
config = load_config('config/config.yaml')
# Returns: {
#     'browserstack': {...},
#     'local_storage': {...},
#     'git': {...}
# }
```

**Key Concepts**:
- Opening and reading files
- Parsing YAML format
- Calling other functions

#### `replace_env_vars(obj)`
**What it does**: Replaces `${VAR_NAME}` with actual environment variable values

```python
# Input: "${BROWSERSTACK_USER}"
# Output: "john@example.com" (from environment)

# Input: {'username': '${BROWSERSTACK_USER}'}
# Output: {'username': 'john@example.com'}
```

**Key Concepts**:
- Recursion (function calls itself)
- Working with dictionaries, lists, strings
- Environment variables with `os.getenv()`

---

### 2. File Operations

#### `build_artifact_path(...)`
**What it does**: Builds the full path to the artifact file

```python
path = build_artifact_path(
    config=config,
    platform='android',
    environment='production',
    build_type='Release',
    app_variant='agent',
    src_folder='\\\\192.1.6.8\\Builds'
)
# Returns: "\\192.1.6.8\Builds\android\production\Release\Android\enterprise\agent\build\app-release.apk"
```

**Key Concepts**:
- String formatting with `.format()`
- Dictionary access with `.get()`
- Default values

#### `validate_artifact_file(artifact_path)`
**What it does**: Checks that the file exists and is valid

```python
info = validate_artifact_file('/path/to/app.apk')
# Returns: {
#     'path': '/path/to/app.apk',
#     'name': 'app.apk',
#     'size': 52428800,
#     'size_mb': 50.0,
#     'md5': 'abc123...',
#     'extension': '.apk'
# }
```

**Key Concepts**:
- File system operations with `pathlib.Path`
- File existence checking
- Reading binary files
- Raising exceptions for errors

#### `calculate_md5(file_path)`
**What it does**: Calculates MD5 checksum of a file

```python
checksum = calculate_md5('/path/to/file.apk')
# Returns: "d41d8cd98f00b204e9800998ecf8427e"
```

**Key Concepts**:
- Reading files in chunks (memory efficient)
- Hashing with `hashlib`
- While loops

---

### 3. BrowserStack Operations

#### `upload_to_browserstack(...)`
**What it does**: Uploads the app file to BrowserStack's API

```python
result = upload_to_browserstack(
    config=config,
    artifact_path='/path/to/app.apk',
    custom_id='android-agent-prod-20250115'
)
# Returns: {
#     'app_id': 'bs://abc123...',
#     'custom_id': 'android-agent-prod-20250115',
#     'timestamp': '2025-01-15T10:30:00Z'
# }
```

**Key Concepts**:
- HTTP POST requests with `requests` library
- Basic authentication
- Opening files in binary mode
- Error handling with try/except
- Parsing JSON responses

---

### 4. Git Operations

#### `clone_git_repo(config)`
**What it does**: Clones the Git repository to a temporary folder

```python
repo_path = clone_git_repo(config)
# Returns: "/tmp/yaml-config-abc123"
```

**Key Concepts**:
- Creating temporary directories
- Running shell commands with `subprocess`
- String manipulation for authentication URLs

#### `create_git_branch(repo_path, branch_name)`
**What it does**: Creates a new Git branch

```python
create_git_branch(
    repo_path='/tmp/yaml-config-abc123',
    branch_name='browserstack-update/android/agent/build-123'
)
```

**Key Concepts**:
- Running multiple git commands
- Error handling for subprocess calls

#### `checkout_existing_branch(repo_path, branch_name)`
**What it does**: Checks out an existing branch and pulls latest changes

```python
checkout_existing_branch(
    repo_path='/tmp/yaml-config-abc123',
    branch_name='main'
)
```

**Key Concepts**:
- Fetching remote changes
- Checking out existing branch
- Pulling latest updates
- Used for direct commits to main

#### `commit_and_push(...)`
**What it does**: Commits changes and pushes to remote

```python
commit_sha = commit_and_push(
    repo_path='/tmp/yaml-config-abc123',
    branch_name='feature-branch',
    files=['config.yml'],
    message='Update app ID'
)
# Returns: "abc123def456..." (commit SHA)
```

**Key Concepts**:
- For loops to process multiple files
- Capturing command output
- String operations (strip, slice)

#### `run_command(cmd, cwd, capture)`
**What it does**: Helper function to run shell commands

```python
# Run command without capturing output
run_command(['git', 'status'], cwd='/path/to/repo')

# Run command and capture output
result = run_command(['git', 'rev-parse', 'HEAD'], cwd='/path/to/repo', capture=True)
output = result.stdout.strip()
```

**Key Concepts**:
- subprocess.run() function
- Keyword arguments
- Conditional logic (if/else)

---

### 5. YAML File Operations

#### `update_yaml_files(...)`
**What it does**: Updates YAML configuration files with new app ID

```python
files = update_yaml_files(
    config=config,
    repo_path='/tmp/yaml-config-abc123',
    platform='android',
    app_variant='agent',
    environment='production',
    build_type='Release',
    new_app_id='bs://abc123...',
    version='1.2.3',
    build_id='jenkins-123'
)
# Returns: ['browserstack_ag_Android.yml', 'shared.yml']
```

**Key Concepts**:
- Reading/writing YAML files
- Creating nested dictionaries
- Conditional logic for optional parameters
- List operations (append)
- File path operations with pathlib

#### `get_yaml_filename(...)`
**What it does**: Gets the correct YAML filename for a platform/variant

```python
filename = get_yaml_filename(config, 'android', 'agent')
# Returns: "browserstack_ag_Android.yml"
```

**Key Concepts**:
- Dictionary lookups with .get()
- Default values
- String concatenation

---

### 6. GitHub API Operations

#### `create_pull_request(...)`
**What it does**: Creates a Pull Request using GitHub's API

```python
pr_url = create_pull_request(
    config=config,
    title='Update BrowserStack app ID',
    body='## Changes\n- Updated app ID',
    branch='feature-branch'
)
# Returns: "https://github.com/org/repo/pull/123"
```

**Key Concepts**:
- REST API calls with POST method
- JSON payloads
- Authentication headers
- String formatting for URLs

---

### 7. Teams Notification

#### `send_teams_notification(...)`
**What it does**: Sends a formatted message to Microsoft Teams

```python
send_teams_notification(
    config=config,
    platform='android',
    app_variant='agent',
    environment='production',
    build_type='Release',
    version='1.2.3',
    old_app_id='bs://old123',
    new_app_id='bs://new456',
    pr_url='https://github.com/org/repo/pull/123',
    source_build_url='https://jenkins.example.com/build/456'
)
```

**Key Concepts**:
- Creating complex data structures (nested dictionaries)
- Dictionary lookups with .get() and defaults
- List operations (append, extend)
- HTTP POST to webhooks

---

### 8. Main Workflow

#### `run_upload_workflow(params, config_file)`
**What it does**: Orchestrates the complete workflow (all 9 steps)

```python
result = run_upload_workflow(
    params={
        'platform': 'android',
        'environment': 'production',
        'build_type': 'Release',
        'app_variant': 'agent',
        'build_id': 'jenkins-123',
        'source_build_url': 'https://...',
        'version': '1.2.3',
        'src_folder': None
    },
    config_file='config/config.yaml'
)
# Returns: {
#     'status': 'SUCCESS',
#     'app_id': 'bs://abc123...',
#     'pr_url': 'https://...',
#     'commit_sha': 'abc123...'
# }
```

**Key Concepts**:
- Function composition (calling functions in sequence)
- Error handling with try/except
- Dictionary access with .get() for optional values
- String formatting (f-strings)

---

### 9. Command Line Interface

#### `main()`
**What it does**: Parses command-line arguments and runs the workflow

```python
# When you run:
# python3 simple_uploader.py --platform android --environment production ...

# This function:
# 1. Creates argument parser
# 2. Defines all arguments
# 3. Parses command line
# 4. Builds params dictionary
# 5. Calls run_upload_workflow()
# 6. Exits with appropriate code
```

**Key Concepts**:
- argparse module for CLI
- sys.exit() for exit codes
- Exception handling
- if __name__ == '__main__' pattern

---

## 🚀 How to Use

### Workflow Modes

The script supports **two workflows** based on config settings:

#### Mode 1: Create Pull Request (Default)
Set in `config.yaml`:
```yaml
git:
  create_pr: true
```

This will:
1. Create a feature branch
2. Commit changes
3. Push to GitHub
4. Create a Pull Request for review

#### Mode 2: Direct Commit to Main
Set in `config.yaml`:
```yaml
git:
  create_pr: false
  target_branch: "main"  # Branch to commit to
```

This will:
1. Checkout target branch (e.g., main)
2. Commit changes directly
3. Push to GitHub
4. Skip PR creation

### Basic Usage

```bash
python3 simple_uploader.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --build-id jenkins-123 \
  --source-build-url https://jenkins.example.com/build/123 \
  --config-file config/config.yaml
```

### With Custom NFS Location

```bash
python3 simple_uploader.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --build-id jenkins-123 \
  --source-build-url https://jenkins.example.com/build/123 \
  --src-folder "\\192.1.6.8\Builds\MobileApp\Nightly_Builds\mainline" \
  --config-file config/config.yaml
```

### With Version

```bash
python3 simple_uploader.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --build-id jenkins-123 \
  --source-build-url https://jenkins.example.com/build/123 \
  --version 1.2.3 \
  --config-file config/config.yaml
```

---

## 📚 Learning Path

### For Complete Beginners

1. **Start by reading the comments**
   - Every function has detailed comments
   - Comments explain what the code does

2. **Understand the workflow**
   - Read `run_upload_workflow()` to see the big picture
   - Follow the 9 steps in order

3. **Study individual functions**
   - Start with simple ones: `calculate_md5()`, `get_yaml_filename()`
   - Then move to more complex: `upload_to_browserstack()`, `update_yaml_files()`

4. **Experiment**
   - Add print statements to see what's happening
   - Try modifying small parts
   - Run with different parameters

### Key Python Concepts to Learn

1. **Functions**
   ```python
   def my_function(arg1, arg2):
       result = arg1 + arg2
       return result
   ```

2. **Dictionaries**
   ```python
   config = {'key': 'value'}
   value = config.get('key', 'default')
   ```

3. **Error Handling**
   ```python
   try:
       risky_operation()
   except Exception as e:
       print(f"Error: {e}")
   ```

4. **File Operations**
   ```python
   with open('file.txt', 'r') as f:
       content = f.read()
   ```

5. **HTTP Requests**
   ```python
   response = requests.post(url, json=data)
   result = response.json()
   ```

---

## 🔍 Comparison with Class-Based Version

### Simple Version (Functions)
```python
# Create config
config = load_config('config.yaml')

# Use functions directly
artifact_path = build_artifact_path(config, platform, ...)
result = upload_to_browserstack(config, artifact_path, ...)
```

**Pros**:
- ✅ Easier to understand
- ✅ Less abstract
- ✅ Clear flow
- ✅ Good for learning

**Cons**:
- ❌ Pass config everywhere
- ❌ Less organized for large projects
- ❌ Harder to test

### Class-Based Version (Original)
```python
# Create clients
storage = LocalStorage(config)
bs_client = BrowserStackClient(config)

# Use methods
artifact_path = storage.construct_artifact_path(platform, ...)
result = bs_client.upload_app(artifact_path, ...)
```

**Pros**:
- ✅ Better organization
- ✅ Encapsulation
- ✅ Easier to test
- ✅ Professional style

**Cons**:
- ❌ More abstract
- ❌ Harder for beginners
- ❌ More files

---

## 🎓 Next Steps

After understanding this simple version:

1. **Study the class-based version** in `src/` folder
   - See how classes organize related functions
   - Understand object-oriented programming

2. **Read the documentation**
   - `docs/BEGINNER_GUIDE.md` - Detailed class explanations
   - `docs/ARCHITECTURE.md` - System architecture
   - `docs/CLASS_DIAGRAM.md` - Class relationships

3. **Try modifying the code**
   - Add more error checking
   - Add logging to files
   - Add support for new platforms

4. **Learn more Python**
   - Classes and objects
   - List comprehensions
   - Decorators
   - Context managers

---

## 💡 Tips for Understanding the Code

1. **Follow the data**
   - Start with parameters
   - See how they're transformed
   - Track the return values

2. **Use print statements**
   ```python
   def upload_to_browserstack(config, artifact_path, custom_id):
       print(f"DEBUG: artifact_path = {artifact_path}")
       print(f"DEBUG: custom_id = {custom_id}")
       # ... rest of function
   ```

3. **Run with verbose output**
   - The script already prints progress
   - Watch what happens at each step

4. **Break it down**
   - Don't try to understand everything at once
   - Focus on one function at a time
   - Use online Python documentation

5. **Draw diagrams**
   - Sketch the workflow on paper
   - Draw how data flows between functions
   - Map out the decision points

---

## 🐛 Common Issues and Solutions

### Issue: "Environment variable not set"
**Solution**: Set required environment variables:
```bash
export BROWSERSTACK_USER="your_username"
export BROWSERSTACK_ACCESS_KEY="your_key"
export GITHUB_TOKEN="your_token"
export TEAMS_WEBHOOK_URL="https://..."
```

### Issue: "Artifact not found"
**Solution**: Check the path is correct:
1. Verify `src_folder` parameter
2. Check path template in config.yaml
3. Ensure file exists at that location

### Issue: "Git clone failed"
**Solution**: Check Git configuration:
1. Verify GITHUB_TOKEN is set
2. Check repo URL in config.yaml
3. Ensure you have repository access

### Issue: "Upload failed"
**Solution**: Check BrowserStack credentials:
1. Verify username and access key
2. Check network connectivity
3. Ensure artifact file is valid

---

## 📝 Summary

This simple version demonstrates:
- ✅ **Function-based programming** - Organize code with functions
- ✅ **Sequential workflow** - Step-by-step execution
- ✅ **Error handling** - Try/except for robustness
- ✅ **API integration** - HTTP requests to external services
- ✅ **File operations** - Reading, writing, validating files
- ✅ **Git automation** - Cloning, committing, pushing
- ✅ **Clear documentation** - Comments and docstrings

Perfect for **learning Python** and understanding **automation workflows**!

---

## 🎯 Challenge Exercises

Try these to improve your skills:

1. **Add a dry-run mode**
   - Add `--dry-run` flag
   - Print what would happen without doing it

2. **Add file logging**
   - Write logs to a file
   - Include timestamps

3. **Add retry logic**
   - Retry failed operations 3 times
   - Wait between retries

4. **Add validation functions**
   - Check version format
   - Validate URLs
   - Verify file sizes

5. **Add color output**
   - Use ANSI color codes
   - Green for success, red for errors

Happy coding! 🚀
