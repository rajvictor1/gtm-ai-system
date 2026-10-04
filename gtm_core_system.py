"""
GTM AI System - Core Scoring Engine
Handles ICP matching, buying signal detection, and account segmentation
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict
from enum import Enum
import json

# ==================== ENUMS ====================

class Segment(Enum):
    QUALIFIED_INBOUND = "qualified_inbound"
    STRATEGIC_FIT = "strategic_fit"
    EMERGING = "emerging"
    LOW_PRIORITY = "low_priority"
    UNQUALIFIED = "unqualified"

class SignalType(Enum):
    DEMO_REQUESTED = ("demo_requested", 10)
    PRICING_PAGE = ("pricing_page", 8)
    JOB_POSTING = ("job_posting", 7)
    FUNDING_ANNOUNCEMENT = ("funding_announcement", 6)
    WEBSITE_SPIKE = ("website_spike", 5)
    EXEC_PROFILE_VIEWS = ("exec_profile_views", 5)
    WHITEPAPER_DOWNLOAD = ("whitepaper_download", 4)
    LINKEDIN_ENGAGEMENT = ("linkedin_engagement", 3)
    CUSTOMER_REVIEW = ("customer_review", 2)
    COMPETITOR_MENTION = ("competitor_mention", 1)

# ==================== DATA MODELS ====================

@dataclass
class ICP:
    """Ideal Customer Profile definition"""
    target_industries: List[str] = field(default_factory=lambda: [
        "SaaS", "FinTech", "MarTech", "Healthcare", "EdTech", "Security", "Retail"
    ])
    min_size: int = 100
    max_size: int = 5000
    min_revenue: float = 10.0
    max_revenue: float = 200.0
    target_locations: List[str] = field(default_factory=lambda: ["US", "UK", "Canada", "Germany", "Australia"])

@dataclass
class Account:
    """Account/Prospect data model"""
    id: str
    name: str
    industry: str
    size: int
    revenue: float
    location: str
    founded: int
    icp_score: float = 0.0
    intent_score: float = 0.0
    combined_score: float = 0.0
    segment: str = "low_priority"
    signals: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)

# ==================== CORE ENGINES ====================

class ICPMatcher:
    """Calculate ICP fit score (0-100)"""

    def __init__(self, icp: ICP):
        self.icp = icp

    def calculate_score(self, account: Account) -> float:
        """Calculate ICP score based on 4 factors (max 100)"""
        score = 0

        # Industry match (30 points)
        if account.industry in self.icp.target_industries:
            score += 30

        # Company size (30 points)
        if self.icp.min_size <= account.size <= self.icp.max_size:
            score += 30
        elif account.size < self.icp.min_size:
            score += max(0, 30 * (account.size / self.icp.min_size))
        elif account.size > self.icp.max_size:
            score += max(0, 30 * (self.icp.max_size / account.size))

        # Annual revenue (20 points)
        if self.icp.min_revenue <= account.revenue <= self.icp.max_revenue:
            score += 20
        elif account.revenue < self.icp.min_revenue:
            score += max(0, 20 * (account.revenue / self.icp.min_revenue))
        elif account.revenue > self.icp.max_revenue:
            score += max(0, 20 * (self.icp.max_revenue / account.revenue))

        # Recency (20 points)
        from datetime import datetime
        current_year = datetime.now().year
        company_age = current_year - account.founded

        if company_age <= 10:
            score += 20
        elif company_age <= 20:
            score += 15
        else:
            score += max(0, 20 * (1 - (company_age - 20) / 20))

        return min(100, max(0, score))

class BuyingSignalAnalyzer:
    """Detect and weight buying signals"""

    SIGNAL_WEIGHTS = {
        "demo_requested": 10,
        "pricing_page": 8,
        "job_posting": 7,
        "funding_announcement": 6,
        "website_spike": 5,
        "exec_profile_views": 5,
        "whitepaper_download": 4,
        "linkedin_engagement": 3,
        "customer_review": 2,
        "competitor_mention": 1
    }

    def calculate_intent_score(self, signals_detected: List[str]) -> float:
        """Calculate buying intent score (0-100)"""
        if not signals_detected:
            return 0

        total_weight = sum(
            self.SIGNAL_WEIGHTS.get(signal, 0)
            for signal in signals_detected
        )

        max_possible_weight = sum(self.SIGNAL_WEIGHTS.values())
        intent_score = (total_weight / max_possible_weight) * 100

        return min(100, max(0, intent_score))

    def get_signal_count(self, signals_detected: List[str]) -> int:
        """Return count of detected signals"""
        return len(signals_detected)

class SegmentationEngine:
    """Route accounts to segments"""

    @staticmethod
    def segment_account(account: Account) -> str:
        """Segment account based on ICP + Intent scores"""

        if account.icp_score > 70 and account.intent_score > 70:
            return "qualified_inbound"
        elif account.icp_score > 80 and 30 <= account.intent_score <= 70:
            return "strategic_fit"
        elif account.intent_score > 30 and 40 <= account.icp_score <= 80:
            return "emerging"
        elif account.icp_score < 20:
            return "unqualified"
        else:
            return "low_priority"

class SampleDataGenerator:
    """Generate realistic sample data"""

    @staticmethod
    def generate_sample_accounts() -> List[Account]:
        """Generate 20 sample accounts (3 hot, 5 mid, 12 cold)"""

        hot = [
            Account(id="ACC_H01", name="FastGrow SaaS", industry="SaaS", size=450,
                   revenue=35.5, location="US", founded=2018),
            Account(id="ACC_H02", name="PaymentPro", industry="FinTech", size=680,
                   revenue=52.3, location="UK", founded=2017),
            Account(id="ACC_H03", name="DataFlow Analytics", industry="SaaS", size=520,
                   revenue=42.1, location="Canada", founded=2019),
        ]

        mid = [
            Account(id="ACC_M01", name="CloudDeploy Systems", industry="SaaS", size=780,
                   revenue=62.4, location="Germany", founded=2016),
            Account(id="ACC_M02", name="MarketingCloud Suite", industry="MarTech", size=680,
                   revenue=52.1, location="US", founded=2015),
            Account(id="ACC_M03", name="HealthTech Innovations", industry="Healthcare", size=450,
                   revenue=28.9, location="Canada", founded=2017),
            Account(id="ACC_M04", name="EduSoft Learning", industry="EdTech", size=220,
                   revenue=16.4, location="India", founded=2020),
            Account(id="ACC_M05", name="SecurityCore Systems", industry="SaaS", size=920,
                   revenue=72.3, location="US", founded=2014),
        ]

        cold = [
            Account(id="ACC_C01", name="DataAnalytics Enterprise", industry="SaaS", size=1400,
                   revenue=108.5, location="US", founded=2012),
            Account(id="ACC_C02", name="PaymentFlow Tech", industry="FinTech", size=650,
                   revenue=55.8, location="UK", founded=2013),
            Account(id="ACC_C03", name="CloudInfrastructure", industry="SaaS", size=1250,
                   revenue=95.8, location="Germany", founded=2013),
            Account(id="ACC_C04", name="TechCorp Solutions", industry="SaaS", size=520,
                   revenue=45.2, location="US", founded=2015),
            Account(id="ACC_C05", name="FinanceCloud Pro", industry="FinTech", size=1100,
                   revenue=85.2, location="US", founded=2013),
            Account(id="ACC_C06", name="InsureAI Solutions", industry="Insurance", size=2500,
                   revenue=150.0, location="US", founded=2010),
            Account(id="ACC_C07", name="RetailX Platform", industry="Retail", size=1800,
                   revenue=95.3, location="Australia", founded=2013),
            Account(id="ACC_C08", name="LogisticsPro", industry="Logistics", size=3200,
                   revenue=180.0, location="UK", founded=2009),
            Account(id="ACC_C09", name="ManufacturingHub", industry="Manufacturing", size=5500,
                   revenue=250.0, location="Germany", founded=2008),
            Account(id="ACC_C10", name="PropertyTech Inc", industry="Real Estate", size=380,
                   revenue=18.5, location="US", founded=2018),
            Account(id="ACC_C11", name="AgriTech Solutions", industry="Agriculture", size=250,
                   revenue=12.3, location="India", founded=2019),
            Account(id="ACC_C12", name="MediaStream Services", industry="Media", size=950,
                   revenue=68.7, location="Canada", founded=2014),
        ]

        return hot + mid + cold

class GTMSystem:
    """Main GTM AI System orchestrator"""

    def __init__(self, icp: ICP = None):
        self.icp = icp or ICP()
        self.icp_matcher = ICPMatcher(self.icp)
        self.signal_analyzer = BuyingSignalAnalyzer()
        self.segmentation = SegmentationEngine()
        self.accounts: List[Account] = []

    def score_account(self, account: Account, signals_detected: List[str] = None) -> Account:
        """Score a single account"""
        if signals_detected is None:
            signals_detected = []

        account.icp_score = self.icp_matcher.calculate_score(account)
        account.intent_score = self.signal_analyzer.calculate_intent_score(signals_detected)
        account.combined_score = (account.icp_score + account.intent_score) / 2
        account.signals = self.signal_analyzer.get_signal_count(signals_detected)
        account.segment = self.segmentation.segment_account(account)

        return account

    def score_all_accounts(self, accounts: List[Account]) -> List[Account]:
        """Score multiple accounts and sort by combined score"""
        self.accounts = []
        for account in accounts:
            import random
            num_signals = random.randint(0, 5) if account.icp_score > 50 else random.randint(0, 2)
            available_signals = list(self.signal_analyzer.SIGNAL_WEIGHTS.keys())
            signals = random.sample(available_signals, min(num_signals, len(available_signals)))

            scored_account = self.score_account(account, signals)
            self.accounts.append(scored_account)

        self.accounts.sort(key=lambda a: a.combined_score, reverse=True)
        return self.accounts

    def get_segment_counts(self) -> Dict[str, int]:
        """Get count of accounts in each segment"""
        counts = {s: 0 for s in ["qualified_inbound", "strategic_fit", "emerging", "low_priority", "unqualified"]}
        for account in self.accounts:
            if account.segment in counts:
                counts[account.segment] += 1
        return counts

    def export_to_dict(self) -> List[Dict]:
        """Export all accounts as dictionaries"""
        return [account.to_dict() for account in self.accounts]

    def export_to_json(self, filename: str):
        """Export accounts to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.export_to_dict(), f, indent=2)
        print(f"✅ Exported {len(self.accounts)} accounts to {filename}")

# Demo
if __name__ == "__main__":
    icp = ICP()
    system = GTMSystem(icp)
    accounts = SampleDataGenerator.generate_sample_accounts()
    scored = system.score_all_accounts(accounts)

    print("=" * 80)
    print("GTM AI SYSTEM - ACCOUNT SCORING RESULTS")
    print("=" * 80)

    for i, account in enumerate(scored[:5], 1):
        print(f"\n{i}. {account.name}")
        print(f"   Industry: {account.industry} | Size: {account.size} | Revenue: ${account.revenue}M")
        print(f"   ICP: {account.icp_score:.1f} | Intent: {account.intent_score:.1f} | Combined: {account.combined_score:.1f}")
        print(f"   Signals: {account.signals} | Segment: {account.segment}")

    counts = system.get_segment_counts()
    print("\n" + "=" * 80)
    print("SEGMENT BREAKDOWN")
    print("=" * 80)
    for segment, count in counts.items():
        print(f"{segment}: {count}")
