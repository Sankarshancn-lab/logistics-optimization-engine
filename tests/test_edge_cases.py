"""
M33.2 - Edge-Case & Failure Testing

Tests the real Graph, Dijkstra, and A* implementations without
touching the Streamlit dashboard or production database.

Run from the project source directory.

Command:
    python -m unittest logistics_engine.tests.test_edge_cases -v
"""

import math
import unittest

from logistics_engine.graph import Graph
from logistics_engine.routing import a_star, dijkstra


class TestRoutingEdgeCases(unittest.TestCase):
    """M33.2 routing robustness tests."""

    def build_graph(self):
        """Create a small deterministic test graph."""
        graph = Graph()

        graph.add_edge(0, 1, 5.0)
        graph.add_edge(1, 2, 3.0)
        graph.add_edge(0, 2, 12.0)
        graph.add_edge(2, 3, 2.0)

        return graph

    def test_01_normal_a_star_route(self):
        """A valid route should be returned successfully."""
        graph = self.build_graph()

        result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [0, 1, 2, 3])
        self.assertAlmostEqual(result.distance, 10.0)

    def test_02_normal_dijkstra_route(self):
        """Dijkstra should find the same shortest distance."""
        graph = self.build_graph()

        result = dijkstra(graph, 0, 3)

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [0, 1, 2, 3])
        self.assertAlmostEqual(result.distance, 10.0)

    def test_03_a_star_and_dijkstra_consistency(self):
        """Zero-heuristic A* should match Dijkstra's shortest distance."""
        graph = self.build_graph()

        a_star_result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )

        dijkstra_result = dijkstra(
            graph,
            0,
            3,
        )

        self.assertIsNotNone(a_star_result)
        self.assertIsNotNone(dijkstra_result)

        self.assertAlmostEqual(
            a_star_result.distance,
            dijkstra_result.distance,
        )

    def test_04_same_source_and_destination_a_star(self):
        """source == destination should return a zero-distance route."""
        graph = self.build_graph()

        result = a_star(
            graph,
            [],
            2,
            2,
            heuristic="zero",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [2])
        self.assertEqual(result.distance, 0.0)
        self.assertEqual(result.nodes_explored, 1)
        self.assertEqual(result.heap_operations, 0)

    def test_05_same_source_and_destination_dijkstra(self):
        """Dijkstra should also handle source == destination."""
        graph = self.build_graph()

        result = dijkstra(graph, 2, 2)

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [2])
        self.assertEqual(result.distance, 0.0)

    def test_06_invalid_source_a_star(self):
        """Unknown source nodes must raise ValueError."""
        graph = self.build_graph()

        with self.assertRaisesRegex(ValueError, "Unknown source node"):
            a_star(
                graph,
                [],
                999,
                3,
                heuristic="zero",
            )

    def test_07_invalid_destination_a_star(self):
        """Unknown destination nodes must raise ValueError."""
        graph = self.build_graph()

        with self.assertRaisesRegex(ValueError, "Unknown destination node"):
            a_star(
                graph,
                [],
                0,
                999,
                heuristic="zero",
            )

    def test_08_invalid_source_dijkstra(self):
        """Dijkstra must reject an unknown source."""
        graph = self.build_graph()

        with self.assertRaisesRegex(ValueError, "Unknown source node"):
            dijkstra(graph, 999, 3)

    def test_09_invalid_destination_dijkstra(self):
        """Dijkstra must reject an unknown destination."""
        graph = self.build_graph()

        with self.assertRaisesRegex(ValueError, "Unknown destination node"):
            dijkstra(graph, 0, 999)

    def test_10_disconnected_graph_returns_no_route(self):
        """Existing nodes with no connecting path should return None."""
        graph = Graph()

        graph.add_edge(0, 1, 4.0)
        graph.add_edge(2, 3, 6.0)

        a_star_result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )

        dijkstra_result = dijkstra(
            graph,
            0,
            3,
        )

        self.assertIsNone(a_star_result)
        self.assertIsNone(dijkstra_result)

    def test_11_single_edge_route(self):
        """A direct one-edge route should be calculated correctly."""
        graph = Graph()
        graph.add_edge(0, 1, 7.5)

        result = a_star(
            graph,
            [],
            0,
            1,
            heuristic="zero",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [0, 1])
        self.assertAlmostEqual(result.distance, 7.5)

    def test_12_shortest_path_is_selected(self):
        """The cheaper multi-edge path must beat a direct expensive edge."""
        graph = Graph()

        graph.add_edge(0, 1, 2.0)
        graph.add_edge(1, 3, 2.0)
        graph.add_edge(0, 3, 20.0)

        result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [0, 1, 3])
        self.assertAlmostEqual(result.distance, 4.0)

    def test_13_negative_edge_is_rejected(self):
        """Graph must reject negative edge weights."""
        graph = Graph()

        with self.assertRaisesRegex(ValueError, "non-negative"):
            graph.add_edge(0, 1, -1.0)

    def test_14_unknown_vertex_neighbors_are_rejected(self):
        """Requesting neighbors for an unknown node must fail clearly."""
        graph = Graph()

        with self.assertRaisesRegex(ValueError, "Unknown vertex"):
            graph.neighbors(999)

    def test_15_route_result_path_is_consistent(self):
        """Returned path must begin at source and end at destination."""
        graph = self.build_graph()

        result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.path[0], 0)
        self.assertEqual(result.path[-1], 3)
        self.assertGreaterEqual(len(result.path), 2)
        self.assertTrue(math.isfinite(result.distance))
        self.assertGreaterEqual(result.distance, 0.0)

    def test_16_invalid_heuristic_is_rejected(self):
        """Unsupported heuristic names must raise ValueError."""
        graph = self.build_graph()

        with self.assertRaisesRegex(ValueError, "Unknown heuristic"):
            a_star(
                graph,
                [],
                0,
                3,
                heuristic="invalid",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
