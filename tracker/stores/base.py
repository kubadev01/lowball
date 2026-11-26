from abc import ABC, abstractmethod

from tracker.models import PriceInfo


class ProductNotFoundError(Exception):
    """Store has no product with the given ID."""


class Store(ABC):
    @abstractmethod
    def fetch_price(self, product_id: str) -> PriceInfo | None:
        """Fetch the current price of the product.

        Returns the current and initial price of the product, discount and currency
        or None if the product is free.

        This method raises ProductNotFoundError if the product wasn't found.
        """
