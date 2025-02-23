from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile, User, UserDepartment


class ProfileInline(admin.StackedInline):
    model = Profile
    max_num = 1
    can_delete = False

class UserDepartmentInline(admin.StackedInline):
    model = UserDepartment
    max_num = 2
    can_delete = False


class AccountsUserAdmin(UserAdmin):
    inlines = [ProfileInline, UserDepartmentInline]


admin.site.unregister(User)
admin.site.register(User, AccountsUserAdmin)