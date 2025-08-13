from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_staff


class FullDjangoModelPermissions(permissions.DjangoModelPermissions):

    # Maps HTTP method to Required model permission:
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
    }


class ViewCustomerHistoryPermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.has_perm("store.view_history")
