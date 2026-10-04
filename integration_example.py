"""
GTM AI System - CRM Integration Examples
Shows how to connect to Salesforce and HubSpot
"""

import os
from dotenv import load_dotenv
from gtm_core_system import GTMSystem, Account
from salesforce_connector import SalesforceConnector
from hubspot_connector import HubSpotConnector

# Load environment variables from .env
load_dotenv()

print("\n" + "="*80)
print("🔗 GTM AI SYSTEM - CRM INTEGRATION EXAMPLES")
print("="*80)

# ============================================================================
# EXAMPLE 1: SALESFORCE INTEGRATION
# ============================================================================

print("\n\n📌 EXAMPLE 1: Salesforce Integration")
print("-" * 80)

try:
    # Initialize Salesforce connector from .env
    print("1️⃣  Connecting to Salesforce...")
    sf = SalesforceConnector.from_env()

    # Fetch all accounts from Salesforce
    print("2️⃣  Fetching accounts from Salesforce...")
    sf_accounts = sf.fetch_accounts(limit=100)

    if sf_accounts:
        # Score them with GTM system
        print("3️⃣  Scoring accounts with GTM AI...")
        gtm_system = GTMSystem()
        scored_accounts = []

        for sf_account in sf_accounts:
            # Convert Salesforce format to our Account class
            account = Account(
                id=sf_account.get('Id'),
                name=sf_account.get('Name'),
                industry=sf_account.get('Industry', 'Unknown'),
                size=sf_account.get('NumberOfEmployees', 0),
                revenue=sf_account.get('AnnualRevenue', 0),
                location=sf_account.get('BillingCountry', 'Unknown'),
                founded=2020  # Would need to fetch from SF if available
            )

            scored = gtm_system.score_account(account, [])
            scored_accounts.append({
                'id': scored.id,
                'sf_id': sf_account.get('Id'),
                'name': scored.name,
                'icp_score': scored.icp_score,
                'intent_score': scored.intent_score,
                'segment': scored.segment
            })

        # Sync scores back to Salesforce
        print("4️⃣  Syncing scores back to Salesforce...")
        success = sf.sync_all_scores(scored_accounts)

        print(f"\n✅ Salesforce Integration Complete!")
        print(f"   • Fetched: {len(sf_accounts)} accounts")
        print(f"   • Scored: {len(scored_accounts)} accounts")
        print(f"   • Synced: {success} accounts")
        print(f"\n   Custom fields updated in Salesforce:")
        print(f"   - GTM_ICP_Score__c (0-100)")
        print(f"   - GTM_Intent_Score__c (0-100)")
        print(f"   - GTM_Segment__c (qualified_inbound, strategic_fit, etc)")
    else:
        print("⚠️  No accounts found in Salesforce")

except Exception as e:
    print(f"❌ Salesforce Integration Error: {e}")
    print(f"   Make sure you have set these in .env:")
    print(f"   - SALESFORCE_INSTANCE_URL")
    print(f"   - SALESFORCE_CLIENT_ID")
    print(f"   - SALESFORCE_CLIENT_SECRET")
    print(f"   - SALESFORCE_USERNAME")
    print(f"   - SALESFORCE_PASSWORD")

# ============================================================================
# EXAMPLE 2: HUBSPOT INTEGRATION
# ============================================================================

print("\n\n📌 EXAMPLE 2: HubSpot Integration")
print("-" * 80)

try:
    # Initialize HubSpot connector from .env
    print("1️⃣  Connecting to HubSpot...")
    hubspot = HubSpotConnector.from_env()

    # Fetch all companies from HubSpot
    print("2️⃣  Fetching companies from HubSpot...")
    hs_companies = hubspot.fetch_companies(limit=100)

    if hs_companies:
        # Score them with GTM system
        print("3️⃣  Scoring companies with GTM AI...")
        gtm_system = GTMSystem()
        scored_companies = []

        for hs_company in hs_companies:
            # Convert HubSpot format to our Account class
            props = hs_company.get('properties', {})
            account = Account(
                id=hs_company.get('id'),
                name=props.get('name', 'Unknown'),
                industry=props.get('industry', 'Unknown'),
                size=int(props.get('numberofemployees', 0) or 0),
                revenue=float(props.get('annualrevenue', 0) or 0),
                location=props.get('country', 'Unknown'),
                founded=2020
            )

            scored = gtm_system.score_account(account, [])
            scored_companies.append({
                'id': scored.id,
                'hs_id': hs_company.get('id'),
                'name': scored.name,
                'icp_score': scored.icp_score,
                'intent_score': scored.intent_score,
                'segment': scored.segment
            })

        # Sync scores back to HubSpot
        print("4️⃣  Syncing scores back to HubSpot...")
        success = hubspot.sync_all_scores(scored_companies)

        print(f"\n✅ HubSpot Integration Complete!")
        print(f"   • Fetched: {len(hs_companies)} companies")
        print(f"   • Scored: {len(scored_companies)} companies")
        print(f"   • Synced: {success} companies")
        print(f"\n   Custom properties created in HubSpot:")
        print(f"   - gtm_icp_score (0-100)")
        print(f"   - gtm_intent_score (0-100)")
        print(f"   - gtm_segment (qualified_inbound, strategic_fit, etc)")
    else:
        print("⚠️  No companies found in HubSpot")

