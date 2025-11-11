"""
Parameter Definitions Module

This module defines all input parameters for the packing schedule optimization model.
Parameters are organized into logical groups for easy extension.
"""

import pyomo.environ as pyo


class ParameterManager:
    """
    Manages all input parameters for the optimization model.

    This class encapsulates parameter definitions and makes it easy to:
    - Add new parameters
    - Organize parameters by category
    - Validate parameter data
    """

    def __init__(self, model, data):
        """
        Initialize parameters on the given Pyomo model.

        Args:
            model: Pyomo ConcreteModel instance
            data: Dictionary containing all input parameter data
        """
        self.model = model
        self.data = data

    def define_all_parameters(self):
        """Define all parameters for the model."""
        self._define_processing_parameters()
        self._define_resource_parameters()
        self._define_inventory_parameters()
        self._define_otif_parameters()
        self._define_workforce_parameters()

    def _define_processing_parameters(self):
        """Define parameters related to processing and setup times."""
        model = self.model
        data = self.data

        # Processing time for order i on line j
        model.p = pyo.Param(
            model.ORDERS, model.LINES,
            initialize=lambda m, i, j: data['processing_time'][i-1, j-1],
            doc="Processing time for order i on line j"
        )

        # Setup time between orders i and k on line j
        model.s = pyo.Param(
            model.ORDERS, model.ORDERS, model.LINES,
            initialize=lambda m, i, k, j: data['setup_time'][i-1, k-1, j-1],
            doc="Setup time between orders i and k on line j"
        )

    def _define_resource_parameters(self):
        """Define parameters related to resources (workers, capacity)."""
        model = self.model
        data = self.data

        # Worker availability
        model.a = pyo.Param(
            model.WORKERS, model.TIME,
            initialize=lambda m, w, t: data['worker_availability'][w-1, t-1],
            doc="Worker w availability at time t"
        )

        # Reserved capacity fraction
        model.alpha = pyo.Param(
            initialize=data['reserved_capacity'],
            doc="Reserved capacity fraction (e.g., 0.1 = 10%)"
        )

    def _define_inventory_parameters(self):
        """Define parameters related to inventory management."""
        model = self.model
        data = self.data

        # Initial inventory
        model.inv0 = pyo.Param(
            model.ORDERS,
            initialize=lambda m, i: data['initial_inventory'][i-1],
            doc="Initial inventory for order i"
        )

    def _define_otif_parameters(self):
        """Define parameters for On-Time In-Full (OTIF) tracking."""
        model = self.model
        data = self.data

        # Due date
        model.due = pyo.Param(
            model.ORDERS,
            initialize=lambda m, i: data['due_date'][i-1],
            doc="Due date for order i"
        )

        # Priority weight
        model.priority = pyo.Param(
            model.ORDERS,
            initialize=lambda m, i: data['priority'][i-1],
            doc="Priority weight for order i (higher = more important)"
        )

    def _define_workforce_parameters(self):
        """Define parameters for workforce management."""
        model = self.model
        data = self.data

        # Target workforce level
        model.workforce_target = pyo.Param(
            initialize=data['workforce_target'],
            doc="Ideal steady-state workforce level"
        )


def add_parameters(model, data):
    """
    Convenience function to add all parameters to a model.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing parameter data
    """
    param_manager = ParameterManager(model, data)
    param_manager.define_all_parameters()
