"""
M33.8 - API Hardening & Contract Tests

Validates the existing FastAPI layer without changing production code.
The suite deliberately exercises the real API module and routing service.

Run from:
    C:\\Users\\Asus\\src

Command:
    python -m unittest logistics_engine.tests.test_api_hardening -v
"""

import asyncio
import unittest
from types import SimpleNamespace


class TestAPIHardening(unittest.TestCase):
    """M33.8 API contract, validation, and failure-handling checks."""

    @staticmethod
    def dataset():
        """Return a minimal dependency-injection dataset."""
        locations = list(range(4))
        roads = [
            SimpleNamespace(source=0, destination=1, distance=2.0, travel_time=3.0),
            SimpleNamespace(source=1, destination=2, distance=3.0, travel_time=4.0),
            SimpleNamespace(source=2, destination=3, distance=4.0, travel_time=5.0),
        ]
        return SimpleNamespace(locations=locations, roads=roads)

    def setUp(self):
        from logistics_engine.api.app import api_app, get_routing_data

        self.api_app = api_app
        self.get_routing_data = get_routing_data
        self.api_app.dependency_overrides[self.get_routing_data] = self.dataset

    def tearDown(self):
        self.api_app.dependency_overrides.clear()

    def test_01_api_app_is_fastapi_application(self):
        """The API object exposes the FastAPI application contract."""
        from fastapi import FastAPI

        self.assertIsInstance(self.api_app, FastAPI)

    def test_02_route_endpoint_is_registered(self):
        """POST /route must be registered in the application."""
        route_paths = {
            (route.path, tuple(sorted(route.methods or [])))
            for route in self.api_app.routes
            if hasattr(route, "methods")
        }

        self.assertTrue(
            any(path == "/route" and "POST" in methods for path, methods in route_paths)
        )

    def test_03_request_schema_rejects_missing_fields(self):
        """RouteRequest requires both source and destination."""
        from pydantic import ValidationError
        from logistics_engine.api.app import RouteRequest

        with self.assertRaises(ValidationError):
            RouteRequest()

    def test_04_request_schema_accepts_integer_nodes(self):
        """Valid integer source/destination values are accepted."""
        from logistics_engine.api.app import RouteRequest

        request = RouteRequest(source=0, destination=3)

        self.assertEqual(request.source, 0)
        self.assertEqual(request.destination, 3)

    def test_05_invalid_source_returns_http_400(self):
        """An out-of-range source is rejected with HTTP 400."""
        from fastapi import HTTPException
        from logistics_engine.api.app import RouteRequest, calculate_route_for_data

        with self.assertRaises(HTTPException) as context:
            calculate_route_for_data(
                RouteRequest(source=99, destination=3),
                self.dataset().locations,
                self.dataset().roads,
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_06_invalid_destination_returns_http_400(self):
        """An out-of-range destination is rejected with HTTP 400."""
        from fastapi import HTTPException
        from logistics_engine.api.app import RouteRequest, calculate_route_for_data

        with self.assertRaises(HTTPException) as context:
            calculate_route_for_data(
                RouteRequest(source=0, destination=99),
                self.dataset().locations,
                self.dataset().roads,
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_07_graph_builder_creates_expected_routing_nodes(self):
        """API graph construction produces the nodes required by routing."""
        from logistics_engine.api.app import create_route_graph

        graph = create_route_graph(self.dataset().roads)
        nodes = graph.nodes()

        self.assertEqual(set(nodes), {0, 1, 2, 3})
        self.assertIn((1, 2.0), graph.adjacency_list[0])
        self.assertIn((0, 2.0), graph.adjacency_list[1])

    def test_08_direct_route_service_returns_successful_result(self):
        """A valid route request must return a route response rather than crash."""
        from logistics_engine.api.app import RouteRequest, calculate_route_for_data

        dataset = self.dataset()
        response = calculate_route_for_data(
            RouteRequest(source=0, destination=3),
            dataset.locations,
            dataset.roads,
        )

        self.assertIsNotNone(response)
        self.assertEqual(response.path[0], 0)
        self.assertEqual(response.path[-1], 3)
        self.assertGreaterEqual(float(response.distance), 0.0)
        self.assertGreaterEqual(int(response.nodes_explored), 0)
        self.assertGreaterEqual(int(response.heap_operations), 0)

    def test_09_asgi_route_endpoint_returns_json_contract(self):
        """The real ASGI endpoint returns JSON for a valid request."""
        import httpx

        async def call_endpoint():
            transport = httpx.ASGITransport(app=self.api_app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                return await client.post(
                    "/route",
                    json={"source": 0, "destination": 3},
                )

        response = asyncio.run(call_endpoint())

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("path", payload)
        self.assertIn("distance", payload)
        self.assertIn("nodes_explored", payload)
        self.assertIn("heap_operations", payload)

    def test_10_asgi_invalid_request_is_client_error(self):
        """Invalid route nodes must not become server errors."""
        import httpx

        async def call_endpoint():
            transport = httpx.ASGITransport(app=self.api_app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                return await client.post(
                    "/route",
                    json={"source": 999, "destination": 3},
                )

        response = asyncio.run(call_endpoint())

        self.assertGreaterEqual(response.status_code, 400)
        self.assertLess(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
