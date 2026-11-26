import pytest

from tracker.models import PriceInfo
from tracker.stores.base import Store


def test_store_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Store()


def test_subclass_without_fetch_price_cannot_be_instantiated():
    class Subclass(Store):
        pass

    with pytest.raises(TypeError):
        Subclass()


def test_subclass_with_fetch_price_works():
    test_product = PriceInfo(
        final=1999, initial=1999, discount_percent=0, currency="USD"
    )

    class Subclass(Store):
        def fetch_price(self, product_id: str) -> PriceInfo | None:
            return test_product

    test_store = Subclass()

    info = test_store.fetch_price("example id")
    assert info == test_product
