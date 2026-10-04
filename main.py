"""
GTM AI System - Main Orchestrator
Orchestrates all components: scoring, research, personalization, measurement
"""

from gtm_core_system import GTMSystem, ICP, SampleDataGenerator, Account
from research_agent import AccountResearchAgent
from personalization_engine import OutreachPersonalizationEngine
from ab_testing import ABTest
from roi_tracking import ROITracker, ConversionEvent
import json
from datetime import datetime

class GTMOrchestrator:
    """Main orchestrator for entire GTM AI system"""

    def __init__(self, api_key: str = None, crm_connector = None):
        """
        Initialize orchestrator

        Args:
            api_key: Anthropic API key for Claude
            crm_connector: Salesforce or HubSpot connector
        """
        self.gtm_system = GTMSystem()
        self.research_agent = AccountResearchAgent(api_key)
        self.personalization_engine = OutreachPersonalizationEngine(api_key)
        self.crm_connector = crm_connector
        self.roi_tracker = ROITracker()
        self.ab_tests = {}
        self.accounts = []

    def run_complete_pipeline(self):
        """Run complete GTM AI pipeline"""
        print("\n" + "="*80)
        print("🚀 GTM AI SYSTEM - COMPLETE PIPELINE")
        print("="*80)

        # Step 1: Load and score accounts
        print("\n📊 STEP 1: Loading and Scoring Accounts")
        print("-" * 80)
        accounts = SampleDataGenerator.generate_sample_accounts()
        self.accounts = self.gtm_system.score_all_accounts(accounts)

        print(f"✅ Scored {len(self.accounts)} accounts")
        counts = self.gtm_system.get_segment_counts()
        for segment, count in counts.items():
            print(f"   • {segment}: {count}")

        # Step 2: Research top 5 accounts
        print("\n🔍 STEP 2: Research Top 5 Accounts")
        print("-" * 80)
        for i, account in enumerate(self.accounts[:5], 1):
            print(f"\n{i}. {account.name}")
            brief = self.research_agent.generate_research_brief(account.to_dict())
            print(f"   {brief[:100]}...")

            talking_points = self.research_agent.generate_talking_points(account.to_dict())
            if talking_points:
                print(f"   Top point: {talking_points[0]}")

        # Step 3: Generate personalized outreach
        print("\n✉️  STEP 3: Generating Personalized Outreach")
        print("-" * 80)
        for i, account in enumerate(self.accounts[:3], 1):
            print(f"\n{i}. {account.name}")
            subject = self.personalization_engine.generate_email_subject(account.to_dict())
            print(f"   Subject: {subject}")

            body = self.personalization_engine.generate_email_body(
                account.to_dict(), "Sales Rep", "Our Company"
            )
            print(f"   Body preview: {body[:80]}...")

        # Step 4: Display metrics
        print("\n📈 STEP 4: Performance Metrics")
        print("-" * 80)
        print("\nTop 5 Accounts by Combined Score:")
        for i, account in enumerate(self.accounts[:5], 1):
            print(f"{i}. {account.name:30} | ICP: {account.icp_score:5.1f} | Intent: {account.intent_score:5.1f} | Segment: {account.segment}")

        print("\n✅ Pipeline Complete!")
        return self.accounts

    def create_ab_test(self, test_id: str, test_name: str, variant_a: dict, variant_b: dict) -> ABTest:
        """Create and track A/B test"""
        test = ABTest(test_id, test_name, variant_a, variant_b)
        self.ab_tests[test_id] = test
        print(f"✅ Created A/B test: {test_name}")
        return test

    def export_accounts_to_json(self, filename: str = "gtm_accounts.json"):
        """Export scored accounts to JSON"""
        self.gtm_system.export_to_json(filename)

    def export_accounts_to_csv(self, filename: str = "gtm_accounts.csv"):
        """Export scored accounts to CSV"""
        import csv

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'name', 'industry', 'size', 'revenue', 'location', 'founded',
                'icp_score', 'intent_score', 'combined_score', 'segment', 'signals'
            ])
            writer.writeheader()
            for account in self.accounts:
                writer.writerow(account.to_dict())

        print(f"✅ Exported {len(self.accounts)} accounts to {filename}")

    def generate_full_report(self) -> str:
        """Generate comprehensive GTM AI report"""
        counts = self.gtm_system.get_segment_counts()

        report = f"""
╔════════════════════════════════════════════════════════════╗
║  GTM AI SYSTEM - COMPREHENSIVE REPORT                     ║
║  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
╚════════════════════════════════════════════════════════════╝

ACCOUNT OVERVIEW
─────────────────────────────────────────────────────────────
Total Accounts: {len(self.accounts)}

Segment Breakdown:
  • Qualified Inbound:  {counts.get('qualified_inbound', 0)} accounts (HOT - Call today)
  • Strategic Fit:      {counts.get('strategic_fit', 0)} accounts (Nurture)
  • Emerging:           {counts.get('emerging', 0)} accounts (Build relationship)
  • Low Priority:       {counts.get('low_priority', 0)} accounts (Monitor)
  • Unqualified:        {counts.get('unqualified', 0)} accounts (Skip)

TOP 10 PRIORITY ACCOUNTS
─────────────────────────────────────────────────────────────
        """

        for i, account in enumerate(self.accounts[:10], 1):
            report += f"\n{i:2}. {account.name:30} | {account.industry:15} | ICP:{account.icp_score:5.1f} | Intent:{account.intent_score:5.1f} | {account.segment}"

        report += f"""

NEXT STEPS
─────────────────────────────────────────────────────────────
1. ✅ Review top {len([a for a in self.accounts if a.segment == 'qualified_inbound'])} hot accounts
2. ✅ Start personalized outreach to qualified_inbound segment
3. ✅ Schedule demos with interested prospects
4. ✅ Track A/B test results for email variants
5. ✅ Monitor ROI and conversion rates

SYSTEM STATUS: ✅ READY FOR DEPLOYMENT
        """

        return report

# Main execution
if __name__ == "__main__":
    # Create orchestrator
    orchestrator = GTMOrchestrator()

    # Run complete pipeline
    accounts = orchestrator.run_complete_pipeline()

    # Export results
    orchestrator.export_accounts_to_json("gtm_accounts.json")
    orchestrator.export_accounts_to_csv("gtm_accounts.csv")

    # Generate report
    report = orchestrator.generate_full_report()
    print("\n" + report)

    print("\n✅ GTM AI System - All files ready!")
    print("   • gtm_accounts.json - Scored accounts (JSON)")
    print("   • gtm_accounts.csv - Scored accounts (CSV)")
