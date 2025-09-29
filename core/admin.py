from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from tags import models as tags_models
from store.admin import ProductAdmin
from store import models as store_models
from .models import User


# Register your models here.


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "usable_password",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "email",
                ),
            },
        ),
    )


class TaggedItemInline(GenericTabularInline):
    model = tags_models.TaggedItem
    extra = 1


@admin.register(store_models.Product)
class ProductCustomAdmin(ProductAdmin):
    # inlines = [ProductImageInline, TaggedItemInline]
    # See MD notes. (Uploading Files > Managing Images in the Admin)
    inlines = list(ProductAdmin.inlines) + [TaggedItemInline]
