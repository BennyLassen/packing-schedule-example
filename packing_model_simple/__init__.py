"""
Simplified Packing Schedule Optimization Model (Problem_4)

This module implements the simplified formulation from Problem_4.pdf:
- No explicit worker assignment (workers counted implicitly)
- Batch indicator variables for setup time optimization
- Setup sequencing variables
- Simplified workforce tracking (range-based)
- 4-term objective function (OTIF, WIP, workforce range, line utilization)

Key differences from Problem_3 (packing_model):
1. Assignment variable x(i,j,t) has NO worker index (vs x(i,j,t,w) in Problem_3)
2. Workers counted by simultaneous active orders, not explicitly assigned
3. Batch indicators b(i,k) for batching logic
4. Setup sequencing y(i,k,j) tracks order sequences
5. No worker movement penalty (omega term removed)
6. Workforce term is simply workersmax - workersmin

This is a significantly simpler formulation suitable for problems where
explicit worker assignment is not required, only worker counting.
"""

from .model import PackingScheduleModelSimple

__all__ = ['PackingScheduleModelSimple']
__version__ = '1.0.0'
