from rest_framework import serializers
from .models import Product, Collection
from decimal import Decimal


class CollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = ["id", "title", "product_count"]

    product_count = serializers.IntegerField()

    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "inventory",
            "unit_price",
            "price_plus_tax",
            "collection",
        ]

    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # price = serializers.DecimalField(
    #     max_digits=6, decimal_places=2, source="unit_price"
    # )

    price_plus_tax = serializers.SerializerMethodField(method_name="get_price_plus_tax")

    def get_price_plus_tax(self, product: Product):
        return round(product.unit_price * Decimal(1.1), 2)

    # - To see collection id of each product:
    # collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
    # - To see collection title:
    # collection = serializers.StringRelatedField()
    #   + `select_related` in view, else N+1 query problem
    # - To see whole collection object:
    #   Define `CollectionSerializer` and use:
    # collection = CollectionSerializer()
    # - To see link to collection endpoint:
    collection = serializers.HyperlinkedRelatedField(
        view_name="collection-detail", queryset=Collection.objects.all()
    )
    # Three things required to make this work:
    # 1. "AssertionError at /store/products/: `HyperlinkedRelatedField` requires the request in the serializer context. Add `context={'request': request}` when instantiating the serializer."
    # 2. `name="collection-detail"` in `urls.urlpatterns.path()`
    # 3. "collections/<int:pk>/" in `urls.urlpatterns.path()` instead of  "collections/<int:id>/", this is DRF's default convention.
