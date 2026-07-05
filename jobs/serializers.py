from rest_framework import serializers

from .models import JobListing, Resume, Application


class JobListingSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="employer.company_name", read_only=True)
    company_logo = serializers.ImageField(source="employer.logo", read_only=True)
    company_location = serializers.CharField(source="employer.location", read_only=True)
    applicant_count = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    has_applied = serializers.SerializerMethodField()

    class Meta:
        model = JobListing
        fields = [
            "id", "title", "slug", "category", "description", "requirements", "responsibilities",
            "job_type", "experience_level", "location", "is_remote", "salary_min", "salary_max",
            "status", "deadline", "created_at", "updated_at", "company_name", "company_logo",
            "company_location", "applicant_count", "is_expired", "has_applied",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_has_applied(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not request.user.is_candidate:
            return False
        candidate_profile = getattr(request.user, "candidate_profile", None)
        if not candidate_profile:
            return False
        return obj.applications.filter(candidate=candidate_profile).exists()

    def create(self, validated_data):
        request = self.context["request"]
        employer_profile = request.user.employer_profile
        return JobListing.objects.create(employer=employer_profile, **validated_data)


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ["id", "title", "file", "is_primary", "uploaded_at"]
        read_only_fields = ["uploaded_at"]

    def create(self, validated_data):
        request = self.context["request"]
        candidate_profile = request.user.candidate_profile
        return Resume.objects.create(candidate=candidate_profile, **validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.employer.company_name", read_only=True)
    candidate_name = serializers.CharField(source="candidate.full_name", read_only=True)
    candidate_headline = serializers.CharField(source="candidate.headline", read_only=True)
    resume_file = serializers.FileField(source="resume.file", read_only=True)
    job = serializers.PrimaryKeyRelatedField(queryset=JobListing.objects.all())

    class Meta:
        model = Application
        fields = [
            "id", "job", "job_title", "company_name", "candidate", "candidate_name",
            "candidate_headline", "resume", "resume_file", "cover_letter", "status",
            "applied_at", "updated_at",
        ]
        read_only_fields = ["candidate", "status", "applied_at", "updated_at"]

    def validate_job(self, job):
        if job.status != JobListing.Status.OPEN:
            raise serializers.ValidationError("This job listing is not currently accepting applications.")
        return job

    def create(self, validated_data):
        request = self.context["request"]
        candidate_profile = request.user.candidate_profile
        job = validated_data["job"]
        if Application.objects.filter(job=job, candidate=candidate_profile).exists():
            raise serializers.ValidationError("You have already applied to this job.")
        return Application.objects.create(candidate=candidate_profile, **validated_data)


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["status"]
