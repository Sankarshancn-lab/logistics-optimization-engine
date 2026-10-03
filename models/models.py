from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class Location:
    id: int
    x: float
    y: float


@dataclass(slots=True, frozen=True)
class Road:
    source: int
    destination: int
    distance: float
    travel_time: float


@dataclass(slots=True, frozen=True)
class PathResult:
    path: list[int]
    distance: float