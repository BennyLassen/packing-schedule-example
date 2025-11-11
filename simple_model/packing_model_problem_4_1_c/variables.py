"""
Decision Variables for Problem_4_1_c Formulation (Relaxed/Continuous Version)

Based on Problem_4_1_c.pdf specification with LP relaxation:
- x(i,j,t): Order assignment (binary)
- prod(i,t): Production at time t (NON-NEGATIVE REAL - relaxed)
- workersused(t), workersmax, workersmin: Workforce tracking (REAL - relaxed)
- inv(i,t): Inventory (NON-NEGATIVE REAL - relaxed)
- ship(i,t): Shipping (binary)
"""

import pyomo.environ as pyo


def define_variables(model):
    """
    Define all decision variables for the Problem_4_1_c packing schedule model.

    This is the RELAXED (continuous) version where integer variables are converted to real.

    Decision Variables (Problem_4_1_c Pages 1-2):
    - Core Assignment:
        - x(i,j,t): Packing order i starts on line j at time t (binary)
        - prod(i,t): Number of units produced at time t (NON-NEGATIVE REAL - relaxed)

    - Workforce tracking (all RELAXED to real):
        - workersused(t): Total workers actually working at time t (real [0,W])
        - workersmax: Maximal workers used in any time slot (real [0,W])
        - workersmin: Minimum workers used in any time slot (real [0,W])

    - WIP tracking:
        - inv(i,t): Number of packing order i in stock (NON-NEGATIVE REAL - relaxed)
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

    # prod(i,t): Number of units of order i produced at time t (RELAXED TO REAL)
    model.prod = pyo.Var(
        model.ORDERS, model.TIME,
        domain=pyo.NonNegativeReals,
        doc="Number of units of order i produced at time t (relaxed to real)"
    )

    # ============================================
    # Workforce Tracking Variables
    # ============================================

    # workersused(t): Total workers actually working at time t (RELAXED TO REAL)
    model.workersused = pyo.Var(
        model.TIME,
        domain=pyo.NonNegativeReals,
        bounds=(0, model.n_workers),
        doc="Number of workers active at time t (relaxed to real)"
    )

    # workersmax: Maximum workers used in any time slot (RELAXED TO REAL)
    model.workersmax = pyo.Var(
        domain=pyo.NonNegativeReals,
        bounds=(0, model.n_workers),
        doc="Maximum workforce level across all time slots (relaxed to real)"
    )

    # workersmin: Minimum workers used in any time slot (RELAXED TO REAL)
    model.workersmin = pyo.Var(
        domain=pyo.NonNegativeReals,
        bounds=(0, model.n_workers),
        doc="Minimum workforce level across all time slots (relaxed to real)"
    )

    # workforcerange: Range of workforce utilization (RELAXED TO REAL)
    model.workforcerange = pyo.Var(
        domain=pyo.NonNegativeReals,
        bounds=(0, model.n_workers),
        doc="Workforce range (max - min) (relaxed to real)"
    )

    # ============================================
    # WIP Tracking Variables
    # ============================================

    # inv(i,t): Inventory of order i at time t (RELAXED TO REAL)
    model.inv = pyo.Var(
        model.ORDERS, model.TIME_WITH_ZERO,
        domain=pyo.NonNegativeReals,
        doc="Inventory of order i at time t (relaxed to real)"
    )

    # ship(i,t): Order i is shipped at time t
    model.ship = pyo.Var(
        model.ORDERS, model.TIME,
        domain=pyo.Binary,
        doc="Order i is shipped at time t"
    )

    return model
