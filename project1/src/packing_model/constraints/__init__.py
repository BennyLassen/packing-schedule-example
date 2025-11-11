"""
Constraints Module

This module organizes all constraint definitions into logical categories.
Each category is defined in its own sub-module for easy extension.
"""

from .assignment import add_assignment_constraints
from .capacity import add_capacity_constraints
from .worker import add_worker_constraints
from .otif import add_otif_constraints
from .wip import add_wip_constraints
from .workforce import add_workforce_constraints
from .shipping import add_shipping_constraints


def add_all_constraints(model, data):
    """
    Add all constraints to the model.

    This function serves as the main entry point for constraint definition.
    It calls each constraint category in sequence.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing problem data (for accessing dimensions)
    """
    add_assignment_constraints(model, data)
    add_capacity_constraints(model, data)
    add_worker_constraints(model, data)
    add_otif_constraints(model, data)
    add_wip_constraints(model, data)
    add_workforce_constraints(model, data)
    add_shipping_constraints(model, data)
