import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from model_bakery import baker
from store.models import Product, Cart, CartItem, Order


User = get_user_model()


# FIXTURES:


@pytest.fixture
def cart():
    return baker.make(Cart)


@pytest.fixture
def product():
    return baker.make(Product)


@pytest.fixture
def add_cart_item(api_client, cart):

    def add(data):
        return api_client.post(path=f"/store/carts/{cart.id}/items/", data=data)

    return add


# ----------------------------------------------------------------------


# TESTS:


@pytest.mark.django_db
class TestAddCartItem:

    def test_new_product_returns_201(self, add_cart_item, product):

        response = add_cart_item(data={"product": product.id, "quantity": 2})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantity"] == 2

    def test_same_product_again_increments_quantity(
        self, add_cart_item, cart, product
    ):

        add_cart_item(data={"product": product.id, "quantity": 2})
        response = add_cart_item(data={"product": product.id, "quantity": 3})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantity"] == 5
        # And it's still a single row (no `unique_together` violation):
        assert CartItem.objects.filter(cart=cart, product=product).count() == 1

    def test_stale_cart_id_returns_400(self, api_client, cart, product):

        cart.delete()

        response = api_client.post(
            path=f"/store/carts/{cart.id}/items/",
            data={"product": product.id, "quantity": 1},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCreateOrder:

    def create_order(self, api_client, cart_id):
        return api_client.post(path="/store/orders/", data={"cart_id": cart_id})

    def test_anonymous_user_returns_401(self, api_client, cart):

        response = self.create_order(api_client, cart.id)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_cart_returns_201_and_deletes_cart(
        self, api_client, cart, product
    ):

        item = CartItem.objects.create(cart=cart, product=product, quantity=3)
        api_client.force_authenticate(user=baker.make(User))

        response = self.create_order(api_client, cart.id)

        assert response.status_code == status.HTTP_201_CREATED
        (order_item,) = response.data["orderitem_set"]
        assert order_item["quantity"] == item.quantity
        assert order_item["unit_price"] == product.unit_price
        # The cart is consumed by the order:
        assert not Cart.objects.filter(pk=cart.id).exists()

    def test_same_cart_again_returns_400(self, api_client, cart, product):

        CartItem.objects.create(cart=cart, product=product, quantity=1)
        api_client.force_authenticate(user=baker.make(User))

        first = self.create_order(api_client, cart.id)
        second = self.create_order(api_client, cart.id)  # double-submit

        assert first.status_code == status.HTTP_201_CREATED
        assert second.status_code == status.HTTP_400_BAD_REQUEST
        assert Order.objects.count() == 1

    def test_empty_cart_returns_400(self, api_client, cart):

        api_client.force_authenticate(user=baker.make(User))

        response = self.create_order(api_client, cart.id)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
