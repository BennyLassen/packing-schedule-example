"""
Variable Definitions Module

This module defines all decision variables for the packing schedule optimization model.
Variables are organized into logical groups for easy extension.
"""

import pyomo.environ as pyo


class VariableManager:
    """
    Manages all decision variables for the optimization model.

    This class encapsulates variable definitions and makes it easy to:
    - Add new variables
    - Organize variables by category
    - Define appropriate domains and bounds
    """

    def __init__(self, model, data):
        """
        Initialize variables on the given Pyomo model.

        Args:
            model: Pyomo ConcreteModel instance
            data: Dictionary containing problem dimensions for bounds
        """
        self.model = model
        self.data = data

    def define_all_variables(self):
        """Define all decision variables for the model."""
        self._define_primary_variables()
        self._define_otif_variables()
        self._define_workforce_variables()
        self._define_wip_variables()
        self._define_shipping_variables()

    def _define_primary_variables(self):
        """Define primary decision variables for scheduling."""
        model = self.model

        # Assignment variable: order i starts on line j at time t with worker w
        model.x = pyo.Var(
            model.ORDERS, model.LINES, model.TIME, model.WORKERS,
            domain=pyo.Binary,
            doc="Order i starts on line j at time t with worker w"
        )

        # Setup indicator: setup between orders i and k on line j
        model.y = pyo.Var(
            model.ORDERS, model.ORDERS, model.LINES,
            domain=pyo.Binary,
            doc="Setup between orders i and k on line j"
        )

        # Batch indicator: orders i and k batched together
        model.b = pyo.Var(
            model.ORDERS, model.ORDERS,
            domain=pyo.Binary,
            doc="Orders i and k batched together"
        )

        # Worker working indicator
        model.w_working = pyo.Var(
            model.WORKERS, model.TIME,
            domain=pyo.Binary,
            doc="Worker w is working during time t"
        )

        # Worker movement indicator
        model.m = pyo.Var(
            model.WORKERS, model.TIME,
            domain=pyo.Binary,
            doc="Worker w moved to another line at time t"
        )

        # Production quantity
        model.prod = pyo.Var(
            model.ORDERS, model.TIME,
            domain=pyo.NonNegativeIntegers,
            doc="Number of units produced for order i at time t"
        )

        # Inventory level
        model.inv = pyo.Var(
            model.ORDERS, model.TIME,
            domain=pyo.NonNegativeIntegers,
            doc="Inventory level of order i at time t"
        )

        # Line in use indicator
        model.u = pyo.Var(
            model.LINES,
            domain=pyo.Binary,
            doc="Line j is used"
        )

    def _define_otif_variables(self):
        """Define variables for On-Time In-Full (OTIF) tracking."""
        model = self.model

        # Late order indicator
        model.late = pyo.Var(
            model.ORDERS,
            domain=pyo.Binary,
            doc="Order i is late (binary indicator)"
        )

        # Lateness amount
        model.lateness = pyo.Var(
            model.ORDERS,
            domain=pyo.NonNegativeIntegers,
            doc="Amount of lateness for order i (time units)"
        )

        # Earliness amount
        model.early = pyo.Var(
            model.ORDERS,
            domain=pyo.NonNegativeIntegers,
            doc="Amount of earliness for order i (time units)"
        )

    def _define_workforce_variables(self):
        """Define variables for workforce tracking and management."""
        model = self.model

        # Total workers used at each time slot
        model.workers_used = pyo.Var(
            model.TIME,
            domain=pyo.NonNegativeIntegers,
            bounds=(0, self.data['n_workers']),
            doc="Total workers active at time t"
        )

        # Maximum workers used
        model.workers_max = pyo.Var(
            domain=pyo.NonNegativeIntegers,
            bounds=(0, self.data['n_workers']),
            doc="Maximum workers used in any time slot"
        )

        # Minimum workers used
        model.workers_min = pyo.Var(
            domain=pyo.NonNegativeIntegers,
            bounds=(0, self.data['n_workers']),
            doc="Minimum workers used in any time slot"
        )

        # Deviation above target workforce
        model.deviation_above = pyo.Var(
            model.TIME,
            domain=pyo.NonNegativeIntegers,
            doc="Workers above target at time t"
        )

        # Deviation below target workforce
        model.deviation_below = pyo.Var(
            model.TIME,
            domain=pyo.NonNegativeIntegers,
            doc="Workers below target at time t"
        )

        # Absolute workforce change between periods
        model.workforce_change = pyo.Var(
            model.TIME,
            domain=pyo.NonNegativeIntegers,
            doc="Absolute change in workforce from t-1 to t"
        )

        # Workforce increase
        model.workforce_increase = pyo.Var(
            model.TIME,
            domain=pyo.NonNegativeIntegers,
            doc="Increase in workforce from t-1 to t"
        )

        # Workforce decrease
        model.workforce_decrease = pyo.Var(
            model.TIME,
            domain=pyo.NonNegativeIntegers,
            doc="Decrease in workforce from t-1 to t"
        )

    def _define_wip_variables(self):
        """Define variables for Work-In-Progress (WIP) tracking."""
        model = self.model

        # Order start time
        model.time_start = pyo.Var(
            model.ORDERS,
            domain=pyo.NonNegativeIntegers,
            bounds=(1, self.data['n_timeslots']),
            doc="Start time for order i"
        )

        # Order completion time
        model.time_completion = pyo.Var(
            model.ORDERS,
            domain=pyo.NonNegativeIntegers,
            bounds=(1, self.data['n_timeslots']),
            doc="Completion time for order i"
        )

        # Shipping time (NEW for Problem 2)
        model.time_ship = pyo.Var(
            model.ORDERS,
            domain=pyo.NonNegativeIntegers,
            bounds=(1, self.data['n_timeslots']),
            doc="Shipping time for order i"
        )

        # Flow time (start to shipping)
        model.time_flow = pyo.Var(
            model.ORDERS,
            domain=pyo.NonNegativeIntegers,
            doc="Flow time (start to shipping) for order i"
        )

        # WIP indicator
        model.wip_indicator = pyo.Var(
            model.ORDERS, model.TIME,
            domain=pyo.Binary,
            doc="Order i is in process at time t"
        )

        # Total WIP count
        model.wip = pyo.Var(
            model.TIME,
            domain=pyo.NonNegativeIntegers,
            doc="Number of orders in process at time t"
        )

        # Value-weighted WIP
        model.wip_weighted = pyo.Var(
            model.TIME,
            domain=pyo.NonNegativeIntegers,
            doc="Value-weighted WIP at time t"
        )

    def _define_shipping_variables(self):
        """Define variables for shipping decisions (NEW for Problem 2)."""
        model = self.model

        # Shipping decision: order i ships at time t
        model.ship = pyo.Var(
            model.ORDERS, model.TIME,
            domain=pyo.Binary,
            doc="Order i ships at time t (binary decision)"
        )

        # Ship early indicator
        model.ship_early = pyo.Var(
            model.ORDERS,
            domain=pyo.Binary,
            doc="Order i ships before due date"
        )

        # Ship late indicator
        model.ship_late = pyo.Var(
            model.ORDERS,
            domain=pyo.Binary,
            doc="Order i ships after due date"
        )


def add_variables(model, data):
    """
    Convenience function to add all variables to a model.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing problem dimensions
    """
    var_manager = VariableManager(model, data)
    var_manager.define_all_variables()
