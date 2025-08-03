from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views


router = DefaultRouter()
router.register(prefix="products", viewset=views.ProductViewSet, basename="products")
router.register(prefix="collections", viewset=views.CollectionViewSet)
router.register(prefix="carts", viewset=views.CartViewSet)
# print(router.urls)  # <class 'list'>

product_router = NestedDefaultRouter(router, "products", lookup="product")
product_router.register("reviews", views.ReviewViewSet, basename="product-reviews")

cart_router = NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items", views.CartItemViewSet, basename="cart-items")

urlpatterns = [
    # path("products/", views.product_list),
    # path("products/", views.ProductList.as_view()),
    # path("products/<int:pk>/", views.ProductDetail.as_view()),
    # path("collections/", views.CollectionList.as_view()),
    # path("collections/<int:pk>/", views.CollectionDetail.as_view(), name="collection-detail"),
] + (router.urls + product_router.urls + cart_router.urls)
