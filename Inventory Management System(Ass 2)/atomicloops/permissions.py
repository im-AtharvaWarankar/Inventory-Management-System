from rest_framework import permissions
# from django.conf import settings
import sys


class UsersPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == "POST":
            return True
        # Instance must have an attribute named email
        try:
            authorize = request.user.email == obj.email or request.user.is_superuser
            if authorize:
                return True
            else:
                False
        except:
            _ = sys.exc_info()[0]
            # with open(settings.exception_error_file, "a") as f:
            #     f.write(str(e) + "\n")
            #     f.close()
            return False


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named email
        try:
            authorize = request.user.email == obj.userId.email or request.user.is_superuser
            if authorize:
                return True
            else:
                False
        except:
            _ = sys.exc_info()[0]
            return False
