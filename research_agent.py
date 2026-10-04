"""
Research Agent - Claude API Integration
Generates research briefs, talking points, and insights
"""

from typing import Dict, List
import os

class AccountResearchAgent:
    """AI-powered account research using Claude API"""

    def __init__(self, api_key: str = None):
        """Initialize with Anthropic API key"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        # Lazy import - only load if API key exists
        if self.api_key:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-opus-5-5"
            self.available = True
        else:
            self.available = False
            print("⚠️  ANTHROPIC_API_KEY not set. Research agent in demo mode.")

    def generate_research_brief(self, account: Dict) -> str:
        """Generate research brief for an account"""

        if not self.available:
            return self._demo_research_brief(account)

        try:
            prompt = f"""
            You are a B2B sales research expert. Generate a 2-paragraph research brief.

            Account: {account['name']} ({account['industry']}, {account['size']} emp, ${account['revenue']}M)
            ICP Fit: {account['icp_score']}/100
            Buying Intent: {account['intent_score']}/100
            Segment: {account['segment']}

            Focus on: fit, pain points, recommended approach (3-4 sentences max).
            """

            message = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text
        except Exception as e:
            print(f"⚠️  API error: {e}. Using demo response.")
            return self._demo_research_brief(account)

    def _demo_research_brief(self, account: Dict) -> str:
        """Demo research brief when API not available"""
        if account['segment'] == 'qualified_inbound':
            return f"{account['name']} shows strong fit ({account['icp_score']:.0f} ICP) with high buying intent ({account['intent_score']:.0f}). They're actively evaluating solutions. Recommend immediate outreach with specific value prop tied to their {account['industry']} challenges."
        elif account['segment'] == 'strategic_fit':
            return f"Excellent strategic fit ({account['icp_score']:.0f} ICP) but early-stage interest ({account['intent_score']:.0f} intent). Position as thought leader in {account['industry']}. Focus on building relationship and demonstrating unique approach."
        else:
            return f"{account['name']} has moderate fit. Limited immediate interest detected. Monitor for changes in signals and build value case over time."

    def generate_talking_points(self, account: Dict) -> List[str]:
        """Generate talking points for sales team"""

        if not self.available:
            return self._demo_talking_points(account)

        try:
            prompt = f"""
            Generate 4 talking points for {account['name']} ({account['industry']}, {account['size']} emp).
            ICP: {account['icp_score']}/100, Intent: {account['intent_score']}/100
            Segment: {account['segment']}

            Each point: 1 sentence, specific, actionable. Format as numbered list.
            """

            message = self.client.messages.create(
                model=self.model,
                max_tokens=250,
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text
            points = [line.strip() for line in response.split('\n') if line.strip() and any(c.isdigit() for c in line[:3])]
            return points[:4]
        except Exception as e:
            print(f"⚠️  API error: {e}. Using demo points.")
            return self._demo_talking_points(account)

    def _demo_talking_points(self, account: Dict) -> List[str]:
        """Demo talking points"""
        return [
            f"Your {account['industry']} business is growing fast - operating at {account['size']} employees.",
            f"With ${account['revenue']}M revenue, you're in prime position to optimize operations.",
            f"Companies like you typically struggle with scaling efficiently in {account['industry']}.",
            "We help teams just like yours compress timelines by 40% while reducing costs."
        ]

    def generate_company_insights(self, company_name: str, industry: str) -> str:
        """Research company and generate insights"""

        if not self.available:
            return f"{company_name} operates in {industry}. Typical challenges: scaling, cost control, team coordination."

        try:
            prompt = f"""
            Research {company_name} ({industry}). Provide 3 key insights:
            1. Business drivers
            2. Typical challenges
            3. Recommended approach

            Keep to 4 sentences. Be specific and actionable.
            """

            message = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text
        except Exception as e:
            return f"{company_name} ({industry}): Typical challenges in {industry} include scaling, cost management, and team coordination."

# Test
if __name__ == "__main__":
    agent = AccountResearchAgent()

    test_account = {
        'name': 'FastGrow SaaS',
        'industry': 'SaaS',
        'size': 450,
        'revenue': 35.5,
        'icp_score': 92,
        'intent_score': 85,
        'segment': 'qualified_inbound'
    }

    print("Research Brief:")
    print(agent.generate_research_brief(test_account))
    print("\nTalking Points:")
    for point in agent.generate_talking_points(test_account):
        print(f"  • {point}")
