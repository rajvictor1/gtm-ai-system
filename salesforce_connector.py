"""
Salesforce Connector - CRM Integration
Connects to Salesforce, syncs accounts, and updates records with GTM scores
"""

import requests
from typing import List, Dict
import os

class SalesforceConnector:
    """Connect to Salesforce and sync accounts"""

    def __init__(self, instance_url: str, client_id: str, client_secret: str, username: str, password: str):
        """
        Initialize Salesforce connection

        Args:
            instance_url: e.g., 'https://yourcompany.salesforce.com'
            client_id: OAuth Client ID
            client_secret: OAuth Client Secret
            username: Salesforce username
            password: Salesforce password + security token
        """
        self.instance_url = instance_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.access_token = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Salesforce OAuth"""
        auth_url = f"{self.instance_url}/services/oauth2/token"
        payload = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.username,
            'password': self.password
        }

        try:
            response = requests.post(auth_url, data=payload, timeout=10)
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                print("✅ Salesforce authentication successful")
            else:
                print(f"❌ Authentication failed: {response.text}")
        except Exception as e:
            print(f"❌ Connection error: {e}")

    def fetch_accounts(self, limit: int = 1000) -> List[Dict]:
        """Fetch all accounts from Salesforce"""

        if not self.access_token:
            print("❌ Not authenticated")
            return []

        query = f"""
        SELECT Id, Name, BillingCity, BillingCountry, NumberOfEmployees, AnnualRevenue, Industry
        FROM Account
        LIMIT {limit}
        """

        url = f"{self.instance_url}/services/data/v57.0/query"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {'q': query}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                records = response.json().get('records', [])
                print(f"✅ Fetched {len(records)} accounts from Salesforce")
                return records
            else:
                print(f"❌ Query failed: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return []

    def sync_scores(self, account_id: str, icp_score: float, intent_score: float, segment: str) -> bool:
        """Update account record with GTM scores"""

        if not self.access_token:
            print("❌ Not authenticated")
            return False

        url = f"{self.instance_url}/services/data/v57.0/sobjects/Account/{account_id}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'GTM_ICP_Score__c': icp_score,
            'GTM_Intent_Score__c': intent_score,
            'GTM_Segment__c': segment
        }

        try:
            response = requests.patch(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 204:
                return True
            else:
                print(f"⚠️  Sync failed for {account_id}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def sync_all_scores(self, accounts_with_scores: List[Dict]) -> int:
        """Batch sync scores to Salesforce"""
        success_count = 0

        for account in accounts_with_scores:
            sf_id = account.get('id') or account.get('sf_id')
            if sf_id and self.sync_scores(sf_id, account['icp_score'], account['intent_score'], account['segment']):
                success_count += 1

        print(f"✅ Synced {success_count}/{len(accounts_with_scores)} accounts to Salesforce")
        return success_count

    @staticmethod
    def from_env():
        """Create connector from environment variables"""
        return SalesforceConnector(
            instance_url=os.getenv('SALESFORCE_INSTANCE_URL'),
            client_id=os.getenv('SALESFORCE_CLIENT_ID'),
            client_secret=os.getenv('SALESFORCE_CLIENT_SECRET'),
            username=os.getenv('SALESFORCE_USERNAME'),
            password=os.getenv('SALESFORCE_PASSWORD')
        )
