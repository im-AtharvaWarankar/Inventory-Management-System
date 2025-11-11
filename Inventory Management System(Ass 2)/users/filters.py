from atomicloops.filters import AtomicDateFilter
from .models import Users, UsersDevices


class UsersFilter(AtomicDateFilter):
    class Meta:
        model = Users
        fields = (
            'createdAt',
            'updatedAt',
            'is_active',
            'is_superuser',
            'is_staff',
            'level'
        )


class UsersDevicesFilter(AtomicDateFilter):
    class Meta:
        model = UsersDevices
        fields = (
            'createdAt',
            'updatedAt',
            'userId',
        )
