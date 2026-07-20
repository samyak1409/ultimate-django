import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from model_bakery import baker


User = get_user_model()

ME_URL = "/store/customers/me/"


@pytest.mark.django_db
class TestCustomerMe:

    def test_anonymous_user_returns_401(self, api_client):

        response = api_client.get(path=ME_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_put_updates_own_profile(self, api_client):

        api_client.force_authenticate(user=baker.make(User))

        response = api_client.put(path=ME_URL, data={"phone": "1234567890"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["phone"] == "1234567890"

    def test_membership_in_payload_is_ignored(self, api_client):

        user = baker.make(User)
        api_client.force_authenticate(user=user)

        # Trying to self-upgrade from the default Bronze to Gold:
        response = api_client.put(
            path=ME_URL, data={"phone": "1234567890", "membership": "G"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["membership"] == "B"
        user.customer.refresh_from_db()
        assert user.customer.membership == "B"
