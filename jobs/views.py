from django.db.models import Count, Q
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JobListing, Resume, Application
from .filters import JobListingFilter
from .permissions import IsEmployer, IsCandidate, IsJobOwnerOrReadOnly
from .serializers import (
    JobListingSerializer, ResumeSerializer,
    ApplicationSerializer, ApplicationStatusUpdateSerializer,
)
from notifications.utils import notify


class JobListingViewSet(viewsets.ModelViewSet):
    serializer_class = JobListingSerializer
    filterset_class = JobListingFilter
    search_fields = ["title", "description", "location", "category"]
    ordering_fields = ["created_at", "salary_min", "salary_max", "deadline"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsJobOwnerOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        qs = JobListing.objects.select_related("employer").annotate(app_count=Count("applications"))
        if self.action in ("list",):
            # Public job board only shows open, non-expired listings by default
            if self.request.query_params.get("mine") != "true":
                qs = qs.filter(status=JobListing.Status.OPEN)
        if self.request.query_params.get("mine") == "true" and self.request.user.is_authenticated:
            qs = qs.filter(employer__user=self.request.user)
        return qs

    def get_permissions(self):
        if self.action in ("create",):
            return [permissions.IsAuthenticated(), IsEmployer()]
        return super().get_permissions()

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated, IsEmployer])
    def my_jobs(self, request):
        jobs = JobListing.objects.filter(employer__user=request.user).annotate(app_count=Count("applications"))
        page = self.paginate_queryset(jobs)
        serializer = self.get_serializer(page or jobs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated, IsEmployer])
    def applicants(self, request, slug=None):
        job = self.get_object()
        if job.employer.user_id != request.user.id:
            return Response({"detail": "Not your job listing."}, status=status.HTTP_403_FORBIDDEN)
        apps = job.applications.select_related("candidate", "resume").all()
        serializer = ApplicationSerializer(apps, many=True, context={"request": request})
        return Response(serializer.data)


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return Resume.objects.filter(candidate__user=self.request.user)


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.is_candidate:
            return Application.objects.filter(candidate__user=user).select_related("job", "job__employer")
        if user.is_employer:
            return Application.objects.filter(job__employer__user=user).select_related(
                "job", "candidate", "resume"
            )
        return Application.objects.none()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsCandidate()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        application = serializer.save()
        notify(
            user=application.job.employer.user,
            message=f"{application.candidate.full_name or 'A candidate'} applied for '{application.job.title}'.",
            link=f"/jobs/{application.job.slug}/applicants",
        )

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsEmployer])
    def status_update(self, request, pk=None):
        application = self.get_object()
        if application.job.employer.user_id != request.user.id:
            return Response({"detail": "Not your job listing."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ApplicationStatusUpdateSerializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        notify(
            user=application.candidate.user,
            message=f"Your application for '{application.job.title}' is now '{application.get_status_display()}'.",
            link=f"/applications",
        )
        return Response(ApplicationSerializer(application, context={"request": request}).data)


class EmployerStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsEmployer]

    def get(self, request):
        jobs = JobListing.objects.filter(employer__user=request.user)
        applications = Application.objects.filter(job__employer__user=request.user)
        status_breakdown = applications.values("status").annotate(count=Count("id"))
        return Response({
            "total_jobs": jobs.count(),
            "open_jobs": jobs.filter(status=JobListing.Status.OPEN).count(),
            "total_applications": applications.count(),
            "status_breakdown": {row["status"]: row["count"] for row in status_breakdown},
            "top_jobs": list(
                jobs.annotate(app_count=Count("applications"))
                .order_by("-app_count")
                .values("title", "slug", "app_count")[:5]
            ),
        })


class PlatformStatsView(APIView):
    """High-level stats for the admin/reporting dashboard (staff only)."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from accounts.models import User, EmployerProfile, CandidateProfile

        applications = Application.objects.all()
        status_breakdown = applications.values("status").annotate(count=Count("id"))
        return Response({
            "total_users": User.objects.count(),
            "total_employers": EmployerProfile.objects.count(),
            "total_candidates": CandidateProfile.objects.count(),
            "total_jobs": JobListing.objects.count(),
            "open_jobs": JobListing.objects.filter(status=JobListing.Status.OPEN).count(),
            "total_applications": applications.count(),
            "status_breakdown": {row["status"]: row["count"] for row in status_breakdown},
        })
