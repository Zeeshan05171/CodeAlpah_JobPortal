from django.contrib import admin
from .models import JobListing, Resume, Application


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ["title", "employer", "job_type", "location", "status", "applicant_count", "created_at", "deadline"]
    list_filter = ["status", "job_type", "experience_level", "is_remote", "category"]
    search_fields = ["title", "employer__company_name", "location"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ["title", "candidate", "is_primary", "uploaded_at"]
    list_filter = ["is_primary"]
    search_fields = ["candidate__full_name", "title"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["candidate", "job", "status", "applied_at", "updated_at"]
    list_filter = ["status", "applied_at"]
    search_fields = ["candidate__full_name", "job__title"]
    date_hierarchy = "applied_at"
