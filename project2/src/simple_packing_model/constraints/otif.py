"""
OTIF (On-Time In-Full) Constraints for Problem_3

Implements lateness tracking and late order identification.

From Problem_3.pdf Page 5:
- Lateness calculation: lateness(d) ≥ ship(d) - due(d)
- Lateness non-negativity: lateness(d) ≥ 0
- Late order identification using binary indicators
"""

import pyomo.environ as pyo


def define_otif_constraints(model):
    """
    Define OTIF (On-Time In-Full) constraints for Problem_3.

    From Page 5:
    Lateness:
    - lateness(d) ≥ ship(d) - due(d)  ∀d
    - lateness(d) ≥ 0  ∀d

    Identify late orders:
    - [late(d) = 1] ⇒ [lateness(d) > 0]
    - [late(d) = 0] ⇒ [lateness(d) = 0]
    """

    def lateness_calculation_rule(m, d):
        """
        Calculate lateness as the difference between ship time and due date.

        lateness(d) ≥ ship(d) - due(d)  ∀d

        If the demand ships late (ship(d) > due(d)), then lateness must be
        at least the difference. If on-time, this constraint doesn't force
        lateness to be positive (the late indicator constraints handle that).
        """
        return m.lateness[d] >= m.ship[d] - m.due[d]

    model.lateness_calculation = pyo.Constraint(
        model.DEMANDS,
        rule=lateness_calculation_rule,
        doc="Lateness is at least ship_time - due_date"
    )

    def lateness_nonnegative_rule(m, d):
        """
        Lateness must be non-negative.

        lateness(d) ≥ 0  ∀d

        This is automatically enforced by the variable domain (NonNegativeReals),
        but we include it explicitly for clarity and to match the PDF specification.
        """
        return m.lateness[d] >= 0

    model.lateness_nonnegative = pyo.Constraint(
        model.DEMANDS,
        rule=lateness_nonnegative_rule,
        doc="Lateness must be non-negative"
    )

    def late_if_positive_lateness_rule(m, d):
        """
        If late(d) = 1, then lateness(d) > 0.

        [late(d) = 1] ⇒ [lateness(d) > 0]

        Reformulated as: lateness(d) ≥ epsilon * late(d)

        This ensures that if late(d) = 1, lateness must be at least epsilon (a small positive value).
        """
        return m.lateness[d] >= m.epsilon * m.late[d]

    model.late_if_positive_lateness = pyo.Constraint(
        model.DEMANDS,
        rule=late_if_positive_lateness_rule,
        doc="If late(d)=1, then lateness(d) > 0"
    )

    def not_late_if_zero_lateness_rule(m, d):
        """
        If late(d) = 0, then lateness(d) = 0.

        [late(d) = 0] ⇒ [lateness(d) = 0]

        Reformulated as: lateness(d) ≤ M * late(d)

        This ensures that if late(d) = 0, lateness must be 0.
        If late(d) = 1, lateness can be up to M (large enough to not constrain).
        """
        return m.lateness[d] <= m.M * m.late[d]

    model.not_late_if_zero_lateness = pyo.Constraint(
        model.DEMANDS,
        rule=not_late_if_zero_lateness_rule,
        doc="If late(d)=0, then lateness(d)=0"
    )

    return model
