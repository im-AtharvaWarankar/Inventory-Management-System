from rest_framework import generics
from users.serializers import UpdatePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from atomicloops.permissions import UsersPermission
from users.models import Users


class UpdatePasswordView(generics.UpdateAPIView):

    queryset = Users.objects.all()
    permission_classes = [IsAuthenticated, UsersPermission]
    serializer_class = UpdatePasswordSerializer
