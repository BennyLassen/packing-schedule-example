"""
WIP (Work-In-Progress) Constraints

This module defines constraints for tracking work-in-progress,
including production, inventory, and flow times.
"""

import pyomo.environ as pyo


def add_wip_constraints(model, data):
    """
    Add WIP-related constraints to the model.

    Args:
        model: Pyomo ConcreteModel instance
        data: Dictionary containing problem data
    """

    # Constraint: Flow time calculation (UPDATED for Problem 2)
    def flow_time_rule(m, i):
        """
        Calculate flow time from start to shipping.

        Flow time = shipping time - start time
        Note: time_ship is now a decision variable (not parameter)
        """
        return m.time_flow[i] == m.time_ship[i] - m.time_start[i]

    model.flow_time = pyo.Constraint(
        model.ORDERS,
        rule=flow_time_rule,
        doc="Calculate flow time for each order"
    )

    # Constraint: Production completion
    def production_rule(m, i, t):
        """
        Determine when production is completed.

        Order i is produced at time t if it started at time (t - processing_time)
        on some line.
        """
        expr = 0
        for j in m.LINES:
            for w in m.WORKERS:
                p_time = int(m.p[i, j])
                if t >= p_time:  # Need at least p_time slots
                    start_time = t - p_time
                    if start_time >= 1:
                        expr += m.x[i, j, start_time, w]
        return m.prod[i, t] == expr

    model.production = pyo.Constraint(
        model.ORDERS, model.TIME,
        rule=production_rule,
        doc="Production completion timing"
    )

    # Constraint: Inventory balance for t=1
    def inventory_balance_first_rule(m, i):
        """
        Inventory balance for first time period.

        inv[i,1] = initial_inventory + production - shipments
        """
        return m.inv[i, 1] == m.inv0[i] + m.prod[i, 1] - m.ship[i, 1]

    model.inventory_balance_first = pyo.Constraint(
        model.ORDERS,
        rule=inventory_balance_first_rule,
        doc="Inventory balance for t=1"
    )

    # Constraint: Inventory balance for t>1
    def inventory_balance_rule(m, i, t):
        """
        Inventory balance for subsequent time periods.

        inv[i,t] = inv[i,t-1] + production - shipments
        """
        if t == 1:
            return pyo.Constraint.Skip
        return m.inv[i, t] == m.inv[i, t-1] + m.prod[i, t] - m.ship[i, t]

    model.inventory_balance = pyo.Constraint(
        model.ORDERS, model.TIME,
        rule=inventory_balance_rule,
        doc="Inventory balance equation"
    )

    # Constraint: WIP indicator
    def wip_indicator_rule(m, i, t):
        """
        Determine if order is in work-in-progress.

        Order i is WIP at time t if:
        - It's currently being processed, OR
        - It's in inventory (produced but not yet shipped)
        """
        expr = 0
        for j in m.LINES:
            for w in m.WORKERS:
                for tau in m.TIME:
                    # Order started at tau and is still processing at t
                    if tau <= t < tau + int(m.p[i, j]):
                        expr += m.x[i, j, tau, w]

        # WIP indicator <= (processing indicator + inventory)
        return m.wip_indicator[i, t] <= expr + m.inv[i, t]

    model.wip_indicator_calc = pyo.Constraint(
        model.ORDERS, model.TIME,
        rule=wip_indicator_rule,
        doc="WIP indicator calculation"
    )

    # Constraint: Total WIP count
    def wip_count_rule(m, t):
        """
        Count total number of orders in WIP.

        Sum WIP indicators across all orders.
        """
        return m.wip[t] == sum(m.wip_indicator[i, t] for i in m.ORDERS)

    model.wip_count = pyo.Constraint(
        model.TIME,
        rule=wip_count_rule,
        doc="Total WIP count at each time"
    )
