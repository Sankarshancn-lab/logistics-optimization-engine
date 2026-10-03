from typing import Optional

class MinHeap:

    def __init__(self) -> None:
        self.heap: list[tuple[float, int]] = []

    def __len__(self) -> int:
        return len(self.heap)

    def is_empty(self) -> bool:
        return not self.heap

    def peek(self) -> Optional[tuple[float, int]]:
        return self.heap[0] if self.heap else None

    def push(self, item: tuple[float, int]) -> None:
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)

    def pop(self) -> Optional[tuple[float, int]]:
        if not self.heap:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        minimum = self.heap[0]
        self.heap[0] = self.heap.pop()

        self._sift_down(0)

        return minimum

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2

            if self.heap[parent] <= self.heap[index]:
                break

            self.heap[parent], self.heap[index] = (
                self.heap[index],
                self.heap[parent]
            )

            index = parent

    def _sift_down(self, index: int) -> None:
        size = len(self.heap)

        while True:
            left = 2 * index + 1
            right = left + 1
            smallest = index

            if (
                left < size
                and self.heap[left] < self.heap[smallest]
            ):
                smallest = left

            if (
                right < size
                and self.heap[right] < self.heap[smallest]
            ):
                smallest = right

            if smallest == index:
                break

            self.heap[index], self.heap[smallest] = (
                self.heap[smallest],
                self.heap[index]
            )

            index = smallest