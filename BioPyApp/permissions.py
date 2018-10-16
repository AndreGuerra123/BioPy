from rest_framework import permissions

class hasServerPermission(permissions.BasePermission):
    message = 'User must be the (server) owner or have admin priviledges.'
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_superuser

class hasEndpointPermission(permissions.BasePermission):
    message = 'User must be the (server, endpoint) owner or have admin priviledges.'
    def has_object_permission(self, request, view, obj):
        return obj.server.owner == request.user or request.user.is_superuser

class hasConfigurationPermission(permissions.BasePermission):
    message = 'User must be the (server, endpoint, configuration) owner or have admin priviledges.'
    def has_object_permission(self, request, view, obj):
        return obj.endpoint.server.owner == request.user or request.user.is_superuser

class hasNodePermission(permissions.BasePermission):
    message = 'User must be the (server, endpoint, configuration, node) owner or have admin priviledges.'
    def has_object_permission(self, request, view, obj):
        return obj.configuration.endpoint.server.owner == request.user or request.user.is_superuser


class hasProcessPermission(permissions.BasePermission):
    message = 'User must be the (process) owner or have admin priviledges.'
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_superuser

class hasBatchPermission(permissions.BasePermission):
    message = 'User must be the (batch, process) owner or have admin priviledges.'
    def has_object_permission(self, request, view, obj):
        return obj.process.owner == request.user or request.user.is_superuser
        

class hasDataPermission(permissions.BasePermission):
    message = 'User must be the (data, batch, process) owner or have admin priviledges.'
    def has_object_permission(self, request, view, obj):
        return obj.batch.process.owner == request.user or request.user.is_superuser