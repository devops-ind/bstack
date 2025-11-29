# SSL Certificate Setup for Corporate Networks

This guide helps you configure the BrowserStack uploader to work with corporate networks that use SSL inspection (HTTPS proxies with custom certificates).

## The Problem

When running in corporate networks, you might see this error:

```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
Basic Constraints of CA cert not marked critical
```

This happens because:
1. Your corporate network uses an **SSL inspection proxy**
2. The proxy intercepts HTTPS traffic and re-signs it with a **corporate CA certificate**
3. Python's `requests` library doesn't trust this corporate CA certificate by default
4. SSL verification fails, blocking the upload to BrowserStack

## Solutions

You have **3 options** to fix this (in order of recommendation):

### ✅ Option 1: Use Corporate CA Certificate (RECOMMENDED)

Configure the uploader to trust your corporate CA certificate.

**Pros:**
- ✅ Secure - SSL verification still enabled
- ✅ Best practice
- ✅ Recommended by security teams

**Cons:**
- Requires obtaining the corporate CA certificate file

---

### ⚠️ Option 2: Disable SSL Verification (TEMPORARY TESTING ONLY)

Disable SSL certificate verification entirely.

**Pros:**
- Quick to test
- No certificate file needed

**Cons:**
- ❌ **Security risk** - vulnerable to man-in-the-middle attacks
- ❌ Not recommended for production
- ❌ Only use in trusted corporate networks for testing

---

### 🔧 Option 3: System-Wide Certificate Installation

Install the corporate CA certificate system-wide.

**Pros:**
- ✅ Works for all Python applications
- ✅ No per-application configuration

**Cons:**
- Requires admin/root access
- Changes system configuration

---

## How to Implement Each Solution

### Solution 1: Use Corporate CA Certificate Bundle (RECOMMENDED)

#### Step 1: Get Your Corporate CA Certificate

Choose one of these methods:

**Method A: Export from Browser (Easiest)**

