from .interface import GraphInterface


class Graph(GraphInterface):

    def __init__(self) -> None:
        self.adjacency_list: dict[int, list[tuple[int, float]]] = {}

    def add_vertex(self, vertex: int) -> None:
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []

    def add_edge(
        self,
        source: int,
        destination: int,
        weight: float,
        bidirectional: bool = True
    ) -> None:

        if weight < 0:
            raise ValueError(
                "Dijkstra requires non-negative edge weights."
            )

        self.add_vertex(source)
        self.add_vertex(destination)

        self.adjacency_list[source].append(
            (destination, weight)
        )

        if bidirectional:
            self.adjacency_list[destination].append(
                (source, weight)
            )

    def neighbors(
        self,
        vertex: int
    ) -> list[tuple[int, float]]:

        if vertex not in self.adjacency_list:
            raise ValueError(f"Unknown vertex: {vertex}")

        return self.adjacency_list[vertex]

    def __len__(self) -> int:
        return len(self.adjacency_list)

    def has_node(self, node: int) -> bool:
        return node in self.adjacency_list

    def nodes(self) -> list[int]:
        return list(self.adjacency_list.keys())


    @property
    def edge_count(self) -> int:
        return sum(
            len(neighbors)
            for neighbors in self.adjacency_list.values()
        )
