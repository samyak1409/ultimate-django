from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from django.db.models.query import QuerySet
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from . import models


# Register your models here.


class InventoryStatusListFilter(admin.SimpleListFilter):
    title = "inventory status"
    parameter_name = "inventory"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [("<10", "Low")]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


# @admin.register(models.Product)
# As we're registering `models.Product` with `store_custom.admin.ProductCustomAdmin(ProductAdmin)`.
# A model can't be registered two times.
# And `ProductAdmin` functionality still works completely since `ProductCustomAdmin` is extending `ProductAdmin`.
# (Video: "Extending Pluggable Apps")
class ProductAdmin(admin.ModelAdmin):
    actions = ["clear_inventory"]
    list_display = [
        "title",
        "unit_price",
        "inventory_status",
        "inventory",
        "collection",
    ]
    list_editable = ["unit_price"]
    list_filter = ["collection", "last_update", InventoryStatusListFilter]
    list_per_page = 10
    ordering = ["title"]
    prepopulated_fields = {"slug": ["title"]}
    search_fields = ["title"]
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        return "OK" if product.inventory >= 10 else "Low"

    @admin.action(description="Clear inventory for")
    def clear_inventory(self, request, queryset: QuerySet):
        count = queryset.update(inventory=0)
        self.message_user(
            request, f"Successfully cleared inventory for {count} product(s)."
        )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products", "featured_product_with_link"]

    @admin.display(ordering="product_count")
    def products(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": collection.id})
        )
        return format_html('<a href="{}">{}</a>', url, collection.product_count)

    @admin.display(ordering="featured_product")
    def featured_product_with_link(self, collection):
        if collection.featured_product_id is None:
            return None
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"id": collection.featured_product_id})
        )
        return format_html('<a href="{}">{}</a>', url, collection.featured_product)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(product_count=Count("product"))


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders"]
    list_editable = ["membership"]
    list_per_page = 10
    ordering = ["first_name", "last_name"]
    search_fields = ["first_name", "last_name"]

    @admin.display(ordering="order_count")
    def orders(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": customer.id})
        )
        return format_html('<a href="{}">{}</a>', url, customer.order_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(order_count=Count("order"))


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ["product"]
    extra = 1  # how many extra empty records should be shown in advance, default is 3
    # min_num, max_num = 1, 10  # min, max records, out of this would not accept the submission


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]
    list_display = ["id", "placed_at", "customer_name"]
    list_select_related = ["customer"]  # not using this = N+1 query problem
    ordering = ["id"]

    def customer_name(self, order):
        return f"{order.customer.first_name} {order.customer.last_name}"
