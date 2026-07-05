from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, EmployerProfile, CandidateProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "role", "is_staff", "is_active", "date_joined"]
    list_filter = ["role", "is_staff", "is_active"]
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Role", {"fields": ("role", "email")}),)


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ["company_name", "user", "industry", "location", "is_verified", "created_at"]
    list_filter = ["is_verified", "industry"]
    search_fields = ["company_name", "user__username"]


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "user", "headline", "experience_years", "location", "created_at"]
    search_fields = ["full_name", "user__username", "skills"]
