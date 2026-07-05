from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a role that determines which profile it owns."""

    class Role(models.TextChoices):
        EMPLOYER = "employer", "Employer"
        CANDIDATE = "candidate", "Candidate"

    role = models.CharField(max_length=20, choices=Role.choices)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_employer(self):
        return self.role == self.Role.EMPLOYER

    @property
    def is_candidate(self):
        return self.role == self.Role.CANDIDATE


class EmployerProfile(models.Model):
    """Company-facing profile owned by a User with role=employer."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employer_profile")
    company_name = models.CharField(max_length=150)
    industry = models.CharField(max_length=100, blank=True)
    company_website = models.URLField(blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=150, blank=True)
    about = models.TextField(blank=True)
    logo = models.ImageField(upload_to="employer_logos/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class CandidateProfile(models.Model):
    """Job-seeker profile owned by a User with role=candidate."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="candidate_profile")
    full_name = models.CharField(max_length=150, blank=True)
    headline = models.CharField(max_length=200, blank=True, help_text="e.g. Frontend Developer")
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=150, blank=True)
    skills = models.CharField(max_length=500, blank=True, help_text="Comma separated skills")
    experience_years = models.PositiveSmallIntegerField(default=0)
    about = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to="candidate_photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.user.username

    @property
    def skills_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]
