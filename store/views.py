from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.decorators import api_view, action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework import permissions
from .models import (
    Product,
    Collection,
    OrderItem,
    Review,
    Cart,
    CartItem,
    Customer,
    Order,
    ProductImage,
)
from .serializers import (
    ProductSerializer,
    CollectionSerializer,
    ReviewSerializer,
    CartSerializer,
    CartItemSerializer,
    UpdateCartItemSerializer,
    CustomerSerializer,
    OrderSerializer,
    CreateOrderSerializer,
    UpdateOrderSerializer,
    ProductImageSerializer,
)
from .filters import ProductFilter
from . import permissions as custom_permissions


# (Without DRF) Function-based View:
# def product_list(request: HttpRequest) -> HttpResponse:
#     return HttpResponse("OK")


# Function-based View:
@api_view(["GET", "POST"])
def product_list(request: Request) -> Response:

    # return Response("OK")

    if request.method == "GET":

        products = Product.objects.prefetch_related("productimage_set")
        # get the queryset

        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )  # convert queryset to list of dicts, returns a serializer obj
        print(type(serializer.data))  # <class 'ReturnList'>
        print(len(serializer.data))  # 1000 (when 1000 products are there)
        print(serializer.data[0])  # {'id': 1, 'title': 'Bread Ww Cluster', ...}

        return Response(serializer.data)  # `.data` gives us the list of dicts

    else:  # if request.method == "POST":

        print(request.data)  # the exact data json sent in the body
        # {'title': 'YO', 'inventory': 1, 'unit_price': 1, 'collection': 1}
        print(type(request.data))  # <class 'dict'>
        serializer = ProductSerializer(data=request.data, context={"request": request})
        print(serializer.initial_data)  # same as `request.data`

        # if serializer.is_valid():
        #     print(serializer.validated_data)
        #     print(type(serializer.validated_data))  # <class 'dict'>
        #     return Response("OK")
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        # {'title': 'YO', 'inventory': 1, 'unit_price': Decimal('1.00'), 'collection': <Collection: Test>}

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Class-based View:
# class ProductList(APIView):

#     def get(self, request):
#         products = Product.objects.prefetch_related("productimage_set")
#         serializer = ProductSerializer(
#             products, many=True, context={"request": request}
#         )
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = ProductSerializer(data=request.data, context={"request": request})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# Generic View:
class ProductList(ListCreateAPIView):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Or we can use methods instead of above if we've some more logic or anything other than just a simple expression:
    # def get_queryset(self):
    #     return Product.objects.all()
    # def get_serializer_class(self):
    #     return ProductSerializer


