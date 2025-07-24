from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from tags import models as tags_models
from store.admin import ProductAdmin
from store import models as store_models


# Register your models here.


class TaggedItemInline(GenericTabularInline):
    model = tags_models.TaggedItem


@admin.register(store_models.Product)
class ProductCustomAdmin(ProductAdmin):
    inlines = [TaggedItemInline]
