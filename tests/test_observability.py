"""
M33.7 - Observability & Operational Diagnostics

Validates the diagnostic information already exposed by the routing engine.
This suite does not modify production routing algorithms or import Streamlit.

Run from:
    C:\\Users\\Asus\\src

Command:
    python -m unittest logistics_engine.tests.test_observability -v
"""

import math
import time
import unittest


class TestObservability(unittest.TestCase):
    """M33.7 operational diagnostics checks."""

    @staticmethod
    def build_graph():
        from logistics_engine.graph import Graph

        graph = Graph()
        graph.add_edge(0, 1, 5.0, bidirectional=True)
        graph.add_edge(1, 2, 3.0, bidirectional=True)
        graph.add_edge(0, 2, 20.0, bidirectional=True)
        graph.add_edge(2, 3, 2.0, bidirectional=True)
        graph.add_edge(1, 3, 15.0, bidirectional=True)
        return graph

    def test_01_successful_route_exposes_operational_metrics(self):
        """A successful route exposes the metrics used by the dashboard."""
        from logistics_engine.routing import a_star

        graph = self.build_graph()
        locations = list(range(4))

        start = time.perf_counter()
        result = a_star(
            graph,
            locations,
            0,
            3,
            heuristic="zero",
        )
        elapsed = time.perf_counter() - start

        self.assertIsNotNone(result)
        self.assertEqual(result.path, [0, 1, 2, 3])
        self.assertAlmostEqual(result.distance, 10.0)
        self.assertGreaterEqual(result.nodes_explored, 1)
        self.assertGreaterEqual(result.heap_operations, 0)
        self.assertGreaterEqual(elapsed, 0.0)
        self.assertTrue(math.isfinite(elapsed))

    def test_02_dijkstra_and_a_star_diagnostics_are_consistent(self):
        """Equivalent routing runs expose consistent distance diagnostics."""
        from logistics_engine.routing import a_star, dijkstra

        graph = self.build_graph()
        locations = list(range(4))

        a_result = a_star(
            graph,
            locations,
            0,
            3,
            heuristic="zero",
        )
        d_result = dijkstra(graph, 0, 3)

        self.assertIsNotNone(a_result)
        self.assertIsNotNone(d_result)
        self.assertAlmostEqual(a_result.distance, d_result.distance)
        self.assertEqual(a_result.path, d_result.path)

    def test_03_no_route_is_diagnosable_without_invalid_result_metrics(self):
        """A disconnected graph returns None rather than a fabricated route."""
        from logistics_engine.graph import Graph
        from logistics_engine.routing import a_star, dijkstra

        graph = Graph()
        graph.add_edge(0, 1, 4.0, bidirectional=True)
        graph.add_edge(2, 3, 6.0, bidirectional=True)

        a_result = a_star(
            graph,
            [],
            0,
            3,
            heuristic="zero",
        )
        d_result = dijkstra(graph, 0, 3)

        self.assertIsNone(a_result)
        self.assertIsNone(d_result)

    def test_04_invalid_inputs_produce_clear_exceptions(self):
        """Invalid nodes produce explicit ValueError diagnostics."""
        from logistics_engine.routing import a_star, dijkstra

        graph = self.build_graph()

        with self.assertRaisesRegex(ValueError, "Unknown source node"):
            a_star(graph, [], 999, 3, heuristic="zero")

        with self.assertRaisesRegex(ValueError, "Unknown destination node"):
            a_star(graph, [], 0, 999, heuristic="zero")

        with self.assertRaisesRegex(ValueError, "Unknown source node"):
            dijkstra(graph, 999, 3)

        with self.assertRaisesRegex(ValueError, "Unknown destination node"):
            dijkstra(graph, 0, 999)

    def test_05_same_node_route_has_meaningful_zero_cost_diagnostics(self):
        """A source equal to destination produces a valid zero-distance result."""
        from logistics_engine.routing import a_star, dijkstra

        graph = self.build_graph()

        a_result = a_star(graph, [], 2, 2, heuristic="zero")
        d_result = dijkstra(graph, 2, 2)

        self.assertIsNotNone(a_result)
        self.assertIsNotNone(d_result)
        self.assertEqual(a_result.path, [2])
        self.assertEqual(d_result.path, [2])
        self.assertEqual(a_result.distance, 0.0)
        self.assertEqual(d_result.distance, 0.0)
        self.assertGreaterEqual(a_result.nodes_explored, 1)
        self.assertGreaterEqual(a_result.heap_operations, 0)

    def test_06_repeated_operations_produce_stable_diagnostics(self):
        """Repeated identical queries keep route diagnostics consistent."""
        from logistics_engine.routing import a_star

        graph = self.build_graph()
        locations = list(range(4))
        observations = []

        for _ in range(10):
            result = a_star(
                graph,
                locations,
                0,
                3,
                heuristic="zero",
            )
            self.assertIsNotNone(result)
            observations.append(
                (result.path, result.distance, result.nodes_explored, result.heap_operations)
            )

        first = observations[0]
        self.assertTrue(all(observation == first for observation in observations))

    def test_07_diagnostic_metrics_are_finite_and_non_negative(self):
        """Operational counters never expose invalid numeric values."""
        from logistics_engine.routing import a_star

        graph = self.build_graph()
        result = a_star(graph, list(range(4)), 0, 3, heuristic="zero")

        self.assertIsNotNone(result)

        metrics = {
            "distance": result.distance,
            "nodes_explored": result.nodes_explored,
            "heap_operations": result.heap_operations,
        }

        for name, value in metrics.items():
            numeric = float(value)
            self.assertTrue(math.isfinite(numeric), msg=f"{name} is not finite")
            self.assertGreaterEqual(numeric, 0.0, msg=f"{name} is negative")

    def test_08_diagnostics_do_not_depend_on_global_state_between_graphs(self):
        """Separate graph instances produce independent routing diagnostics."""
        from logistics_engine.graph import Graph
        from logistics_engine.routing import a_star

        graph_a = Graph()
        graph_a.add_edge(0, 1, 2.0, bidirectional=True)

        graph_b = Graph()
        graph_b.add_edge(10, 11, 7.0, bidirectional=True)

        result_a = a_star(graph_a, [0, 1], 0, 1, heuristic="zero")
        result_b = a_star(graph_b, list(range(12)), 10, 11, heuristic="zero")

        self.assertIsNotNone(result_a)
        self.assertIsNotNone(result_b)
        self.assertEqual(result_a.path, [0, 1])
        self.assertEqual(result_b.path, [10, 11])
        self.assertAlmostEqual(result_a.distance, 2.0)
        self.assertAlmostEqual(result_b.distance, 7.0)


if __name__ == "__main__":
    unittest.main()
