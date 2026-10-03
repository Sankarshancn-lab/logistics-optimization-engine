from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Optional
from logistics_engine.graph import GraphInterface
from logistics_engine.models import Location, PathResult
from logistics_engine.routing.heap import MinHeap
from logistics_engine.spatial import euclidean_heuristic

def dijkstra(graph: GraphInterface, source: int, destination: int) -> Optional[PathResult]:
    if not graph.has_node(source):
        raise ValueError(f'Unknown source node: {source}')
    if not graph.has_node(destination):
        raise ValueError(f'Unknown destination node: {destination}')
    if source == destination:
        return PathResult(path=[source], distance=0.0)
    nodes = graph.nodes()
    distances = {node: math.inf for node in nodes}
    previous: dict[int, Optional[int]] = {node: None for node in nodes}
    distances[source] = 0.0
    queue = MinHeap()
    queue.push((0.0, source))
    while not queue.is_empty():
        current_distance, current_node = queue.pop()
        if current_distance != distances[current_node]:
            continue
        if current_node == destination:
            break
        for neighbor, weight in graph.neighbors(current_node):
            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                queue.push((new_distance, neighbor))
    if distances[destination] == math.inf:
        return None
    path = []
    current: Optional[int] = destination
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    return PathResult(path=path, distance=distances[destination])

@dataclass(slots=True, frozen=True)
class SearchResult:
    path: list[int]
    distance: float
    nodes_explored: int
    heap_operations: int

def a_star(
    graph: GraphInterface,
    locations: list[Location],
    source: int,
    destination: int,
    heuristic: str = "zero",
) -> Optional[SearchResult]:

    if not graph.has_node(source):
        raise ValueError(f"Unknown source node: {source}")

    if not graph.has_node(destination):
        raise ValueError(f"Unknown destination node: {destination}")

    if heuristic not in {"zero", "euclidean"}:
        raise ValueError(
            f"Unknown heuristic: {heuristic}. "
            "Expected 'zero' or 'euclidean'."
        )

    if source == destination:
        return SearchResult(
            path=[source],
            distance=0.0,
            nodes_explored=1,
            heap_operations=0,
        )

    if heuristic == "euclidean":
        if source >= len(locations):
            raise ValueError(
                f"Missing location for source node: {source}"
            )

        if destination >= len(locations):
            raise ValueError(
                f"Missing location for destination node: {destination}"
            )

    def calculate_heuristic(node: int) -> float:
        if heuristic == "zero":
            return 0.0

        if node >= len(locations):
            raise ValueError(
                f"Missing location for node: {node}"
            )

        return euclidean_heuristic(
            locations,
            node,
            destination,
        )

    distances = {
        node: math.inf
        for node in graph.nodes()
    }

    previous: dict[int, Optional[int]] = {
        node: None
        for node in graph.nodes()
    }

    distances[source] = 0.0

    queue = MinHeap()

    initial_priority = calculate_heuristic(source)

    queue.push(
        (initial_priority, source)
    )

    nodes_explored = 0
    heap_operations = 1

    while not queue.is_empty():

        current_priority, current_node = queue.pop()

        heap_operations += 1

        current_g = distances[current_node]

        expected_priority = (
            current_g
            + calculate_heuristic(current_node)
        )

        if current_priority > expected_priority:
            continue

        nodes_explored += 1

        if current_node == destination:
            break

        for neighbor, weight in graph.neighbors(current_node):

            new_distance = (
                current_g + weight
            )

            if new_distance < distances[neighbor]:

                distances[neighbor] = new_distance

                previous[neighbor] = current_node

                priority = (
                    new_distance
                    + calculate_heuristic(neighbor)
                )

                queue.push(
                    (priority, neighbor)
                )

                heap_operations += 1

    if distances[destination] == math.inf:
        return None

    path = []

    current: Optional[int] = destination

    while current is not None:

        path.append(current)

        current = previous[current]

    path.reverse()

    return SearchResult(
        path=path,
        distance=distances[destination],
        nodes_explored=nodes_explored,
        heap_operations=heap_operations,
    )