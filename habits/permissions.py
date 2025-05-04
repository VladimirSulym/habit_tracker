from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только владельцам привычек редактировать их
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено для любого запроса
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешения на запись только владельцу привычки
        return obj.user == request.user