except Exception as e:
    print(f"❌ HubSpot Integration Error: {e}")
    print(f"   Make sure you have set this in .env:")
    print(f"   - HUBSPOT_API_KEY")

# ============================================================================
# EXAMPLE 3: USING BOTH SALESFORCE AND HUBSPOT TOGETHER
# ============================================================================

print("\n\n📌 EXAMPLE 3: Sync to Both CRMs Simultaneously")
print("-" * 80)

try:
    print("🚀 Syncing accounts to BOTH Salesforce and HubSpot...")

    gtm_system = GTMSystem()

    # Try Salesforce
    sf_success = 0
    try:
        print("\n1️⃣  Syncing to Salesforce...")
        sf = SalesforceConnector.from_env()
        sf_accounts = sf.fetch_accounts(limit=100)

        scored_sf = []
        for sf_account in sf_accounts:
            account = Account(
                id=sf_account.get('Id'),
                name=sf_account.get('Name'),
                industry=sf_account.get('Industry', 'Unknown'),
                size=sf_account.get('NumberOfEmployees', 0),
                revenue=sf_account.get('AnnualRevenue', 0),
                location=sf_account.get('BillingCountry', 'Unknown'),
                founded=2020
            )
            scored = gtm_system.score_account(account, [])
            scored_sf.append({
                'id': scored.id,
                'sf_id': sf_account.get('Id'),
                'icp_score': scored.icp_score,
                'intent_score': scored.intent_score,
                'segment': scored.segment
            })

        sf_success = sf.sync_all_scores(scored_sf)
        print(f"   ✅ Synced {sf_success} to Salesforce")
    except Exception as e:
        print(f"   ⚠️  Salesforce sync skipped: {e}")

    # Try HubSpot
    hs_success = 0
    try:
        print("2️⃣  Syncing to HubSpot...")
        hubspot = HubSpotConnector.from_env()
        hs_companies = hubspot.fetch_companies(limit=100)

        scored_hs = []
        for hs_company in hs_companies:
            props = hs_company.get('properties', {})
            account = Account(
                id=hs_company.get('id'),
                name=props.get('name', 'Unknown'),
                industry=props.get('industry', 'Unknown'),
                size=int(props.get('numberofemployees', 0) or 0),
                revenue=float(props.get('annualrevenue', 0) or 0),
                location=props.get('country', 'Unknown'),
                founded=2020
            )
            scored = gtm_system.score_account(account, [])
            scored_hs.append({
                'id': scored.id,
                'hs_id': hs_company.get('id'),
                'icp_score': scored.icp_score,
                'intent_score': scored.intent_score,
                'segment': scored.segment
            })

        hs_success = hubspot.sync_all_scores(scored_hs)
        print(f"   ✅ Synced {hs_success} to HubSpot")
    except Exception as e:
        print(f"   ⚠️  HubSpot sync skipped: {e}")

    if sf_success + hs_success > 0:
        print(f"\n✅ Dual CRM Sync Complete!")
        print(f"   Total Synced: {sf_success + hs_success} accounts")

except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# SETUP GUIDE
# ============================================================================

print("\n\n" + "="*80)
print("🔧 SETUP INSTRUCTIONS FOR CRM INTEGRATION")
print("="*80)

print("""
SALESFORCE SETUP:
─────────────────────────────────────────────────────────────
1. In Salesforce Setup, search for "App Manager"
2. Create New Connected App:
   - Name: GTM AI System
   - Enable OAuth Settings
   - Callback URL: http://localhost:8000/callback
   - Scopes: Full, Refresh Token, Perform Requests
3. Get: Client ID, Client Secret
4. Create custom fields on Account object:
   - GTM_ICP_Score__c (Number, 0-100)
   - GTM_Intent_Score__c (Number, 0-100)
   - GTM_Segment__c (Text, 100 chars)
5. Add to .env:
   SALESFORCE_INSTANCE_URL=https://your-domain.salesforce.com
   SALESFORCE_CLIENT_ID=your_client_id
   SALESFORCE_CLIENT_SECRET=your_client_secret
   SALESFORCE_USERNAME=your_email@company.com
   SALESFORCE_PASSWORD=your_password+security_token

HUBSPOT SETUP:
─────────────────────────────────────────────────────────────
1. Go to HubSpot Settings → Integrations → Private Apps
2. Create Private App:
   - Name: GTM AI System
   - Scopes: crm.objects.companies.read, crm.objects.companies.write
3. Get: Access Token
4. Create custom properties on Companies:
   - gtm_icp_score (Number, 0-100)
   - gtm_intent_score (Number, 0-100)
   - gtm_segment (Single select)
5. Add to .env:
   HUBSPOT_API_KEY=pat-na1-xxxxxxxx

RUN THIS FILE:
─────────────────────────────────────────────────────────────
python integration_example.py

This will:
  • Connect to your CRM(s)
  • Fetch all accounts
  • Score them with GTM AI
  • Sync scores back to custom fields
  • Show results
""")

print("\n" + "="*80)
print("✅ Integration examples complete!")
print("="*80 + "\n")
