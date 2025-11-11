"""
Problem_3 Packing Schedule Model

This module implements the MILP formulation from Problem_3.pdf.

Key features:
- Event-based workforce tracking (start and completion events)
- Continuous time formulation (not discretized)
- Setup times between different product types
- Demand fulfillment with due dates
- WIP inventory tracking
- Workforce variability minimization
"""

from .model import PackingScheduleModelProblem3

__all__ = ['PackingScheduleModelProblem3']
__version__ = '1.0.0'
