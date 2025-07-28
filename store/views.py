# from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Collection
from .serializers import ProductSerializer, CollectionSerializer


# def product_list(request: HttpRequest) -> HttpResponse:
#     return HttpResponse("OK")


@api_view(["GET", "POST"])
def product_list(request: Request) -> Response:

    # return Response("OK")

    if request.method == "GET":

        products = Product.objects.select_related("collection").all()
        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )
        # print(serializer)
        # print(len(serializer.data))
        # print(type(serializer.data))  # <class 'ReturnList'>
        return Response(serializer.data)

    else:  # if request.method == "POST":

        serializer = ProductSerializer(data=request.data, context={"request": request})
        print(request.data)
        # print(type(request.data))  # <class 'dict'>
        # print(serializer.initial_data)  # same as `request.data`
        # if serializer.is_valid():
        #     # print(serializer.validated_data)
        #     # print(type(serializer.validated_data))  # <class 'dict'>
        #     return Response("OK")
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def product_detail(request, pk: int):

    # return Response(pk)

    # try:
    #     product = Product.objects.get(pk=pk)  # get the object (or queryset)
    # except Product.DoesNotExist:  # when product with id `pk` does not exist
    #     # We can just do:
    #     # return Response(status=404)
    #     # But, we should:
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    # Above 4 SLOCs are same as this line:
    product = get_object_or_404(Product, pk=pk)

    if request.method == "GET":

        serializer = ProductSerializer(product, context={"request": request})
        # convert object (or queryset) to dict (or list of dicts), returns a serializer obj
        # print(serializer)
        # print(serializer.data)
        # print(type(serializer.data))  # <class 'ReturnDict'>
        return Response(serializer.data)  # `.data` gives us the dict (or list of dicts)

    elif request.method == "PUT":

        serializer = ProductSerializer(
            product, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    else:  # if request.method == "DELETE":

        # `ProtectedError`: protected foreign keys
        if product.orderitem_set.count() > 0:
            return Response(
                {
                    "error": "Product cannot be deleted as it is associated with an order item."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

        if collection.product_set.count() > 0:
            return Response(
                {
                    "error": "Collection cannot be deleted as it is contains one or more products."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
