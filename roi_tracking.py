"""
ROI Tracking - Measurement and Impact Analysis
Tracks conversions, costs, and calculates ROI
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConversionEvent:
    """Track conversion from account to revenue"""
    account_id: str
    account_name: str
    segment: str
    event_type: str  # 'contacted', 'demo', 'proposal', 'won'
    amount: float
    date: str

class ROITracker:
    """Track ROI of GTM AI system"""

    def __init__(self):
        self.conversions: List[ConversionEvent] = []
        self.costs = {
            'platform': 0,
            'labor': 0,
            'data': 0
        }

    def add_conversion(self, event: ConversionEvent):
        """Record a conversion event"""
        self.conversions.append(event)

    def add_monthly_cost(self, cost_type: str, amount: float):
        """Add monthly cost"""
        if cost_type in self.costs:
            self.costs[cost_type] += amount

    def segment_performance(self) -> Dict:
        """Calculate performance by segment"""
        performance = {}

        for event in self.conversions:
            if event.segment not in performance:
                performance[event.segment] = {
                    'contacts': 0,
                    'demos': 0,
                    'proposals': 0,
                    'wins': 0,
                    'revenue': 0,
                    'conversion_rate': 0
                }

            if event.event_type == 'contacted':
                performance[event.segment]['contacts'] += 1
            elif event.event_type == 'demo':
                performance[event.segment]['demos'] += 1
            elif event.event_type == 'proposal':
                performance[event.segment]['proposals'] += 1
            elif event.event_type == 'won':
                performance[event.segment]['wins'] += 1
                performance[event.segment]['revenue'] += event.amount

        for segment in performance:
            if performance[segment]['contacts'] > 0:
                performance[segment]['conversion_rate'] = (
                    performance[segment]['wins'] / performance[segment]['contacts']
                )

        return performance

    def calculate_roi(self, months: int = 3) -> Dict:
        """Calculate ROI of GTM AI system"""

        total_revenue = sum(e.amount for e in self.conversions if e.event_type == 'won')
        total_costs = sum(self.costs.values()) * months
        gross_profit = total_revenue - total_costs
        roi_percent = (gross_profit / total_costs * 100) if total_costs > 0 else 0

        payback_months = (total_costs / (total_revenue / months)) if total_revenue > 0 else float('inf')

        return {
            'total_revenue': total_revenue,
            'total_costs': total_costs,
            'gross_profit': gross_profit,
            'roi_percent': roi_percent,
            'payback_months': payback_months,
            'revenue_per_month': total_revenue / months if months > 0 else 0
        }

    def cost_per_acquisition(self) -> Dict:
        """Calculate cost per acquisition"""
        wins = sum(1 for e in self.conversions if e.event_type == 'won')
        total_costs = sum(self.costs.values())

        if wins == 0:
            return {'cost_per_win': 0, 'wins': 0, 'total_costs': total_costs}

        return {
            'cost_per_win': total_costs / wins,
            'wins': wins,
            'total_costs': total_costs
        }

    def generate_roi_report(self, months: int = 3) -> str:
        """Generate ROI report"""
        roi = self.calculate_roi(months)
        segment_perf = self.segment_performance()
        cpa = self.cost_per_acquisition()

        report = f"""
╔════════════════════════════════════════╗
║  GTM AI SYSTEM - ROI REPORT            ║
║  {months}-Month Analysis               ║
╚════════════════════════════════════════╝

FINANCIAL PERFORMANCE
─────────────────────────
Total Revenue: ${roi['total_revenue']:,.0f}
Total Costs: ${roi['total_costs']:,.0f}
Gross Profit: ${roi['gross_profit']:,.0f}
ROI: {roi['roi_percent']:.1f}%
Revenue/Month: ${roi['revenue_per_month']:,.0f}
Payback Period: {roi['payback_months']:.1f} months

ACQUISITION METRICS
─────────────────────────
Cost Per Win: ${cpa['cost_per_win']:,.0f}
Total Wins: {cpa['wins']}

SEGMENT PERFORMANCE
─────────────────────────
        """

        for segment, metrics in segment_perf.items():
            report += f"""
{segment.upper()}
  Contacts: {metrics['contacts']}
  Demos: {metrics['demos']}
  Proposals: {metrics['proposals']}
  Won: {metrics['wins']}
  Revenue: ${metrics['revenue']:,.0f}
  Conversion Rate: {metrics['conversion_rate']:.1%}
        """

        return report

# Test
if __name__ == "__main__":
    tracker = ROITracker()

    # Add costs
    tracker.add_monthly_cost('platform', 500)
    tracker.add_monthly_cost('labor', 2000)

    # Add conversions
    tracker.add_conversion(ConversionEvent(
        'ACC_1', 'Company A', 'qualified_inbound', 'won', 50000, '2024-01-15'
    ))
    tracker.add_conversion(ConversionEvent(
        'ACC_2', 'Company B', 'qualified_inbound', 'won', 75000, '2024-02-20'
    ))
    tracker.add_conversion(ConversionEvent(
        'ACC_3', 'Company C', 'strategic_fit', 'won', 25000, '2024-03-10'
    ))

    print(tracker.generate_roi_report(3))
