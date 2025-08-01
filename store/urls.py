from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views


router = DefaultRouter()
router.register(prefix="products", viewset=views.ProductViewSet, basename="products")
router.register(prefix="collections", viewset=views.CollectionViewSet)
# print(router.urls)  # <class 'list'>

products_router = NestedDefaultRouter(router, "products", lookup="product")
products_router.register("reviews", views.ReviewViewSet, basename="product-reviews")

urlpatterns = [
    # path("products/", views.product_list),
    # path("products/", views.ProductList.as_view()),
    # path("products/<int:pk>/", views.ProductDetail.as_view()),
    # path("collections/", views.CollectionList.as_view()),
    # path("collections/<int:pk>/", views.CollectionDetail.as_view(), name="collection-detail"),
] + (router.urls + products_router.urls)