1. Open Chrome/Firefox
2. Visit any HTTPS site (e.g., https://google.com)
3. Click the padlock icon → Certificate
4. Go to the **Certification Path** tab
5. Select the **ROOT** certificate (top of the chain)
6. Click **View Certificate**
7. Go to **Details** tab
8. Click **Export** or **Copy to File**
9. Choose format: **DER** or **Base64-encoded X.509 (.CER)**
10. Save as: `corporate-ca.crt`

**Method B: Ask IT Department**

Contact your IT/Security team and request:
- "Corporate root CA certificate"
- "SSL inspection certificate"
- "Proxy CA certificate"

File format: `.crt`, `.cer`, or `.pem`

**Method C: Extract from Windows Certificate Store (Windows only)**

```powershell
# Open PowerShell as Administrator

# List corporate certificates
Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object {$_.Subject -like "*YourCompany*"}

# Export specific certificate (replace thumbprint)
$cert = Get-Item -Path Cert:\LocalMachine\Root\<THUMBPRINT>
Export-Certificate -Cert $cert -FilePath "C:\corporate-ca.crt"
```

**Method D: Download from Corporate Intranet**

Many companies provide the CA certificate on their intranet portal.

#### Step 2: Convert Certificate Format (if needed)

If you have a `.cer` or `.der` file, convert to PEM format:

```bash
# Convert DER to PEM
openssl x509 -inform DER -in corporate-ca.cer -out corporate-ca.crt

# Verify certificate
openssl x509 -in corporate-ca.crt -text -noout
```

#### Step 3: Configure the Uploader

Edit `config/config.yaml`:

```yaml
browserstack:
  # ... other settings ...

  # Set path to your corporate CA certificate
  ssl_ca_bundle: "/path/to/corporate-ca.crt"  # Use absolute path

  # Keep verification enabled
  ssl_verify: true
```

**Examples:**

```yaml
# Windows
ssl_ca_bundle: "C:\\certs\\corporate-ca.crt"

# Linux
ssl_ca_bundle: "/etc/ssl/certs/corporate-ca.crt"

# MacOS
ssl_ca_bundle: "/usr/local/share/ca-certificates/corporate-ca.crt"

# Relative path (from project root)
ssl_ca_bundle: "certs/corporate-ca.crt"
```

#### Step 4: Test

```bash
# Run the uploader
python3 src/main.py --platform android --environment staging \
  --build-type Debug --app-variant agent \
  --build-id test-001 --source-build-url http://test.com \
  --verbose

# You should see this log message:
# Using custom CA bundle: /path/to/corporate-ca.crt
```

---

### Solution 2: Disable SSL Verification (TEMPORARY ONLY)

**⚠️ WARNING: Only use this for testing! Not for production!**

Edit `config/config.yaml`:

```yaml
browserstack:
  # ... other settings ...

  ssl_ca_bundle: null  # Not using custom CA

  # Disable SSL verification
  ssl_verify: false  # ⚠️ SECURITY RISK
```

When you run the uploader, you'll see:

```
WARNING: SSL certificate verification is DISABLED - this is a security risk!
```

**Use this only for:**
- Quick testing to confirm it fixes the issue
- Debugging in secure corporate networks
- Temporary workaround while waiting for CA certificate

**Do NOT use this for:**
- Production deployments
- Automated pipelines
- Public networks
- Long-term solutions

---

### Solution 3: System-Wide Certificate Installation

#### On Linux (Ubuntu/Debian)

```bash
# Copy CA certificate to system location
sudo cp corporate-ca.crt /usr/local/share/ca-certificates/

# Update CA certificates
sudo update-ca-certificates

# Verify
python3 -c "import requests; requests.get('https://api-cloud.browserstack.com')"
```

#### On Linux (RHEL/CentOS)

```bash
# Copy CA certificate
sudo cp corporate-ca.crt /etc/pki/ca-trust/source/anchors/

# Update CA trust
sudo update-ca-trust

# Verify
python3 -c "import requests; requests.get('https://api-cloud.browserstack.com')"
```

#### On Windows

1. Open `certmgr.msc` (Certificate Manager)
2. Navigate to: Trusted Root Certification Authorities → Certificates
3. Right-click → All Tasks → Import
4. Select your `corporate-ca.crt` file
5. Complete the wizard

#### On macOS

```bash
# Add to system keychain
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain corporate-ca.crt

# Verify
python3 -c "import requests; requests.get('https://api-cloud.browserstack.com')"
```

After system-wide installation, use default settings in `config.yaml`:

```yaml
browserstack:
  ssl_ca_bundle: null  # Use system certificates
  ssl_verify: true     # Verify using system trust store
```

---

## How to Create a CA Bundle with Multiple Certificates

If your network uses multiple CA certificates (root + intermediate), create a bundle:

```bash
# Combine multiple certificates into one file
cat root-ca.crt intermediate-ca.crt > ca-bundle.crt

# Use the bundle
```

In `config.yaml`:

```yaml
browserstack:
  ssl_ca_bundle: "/path/to/ca-bundle.crt"
```

---

## Troubleshooting

### Error: "Could not find a suitable TLS CA certificate bundle"

**Problem:** Certificate file path is incorrect

**Solutions:**
- Use absolute path instead of relative path
- Verify file exists: `ls -la /path/to/corporate-ca.crt`
- Check file permissions: `chmod 644 corporate-ca.crt`

### Error: "SSL: CERTIFICATE_VERIFY_FAILED" (still occurring)

**Problem:** Wrong certificate or incomplete chain

**Solutions:**

1. **Verify you have the ROOT certificate** (not intermediate):
   ```bash
   openssl x509 -in corporate-ca.crt -text -noout | grep "Subject:"
   # Should show your company's root CA
   ```

2. **Check certificate is valid:**
   ```bash
   openssl verify -CAfile corporate-ca.crt corporate-ca.crt
   # Should show: corporate-ca.crt: OK
   ```

3. **Create a full certificate chain:**
   ```bash
   # Get the full chain from your browser
   # Export all certificates in the path (root + intermediates)
   cat root.crt intermediate1.crt intermediate2.crt > full-chain.crt
   ```

4. **Test certificate works with curl:**
   ```bash
   curl --cacert corporate-ca.crt https://api-cloud.browserstack.com
   # Should succeed without errors
   ```

### Error: "unable to get local issuer certificate"

**Problem:** Missing intermediate certificates

**Solution:** Export the complete certificate chain from your browser:

1. Browser → Padlock → Certificate → Certification Path
2. Export **all certificates** in the chain (from root to leaf)
3. Combine into one file:
   ```bash
   cat root-ca.crt intermediate-ca.crt > ca-bundle.crt
   ```

### Certificate Works in Browser but Not in Python

**Problem:** Browser uses different certificate store

**Solutions:**

1. **Set environment variable:**
   ```bash
   export REQUESTS_CA_BUNDLE=/path/to/corporate-ca.crt
   python3 src/main.py ...
   ```

2. **Set Python environment variable:**
   ```bash
   export SSL_CERT_FILE=/path/to/corporate-ca.crt
   python3 src/main.py ...
   ```

3. **Use certifi (Python certificate bundle):**
   ```bash
   # Find certifi location
   python3 -c "import certifi; print(certifi.where())"

   # Append corporate CA to certifi bundle
   cat corporate-ca.crt >> $(python3 -c "import certifi; print(certifi.where())")
   ```

---

## Verification Steps

After configuration, verify the setup:

### 1. Test Certificate File

```bash
# Verify certificate is readable
cat /path/to/corporate-ca.crt

# Check certificate details
openssl x509 -in /path/to/corporate-ca.crt -text -noout
```

### 2. Test with Python Requests

```python
import requests

# Test with custom CA bundle
response = requests.get(
    'https://api-cloud.browserstack.com',
    verify='/path/to/corporate-ca.crt'
)
print(f"Status: {response.status_code}")  # Should be 200 or 403
```

### 3. Test with BrowserStack Uploader

```bash
python3 src/main.py \
  --platform android \
  --environment staging \
  --build-type Debug \
  --app-variant agent \
  --build-id test-ssl \
  --source-build-url http://test.com \
  --verbose
```

Look for these log messages:

```
✅ SUCCESS:
INFO: Using custom CA bundle: /path/to/corporate-ca.crt
INFO: Upload successful: bs://abc123...

❌ FAILURE:
ERROR: SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

---

## Security Best Practices

1. ✅ **Always prefer Option 1** (custom CA bundle) over disabling verification
2. ✅ **Store certificates securely** - readable only by necessary users
3. ✅ **Use absolute paths** to avoid path resolution issues
4. ✅ **Version control** certificate setup (but not the cert file itself)
5. ✅ **Document certificate source** for future reference
6. ❌ **Never commit certificates to Git** (add to `.gitignore`)
7. ❌ **Never disable SSL in production** environments

---

## Configuration Examples

### Development Environment (Local Testing)

```yaml
# config/config.yaml
browserstack:
  ssl_ca_bundle: "certs/corporate-ca.crt"
  ssl_verify: true
```

### Jenkins Pipeline

```groovy
// Jenkinsfile
environment {
    SSL_CA_BUNDLE = '/var/jenkins/certs/corporate-ca.crt'
}

stage('Upload') {
    steps {
        sh '''
            # Use Jenkins-managed certificate
            python3 src/main.py \
              --config-file config/config.yaml \
              --verbose
        '''
    }
}
```

Update `config.yaml` to read from environment variable:

```yaml
browserstack:
  ssl_ca_bundle: ${SSL_CA_BUNDLE}  # Reads from environment
  ssl_verify: true
```

### Docker Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Copy corporate CA certificate
COPY certs/corporate-ca.crt /etc/ssl/certs/corporate-ca.crt

# Update CA certificates
RUN update-ca-certificates

# Application will use system certificates
```

```yaml
# config.yaml - Use system certificates
browserstack:
  ssl_ca_bundle: null  # Use system CA store
  ssl_verify: true
```

---

## Quick Reference

| Scenario | ssl_verify | ssl_ca_bundle | Security Level |
|----------|------------|---------------|----------------|
| Default (no proxy) | `true` | `null` | ✅ High |
| Corporate proxy (recommended) | `true` | `"/path/to/ca.crt"` | ✅ High |
| System-wide cert installed | `true` | `null` | ✅ High |
| Testing only (NOT production) | `false` | `null` | ⚠️ **LOW - INSECURE** |

---

## Getting Help

If you're still experiencing SSL issues:

1. **Capture detailed error:**
   ```bash
   python3 src/main.py ... --verbose 2>&1 | tee ssl-error.log
   ```

2. **Test SSL connectivity:**
   ```bash
   openssl s_client -connect api-cloud.browserstack.com:443 \
     -CAfile /path/to/corporate-ca.crt
   ```

3. **Check proxy settings:**
   ```bash
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   ```

4. **Contact your IT department:**
   - Request corporate root CA certificate
   - Ask about SSL inspection proxy configuration
   - Confirm if custom certificates are required

---

## Summary

**For corporate networks with SSL inspection:**

1. 🎯 **RECOMMENDED:** Get corporate CA certificate from IT and configure `ssl_ca_bundle`
2. ⚠️ **TEMPORARY:** Set `ssl_verify: false` for quick testing only
3. 🔧 **ALTERNATIVE:** Install CA certificate system-wide

**Configuration:**

```yaml
browserstack:
  # Option 1: Custom CA bundle (recommended)
  ssl_ca_bundle: "/path/to/corporate-ca.crt"
  ssl_verify: true

  # Option 2: Disable verification (testing only - security risk!)
  # ssl_ca_bundle: null
  # ssl_verify: false
```

For most corporate users, **Option 1 with a custom CA bundle** is the right solution!
