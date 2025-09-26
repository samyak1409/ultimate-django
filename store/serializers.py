from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import (
    Product,
    Collection,
    Review,
    Cart,
    CartItem,
    Customer,
    Order,
    OrderItem,
    ProductImage,
)
from .signals import order_created


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


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ["id", "image"]
        # not including "product" since it's already in the url (/products/1/images/)

    # Overriding to get the product (using product id from url), and attach (since it's a related field) to the image:
    def create(self, validated_data):
        return ProductImage.objects.create(
            product_id=self.context["product_id"], **validated_data
        )


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
            "productimage_set",
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
    # - To see collection's str repr (`__str__()`):
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

    productimage_set = ProductImageSerializer(many=True, read_only=True)


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        exclude = ["product"]

    # Overriding to get the product (using product id from url), and attach (since it's a related field) to the review:
    def create(self, validated_data):
        # return Review.objects.create(
        #     product_id=self.context["product_id"], **validated_data
        # )
        # Mosh taught above, but we should instead do following:
        # (Read MD notes of `Advanced API Concepts > Nested Routers`.)
        return super().create(
            validated_data | {"product_id": self.context["product_id"]}
        )


class SimpleProductSerializer(serializers.ModelSerializer):
    """Defined to show lesser `Product` fields in `CartItemSerializer`, `OrderItemSerializer`, etc. when using whole object as a field: `product = SimpleProductSerializer()`"""

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


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "phone", "birth_date", "membership"]


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "unit_price"]

    product = SimpleProductSerializer()


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ["id", "placed_at", "payment_status", "customer", "orderitem_set"]
        read_only_fields = ["placed_at", "customer"]
        # `read_only_fields` not working at all, neither `read_only=True` below.
        # Read in: Notes > Part 2 > 6. Designing and Building the Orders API > Updating an Order

    orderitem_set = OrderItemSerializer(many=True, read_only=True)


class CreateOrderSerializer(serializers.Serializer):

    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError("No cart with given cart id.")
        if not CartItem.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError("Cart is empty.")
        return cart_id

    def save(self, **kwargs):

        with transaction.atomic():
            # Create order:
            customer = Customer.objects.only("id").get(user_id=self.context["user_id"])
            order = Order.objects.create(customer_id=customer.id)

            # Create order items:
            cart_id = self.validated_data["cart_id"]
            cart_items = CartItem.objects.select_related("product").filter(
                cart_id=cart_id
            )
            order_items = [
                OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.unit_price,
                )
                for cart_item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            # Delete cart:
            Cart.objects.get(id=cart_id).delete()

            # Custom signal:
            order_created.send_robust(sender=self.__class__, order=order)

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ["payment_status"]
