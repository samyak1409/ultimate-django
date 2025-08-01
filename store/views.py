# from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from .models import Product, Collection, OrderItem, Review
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer
from .filters import ProductFilter


# def product_list(request: HttpRequest) -> HttpResponse:
#     return HttpResponse("OK")


# Function-based View:
# @api_view(["GET", "POST"])
# def product_list(request: Request) -> Response:

#     # return Response("OK")

#     if request.method == "GET":

#         products = Product.objects.select_related("collection")
#         serializer = ProductSerializer(
#             products, many=True, context={"request": request}
#         )
#         # print(serializer)
#         # print(len(serializer.data))
#         # print(type(serializer.data))  # <class 'ReturnList'>
#         return Response(serializer.data)

#     else:  # if request.method == "POST":

#         serializer = ProductSerializer(data=request.data, context={"request": request})
#         print(request.data)
#         # print(type(request.data))  # <class 'dict'>
#         # print(serializer.initial_data)  # same as `request.data`
#         # if serializer.is_valid():
#         #     # print(serializer.validated_data)
#         #     # print(type(serializer.validated_data))  # <class 'dict'>
#         #     return Response("OK")
#         # else:
#         #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         serializer.is_valid(raise_exception=True)
#         print(serializer.validated_data)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# Class-based View:
# class ProductList(APIView):

#     def get(self, request):
#         products = Product.objects.all()
#         serializer = ProductSerializer(
#             products, many=True, context={"request": request}

#    )
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = ProductSerializer(data=request.data, context={"request": request})
#         print(request.data)
#         serializer.is_valid(raise_exception=True)
#         print(serializer.validated_data)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# Generic (`rest_framework.generics`) View:
class ProductList(ListCreateAPIView):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Or we can use methods instead of above if we've some more logic or anything other than just a simple expression.
    # def get_queryset(self):
    #     return Product.objects.all()
    # def get_serializer_class(self):
    #     return ProductSerializer


# Function-based View:
# @api_view(["GET", "PUT", "DELETE"])
# def product_detail(request, pk: int):

#     # return Response(pk)

#     # try:
#     #     product = Product.objects.get(pk=pk)  # get the object (or queryset)
#     # except Product.DoesNotExist:  # when product with id `pk` does not exist
#     #     # We can just do:
#     #     # return Response(status=404)
#     #     # But, we should:
#     #     return Response(status=status.HTTP_404_NOT_FOUND)

#     # Above 4 SLOCs are same as this line:
#     product = get_object_or_404(Product, pk=pk)

#     if request.method == "GET":

#         serializer = ProductSerializer(product, context={"request": request})
#         # convert object (or queryset) to dict (or list of dicts), returns a serializer obj
#         # print(serializer)
#         # print(serializer.data)
#         # print(type(serializer.data))  # <class 'ReturnDict'>
#         return Response(serializer.data)  # `.data` gives us the dict (or list of dicts)

#     elif request.method == "PUT":

#         serializer = ProductSerializer(
#             product, data=request.data, context={"request": request}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     else:  # if request.method == "DELETE":

#         # `ProtectedError`: protected foreign keys
#         if product.orderitem_set.exists():
#             return Response(
#                 {
#                     "error": "Product cannot be deleted as it is associated with an order item."
#                 },
#                 status=status.HTTP_409_CONFLICT,
#             )
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# Class-based View:
# class ProductDetail(APIView):

#     def get(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product, context={"request": request})
#         return Response(serializer.data)

#     def put(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(
#             product, data=request.data, context={"request": request}
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


# Generic (`rest_framework.generics`) View:
class ProductDetail(RetrieveUpdateDestroyAPIView):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitem_set.exists():
            return Response(
                {
                    "error": "Product cannot be deleted as it is associated with an order item."
                },
                status=status.HTTP_409_CONFLICT,
            )
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ViewSet:
class ProductViewSet(ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # For applying filtering functionality:
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

    # Searching:
    search_fields = ["title"]

    # Ordering:
    ordering_fields = ["unit_price", "last_update"]

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs["pk"]).exists():
            return Response(
                {
                    "error": "Product cannot be deleted as it is associated with an order item."
                },
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


# Function-based View:
# @api_view(["GET", "POST"])
# def collection_list(request: Request) -> Response:

#     if request.method == "GET":

#         collections = Collection.objects.annotate(product_count=Count("product"))
#         # Why `product` and not `product_set`?
#         # https://github.com/samyak1409/ultimate-django/blob/main/Notes/Part%201/4.%20Django%20ORM.md#grouping-data
#         serializer = CollectionSerializer(collections, many=True)
#         return Response(serializer.data)

#     else:  # if request.method == "POST":

#         serializer = CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# Generic (`rest_framework.generics`) View:
class CollectionList(ListCreateAPIView):

    queryset = Collection.objects.annotate(product_count=Count("product"))
    serializer_class = CollectionSerializer


# Function-based View:
# @api_view(["GET", "PUT", "DELETE"])
# def collection_detail(request, pk: int):

#     collection = get_object_or_404(
#         Collection.objects.annotate(product_count=Count("product")), pk=pk
#     )

#     if request.method == "GET":

#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)

#     elif request.method == "PUT":

#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     else:  # if request.method == "DELETE":

#         if collection.product_set.exists():
#             return Response(
#                 {
#                     "error": "Collection cannot be deleted as it is contains one or more products."
#                 },
#                 status=status.HTTP_409_CONFLICT,
#             )
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# Generic (`rest_framework.generics`) View:
class CollectionDetail(RetrieveUpdateDestroyAPIView):

    queryset = Collection.objects.annotate(product_count=Count("product"))
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.product_set.exists():
            return Response(
                {
                    "error": "Collection cannot be deleted as it is contains one or more products."
                },
                status=status.HTTP_409_CONFLICT,
            )
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ViewSet:
class CollectionViewSet(ModelViewSet):

    queryset = Collection.objects.annotate(product_count=Count("product"))
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs["pk"]).exists():
            return Response(
                {
                    "error": "Collection cannot be deleted as it is contains one or more products."
                },
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):

    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    # Since we've the endpoint `/products/<pk>/reviews`, we want reviews to be dynamically fetched on the basis of product's pk,
    # hence we need to use method instead of attribute:
    def get_queryset(self):
        return Review.objects.filter(product=self.kwargs["product_pk"])

    # Overriding to pass the product id from url to `ReviewSerializer.create`:
    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}
