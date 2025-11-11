"""
Decision Variables for Problem_4 Simplified Formulation

Key simplification: x(i,j,t) has NO worker index compared to Problem_3.
Workers are counted implicitly based on number of simultaneously active orders.
"""

import pyomo.environ as pyo


def define_variables(model):
    """
    Define all decision variables for the simplified packing schedule model.

    This is Problem_4 formulation - significantly simpler than Problem_3:
    - No worker index on assignment variable
    - Workers counted by simultaneous orders, not explicitly assigned
    - Batch indicators for setup optimization
    - Setup sequencing variables
    """

    # ============================================
    # Core Assignment Variables
    # ============================================

    # x(i,j,t): Packing order i starts on line j at time t
    # KEY DIFFERENCE: NO worker index (vs x(i,j,t,w) in Problem_3)
    model.x = pyo.Var(
        model.ORDERS, model.LINES, model.TIME,
        domain=pyo.Binary,
        doc="Order i starts on line j at time t"
    )

    # y(i,k,j): Setup between orders i and k on line j
    model.y = pyo.Var(
        model.ORDERS, model.ORDERS, model.LINES,
        domain=pyo.Binary,
        doc="Setup occurs between orders i and k on line j"
    )

    # b(i,k): Batch indicator - orders i and k are batched together
    model.b = pyo.Var(
        model.ORDERS, model.ORDERS,
        domain=pyo.Binary,
        doc="Orders i and k are batched together (same family, no setup)"
    )

    # prod(i,t): Number of units of order i produced at time t
    model.prod = pyo.Var(
        model.ORDERS, model.TIME,
        domain=pyo.NonNegativeIntegers,
        doc="Number of units of order i produced at time t"
    )

    # u(j): Line j is in use
    model.u = pyo.Var(
        model.LINES,
        domain=pyo.Binary,
        doc="Line j is activated/used"
    )

    # ============================================
    # OTIF Tracking Variables
    # ============================================

    # late(i): Binary indicator if order i is late
    model.late = pyo.Var(
        model.ORDERS,
        domain=pyo.Binary,
        doc="Order i is delivered late"
    )

    # lateness(i): How many time slots order i is late
    model.lateness = pyo.Var(
        model.ORDERS,
        domain=pyo.NonNegativeIntegers,
        doc="Lateness of order i in time slots"
    )

    # ============================================
    # Workforce Tracking Variables (Simplified)
    # ============================================

    # workersused(t): Total workers actually working at time t
    # This is computed by counting simultaneous orders
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

    # workforcerange: Range of workforce utilization
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

    # timeship(i): Time slot when order i is shipped
    # Note: Bounded by TIME set, but completion can exceed horizon
    model.timeship = pyo.Var(
        model.ORDERS,
        domain=pyo.NonNegativeIntegers,
        bounds=(1, model.n_timeslots),  # Must ship within horizon
        doc="Shipping time for order i"
    )

    # hasinv(i,t): Order i has available inventory at time t
    model.hasinv = pyo.Var(
        model.ORDERS, model.TIME,
        domain=pyo.Binary,
        doc="Order i has inventory available at time t"
    )

    # timestart(i): Actual start time for packing order i
    model.timestart = pyo.Var(
        model.ORDERS,
        domain=pyo.NonNegativeIntegers,
        bounds=(1, model.n_timeslots),
        doc="Start time for order i"
    )

    # timecompletion(i): Actual completion time for packing order i
    model.timecompletion = pyo.Var(
        model.ORDERS,
        domain=pyo.NonNegativeIntegers,
        bounds=(1, model.n_timeslots),
        doc="Completion time for order i"
    )

    # timeflow(i): Time from start to completion for packing order i
    model.timeflow = pyo.Var(
        model.ORDERS,
        domain=pyo.NonNegativeIntegers,
        doc="Flow time for order i (ship - start)"
    )

    return model
