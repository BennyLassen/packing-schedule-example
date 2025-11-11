"""
Decision Variables for Problem_4_1 Formulation

Based on Problem_4_1.pdf specification:
- x(i,j,t): Order assignment (binary)
- prod(i,t): Production at time t (positive integer)
- workersused(t), workersmax, workersmin: Workforce tracking
- inv(i,t), ship(i,t): WIP tracking
"""

import pyomo.environ as pyo


def define_variables(model):
    """
    Define all decision variables for the Problem_4_1 packing schedule model.

    Decision Variables (Problem_4_1 Pages 1-2):
    - Core Assignment:
        - x(i,j,t): Packing order i starts on line j at time t (binary)
        - prod(i,t): Number of units produced at time t (positive integer)

    - Workforce tracking:
        - workersused(t): Total workers actually working at time t
        - workersmax: Maximal workers used in any time slot
        - workersmin: Minimum workers used in any time slot

    - WIP tracking:
        - inv(i): Number of packing order i in stock (positive integer)
        - ship(i,t): Packing order i is shipped at time t (binary)
    """

    # ============================================
    # Core Assignment Variables
    # ============================================

    # x(i,j,t): Packing order i starts on line j at time t
    model.x = pyo.Var(
        model.ORDERS, model.LINES, model.TIME,
        domain=pyo.Binary,
        doc="Order i starts on line j at time t"
    )

    # prod(i,t): Number of units of order i produced at time t
    model.prod = pyo.Var(
        model.ORDERS, model.TIME,
        domain=pyo.NonNegativeIntegers,
        doc="Number of units of order i produced at time t"
    )

    # ============================================
    # Workforce Tracking Variables
    # ============================================

    # workersused(t): Total workers actually working at time t
    model.workersused = pyo.Var(
        model.TIME,
        domain=pyo.NonNegativeIntegers,
        bounds=(0, model.n_workers),
        doc="Number of workers active at time t"
    )

    # workersmax: Maximum workers used in any time slot
    model.workersmax = pyo.Var(
        domain=pyo.NonNegativeIntegers,
        bounds=(0, model.n_workers),
        doc="Maximum workforce level across all time slots"
    )

    # workersmin: Minimum workers used in any time slot
    model.workersmin = pyo.Var(
        domain=pyo.NonNegativeIntegers,
        bounds=(0, model.n_workers),
        doc="Minimum workforce level across all time slots"
    )

    # workforcerange: Range of workforce utilization (derived variable)
    model.workforcerange = pyo.Var(
        domain=pyo.NonNegativeIntegers,
        bounds=(0, model.n_workers),
        doc="Workforce range (max - min)"
    )

    # ============================================
    # WIP Tracking Variables
    # ============================================

    # inv(i,t): Inventory of order i at time t
    model.inv = pyo.Var(
        model.ORDERS, model.TIME_WITH_ZERO,
        domain=pyo.NonNegativeIntegers,
        doc="Inventory of order i at time t"
    )

    # ship(i,t): Order i is shipped at time t
    model.ship = pyo.Var(
        model.ORDERS, model.TIME,
        domain=pyo.Binary,
        doc="Order i is shipped at time t"
    )

    return model
