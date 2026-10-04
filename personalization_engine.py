"""
Personalization Engine - AI-powered Outreach Generation
Generates personalized emails, subjects, and messaging
"""

from typing import Dict, List
import os

class OutreachPersonalizationEngine:
    """Generate personalized outreach messages"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if self.api_key:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-opus-5-5"
            self.available = True
        else:
            self.available = False

    def generate_email_subject(self, account: Dict, tone: str = "professional") -> str:
        """Generate personalized email subject"""

        if not self.available:
            return self._demo_subject(account)

        try:
            segment_context = {
                'qualified_inbound': 'High buying intent - focus on urgency and immediate value',
                'strategic_fit': 'Great fit but early stage - focus on long-term value',
                'emerging': 'Some interest - focus on education',
                'low_priority': 'Low fit - keep brief'
            }

            prompt = f"""
            Write 1 email subject line for {account['name']} ({account['industry']}).
            Context: {segment_context.get(account['segment'], 'Unknown')}

            Rules: Personalized, action-oriented, <50 chars, mention company OR specific trigger.
            Return ONLY the subject line.
            """

            message = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text.strip()
        except:
            return self._demo_subject(account)

    def _demo_subject(self, account: Dict) -> str:
        """Demo subject lines"""
        subjects = {
            'qualified_inbound': f"{account['name']}: Quick synergy opportunity?",
            'strategic_fit': f"Thought on {account['industry']} - {account['name']}",
            'emerging': f"How {account['name']} can stay ahead",
            'low_priority': f"Idea for {account['name']}"
        }
        return subjects.get(account['segment'], f"Quick idea for {account['name']}")

    def generate_email_body(self, account: Dict, rep_name: str, company_name: str) -> str:
        """Generate personalized email body"""

        if not self.available:
            return self._demo_body(account, rep_name, company_name)

        try:
            segment_templates = {
                'qualified_inbound': 'Emphasize urgency, offer immediate value, mention their signals',
                'strategic_fit': 'Educate on use case, build relationship, share thought leadership',
                'emerging': 'Share insight, invite to event, soften pitch',
                'low_priority': 'Focus on specific trigger, keep brief'
            }

            prompt = f"""
            Write 3-4 sentence email from {rep_name} at {company_name} to {account['name']}.

            Account: {account['name']} ({account['industry']}, {account['size']} emp, ${account['revenue']}M)
            Segment: {account['segment']}
            Approach: {segment_templates.get(account['segment'])}

            Rules: Personal, 1 specific insight, clear CTA (meeting/demo/chat), professional tone.
            Return ONLY email body.
            """

            message = self.client.messages.create(
                model=self.model,
                max_tokens=250,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text.strip()
        except:
            return self._demo_body(account, rep_name, company_name)

    def _demo_body(self, account: Dict, rep_name: str, company_name: str) -> str:
        """Demo email body"""
        if account['segment'] == 'qualified_inbound':
            return f"Hi,\n\nI noticed your team at {account['name']} recently showed interest in sales productivity solutions. Given your {account['size']} person team and {account['industry']} focus, I think we could save you 40% on sales ops time.\n\nWould a 20-min call next week make sense?\n\nBest,\n{rep_name}"
        else:
            return f"Hi,\n\nThought you'd find this relevant for {account['name']} - companies in {account['industry']} are typically struggling with X. We've helped teams like yours with Y.\n\nWorth a quick conversation?\n\nBest,\n{rep_name}"

    def generate_linkedin_message(self, account: Dict, target_person: str) -> str:
        """Generate LinkedIn connection message"""

        if not self.available:
            return f"Hi {target_person}, I follow {account['name']}'s work in {account['industry']} and thought we should connect. Would love to chat."

        try:
            prompt = f"""
            Write 2-3 sentence LinkedIn connection message from you to {target_person} at {account['name']}.
            Company: {account['name']} ({account['industry']}, {account['size']} emp)

            Rules: Casual, specific insight, suggest conversation (not hard sell).
            Return ONLY message text.
            """

            message = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text.strip()
        except:
            return f"Hi {target_person}, I follow {account['name']}'s work and thought we should connect."

    def generate_campaign_variants(self, account: Dict, num_variants: int = 3) -> List[Dict]:
        """Generate multiple message variants for A/B testing"""

        if not self.available:
            return self._demo_variants(account, num_variants)

        try:
            prompt = f"""
            Generate {num_variants} different email approaches for {account['name']} ({account['industry']}).
            Segment: {account['segment']}, ICP: {account['icp_score']:.0f}, Intent: {account['intent_score']:.0f}

            For each, provide:
            1. Angle (focus point) - 3 words max
            2. Subject line - 8 words max
            3. Opening - 1 sentence

            Make each distinctly different. Format: "Angle: X / Subject: Y / Opening: Z"
            """

            message = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text
            variants = []

            for i, line in enumerate(response.split('\n')[:num_variants], 1):
                variants.append({
                    'variant_id': f'var_{i}',
                    'content': line.strip()
                })

            return variants
        except:
            return self._demo_variants(account, num_variants)

    def _demo_variants(self, account: Dict, num_variants: int) -> List[Dict]:
        """Demo variants"""
        angles = ['Urgency', 'Value', 'Education', 'Relationship']
        return [
            {
                'variant_id': f'var_{i+1}',
                'angle': angles[i % len(angles)],
                'subject': f'{account["name"]}: {angles[i % len(angles)].lower()} angle',
                'opening': f'Quick thought on how {account["name"]} can improve.'
            }
            for i in range(min(num_variants, 4))
        ]

# Test
if __name__ == "__main__":
    engine = OutreachPersonalizationEngine()

    test_account = {
        'name': 'FastGrow SaaS',
        'industry': 'SaaS',
        'size': 450,
        'revenue': 35.5,
        'icp_score': 92,
        'intent_score': 85,
        'segment': 'qualified_inbound'
    }

    print("Email Subject:")
    print(engine.generate_email_subject(test_account))
    print("\nEmail Body:")
    print(engine.generate_email_body(test_account, "Alice", "Our Company"))
    print("\nA/B Variants:")
    for v in engine.generate_campaign_variants(test_account, 2):
        print(f"  Variant {v.get('variant_id', 'N/A')}: {v}")
