from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from logistics_engine.database.connection import Base


class LocationDB(Base):

    __tablename__ = "locations"

    id = Column(
        Integer,
        primary_key=True
    )

    x = Column(
        Float,
        nullable=False
    )

    y = Column(
        Float,
        nullable=False
    )


class RoadDB(Base):

    __tablename__ = "roads"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    source = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False
    )

    destination = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False
    )

    distance = Column(
        Float,
        nullable=False
    )

    travel_time = Column(
        Float,
        nullable=False
    )


class CustomerDB(Base):

    __tablename__ = "customers"

    id = Column(
        Integer,
        primary_key=True
    )

    location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False
    )

    demand = Column(
        Float,
        nullable=False
    )

    ready_time = Column(
        Float,
        nullable=False
    )

    due_time = Column(
        Float,
        nullable=False
    )

    service_time = Column(
        Float,
        nullable=False
    )


class VehicleDB(Base):

    __tablename__ = "vehicles"

    id = Column(
        Integer,
        primary_key=True
    )

    capacity = Column(
        Float,
        nullable=False
    )


class RouteDB(Base):

    __tablename__ = "routes"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    source = Column(
        Integer,
        nullable=False
    )

    destination = Column(
        Integer,
        nullable=False
    )

    distance = Column(
        Float,
        nullable=False
    )

    path = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class OptimizationResultDB(Base):

    __tablename__ = "optimization_results"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    algorithm = Column(
        String(100),
        nullable=False
    )

    objective_value = Column(
        Float,
        nullable=False
    )

    runtime_seconds = Column(
        Float,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
