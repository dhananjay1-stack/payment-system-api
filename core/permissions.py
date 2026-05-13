from rest_framework.permissions import BasePermission


class IsAccountOwner(BasePermission):
    """
    Only allow the owner of a bank account to access it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
