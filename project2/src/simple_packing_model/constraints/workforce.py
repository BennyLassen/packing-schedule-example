"""
Workforce Constraints for Problem_3

Implements workforce tracking based on events (start and completion times).

From Problem_3.pdf Page 8:
- Active workers per time slot (event)
- Maximum and minimum workforce tracking
- Workforce range calculation
"""

import pyomo.environ as pyo


def define_workforce_constraints(model):
    """
    Define workforce tracking constraints for Problem_3.

    From Page 8:
    1. Active workers: active(i,e) = started(i,e) ∧ notcomplete(i,e)
    2. Worker count: workersused(e) = ∑_i active(i,e)
    3. Started tracking: [started(i,e) = 1] ⇒ [s(i) ≤ t(e)]
    4. Not complete tracking: [notcomplete(i,e) = 1] ⇒ [c(i) > t(e)]
    5. Max/min tracking: workersmax ≥ workersused(e), workersused(e) ≥ workersmin
    6. Range: workforcerange = workersmax - workersmin
    """

    # First, we need to link event times to order start/completion times
    def event_time_start_rule(m, i):
        """
        Link event corresponding to order i's start to its start time.

        Event index for start of order i is i.
        t_event(i) = start(i)
        """
        return m.t_event[i] == m.start[i]

    model.event_time_start = pyo.Constraint(
        model.ORDERS,
        rule=event_time_start_rule,
        doc="Event time for start of order i"
    )

    def event_time_completion_rule(m, i):
        """
        Link event corresponding to order i's completion to its completion time.

        Event index for completion of order i is n_orders + i.
        t_event(n_orders + i) = complete(i)
        """
        event_idx = m.n_orders + i
        return m.t_event[event_idx] == m.complete[i]

    model.event_time_completion = pyo.Constraint(
        model.ORDERS,
        rule=event_time_completion_rule,
        doc="Event time for completion of order i"
    )

    # Active worker tracking (logical AND constraint)
    def active_constraint_1_rule(m, i, e):
        """
        is_active(i,e) ≤ started(i,e)

        Part of: is_active(i,e) = started(i,e) ∧ notcomplete(i,e)
        """
        return m.is_active[i, e] <= m.started[i, e]

    model.active_constraint_1 = pyo.Constraint(
        model.ORDERS, model.EVENTS,
        rule=active_constraint_1_rule,
        doc="Active implies started"
    )

    def active_constraint_2_rule(m, i, e):
        """
        is_active(i,e) ≤ notcomplete(i,e)

        Part of: is_active(i,e) = started(i,e) ∧ notcomplete(i,e)
        """
        return m.is_active[i, e] <= m.notcomplete[i, e]

    model.active_constraint_2 = pyo.Constraint(
        model.ORDERS, model.EVENTS,
        rule=active_constraint_2_rule,
        doc="Active implies not complete"
    )

    def active_constraint_3_rule(m, i, e):
        """
        is_active(i,e) ≥ started(i,e) + notcomplete(i,e) - 1

        Part of: is_active(i,e) = started(i,e) ∧ notcomplete(i,e)
        This enforces: if both started and notcomplete are 1, then is_active must be 1.
        """
        return m.is_active[i, e] >= m.started[i, e] + m.notcomplete[i, e] - 1

    model.active_constraint_3 = pyo.Constraint(
        model.ORDERS, model.EVENTS,
        rule=active_constraint_3_rule,
        doc="Started and not complete implies active"
    )

    # Started tracking
    def started_true_rule(m, i, e):
        """
        If started(i,e) = 1, then start(i) ≤ t(e)

        Reformulated as: start(i) ≤ t(e) + M * (1 - started(i,e))
        """
        return m.start[i] <= m.t_event[e] + m.M * (1 - m.started[i, e])

    model.started_true = pyo.Constraint(
        model.ORDERS, model.EVENTS,
        rule=started_true_rule,
        doc="If started, then start time before event time"
    )

    def started_false_rule(m, i, e):
        """
        If started(i,e) = 0, then start(i) > t(e)

        Reformulated as: start(i) ≥ t(e) + epsilon - M * started(i,e)
        """
        return m.start[i] >= m.t_event[e] + m.epsilon - m.M * m.started[i, e]

    model.started_false = pyo.Constraint(
        model.ORDERS, model.EVENTS,
        rule=started_false_rule,
        doc="If not started, then start time after event time"
    )

    # Not complete tracking
    def notcomplete_true_rule(m, i, e):
        """
        If notcomplete(i,e) = 1, then complete(i) > t(e)

        Reformulated as: complete(i) ≥ t(e) + epsilon - M * (1 - notcomplete(i,e))
        """
        return m.complete[i] >= m.t_event[e] + m.epsilon - m.M * (1 - m.notcomplete[i, e])

    model.notcomplete_true = pyo.Constraint(
        model.ORDERS, model.EVENTS,
        rule=notcomplete_true_rule,
        doc="If not complete, then completion time after event time"
    )

    def notcomplete_false_rule(m, i, e):
        """
        If notcomplete(i,e) = 0, then complete(i) ≤ t(e)

        Reformulated as: complete(i) ≤ t(e) + M * notcomplete(i,e)
        """
        return m.complete[i] <= m.t_event[e] + m.M * m.notcomplete[i, e]

    model.notcomplete_false = pyo.Constraint(
        model.ORDERS, model.EVENTS,
        rule=notcomplete_false_rule,
        doc="If complete, then completion time before event time"
    )

    # Workers used at each event
    def workers_used_rule(m, e):
        """
        Count total workers active at event e.

        workersused(e) = ∑_i is_active(i,e)  ∀e
        """
        return m.workersused[e] == sum(m.is_active[i, e] for i in m.ORDERS)

    model.workers_used = pyo.Constraint(
        model.EVENTS,
        rule=workers_used_rule,
        doc="Count active workers at each event"
    )

    # Maximum workforce
    def max_workforce_rule(m, e):
        """
        Track maximum workforce across all events.

        workersmax ≥ workersused(e)  ∀e
        """
        return m.workersmax >= m.workersused[e]

    model.max_workforce = pyo.Constraint(
        model.EVENTS,
        rule=max_workforce_rule,
        doc="Maximum workforce tracking"
    )

    # Minimum workforce
    def min_workforce_rule(m, e):
        """
        Track minimum workforce across all events.

        workersused(e) ≥ workersmin  ∀e
        """
        return m.workersused[e] >= m.workersmin

    model.min_workforce = pyo.Constraint(
        model.EVENTS,
        rule=min_workforce_rule,
        doc="Minimum workforce tracking"
    )

    # Workforce range
    def workforce_range_rule(m):
        """
        Define workforce range as difference between max and min.

        workforcerange = workersmax - workersmin
        """
        return m.workforcerange == m.workersmax - m.workersmin

    model.workforce_range = pyo.Constraint(
        rule=workforce_range_rule,
        doc="Workforce range definition"
    )

    return model
