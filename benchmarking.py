from dataclasses import dataclass
from statistics import mean, stdev
from time import perf_counter


@dataclass(frozen=True)
class BenchmarkResult:
    algorithm: str
    trials: int
    mean_seconds: float
    std_seconds: float
    min_seconds: float
    max_seconds: float


def benchmark_function(
    func,
    trials: int = 10,
    warmup: int = 2,
) -> tuple[list[float], BenchmarkResult]:

    if trials < 1:
        raise ValueError("trials must be at least 1")

    if warmup < 0:
        raise ValueError("warmup cannot be negative")

    for _ in range(warmup):
        func()

    timings = []

    for _ in range(trials):

        start = perf_counter()

        func()

        elapsed = perf_counter() - start

        timings.append(elapsed)

    std_seconds = (
        stdev(timings)
        if len(timings) > 1
        else 0.0
    )

    result = BenchmarkResult(
        algorithm=getattr(
            func,
            "__name__",
            "anonymous",
        ),
        trials=trials,
        mean_seconds=mean(timings),
        std_seconds=std_seconds,
        min_seconds=min(timings),
        max_seconds=max(timings),
    )

    return timings, result
