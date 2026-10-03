"""Business and operational metrics used by the logistics dashboard."""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class NetworkMetrics:
    location_count: int
    road_count: int
    total_network_distance: float
    average_road_distance: float


@dataclass(frozen=True)
class RouteMetrics:
    source: int
    destination: int
    distance: float
    stop_count: int
    nodes_explored: int
    heap_operations: int


def calculate_network_metrics(
    locations: Sequence,
    roads: Sequence,
) -> NetworkMetrics:
    """Calculate high-level network KPIs."""

    location_count = len(locations)
    road_count = len(roads)

    total_distance = sum(float(road.distance) for road in roads)

    average_distance = (
        total_distance / road_count
        if road_count
        else 0.0
    )

    return NetworkMetrics(
        location_count=location_count,
        road_count=road_count,
        total_network_distance=total_distance,
        average_road_distance=average_distance,
    )


def calculate_route_metrics(
    source: int,
    destination: int,
    distance: float,
    path: Sequence[int],
    nodes_explored: int,
    heap_operations: int,
) -> RouteMetrics:
    """Convert a routing result into dashboard-friendly metrics."""

    return RouteMetrics(
        source=source,
        destination=destination,
        distance=float(distance),
        stop_count=len(path),
        nodes_explored=int(nodes_explored),
        heap_operations=int(heap_operations),
    )
