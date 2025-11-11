# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Users, UsersDevices, ExportData


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'createdAt',
        'updatedAt',
        'firstName',
        'lastName',
        'email',
        'password',
        'level',
        'is_active',
        'is_staff',
        'is_superuser',
        'isVerified',
    )
    list_filter = (
        'createdAt',
        'updatedAt',
        'is_active',
        'is_staff',
        'is_superuser',
        'isVerified'
    )
    raw_id_fields = ('groups', 'user_permissions')


@admin.register(UsersDevices)
class UsersDevicesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'createdAt',
        'updatedAt',
        'userId',
        'deviceId',
        'token',
        'deviceType',
    )
    list_filter = ('createdAt', 'updatedAt', 'userId')


@admin.register(ExportData)
class ExportDataAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'createdAt',
        'updatedAt',
        'userId',
        'fileUrl',
    )
