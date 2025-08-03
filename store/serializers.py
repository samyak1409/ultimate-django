from rest_framework import serializers
from .models import Product, Collection, Review, Cart, CartItem
from decimal import Decimal


class CollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = ["id", "title", "product_count"]
        # read_only_fields = ["product_count"]
        # If I remove `read_only=True` and instead use this, it's not working.
        # https://www.django-rest-framework.org/api-guide/serializers/#specifying-read-only-fields
        # Can't find the reason in the above link as well, but what's happening is, if a new field is defined here in the serializer,
        # or if an actual DB field is re-defined here in the serializer, then only `read_only` param would work.

    # Since `product_count` is not a DB field:
    product_count = serializers.IntegerField(read_only=True)
    # `read_only=True`: Restrict adding/changing while `POST`/`PUT`/`PATCH`.

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


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        exclude = ["product"]

    # Overriding to get the product (using product id from url), and attach (since it's a related field) to the review:
    def create(self, validated_data):
        return Review.objects.create(
            product_id=self.context["product_id"], **validated_data
        )


class SimpleProductSerializer(serializers.ModelSerializer):
    """Defined to show lesser `Product` fields in `CartItemSerializer` when using whole object as a field: `product = SimpleProductSerializer()`"""

    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]

    # product = SimpleProductSerializer()

    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, item: CartItem):
        return item.product.unit_price * item.quantity

    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        try:
            # 1. Attempt to get the existing item
            item = CartItem.objects.get(
                cart_id=cart_id, product=self.validated_data["product"]
            )
            # 2. If it exists, MANUALLY update its fields and save it
            item.quantity += self.validated_data["quantity"]
            item.save()
            self.instance = item  # Set self.instance to the updated object
        except CartItem.DoesNotExist:
            # 3. If it doesn't exist, let the default behavior create a new one
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ["quantity"]


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ["id", "cartitem_set", "total_value"]
        read_only_fields = ["id"]

    cartitem_set = CartItemSerializer(many=True, read_only=True)

    total_value = serializers.SerializerMethodField(method_name="get_total_value")

    def get_total_value(self, cart: Cart):
        return sum(
            item.product.unit_price * item.quantity for item in cart.cartitem_set.all()
        )
