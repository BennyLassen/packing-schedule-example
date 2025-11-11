"""
Model Parameters for Problem_4 Simplified Formulation

Defines sets and parameters based on Problem_4.pdf input specification.
"""

import pyomo.environ as pyo
import numpy as np


def define_parameters(model, data):
    """
    Define sets and parameters for the simplified packing schedule model.

    Args:
        model: Pyomo ConcreteModel
        data: Dictionary with input data

    Required data keys:
        - n_orders: Number of packing orders
        - n_lines: Number of production lines
        - n_timeslots: Number of time slots in planning horizon
        - n_workers: Number of available workers (used for counting only)
        - processing_time: Array[n_orders, n_lines] - processing times
        - setup_time: Array[n_orders, n_orders, n_lines] - setup times
        - initial_inventory: Array[n_orders] - initial stock
        - reserved_capacity: Float - fraction of capacity to reserve (alpha)
        - due_date: Array[n_orders] - due dates
        - priority: Array[n_orders] - priority weights
    """

    # Extract dimensions
    n_orders = data['n_orders']
    n_lines = data['n_lines']
    n_timeslots = data['n_timeslots']
    n_workers = data['n_workers']

    # Store dimensions
    model.n_orders = n_orders
    model.n_lines = n_lines
    model.n_timeslots = n_timeslots
    model.n_workers = n_workers  # Used for bounds/counting, not assignment

    # ============================================
    # Sets
    # ============================================

    model.ORDERS = pyo.RangeSet(1, n_orders)
    model.LINES = pyo.RangeSet(1, n_lines)
    model.TIME = pyo.RangeSet(1, n_timeslots)
    model.TIME_WITH_ZERO = pyo.RangeSet(0, n_timeslots)

    # ============================================
    # Processing and Setup Parameters
    # ============================================

    # p(i,j): Processing time for order i on line j
    processing_time = data['processing_time']
    model.p = pyo.Param(
        model.ORDERS, model.LINES,
        initialize=lambda m, i, j: float(processing_time[i-1, j-1]),
        doc="Processing time for order i on line j"
    )

    # s(i,k,j): Setup time between orders i and k on line j
    setup_time = data['setup_time']
    model.s = pyo.Param(
        model.ORDERS, model.ORDERS, model.LINES,
        initialize=lambda m, i, k, j: float(setup_time[i-1, k-1, j-1]),
        doc="Setup time from order i to order k on line j"
    )

    # ============================================
    # Initial Inventory
    # ============================================

    # inv0(i): Initial inventory for order i
    initial_inventory = data['initial_inventory']
    model.inv0 = pyo.Param(
        model.ORDERS,
        initialize=lambda m, i: int(initial_inventory[i-1]),
        doc="Initial inventory for order i"
    )

    # ============================================
    # Capacity Reservation
    # ============================================

    # alpha: Reserved capacity (fraction of total capacity)
    model.alpha = pyo.Param(
        initialize=float(data['reserved_capacity']),
        doc="Reserved capacity fraction"
    )

    # ============================================
    # OTIF Parameters
    # ============================================

    # due(i): Due date for order i
    due_date = data['due_date']
    model.due = pyo.Param(
        model.ORDERS,
        initialize=lambda m, i: int(due_date[i-1]),
        doc="Due date for order i"
    )

    # priority(i): Priority weight for order i
    priority = data['priority']
    model.priority = pyo.Param(
        model.ORDERS,
        initialize=lambda m, i: int(priority[i-1]),
        doc="Priority weight for order i"
    )

    # ============================================
    # Big-M Parameter
    # ============================================

    # Large constant for indicator constraints
    model.M = pyo.Param(
        initialize=10000,
        doc="Big-M constant for indicator constraints"
    )

    return model
