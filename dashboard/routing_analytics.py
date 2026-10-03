"""Routing algorithm comparison services."""

from dataclasses import dataclass
from time import perf_counter

from logistics_engine.routing import a_star, dijkstra


@dataclass(frozen=True)
class AlgorithmComparison:
    """Comparison between A* and Dijkstra."""

    source: int
    destination: int

    a_star_distance: float
    dijkstra_distance: float

    a_star_path_nodes: int
    dijkstra_path_nodes: int

    a_star_nodes_explored: int
    a_star_heap_operations: int

    a_star_runtime_seconds: float
    dijkstra_runtime_seconds: float

    distance_difference: float


def compare_routing_algorithms(
    graph,
    locations,
    source: int,
    destination: int,
) -> AlgorithmComparison:
    """Compare A* and Dijkstra."""

    a_start = perf_counter()

    a_star_result = a_star(
        graph,
        locations,
        source,
        destination,
        heuristic="zero",
    )

    a_runtime = perf_counter() - a_start

    if a_star_result is None:
        raise ValueError("A* could not find a route.")

    d_start = perf_counter()

    dijkstra_result = dijkstra(
        graph,
        source,
        destination,
    )

    d_runtime = perf_counter() - d_start

    if dijkstra_result is None:
        raise ValueError("Dijkstra could not find a route.")

    a_star_distance = float(a_star_result.distance)
    dijkstra_distance = float(dijkstra_result.distance)

    distance_difference = abs(
        a_star_distance - dijkstra_distance
    )

    a_star_path_nodes = len(a_star_result.path)
    dijkstra_path_nodes = len(dijkstra_result.path)

    a_star_nodes_explored = int(
        a_star_result.nodes_explored
    )

    a_star_heap_operations = int(
        a_star_result.heap_operations
    )

    return AlgorithmComparison(
        source=source,
        destination=destination,
        a_star_distance=a_star_distance,
        dijkstra_distance=dijkstra_distance,
        a_star_path_nodes=a_star_path_nodes,
        dijkstra_path_nodes=dijkstra_path_nodes,
        a_star_nodes_explored=a_star_nodes_explored,
        a_star_heap_operations=a_star_heap_operations,
        a_star_runtime_seconds=a_runtime,
        dijkstra_runtime_seconds=d_runtime,
        distance_difference=distance_difference,
    )