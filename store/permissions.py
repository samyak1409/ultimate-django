from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_staff


class FullDjangoModelPermissions(permissions.DjangoModelPermissions):

    # `perms_map`: Maps HTTP method to Required model permission.
    # Copy the base map instead of mutating it in `__init__` — `self.perms_map[...] = ...`
    # writes into the class-level dict shared with `DjangoModelPermissions` itself,
    # changing GET's requirement for every view using it across the whole process.
    perms_map = {
        **permissions.DjangoModelPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
    }


class ViewCustomerHistoryPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.has_perm("store.view_history")
