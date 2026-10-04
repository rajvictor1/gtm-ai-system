"""
A/B Testing Framework - Multi-variant test management
Tracks conversions and calculates winners
"""

from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class TestMetrics:
    """Metrics for a test variant"""
    sent: int = 0
    opened: int = 0
    clicked: int = 0
    replied: int = 0
    meetings: int = 0

    def open_rate(self) -> float:
        return self.opened / self.sent if self.sent > 0 else 0

    def click_rate(self) -> float:
        return self.clicked / self.sent if self.sent > 0 else 0

    def reply_rate(self) -> float:
        return self.replied / self.sent if self.sent > 0 else 0

    def meeting_rate(self) -> float:
        return self.meetings / self.sent if self.sent > 0 else 0

    def engagement_score(self) -> float:
        """0-100 engagement score"""
        if self.sent == 0:
            return 0
        score = (
            (self.open_rate() * 20) +
            (self.click_rate() * 30) +
            (self.reply_rate() * 30) +
            (self.meeting_rate() * 20)
        )
        return min(100, max(0, score))

class ABTest:
    """A/B test for email variants, messaging, etc."""

    def __init__(self, test_id: str, test_name: str, variant_a: Dict, variant_b: Dict):
        """
        Args:
            test_id: Unique test identifier
            test_name: Human-readable test name
            variant_a: Control variant dict
            variant_b: Treatment variant dict
        """
        self.test_id = test_id
        self.test_name = test_name
        self.variant_a = variant_a
        self.variant_b = variant_b
        self.created_at = datetime.now()
        self.status = "running"
        self.results = {
            'A': TestMetrics(),
            'B': TestMetrics()
        }

    def record_send(self, variant: str):
        """Record email sent"""
        if variant in self.results:
            self.results[variant].sent += 1

    def record_open(self, variant: str):
        """Record email opened"""
        if variant in self.results:
            self.results[variant].opened += 1

    def record_click(self, variant: str):
        """Record link clicked"""
        if variant in self.results:
            self.results[variant].clicked += 1

    def record_reply(self, variant: str):
        """Record email reply"""
        if variant in self.results:
            self.results[variant].replied += 1

    def record_meeting(self, variant: str):
        """Record meeting booked"""
        if variant in self.results:
            self.results[variant].meetings += 1

    def get_winner(self) -> str:
        """Determine winner based on meeting rate"""
        rate_a = self.results['A'].meeting_rate()
        rate_b = self.results['B'].meeting_rate()

        if rate_a > rate_b:
            diff = (rate_a - rate_b) * 100
            return f"A (wins by {diff:.1f}%)"
        elif rate_b > rate_a:
            diff = (rate_b - rate_a) * 100
            return f"B (wins by {diff:.1f}%)"
        else:
            return "Tie"

    def is_statistically_significant(self) -> bool:
        """Check if difference is statistically significant"""
        min_samples = 30

        if self.results['A'].sent < min_samples or self.results['B'].sent < min_samples:
            return False

        rate_a = self.results['A'].meeting_rate()
        rate_b = self.results['B'].meeting_rate()
        difference = abs(rate_a - rate_b)

        return difference > 0.05

    def generate_report(self) -> str:
        """Generate test report"""
        winner = self.get_winner()
        sig = self.is_statistically_significant()

        report = f"""
╔════════════════════════════════════════╗
║  A/B TEST REPORT                       ║
║  {self.test_name}                      ║
╚════════════════════════════════════════╝

Created: {self.created_at.strftime('%Y-%m-%d %H:%M')}
Status: {self.status}

VARIANT A (CONTROL)
─────────────────────────
Sent: {self.results['A'].sent}
Open Rate: {self.results['A'].open_rate()*100:.1f}%
Click Rate: {self.results['A'].click_rate()*100:.1f}%
Reply Rate: {self.results['A'].reply_rate()*100:.1f}%
Meeting Rate: {self.results['A'].meeting_rate()*100:.1f}%
Engagement: {self.results['A'].engagement_score():.1f}/100

VARIANT B (TREATMENT)
─────────────────────────
Sent: {self.results['B'].sent}
Open Rate: {self.results['B'].open_rate()*100:.1f}%
Click Rate: {self.results['B'].click_rate()*100:.1f}%
Reply Rate: {self.results['B'].reply_rate()*100:.1f}%
Meeting Rate: {self.results['B'].meeting_rate()*100:.1f}%
Engagement: {self.results['B'].engagement_score():.1f}/100

WINNER: {winner}
Statistically Significant: {'✅ Yes' if sig else '❌ No (need more samples)'}

RECOMMENDATION:
{'✅ Scale the winning variant' if sig else '⚠️  Collect more data'}
        """

        return report

# Test
if __name__ == "__main__":
    test = ABTest(
        'test_1',
        'Email Subject Line Test',
        {'subject': 'Quick question'},
        {'subject': 'FastGrow: 40% time savings'}
    )

    # Simulate results
    for i in range(50):
        test.record_send('A')
        test.record_send('B')

    test.results['A'].opened = 15
    test.results['A'].clicked = 5
    test.results['A'].replied = 3
    test.results['A'].meetings = 1

    test.results['B'].opened = 18
    test.results['B'].clicked = 7
    test.results['B'].replied = 5
    test.results['B'].meetings = 2

    print(test.generate_report())
