"""
Decision Variables for Problem_4_1_c2 Formulation

Implements all decision variables from Problem_4_1_c2.pdf including:
- Core assignment variables: x(i,j), s(i), c(i)
- Workforce tracking: started(i,e), notcomplete(i,e), workersused(t), workersmax, workersmin
- WIP tracking: prodbefore(u,d), prodorder(i,d), inv(u,d), ship(d)
"""

import pyomo.environ as pyo


def define_variables(model):
    """
    Define all decision variables for Problem_4_1_c2 packing schedule model.

    Variables are organized into groups:
    1. Core assignment and timing variables
    2. Workforce tracking variables
    3. WIP (Work-in-Progress) tracking variables
    4. Helper variables for sequencing
    """

    # ============================================
    # Core Assignment Variables
    # ============================================

    # x(i,j): Order i is assigned to line j (binary)
    model.x = pyo.Var(
        model.ORDERS, model.LINES,
        domain=pyo.Binary,
        doc="Order i is assigned to line j"
    )

    # start(i): Start time of order i (non-negative real)
    # Note: Using 'start' instead of 's' to avoid conflict with setup time parameter
    model.start = pyo.Var(
        model.ORDERS,
        domain=pyo.NonNegativeReals,
        bounds=(0, model.T_max),
        doc="Start time of order i"
    )

    # complete(i): Completion time of order i (non-negative real)
    # Note: Using 'complete' instead of 'c' for clarity
    model.complete = pyo.Var(
        model.ORDERS,
        domain=pyo.NonNegativeReals,
        bounds=(0, model.T_max),
        doc="Completion time of order i"
    )

    # y(i,k): Binary variable for sequencing (order i before k)
    # Used in line capacity constraints
    model.y = pyo.Var(
        model.ORDERS, model.ORDERS,
        domain=pyo.Binary,
        doc="Order i is scheduled before order k on the same line"
    )

    # u(j): Line j is in use (binary)
    # From Problem_4_1_c2.pdf Page 1
    model.u = pyo.Var(
        model.LINES,
        domain=pyo.Binary,
        doc="Line j is in use"
    )

    # ============================================
    # Workforce Tracking Variables
    # ============================================

    # started(i,e): Order i has started before event e (binary)
    model.started = pyo.Var(
        model.ORDERS, model.EVENTS,
        domain=pyo.Binary,
        doc="Order i has started before event e"
    )

    # notcomplete(i,e): Order i is not complete before event e (binary)
    model.notcomplete = pyo.Var(
        model.ORDERS, model.EVENTS,
        domain=pyo.Binary,
        doc="Order i is not complete before event e"
    )

    # is_active(i,e): Order i is active (started but not complete) at event e (binary)
    # Note: Using 'is_active' instead of 'active' as 'active' is a reserved Pyomo attribute
    model.is_active = pyo.Var(
        model.ORDERS, model.EVENTS,
        domain=pyo.Binary,
        doc="Order i is active at event e"
    )

    # workersused(e): Total workers actually working at event e
    # Note: In the PDF it says workersused(t), but we track at events
    # We'll use a continuous variable that can be relaxed to real [0, W]
    # We need to know max workers W from data
    max_workers = model.n_orders  # Assume max workers = max concurrent orders
    model.workersused = pyo.Var(
        model.EVENTS,
        domain=pyo.NonNegativeReals,
        bounds=(0, max_workers),
        doc="Total workers actually working at event e"
    )

    # workersmax: Maximal workers used in any time slot
    model.workersmax = pyo.Var(
        domain=pyo.NonNegativeReals,
        bounds=(0, max_workers),
        doc="Maximum workers used in any event"
    )

    # workersmin: Minimum workers used in any time slot
    model.workersmin = pyo.Var(
        domain=pyo.NonNegativeReals,
        bounds=(0, max_workers),
        doc="Minimum workers used in any event"
    )

    # workforcerange: Workforce range (max - min)
    model.workforcerange = pyo.Var(
        domain=pyo.NonNegativeReals,
        bounds=(0, max_workers),
        doc="Workforce range (max - min)"
    )

    # ============================================
    # WIP Tracking Variables
    # ============================================

    # prodbefore(u,d): Number of units of product u produced and ready before demand d ships
    model.prodbefore = pyo.Var(
        model.TYPES, model.DEMANDS,
        domain=pyo.NonNegativeIntegers,
        doc="Units of product u produced before demand d ships"
    )

    # prodorder(i,d): Order i is produced before demand d ships
    model.prodorder = pyo.Var(
        model.ORDERS, model.DEMANDS,
        domain=pyo.Binary,
        doc="Order i is produced before demand d ships"
    )

    # inv(u,d): Number of item type u in stock after fulfilling demand d
    model.inv = pyo.Var(
        model.TYPES, model.DEMANDS,
        domain=pyo.NonNegativeIntegers,
        doc="Inventory of type u after fulfilling demand d"
    )

    # ship(d): Shipping time of demand d (non-negative real)
    model.ship = pyo.Var(
        model.DEMANDS,
        domain=pyo.NonNegativeReals,
        bounds=(0, model.T_max),
        doc="Shipping time of demand d"
    )

    # shipped(d1,d): Demand d1 is shipped before or at the same time as demand d (binary)
    model.shipped = pyo.Var(
        model.DEMANDS, model.DEMANDS,
        domain=pyo.Binary,
        doc="Demand d1 is shipped before or at the same time as demand d"
    )

    # ============================================
    # OTIF (On-Time In-Full) Variables
    # ============================================

    # lateness(d): Lateness of demand d (ship_time - due_date if late, else 0)
    model.lateness = pyo.Var(
        model.DEMANDS,
        domain=pyo.NonNegativeReals,
        doc="Lateness of demand d (ship_time - due_date if late, else 0)"
    )

    # late(d): Binary indicator for late demand (1 if late, 0 if on-time)
    model.late = pyo.Var(
        model.DEMANDS,
        domain=pyo.Binary,
        doc="Binary indicator: 1 if demand d is late, 0 if on-time"
    )

    # ============================================
    # Event Time Mapping Variables (Helper)
    # ============================================

    # t(e): Time of event e (for tracking event times)
    # Events correspond to start and completion times
    model.t_event = pyo.Var(
        model.EVENTS,
        domain=pyo.NonNegativeReals,
        bounds=(0, model.T_max),
        doc="Time of event e"
    )

    return model
