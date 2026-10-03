"""Database-backed data services for the logistics dashboard."""

from dataclasses import dataclass

from logistics_engine.database import (
    SessionLocal,
    LocationDB,
    RoadDB,
    RouteDB,
    OptimizationResultDB,
)


@dataclass(frozen=True)
class DashboardData:
    locations: list
    roads: list
    routes: list
    optimization_results: list


def load_dashboard_data() -> DashboardData:
    """Load dashboard data from the production database."""

    session = SessionLocal()

    try:
        locations = session.query(LocationDB).all()
        roads = session.query(RoadDB).all()
        routes = session.query(RouteDB).all()
        optimization_results = (
            session.query(OptimizationResultDB).all()
        )

        return DashboardData(
            locations=locations,
            roads=roads,
            routes=routes,
            optimization_results=optimization_results,
        )

    finally:
        session.close()
