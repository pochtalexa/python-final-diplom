from rest_framework import permissions


class DenyAny(permissions.BasePermission):
    def has_permission(self, request, view):
        self.message = 'Method are not allowed'
        return False

    def has_object_permission(self, request, view, obj):
        self.message = 'Method are not allowed'
        return False

class IsShop(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.type != 'shop':
            self.message = 'Method are allowed only for shop'
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.type != 'shop':
            self.message = 'Method are allowed only for shop'
            return False
        return True


