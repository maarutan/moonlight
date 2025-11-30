from typing import TypeVar

T = TypeVar("T")


def singletonclass(cls: type[T]) -> T:
    """Decorator to make a class a singleton"""
    return cls()
