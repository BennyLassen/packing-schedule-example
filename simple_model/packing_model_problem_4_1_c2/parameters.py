"""
Model Parameters for Problem_4_1_c2 Formulation

Defines sets and parameters based on Problem_4_1_c2.pdf specification.
This formulation tracks events (start/completion times) and uses them for workforce tracking.
"""

import pyomo.environ as pyo
import numpy as np


def define_parameters(model, data):
    """
    Define sets and parameters for the Problem_4_1_c2 packing schedule model.

    Args:
        model: Pyomo ConcreteModel
        data: Dictionary with input data

    Required data keys:
        - n_unique_types (U): Number of unique packing types
        - n_orders (I): Number of production orders
        - n_demands (D): Number of demand/shipping requirements
        - n_lines (J): Number of production lines
        - processing_time: Array[n_unique_types, n_lines] - p(u,j)
        - setup_time: Array[n_unique_types, n_unique_types] - s(u,v)
        - initial_inventory: Array[n_unique_types] - inv0(u)
        - T_max: Planning horizon (positive real)
        - order_type: Array[n_orders] - type(i): unit type of order i
        - due_date: Array[n_demands] - due(d)
        - demand_type: Array[n_demands] - prodtype(d)
        - demand_qty: Array[n_demands] - qty(d)
        - priority: Array[n_orders] - priority(i)
    """

    # Extract dimensions
    n_unique_types = data['n_unique_types']
    n_orders = data['n_orders']
    n_demands = data['n_demands']
    n_lines = data['n_lines']
    T_max = data['T_max']

    # Store dimensions
    model.n_unique_types = n_unique_types
    model.n_orders = n_orders
    model.n_demands = n_demands
    model.n_lines = n_lines
    model.T_max = T_max

    # ============================================
    # Sets
    # ============================================

    # u = 1, U: unique packing types
    model.TYPES = pyo.RangeSet(1, n_unique_types)

    # i = 1, I: production orders
    model.ORDERS = pyo.RangeSet(1, n_orders)

    # d = 1, D: demand (shipping requirements)
    model.DEMANDS = pyo.RangeSet(1, n_demands)

    # j = 1, J: line numbers
    model.LINES = pyo.RangeSet(1, n_lines)

    # Events set: E = {s1, ..., sn, c1, ..., cn}
    # We'll use a combined set for event indices
    # Events are ordered: [start events for all orders, completion events for all orders]
    model.EVENTS = pyo.RangeSet(1, 2 * n_orders)

    # ============================================
    # Processing and Setup Parameters
    # ============================================

    # p(u,j): Processing time for item type u on line j
    processing_time = data['processing_time']
    model.p = pyo.Param(
        model.TYPES, model.LINES,
        initialize=lambda m, u, j: float(processing_time[u-1, j-1]),
        doc="Processing time for item type u on line j"
    )

    # setup_time(u,v): Setup time for changing from item type u to item type v
    # Note: Using 'setup_time' instead of 's' to avoid conflict with start time variable
    setup_time = data['setup_time']
    model.setup_time = pyo.Param(
        model.TYPES, model.TYPES,
        initialize=lambda m, u, v: float(setup_time[u-1, v-1]),
        doc="Setup time from type u to type v"
    )

    # ============================================
    # Initial Inventory
    # ============================================

    # inv0(u): Initial inventory stock for packing unit type u
    initial_inventory = data['initial_inventory']
    model.inv0 = pyo.Param(
        model.TYPES,
        initialize=lambda m, u: int(initial_inventory[u-1]),
        doc="Initial inventory for packing unit type u"
    )

    # ============================================
    # Planning Horizon
    # ============================================

    # T_max: The planning horizon
    model.T_max_param = pyo.Param(
        initialize=float(T_max),
        doc="Planning horizon"
    )

    # ============================================
    # Order Type Mapping
    # ============================================

    # type(i): Unit type of order i
    order_type = data['order_type']
    model.order_type = pyo.Param(
        model.ORDERS,
        initialize=lambda m, i: int(order_type[i-1]),
        doc="Unit type of order i"
    )

    # ============================================
    # OTIF/Demand Parameters
    # ============================================

    # due(d): Due date for demand d
    due_date = data['due_date']
    model.due = pyo.Param(
        model.DEMANDS,
        initialize=lambda m, d: float(due_date[d-1]),
        doc="Due date for demand d"
    )

    # prodtype(d): Unit type for demand d
    demand_type = data['demand_type']
    model.prodtype = pyo.Param(
        model.DEMANDS,
        initialize=lambda m, d: int(demand_type[d-1]),
        doc="Unit type for demand d"
    )

    # qty(d): Quantity for demand d
    demand_qty = data['demand_qty']
    model.qty = pyo.Param(
        model.DEMANDS,
        initialize=lambda m, d: int(demand_qty[d-1]),
        doc="Quantity for demand d"
    )

    # priority(i): Priority weight for order i
    priority = data['priority']
    model.priority = pyo.Param(
        model.ORDERS,
        initialize=lambda m, i: int(priority[i-1]),
        doc="Priority weight for order i"
    )

    # ============================================
    # Additional Parameters
    # ============================================

    # Epsilon for strict inequalities
    model.epsilon = pyo.Param(
        initialize=0.01,
        doc="Small epsilon for strict inequalities"
    )

    # Big-M for indicator constraints
    model.M = pyo.Param(
        initialize=10 * T_max,
        doc="Big-M constant for indicator constraints"
    )

    # Objective weights (if provided)
    obj_weights = data.get('objective_weights', {
        'alpha': 1.0,
        'beta': 1.0,
        'gamma': 1.0,
        'delta': 1.0
    })
    model.alpha = pyo.Param(initialize=obj_weights.get('alpha', 1.0), doc="OTIF weight")
    model.beta = pyo.Param(initialize=obj_weights.get('beta', 1.0), doc="WIP weight")
    model.gamma = pyo.Param(initialize=obj_weights.get('gamma', 1.0), doc="Workforce weight")
    model.delta = pyo.Param(initialize=obj_weights.get('delta', 1.0), doc="Not utilized weight")

    return model
