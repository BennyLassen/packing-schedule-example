"""
Packing Schedule Optimization Model Package

This package provides a modular implementation of a MILP packing schedule optimizer.

Main components:
- parameters: Input parameter definitions
- variables: Decision variable definitions
- constraints: Constraint definitions (organized by category)
- objective: Objective function definition
- model: Main model class that ties everything together
"""

from .model import PackingScheduleModel

__all__ = ['PackingScheduleModel']
__version__ = '1.0.0'
