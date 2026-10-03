from __future__ import annotations

import math

from logistics_engine.models import Location

def euclidean_heuristic(
    locations: list[Location],
    node: int,
    destination: int
) -> float:

    current = locations[node]
    target = locations[destination]

    return math.hypot(
        current.x - target.x,
        current.y - target.y
    )
