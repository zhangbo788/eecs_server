from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]
    list_display_links = ['name', ]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'role_name',
        'user_username'
    ]

    def role_name(self, obj):
        return obj.role.name

    role_name.__name__ = "角色"

    def user_username(self, obj):
        return obj.user.username

    user_username.__name__ = "用户"
    list_display_links = ['id', ]


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'code',
        'name',
        'manager_name'
    ]

    def manager_name(self, obj):
        return obj.manager.username

    manager_name.__name__ = "专业负责人"

    list_display_links = ['id', ]


@admin.register(Point1)
class Point1Admin(admin.ModelAdmin):
    list_display = [
        'id',
        'major_name',
        'index',
        'content'
    ]

    def major_name(self, obj):
        return obj.major.name

    major_name.__name__ = "专业负责人"
    list_display_links = ['id', ]


@admin.register(Point2)
class Point2Admin(admin.ModelAdmin):
    list_display = [
        'id',
        'point1_index',
        'index',
        'content'
    ]

    def point1_index(self, obj):
        return obj.point1.index

    point1_index.__name__ = "毕业要求序号"
    list_display_links = ['id', ]
