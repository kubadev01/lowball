from dataclasses import dataclass


@dataclass(frozen=True)
class PriceInfo:
    final: int
    initial: int
    discount_percent: int
    currency: str
