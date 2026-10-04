# CRM Integration Guide - GTM AI System

**Complete step-by-step guide for Salesforce and HubSpot integration**

---

## 📋 Table of Contents

1. [Salesforce Setup](#salesforce-setup)
2. [HubSpot Setup](#hubspot-setup)
3. [Running the Integration](#running-the-integration)
4. [Troubleshooting](#troubleshooting)
5. [Testing](#testing)

---

## 🔧 Salesforce Setup

### Step 1: Create OAuth Connected App

1. Go to **Salesforce** → **Setup** (gear icon)
2. In left sidebar, search for **"App Manager"**
3. Click **"New Connected App"** (top right)

### Step 2: Fill in Connected App Details

```
Connected App Name: GTM AI System
API Name: gtm_ai_system
Contact Email: your_email@company.com
```

### Step 3: Enable OAuth Settings

1. Check: **"Enable OAuth Settings"**
2. Callback URL: `http://localhost:8000/callback`
3. Under **Selected OAuth Scopes**, add:
   - `Full` (full)
   - `Refresh Token` (refresh_token)
   - `Perform Requests` (api)
4. Click **"Save"**

### Step 4: Get Credentials

1. After saving, go to the app
2. Click **"View"** next to the app name
3. Copy these values:
   - **Client ID**
   - **Client Secret** (click "Click to reveal")

### Step 5: Create Security Token

1. In Salesforce, click your **profile icon** (top right)
2. Select **"Settings"**
3. In left sidebar, search for **"Reset My Security Token"**
4. Click **"Reset Security Token"**
5. Check your email for the security token

### Step 6: Create Custom Fields on Account

1. In Salesforce Setup, search for **"Account"**
2. Click **"Account"** (under Objects)
3. Scroll to **"Custom Fields & Relationships"**
4. Click **"New"** to create custom field

**Field 1: ICP Score**
```
Field Type: Number
Field Label: GTM ICP Score
Field Name: GTM_ICP_Score (auto-fills as GTM_ICP_Score__c)
Decimal Places: 1
Required: Unchecked
Unique: Unchecked
```

**Field 2: Intent Score**
```
Field Type: Number
Field Label: GTM Intent Score
Field Name: GTM_Intent_Score (auto-fills as GTM_Intent_Score__c)
Decimal Places: 1
Required: Unchecked
```

**Field 3: Segment**
```
Field Type: Text
Field Label: GTM Segment
Field Name: GTM_Segment (auto-fills as GTM_Segment__c)
Length: 100
```

### Step 7: Configure .env File

Edit your `.env` file and add:

```bash
# Salesforce Configuration
SALESFORCE_INSTANCE_URL=https://your-domain.salesforce.com
SALESFORCE_CLIENT_ID=your_client_id_here
SALESFORCE_CLIENT_SECRET=your_client_secret_here
SALESFORCE_USERNAME=your_email@company.com
SALESFORCE_PASSWORD=your_password_plus_security_token_concatenated
```

**Important:** Concatenate password + security token:
```
Password: MyPassword123
Token: ABCDEF1234567890
Result: MyPassword123ABCDEF1234567890
```

---

## 🔗 HubSpot Setup

### Step 1: Create Private App

1. Go to **HubSpot** → **Settings** (gear icon)
2. In left sidebar, search for **"Private Apps"**
3. Click **"Create Private App"**

### Step 2: Basic Info

```
App Name: GTM AI System
App Description: AI-powered account scoring and segmentation
```

### Step 3: Set Scopes

Click the **"Scopes"** tab and enable:

- ✅ `crm.objects.companies.read` (Read companies)
- ✅ `crm.objects.companies.write` (Update companies)
- ✅ `timeline.events.create` (Create timeline events - optional)

### Step 4: Create App

1. Click **"Create app"**
2. Agree to the terms
3. Click **"Install app"**

### Step 5: Get Access Token

1. Go to **"Show token"**
2. Copy the **Access Token** (starts with `pat-na1-`)

### Step 6: Create Custom Properties

1. In HubSpot, go to **"Objects"** → **"Companies"**
2. Click **"Manage custom properties"** (or find in settings)
3. Click **"Create property"**

**Property 1: ICP Score**
```
Internal Name: gtm_icp_score
Label: GTM ICP Score
Field Type: Number
```

**Property 2: Intent Score**
```
Internal Name: gtm_intent_score
Label: GTM Intent Score
Field Type: Number
```

**Property 3: Segment**
```
Internal Name: gtm_segment
Label: GTM Segment
Field Type: Single select
Options: qualified_inbound, strategic_fit, emerging, low_priority, unqualified
```

### Step 7: Configure .env File

Edit your `.env` file and add:

```bash
# HubSpot Configuration
HUBSPOT_API_KEY=pat-na1-xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ▶️ Running the Integration

### Option 1: Use the Integration Example (Recommended)

```bash
cd gtm-ai-system
python integration_example.py
```

This runs all 3 integration scenarios:
1. Salesforce only
2. HubSpot only
3. Both simultaneously

### Option 2: Use in Your Own Code

**Salesforce Example:**
```python
from salesforce_connector import SalesforceConnector
from gtm_core_system import GTMSystem

# Connect
sf = SalesforceConnector.from_env()

# Fetch accounts
accounts = sf.fetch_accounts(limit=100)
print(f"Fetched {len(accounts)} from Salesforce")

# Score them
system = GTMSystem()
scored = []
for account in accounts:
    scored.append(system.score_account(account, []))

# Sync back
sf.sync_all_scores(scored)
print("✅ Synced to Salesforce!")
```

**HubSpot Example:**
```python
from hubspot_connector import HubSpotConnector
from gtm_core_system import GTMSystem

# Connect
hubspot = HubSpotConnector.from_env()

# Fetch companies
companies = hubspot.fetch_companies(limit=100)
print(f"Fetched {len(companies)} from HubSpot")

# Score them
system = GTMSystem()
scored = []
for company in companies:
    scored.append(system.score_account(company, []))

# Sync back
hubspot.sync_all_scores(scored)
print("✅ Synced to HubSpot!")
```

**Both CRMs:**
```python
from salesforce_connector import SalesforceConnector
from hubspot_connector import HubSpotConnector
from gtm_core_system import GTMSystem

system = GTMSystem()

# Salesforce
sf = SalesforceConnector.from_env()
sf_accounts = sf.fetch_accounts()
sf_scored = [system.score_account(a, []) for a in sf_accounts]
sf.sync_all_scores(sf_scored)
print(f"✅ Synced {len(sf_scored)} to Salesforce")

# HubSpot
hubspot = HubSpotConnector.from_env()
hs_companies = hubspot.fetch_companies()
hs_scored = [system.score_account(c, []) for c in hs_companies]
hubspot.sync_all_scores(hs_scored)
print(f"✅ Synced {len(hs_scored)} to HubSpot")
```

### Option 3: Dry Run (Test First)

Test without making actual changes:

```python
sf = SalesforceConnector.from_env()
sf.dry_run = True

accounts = sf.fetch_accounts()
scored = [system.score_account(a, []) for a in accounts]
sf.sync_all_scores(scored)  # Won't actually update Salesforce

# Once verified, remove dry_run
sf.dry_run = False
sf.sync_all_scores(scored)  # Now it updates
```

---

## 🔄 What Gets Synced

### Salesforce Custom Fields

When you sync, these fields are updated on the Account object:

```
GTM_ICP_Score__c      → 0-100 (ICP matching score)
GTM_Intent_Score__c   → 0-100 (Buying intent score)
GTM_Segment__c        → Text (qualified_inbound, strategic_fit, emerging, low_priority, unqualified)
```

### HubSpot Custom Properties

When you sync, these properties are updated on the Company object:

```
gtm_icp_score         → Number (0-100)
gtm_intent_score      → Number (0-100)
gtm_segment           → Single select (qualified_inbound, strategic_fit, etc)
```

---

## 🐛 Troubleshooting

### Salesforce Issues

**"Invalid credentials"**
- Check SALESFORCE_INSTANCE_URL includes `https://`
- Verify Client ID and Client Secret are correct
- Ensure Security Token is appended to password

**"Insufficient permissions"**
- Ensure OAuth app has correct scopes
- User needs permission to read/write Account objects
- Custom fields must exist on Account object

**"Field not found"**
- Verify custom field names match exactly:
  - `GTM_ICP_Score__c` (note the `__c` suffix)
  - `GTM_Intent_Score__c`
  - `GTM_Segment__c`

**"Connection timeout"**
- Check internet connection
- Verify SALESFORCE_INSTANCE_URL is correct
- Try with fewer accounts first (limit=10)

### HubSpot Issues

**"Invalid API key"**
- Verify HUBSPOT_API_KEY starts with `pat-na1-`
- Make sure it's the full token (not truncated)
- Check the app is still active in HubSpot

**"Insufficient permissions"**
- Verify Private App has scopes:
  - `crm.objects.companies.read`
  - `crm.objects.companies.write`

**"Property not found"**
- Verify custom property names:
  - `gtm_icp_score` (lowercase)
  - `gtm_intent_score`
  - `gtm_segment`

**"Rate limit exceeded"**
- HubSpot: Max 10 requests/second
- Add delay: `import time; time.sleep(0.5)`
- Reduce batch size

### General Issues

**.env file not found**
```bash
cp .env.example .env
# Edit with your credentials
```

**Import errors**
```bash
pip install -r requirements.txt
```

**Python version**
- Requires Python 3.7+
- Check: `python --version`

---

## ✅ Testing

### Test 1: Verify Credentials

```python
from salesforce_connector import SalesforceConnector

try:
    sf = SalesforceConnector.from_env()
    print("✅ Salesforce credentials valid")
except Exception as e:
    print(f"❌ Salesforce error: {e}")
```

### Test 2: Fetch Data

```python
accounts = sf.fetch_accounts(limit=1)
print(f"✅ Fetched {len(accounts)} accounts")
for account in accounts:
    print(f"   - {account.get('Name')}")
```

### Test 3: Score Test

```python
from gtm_core_system import GTMSystem

system = GTMSystem()
if len(accounts) > 0:
    scored = system.score_account(accounts[0], [])
    print(f"✅ ICP: {scored.icp_score}, Intent: {scored.intent_score}")
```

### Test 4: Dry Run Sync

```python
sf.dry_run = True
sf.sync_all_scores([scored])
print("✅ Dry run successful - no data changed")
```

### Test 5: Real Sync

```python
sf.dry_run = False
success = sf.sync_all_scores([scored])
print(f"✅ Synced {success} accounts")

# Verify in Salesforce UI
# Go to Account detail → check GTM_ICP_Score__c field
```

---

## 📊 Scheduling Daily Syncs

### Option 1: Cron Job (Linux/Mac)

```bash
# crontab -e

# Every day at 9 AM
0 9 * * * cd /path/to/gtm-ai-system && python integration_example.py >> logs/sync.log 2>&1
```

### Option 2: Windows Task Scheduler

1. Open **Task Scheduler**
2. Create **New Task**
3. Set trigger: **Daily** at 9 AM
4. Set action: Run `python C:\path\to\gtm-ai-system\integration_example.py`

### Option 3: GitHub Actions

Create `.github/workflows/daily-sync.yml`:

```yaml
name: Daily GTM Sync
on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM UTC

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python integration_example.py
        env:
          SALESFORCE_INSTANCE_URL: ${{ secrets.SALESFORCE_INSTANCE_URL }}
          SALESFORCE_CLIENT_ID: ${{ secrets.SALESFORCE_CLIENT_ID }}
          SALESFORCE_CLIENT_SECRET: ${{ secrets.SALESFORCE_CLIENT_SECRET }}
          SALESFORCE_USERNAME: ${{ secrets.SALESFORCE_USERNAME }}
          SALESFORCE_PASSWORD: ${{ secrets.SALESFORCE_PASSWORD }}
          HUBSPOT_API_KEY: ${{ secrets.HUBSPOT_API_KEY }}
```

---

## 🎯 Best Practices

1. **Start with sample data first**
   ```bash
   python main.py  # Uses 20 test accounts
   ```

2. **Test with dry_run=True before real sync**
   ```python
   sf.dry_run = True
   ```

3. **Monitor first sync carefully**
   - Check 1-2 accounts in your CRM
   - Verify fields are correct
   - Check for data issues

4. **Keep .env file safe**
   - Never commit .env to GitHub
   - Use .gitignore to exclude it
   - Store securely (1Password, AWS Secrets, etc)

5. **Regular testing**
   - Weekly: Run dry_run to check
   - Monthly: Full sync and verify
   - Log all syncs for audit trail

6. **Error handling**
   - Check logs for failures
   - Verify API quotas
   - Handle timeouts gracefully

---

## 📞 Support

**Common Questions:**

Q: How often should I sync?
A: Daily (via scheduler) or on-demand via API integration

Q: What happens if sync fails?
A: Check logs, verify credentials, retry with fewer accounts

Q: Can I customize the sync?
A: Yes, edit `salesforce_connector.py` or `hubspot_connector.py`

Q: What if I only want to sync specific accounts?
A: Filter before calling `sync_all_scores()`:
```python
filtered = [a for a in scored if a['icp_score'] > 70]
sf.sync_all_scores(filtered)
```

Q: Can I sync both CRMs with different data?
A: Yes, handle separately or add logic to split data

---

## ✅ Integration Checklist

Before going to production:

- [ ] Created Salesforce Connected App (or HubSpot Private App)
- [ ] Created custom fields/properties in CRM
- [ ] Added credentials to .env file
- [ ] Ran `python integration_example.py` successfully
- [ ] Tested with 1-2 accounts using dry_run
- [ ] Verified fields updated in CRM
- [ ] Checked for any errors in logs
- [ ] Set up scheduling (cron/task scheduler/GitHub Actions)
- [ ] Documented the sync process
- [ ] Trained team on checking results

---

**Status:** ✅ Ready for Production Integration

**Last Updated:** October 4, 2026