# Function-based View:
@api_view(["GET", "PUT", "DELETE"])
def product_detail(request, pk: int):

    # return Response(pk)

    # try:
    #     product = Product.objects.get(pk=pk)  # get the object
    # except Product.DoesNotExist:  # when product with id `pk` does not exist
    #     # We can just:
    #     # return Response(status=404)
    #     # But, we should:
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    # Above 4 SLOCs are same as this line:
    product = get_object_or_404(Product, pk=pk)

    if request.method == "GET":

        serializer = ProductSerializer(product, context={"request": request})
        # convert object to dict, returns a serializer obj
        print(serializer.data)  # {'id': 1, 'title': 'Bread Ww Cluster', ...}
        print(type(serializer.data))  # <class 'ReturnDict'>

        return Response(serializer.data)  # `.data` gives us the dict

    elif request.method == "PUT":

        serializer = ProductSerializer(
            instance=product, data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

    else:  # if request.method == "DELETE":

        # `ProtectedError`: protected foreign keys
        if product.orderitem_set.exists():
            return Response(
                {
                    "error": "Product cannot be deleted as it is associated with an order item."
                },
                status=status.HTTP_409_CONFLICT,
            )

        product.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# # Class-based View:
# class ProductDetail(APIView):

#     def get(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product, context={"request": request})
#         return Response(serializer.data)

#     def put(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(
#             instance=product, data=request.data, context={"request": request}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitem_set.exists():
#             return Response(
#                 {
#                     "error": "Product cannot be deleted as it is associated with an order item."
#                 },
#                 status=status.HTTP_409_CONFLICT,
#             )
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# Generic View:
class ProductDetail(RetrieveUpdateDestroyAPIView):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def delete(self, request, *args, **kwargs):

        # Custom logic:
        if OrderItem.objects.filter(product_id=kwargs["pk"]).exists():
            return Response(
                {
                    "error": "Product cannot be deleted as it is associated with one or more order items."
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Now delete:
        # product.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)
        # Mosh did above but we should instead just call parent's `delete` now to delete
        # (see the definition in `RetrieveUpdateDestroyAPIView`, `DestroyModelMixin`):
        return super().delete(request, *args, **kwargs)


# ViewSet:
class ProductViewSet(ModelViewSet):

    queryset = Product.objects.prefetch_related("productimage_set")
    serializer_class = ProductSerializer

    # For applying filtering functionality (manually):
    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-query-parameters
    # def get_queryset(self):
    #     collection_id = self.request.query_params.get("collection_id")
    #     if collection_id is not None:
    #         return Product.objects.filter(collection_id=collection_id)
    #     return Product.objects.all()
    # Using `django_filters.rest_framework.DjangoFilterBackend`, we just need to set:
    # filterset_fields = ["collection_id", "unit_price"]
    # Advanced filtering (check `ProductFilter`):
    filterset_class = ProductFilter

    search_fields = ["title"]

    ordering_fields = ["unit_price", "last_update"]

    permission_classes = [custom_permissions.IsAdminOrReadOnly]

    def destroy(self, request, pk):
        if OrderItem.objects.filter(product_id=pk).exists():
            return Response(
                {
                    "error": "Product cannot be deleted as it is associated with one or more order items."
                },
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, pk)


# Function-based View:
@api_view(["GET", "POST"])
def collection_list(request: Request) -> Response:

    if request.method == "GET":

        collections = Collection.objects.annotate(product_count=Count("product"))
        # Why `product` and not `product_set`?
        # https://github.com/samyak1409/ultimate-django/blob/main/Notes/Part%201/4.%20Django%20ORM.md#grouping-data
        serializer = CollectionSerializer(collections, many=True)
        return Response(serializer.data)

    else:  # if request.method == "POST":

        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Generic View:
class CollectionList(ListCreateAPIView):

    queryset = Collection.objects.annotate(product_count=Count("product"))
    serializer_class = CollectionSerializer


# Function-based View:
@api_view(["GET", "PUT", "DELETE"])
def collection_detail(request, pk: int):

    collection = get_object_or_404(
        Collection.objects.annotate(product_count=Count("product")), pk=pk
    )

    if request.method == "GET":

        serializer = CollectionSerializer(collection)
        return Response(serializer.data)

    elif request.method == "PUT":

        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    else:  # if request.method == "DELETE":

        if collection.product_set.exists():
            return Response(
                {
                    "error": "Collection cannot be deleted as it is contains one or more products."
                },
                status=status.HTTP_409_CONFLICT,
            )
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Generic View:
class CollectionDetail(RetrieveUpdateDestroyAPIView):

    queryset = Collection.objects.annotate(product_count=Count("product"))
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        if Product.objects.filter(collection_id=pk).exists():
            return Response(
                {
                    "error": "Collection cannot be deleted as it is contains one or more products."
                },
                status=status.HTTP_409_CONFLICT,
            )
        return super().delete(request, pk)


# ViewSet:
class CollectionViewSet(ModelViewSet):

    queryset = Collection.objects.annotate(product_count=Count("product"))
    serializer_class = CollectionSerializer

    permission_classes = [custom_permissions.IsAdminOrReadOnly]

    def destroy(self, request, pk):
        if Product.objects.filter(collection_id=pk).exists():
            return Response(
                {
                    "error": "Collection cannot be deleted as it is contains one or more products."
                },
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, pk)


class ReviewViewSet(ModelViewSet):

    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    # Since we've the endpoint `/products/<pk>/reviews`, we want reviews to be dynamically fetched on the basis of product's pk,
    # hence we need to use method instead of attribute:
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    # Overriding to pass the product id from url to `ReviewSerializer.create`:
    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):

    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related("cartitem_set__product")


class CartItemViewSet(ModelViewSet):

    http_method_names = ["get", "post", "patch", "delete"]
    # disallow `put` method to make `UpdateCartItemSerializer.Meta.fields` work, else it keeps showing `product` even when it's not in the `fields`

    # serializer_class = CartItemSerializer
    # Instead of above, dynamically depending on request method:
    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UpdateCartItemSerializer
            # Which has `fields = ["quantity"]`.
        # For all 3 other methods:
        return CartItemSerializer

    # queryset = CartItem.objects.all()
    # Above would return items across all the carts!!
    # But what we instead want is, items from a single cart. Just like we did in `ReviewViewSet`.
    # So, we need `get_queryset`:
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related(
            "product"
        )
        # Note: Even if we don't use `product = SimpleProductSerializer()` in `CartItemSerializer`,
        # `.select_related("product")` is still needed since we've `product.unit_price` in `CartItemSerializer.get_total_price`.

    # Overriding to pass the cart id from url to `CartItemSerializer.save`:
    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}


class CustomerViewSet(ModelViewSet):

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    permission_classes = [custom_permissions.FullDjangoModelPermissions]

    @action(
        detail=False,
        methods=["GET", "PUT"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request: Request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)

    @action(
        detail=True,
        permission_classes=[custom_permissions.ViewCustomerHistoryPermission],
    )
    def history(self, request: Request, pk: int):
        return Response(pk)


class OrderViewSet(ModelViewSet):

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        if self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.prefetch_related("orderitem_set__product")

        customer = Customer.objects.only("id").get(user_id=user.id)
        return Order.objects.filter(customer_id=customer.id).prefetch_related(
            "orderitem_set__product"
        )

    # (Read: Notes > Part 2 > 6. Designing and Building the Orders API > Returning the Created Order)
    def create(self, request, *args, **kwargs):
        input_sr = CreateOrderSerializer(
            data=request.data, context={"user_id": self.request.user.id}
        )
        input_sr.is_valid(raise_exception=True)
        order = input_sr.save()

        output_sr = OrderSerializer(order)
        return Response(output_sr.data)

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    http_method_names = ["post", "get", "patch", "delete", "head", "options"]


class ProductImageViewSet(ModelViewSet):

    serializer_class = ProductImageSerializer

    # Since we've the endpoint `/products/<pk>/images`, we want images to be dynamically fetched on the basis of product's pk,
    # hence we need to use method instead of attribute:
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs["product_pk"])

    # Overriding to pass the product id from url to `ProductImageSerializer.create`:
    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}
