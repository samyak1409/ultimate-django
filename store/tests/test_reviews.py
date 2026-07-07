import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from model_bakery import baker
from store.models import Product, Review


User = get_user_model()
# (Not using `baker.make(Customer)`: baker would create the related user, whose
# `post_save` signal already creates a `Customer`, and then baker's own `Customer`
# insert would violate the one-to-one constraint. So we make users and use the
# signal-created `user.customer` instead.)


# FIXTURES:


@pytest.fixture
def product():
    return baker.make(Product)


@pytest.fixture
def create_review(api_client, product):

    def create(data):
        return api_client.post(
            path=f"/store/products/{product.id}/reviews/", data=data
        )

    return create


# ----------------------------------------------------------------------


# TESTS:


@pytest.mark.django_db
class TestCreateReview:

    def test_anonymous_user_returns_401(self, create_review):

        response = create_review(data={"text": "Nice!"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_returns_201_with_self_as_author(
        self, api_client, create_review
    ):

        user = baker.make(User)
        api_client.force_authenticate(user=user)

        response = create_review(data={"text": "Nice!"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["customer"] == user.customer.id

    def test_customer_in_payload_is_ignored(self, api_client, create_review):

        user, other_user = baker.make(User), baker.make(User)
        api_client.force_authenticate(user=user)

        # Trying to post a review as someone else:
        response = create_review(
            data={"text": "Nice!", "customer": other_user.customer.id}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["customer"] == user.customer.id


@pytest.mark.django_db
class TestReadReview:

    def test_anonymous_user_can_list_returns_200(self, api_client, product):

        author = baker.make(User)
        review = Review.objects.create(
            product=product, customer=author.customer, text="Nice!"
        )

        response = api_client.get(path=f"/store/products/{product.id}/reviews/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["id"] == review.id


@pytest.mark.django_db
class TestDeleteReview:

    @pytest.fixture
    def review(self, product):
        author = baker.make(User)
        return Review.objects.create(
            product=product, customer=author.customer, text="Nice!"
        )

    def delete(self, api_client, review):
        return api_client.delete(
            path=f"/store/products/{review.product_id}/reviews/{review.id}/"
        )

    def test_non_author_returns_403(self, api_client, review):

        api_client.force_authenticate(user=baker.make(User))

        response = self.delete(api_client, review)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_author_returns_204(self, api_client, review):

        api_client.force_authenticate(user=review.customer.user)

        response = self.delete(api_client, review)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_staff_returns_204(self, api_client, review):

        api_client.force_authenticate(user=baker.make(User, is_staff=True))

        response = self.delete(api_client, review)

        assert response.status_code == status.HTTP_204_NO_CONTENT
