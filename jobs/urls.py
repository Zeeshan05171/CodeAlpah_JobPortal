from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import JobListingViewSet, ResumeViewSet, ApplicationViewSet, EmployerStatsView, PlatformStatsView

router = DefaultRouter()
router.register("listings", JobListingViewSet, basename="joblisting")
router.register("resumes", ResumeViewSet, basename="resume")
router.register("applications", ApplicationViewSet, basename="application")

urlpatterns = [
    path("stats/employer/", EmployerStatsView.as_view(), name="employer-stats"),
    path("stats/platform/", PlatformStatsView.as_view(), name="platform-stats"),
] + router.urls
