"""
Worker Constraints

This module defines constraints related to worker assignments and availability.
"""

import pyomo.environ as pyo


def add_worker_constraints(model, data):
    """
    Add worker-related constraints to the model.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing problem data
    """

    # Constraint: Worker working indicator
    def worker_working_rule(m, w, tau):
        """
        Link worker working indicator to order assignments.

        Worker w is working at time tau if they're assigned to an order
        that is being processed at time tau.
        """
        expr = 0
        for i in m.ORDERS:
            for j in m.LINES:
                for t in m.TIME:
                    # Check if order starting at t is being processed at tau
                    if t <= tau < t + int(m.p[i, j]):
                        expr += m.x[i, j, t, w]
        return expr == m.w_working[w, tau]

    model.worker_working = pyo.Constraint(
        model.WORKERS, model.TIME,
        rule=worker_working_rule,
        doc="Worker working indicator definition"
    )

    # Constraint: Worker availability
    def worker_availability_rule(m, w, t):
        """
        Workers can only work when they are available.

        The working indicator must be 0 when the worker is not available.
        """
        return m.w_working[w, t] <= m.a[w, t]

    model.worker_availability = pyo.Constraint(
        model.WORKERS, model.TIME,
        rule=worker_availability_rule,
        doc="Workers only work when available"
    )

    # Constraint: Reserved worker capacity
    def reserved_worker_capacity_rule(m):
        """
        Reserve a fraction of total worker capacity.

        Total worker-time used should not exceed (1 - alpha) * total
        available worker-time, where alpha is the reserved capacity fraction.
        """
        total_used = sum(
            m.w_working[w, t]
            for w in m.WORKERS
            for t in m.TIME
        )
        total_available = sum(
            m.a[w, t]
            for w in m.WORKERS
            for t in m.TIME
        )
        return total_used <= (1 - m.alpha) * total_available

    model.reserved_worker_capacity = pyo.Constraint(
        rule=reserved_worker_capacity_rule,
        doc="Reserve fraction of worker capacity"
    )

    # Constraint: Worker movement balance
    def worker_movement_rule(m, w, j, t):
        """
        Track worker movements between lines.

        Worker movement indicator m(w,t) is 1 if worker w is working on
        a different line at time t compared to time t-1.

        This constraint is from Problem_3: m(w,t) >= sum_i(x(i,j,w,t) - x(i,j,w,t-1))
        for each line j. The movement indicator captures when a worker switches lines.
        """
        if t == 1:
            # No movement at first time slot (no previous state)
            return pyo.Constraint.Skip

        # Sum of differences for this line
        expr = sum(
            m.x[i, j, t, w] - m.x[i, j, t-1, w]
            for i in m.ORDERS
        )

        return m.m[w, t] >= expr

    model.worker_movement = pyo.Constraint(
        model.WORKERS, model.LINES, model.TIME,
        rule=worker_movement_rule,
        doc="Worker movement between lines tracking"
    )
