from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'branch', 'is_active')
    list_filter = ('role', 'branch', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Business Info', {'fields': ('role', 'branch', 'phone')}),
    )