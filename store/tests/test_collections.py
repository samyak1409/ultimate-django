import pytest
from rest_framework import status
from store.models import Collection
from model_bakery import baker


# FIXTURES:
@pytest.fixture
def create_collection(api_client):

    def create(title):
        return api_client.post(path="/store/collections/", data={"title": title})

    return create


# TESTS:
@pytest.mark.django_db
class TestCreateCollection:

    def test_if_user_is_anonymous_returns_401(self, create_collection):

        # Arrange

        # Act
        response = create_collection(title="X")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, create_collection):

        authenticate()

        response = create_collection(title="X")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, create_collection):

        authenticate(is_staff=True)

        response = create_collection(title="")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.data

    def test_if_data_is_valid_returns_201(self, authenticate, create_collection):

        authenticate(is_staff=True)

        response = create_collection(title="X")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


@pytest.mark.django_db
class TestRetrieveCollection:

    def test_if_collection_does_not_exists_returns_404(self, api_client):

        response = api_client.get(path=f"/store/collections/1/")
        # any id would work since in the test db, no id would be present
        # (if none is created through custom migration)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_collection_exists_returns_200(self, api_client):

        # collection = Collection.objects.create(title="X")
        # Using model-bakery:
        collection = baker.make(Collection)

        response = api_client.get(path=f"/store/collections/{collection.id}/")
        print(response.data)  # only prints when test fails

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": collection.id,
            "title": collection.title,
            "product_count": 0,
        }
