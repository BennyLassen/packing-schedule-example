"""
Problem_4_1_c2 Packing Schedule Model

This module implements the MILP formulation from Problem_4_1_c2.pdf.

Key features:
- Event-based workforce tracking (start and completion events)
- Continuous time formulation (not discretized)
- Setup times between different product types
- Demand fulfillment with due dates
- WIP inventory tracking
- Workforce variability minimization
"""

from .model import PackingScheduleModelProblem4_1_c2

__all__ = ['PackingScheduleModelProblem4_1_c2']
__version__ = '1.0.0'
