# Getting Started - 10 Minute Setup Guide

## 🎯 Goal

Get the BrowserStack Uploader running on your machine in 10 minutes.

## ✅ Prerequisites

- Python 3.11 or higher: `python3 --version`
- Git: `git --version`
- Internet connection

## 📋 Step-by-Step Setup

### Step 1: Install Python Libraries (2 minutes)

```bash
cd /path/to/bstack
pip install -r requirements.txt
```

**What this does:**
- Installs PyYAML (reads config files)
- Installs requests (makes API calls)
- Installs GitPython (git operations)

**Expected output:**
```
Successfully installed pyyaml-6.0 requests-2.28.0 gitpython-3.1.30
```

### Step 2: Set Up Credentials (3 minutes)

Create a file called `.env` in the project root:

```bash
cat > .env << 'EOF'
export BROWSERSTACK_USER="your_username"
export BROWSERSTACK_ACCESS_KEY="your_access_key"
export GITHUB_TOKEN="your_github_token"
export TEAMS_WEBHOOK_URL="https://outlook.webhook.office.com/..."
EOF
```

**Where to get these:**
- **BrowserStack**: Account → Settings → API Key
- **GitHub**: Settings → Developer settings → Personal access tokens
- **Teams**: Get from your Teams channel integration

Load the environment variables:
```bash
source .env
```

**To verify:**
```bash
echo $BROWSERSTACK_USER  # Should print your username
```

### Step 3: Configure Settings (3 minutes)

Edit `config/config.yaml`:

```bash
nano config/config.yaml
```

Change these values:
```yaml
browserstack:
  username: ${BROWSERSTACK_USER}      # ← Leave as-is
  access_key: ${BROWSERSTACK_ACCESS_KEY}

github:
  org: "your-organization"            # ← Change to your org
  repo: "yaml-configs"                # ← Change to your repo

local_storage:
  artifact_base_path: "/path/to/builds"  # ← Change to your path
```

### Step 4: Verify Installation (2 minutes)

Test that everything is installed:

```bash
python3 src/main.py --help
```

**Expected output:**
```
usage: main.py [-h] --platform {android,android_hw,ios} ...

BrowserStack Artifact Uploader

optional arguments:
  -h, --help            show this help message and exit
  --platform {android,android_hw,ios}
                        Mobile platform
  ...
```

If you see the help message, you're ready! ✅

## 🧪 Test Run (Optional)

To test without uploading anything:

```bash
python3 src/main.py \
  --platform android \
  --environment production \
  --build-type Release \
  --app-variant agent \
  --version 1.0.0 \
  --build-id test-1 \
  --source-build-url https://example.com/build/1 \
  --config-file config/config.yaml \
  --verbose
```

This will:
- Validate your parameters
- Check that config is correct
- Stop before uploading (if artifact file doesn't exist)

## 📁 Project Structure Quick Reference

```
bstack/                          # Root directory
├── src/                         # Python source code
│   ├── main.py          ← ENTRY POINT (start here)
│   ├── config.py        ← Load configuration
│   ├── logger.py        ← Setup logging
│   ├── local_storage.py ← Validate artifacts
│   ├── browserstack_client.py ← Upload to BrowserStack
│   ├── github_client.py ← Git operations
│   ├── yaml_updater.py  ← Update YAML files
│   ├── teams_notifier.py← Send Teams messages
│   └── utils.py         ← Helper functions
│
├── config/
│   └── config.yaml      ← EDIT THIS (your settings)
│
├── docs/                ← DETAILED DOCUMENTATION
│   ├── SETUP.md         ← Installation guide
│   ├── CONFIGURATION.md ← Config options
│   ├── USAGE.md         ← How to use
│   └── TROUBLESHOOTING.md ← Fix errors
│
├── examples/            ← CODE EXAMPLES
│   ├── basic_example.py
│   └── advanced_example.py
│
├── requirements.txt     ← Python dependencies
├── .gitignore          ← Git ignore rules
└── PROJECT_README.md   ← Full project guide
```

## 🚀 Running Your First Upload

When you have an actual artifact file:

```bash
python3 src/main.py \
  --platform android \
  --environment staging \
  --build-type Debug \
  --app-variant agent \
  --version 1.2.3 \
  --build-id jenkins-5678 \
  --source-build-url https://jenkins.company.com/job/build/5678 \
  --config-file config/config.yaml \
  --verbose
```

**What happens:**
1. Validates your parameters
2. Checks the artifact file (APK/IPA)
3. Uploads to BrowserStack
4. Updates YAML configuration
5. Creates a pull request
6. Notifies your team on Teams
7. Saves audit trail

**Output:** Success or detailed error messages

## 📚 Learning Path (For Beginners)

1. **Understand the flow**: Read `PROJECT_README.md`
2. **Read main entry point**: `cat src/main.py` (top 50 lines)
3. **Pick one module**: Read config.py, logger.py, or utils.py
4. **Try an example**: `python3 examples/basic_example.py`
5. **Run the tool**: `python3 src/main.py --help`

## ❓ Common Issues

### Issue: "ModuleNotFoundError: No module named 'yaml'"
**Fix:** Run `pip install -r requirements.txt`

### Issue: "Environment variable not set: BROWSERSTACK_USER"
**Fix:** Run `source .env` to load credentials

### Issue: "No such file or directory: config.yaml"
**Fix:** Use `--config-file config/config.yaml` (include full path)

### Issue: "Artifact not found"
**Fix:** Check `artifact_base_path` in config.yaml points to correct location

See `docs/TROUBLESHOOTING.md` for more solutions.

## 📖 Next Steps

1. ✅ Read this guide (you're doing it!)
2. ✅ Install dependencies
3. ✅ Set up credentials
4. ✅ Edit configuration
5. ➡️ Read `PROJECT_README.md` for full understanding
6. ➡️ Check `docs/CONFIGURATION.md` for all options
7. ➡️ Look at `examples/` for code samples
8. ➡️ Run your first upload!

## 💡 Pro Tips

- **Use verbose mode** for debugging: `--verbose`
- **Save results** to file: `--output-file result.json`
- **Test your config**: Run `--help` first
- **Check logs** for detailed information
- **Keep audit trails** for compliance

## 🎓 Learning Resources

- **Beginners**: Start with `PROJECT_README.md`
- **Config details**: Read `docs/CONFIGURATION.md`
- **How to use**: See `docs/USAGE.md`
- **Code examples**: Check `examples/` folder
- **Code walkthrough**: Read inline comments in `src/`

---

## 🎉 You're Done!

You now have a working BrowserStack Uploader installation!

**Next**: Pick an example from the `examples/` folder and run it, or read through `src/main.py` to understand how it works.

**Questions?** Check `docs/TROUBLESHOOTING.md` or review the inline comments in the Python files.

Happy learning! 🚀
