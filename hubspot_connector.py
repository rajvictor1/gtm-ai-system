"""
HubSpot Connector - CRM Integration
Connects to HubSpot, syncs accounts, and updates records with GTM scores
"""

import requests
from typing import List, Dict
import os

class HubSpotConnector:
    """Connect to HubSpot and sync accounts"""

    def __init__(self, api_key: str):
        """
        Initialize HubSpot connection

        Args:
            api_key: HubSpot private app API key
        """
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def fetch_companies(self, limit: int = 100) -> List[Dict]:
        """Fetch all companies from HubSpot"""

        url = f"{self.base_url}/crm/v3/objects/companies"
        params = {
            'limit': limit,
            'properties': ['name', 'city', 'state', 'country', 'numberofemployees', 'annualrevenue', 'industry']
        }

        all_companies = []
        after = None

        try:
            while True:
                if after:
                    params['after'] = after

                response = requests.get(url, headers=self.headers, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    all_companies.extend(data.get('results', []))

                    if 'paging' in data and 'next' in data['paging']:
                        after = data['paging']['next']['after']
                    else:
                        break
                else:
                    print(f"❌ Fetch failed: {response.text}")
                    break

            print(f"✅ Fetched {len(all_companies)} companies from HubSpot")
            return all_companies
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def sync_scores(self, company_id: str, icp_score: float, intent_score: float, segment: str) -> bool:
        """Update company record with GTM scores"""

        url = f"{self.base_url}/crm/v3/objects/companies/{company_id}"

        payload = {
            'properties': {
                'gtm_icp_score': str(icp_score),
                'gtm_intent_score': str(intent_score),
                'gtm_segment': segment
            }
        }

        try:
            response = requests.patch(url, headers=self.headers, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                print(f"⚠️  Sync failed for {company_id}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def sync_all_scores(self, companies_with_scores: List[Dict]) -> int:
        """Batch sync scores to HubSpot"""
        success_count = 0

        for company in companies_with_scores:
            hs_id = company.get('id') or company.get('hs_id')
            if hs_id and self.sync_scores(hs_id, company['icp_score'], company['intent_score'], company['segment']):
                success_count += 1

        print(f"✅ Synced {success_count}/{len(companies_with_scores)} companies to HubSpot")
        return success_count

    @staticmethod
    def from_env():
        """Create connector from environment variables"""
        api_key = os.getenv('HUBSPOT_API_KEY')
        if not api_key:
            raise ValueError("HUBSPOT_API_KEY not set")
        return HubSpotConnector(api_key)
