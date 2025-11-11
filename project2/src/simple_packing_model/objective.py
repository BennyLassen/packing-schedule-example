"""
Objective Function for Problem_4_1_c2 Formulation

Implements the four-term objective function from Problem_4_1_c2.pdf Page 9:
1. OTIF: On-Time In-Full delivery performance
2. WIP: Work-in-progress inventory minimization
3. Workforce: Workforce variability (range: max - min)
4. Total not utilized: (Note: The PDF doesn't clearly specify this term)

f = α * otif + β * wip_obj + γ * workforce + δ * total_not_utilized
"""

import pyomo.environ as pyo


class ObjectiveManager:
    """
    Manages the objective function for Problem_4_1_c2 packing schedule model.

    Problem_4_1_c2 Page 9:
    f = α * otif + β * wip_obj + γ * workforce + δ * total_not_utilized

    where:
    - otif = ∑_d priority(d) * (7 * late(d) + 3 * lateness(d))
    - wip_obj = ∑_u ∑_d inv(u,d)
    - workforce = workersrange
    - total_not_utilized = ∑_j u(j) (number of lines in use)
    """

    def __init__(self, data):
        """
        Initialize objective manager with user-specified weights.

        Args:
            data: Dictionary containing 'objective_weights' with keys:
                  - alpha: OTIF weight
                  - beta: WIP weight
                  - gamma: Workforce variability weight
                  - delta: Not utilized weight
        """
        self.weights = data.get('objective_weights', {
            'alpha': 1.0,   # OTIF weight
            'beta': 1.0,    # WIP weight
            'gamma': 1.0,   # Workforce variability weight
            'delta': 0.0    # Not utilized weight (disabled by default)
        })

    def _otif_term(self, m):
        """
        OTIF term: Minimize late deliveries and lateness.

        Problem_4_1_c2 Page 9:
        otif = ∑_d priority(d) * (7 * late(d) + 3 * lateness(d))

        This penalizes:
        - Being late (binary late(d) with weight 7)
        - Amount of lateness (continuous lateness(d) with weight 3)
        Each weighted by the demand's priority.
        """
        return sum(
            m.priority[d] * (7 * m.late[d] + 3 * m.lateness[d])
            for d in m.DEMANDS
        )

    def _wip_term(self, m):
        """
        WIP term: Minimize total inventory across all demands.

        Problem_4_1_c2 Page 9:
        wip_obj = ∑_u ∑_d inv(u,d)

        Summing inventory across all types and demands.
        """
        return sum(
            m.inv[u, d]
            for u in m.TYPES
            for d in m.DEMANDS
        )

    def _workforce_term(self, m):
        """
        Workforce term: Minimize workforce variability.

        Problem_4_1_c2 Page 9:
        workforce = workersrange

        This is the range of workforce utilization (max - min).
        Lower range means more stable workforce utilization.
        """
        return m.workforcerange

    def _not_utilized_term(self, m):
        """
        Total not utilized term: Number of lines fully utilized.

        Problem_4_1_c2 Page 9:
        total_not_utilized = ∑_j u(j)

        This counts the number of production lines that are in use.
        Minimizing this encourages using fewer lines (consolidation).
        """
        return sum(m.u[j] for j in m.LINES)

    def define_objective(self, model):
        """
        Define the complete objective function for the model.

        Problem_4_1_c2 Page 9:
        minimize: α * otif + β * wip_obj + γ * workforce + δ * total_not_utilized

        Four terms weighted by user-specified parameters:
        1. OTIF (alpha): On-time delivery performance
        2. WIP (beta): Total inventory across types and demands
        3. Workforce (gamma): Workforce range (max - min)
        4. Not utilized (delta): Number of lines in use (encourages line consolidation)
        """

        def objective_rule(m):
            """Calculate the weighted sum of all objective terms."""
            return (
                m.alpha * self._otif_term(m) +
                m.beta * self._wip_term(m) +
                m.gamma * self._workforce_term(m) +
                m.delta * self._not_utilized_term(m)
            )

        model.objective = pyo.Objective(
            rule=objective_rule,
            sense=pyo.minimize,
            doc="Minimize weighted sum of OTIF, WIP, workforce, and not utilized"
        )

        return model


def define_objective(model, data):
    """
    Convenience function to define the objective for a model.

    Args:
        model: Pyomo ConcreteModel
        data: Dictionary with input data including objective_weights

    Returns:
        model: Model with objective defined
    """
    obj_manager = ObjectiveManager(data)
    return obj_manager.define_objective(model)
