from rest_framework import permissions


class IsTenantOrOwnerReadOnly(permissions.BasePermission):
    """
    Allows read access to tenant or property owner.
    """
    def has_object_permission(self, request, view, obj): 
        if request.method in permissions.SAFE_METHODS:
            return (
                obj.tenant == request.user or
                obj.property.owner == request.user
            )
        return False


class IsPropertyOwner(permissions.BasePermission):
    """
    Allows access only to the owner of the property associated with the lease.
    """
    def has_object_permission(self, request, view, obj):  
        return obj.property.owner == request.user


class IsTenant(permissions.BasePermission):
    """
    Allows access only to the tenant of the lease.
    """
    def has_object_permission(self, request, view, obj):
        return obj.tenant == request.user