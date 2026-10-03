from __future__ import annotations

from __future__ import annotations
import numpy as np
from logistics_engine.graph.interface import GraphInterface
from logistics_engine.models import Road

class CSRGraph(GraphInterface):

    def __init__(self, num_nodes: int, roads: list[Road]) -> None:
        self.num_nodes = num_nodes
        degree = np.zeros(num_nodes, dtype=np.int64)
        for road in roads:
            degree[road.source] += 1
            degree[road.destination] += 1
        self.offsets = np.zeros(num_nodes + 1, dtype=np.int64)
        self.offsets[1:] = np.cumsum(degree)
        num_edges = int(self.offsets[-1])
        self.neighbors_array = np.empty(num_edges, dtype=np.int32)
        self.weights_array = np.empty(num_edges, dtype=np.float64)
        current_position = self.offsets[:-1].copy()
        for road in roads:
            source_position = current_position[road.source]
            self.neighbors_array[source_position] = road.destination
            self.weights_array[source_position] = road.distance
            current_position[road.source] += 1
            destination_position = current_position[road.destination]
            self.neighbors_array[destination_position] = road.source
            self.weights_array[destination_position] = road.distance
            current_position[road.destination] += 1

    def has_node(self, node: int) -> bool:
        return 0 <= node < self.num_nodes

    def nodes(self) -> list[int]:
        return list(range(self.num_nodes))

    def neighbors(self, node: int):
        start = self.offsets[node]
        end = self.offsets[node + 1]
        return [(int(neighbor), float(weight)) for neighbor, weight in zip(*(self.neighbors_array[start:end], self.weights_array[start:end]))]

    def __len__(self) -> int:
        return self.num_nodes

    @property
    def edge_count(self) -> int:
        return len(self.neighbors_array)