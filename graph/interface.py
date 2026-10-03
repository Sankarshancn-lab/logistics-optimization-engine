from abc import ABC, abstractmethod


class GraphInterface(ABC):

    @abstractmethod
    def neighbors(self, node: int) -> list[tuple[int, float]]:
        raise NotImplementedError

    @abstractmethod
    def has_node(self, node: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def nodes(self) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def edge_count(self) -> int:
        raise NotImplementedError
