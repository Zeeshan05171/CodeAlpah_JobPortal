from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class JobListing(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = "full_time", "Full-time"
        PART_TIME = "part_time", "Part-time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"
        REMOTE = "remote", "Remote"

    class ExperienceLevel(models.TextChoices):
        ENTRY = "entry", "Entry level"
        MID = "mid", "Mid level"
        SENIOR = "senior", "Senior level"
        LEAD = "lead", "Lead / Principal"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        DRAFT = "draft", "Draft"

    employer = models.ForeignKey(
        "accounts.EmployerProfile", on_delete=models.CASCADE, related_name="jobs"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.ENTRY)
    location = models.CharField(max_length=150)
    is_remote = models.BooleanField(default=False)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.employer.company_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.employer.company_name}")[:200]
            slug = base_slug
            counter = 1
            while JobListing.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return bool(self.deadline and self.deadline < timezone.now().date())

    @property
    def applicant_count(self):
        return self.applications.count()


class Resume(models.Model):
    candidate = models.ForeignKey(
        "accounts.CandidateProfile", on_delete=models.CASCADE, related_name="resumes"
    )
    title = models.CharField(max_length=150, default="My Resume")
    file = models.FileField(upload_to="resumes/")
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.title} ({self.candidate})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_primary:
            Resume.objects.filter(candidate=self.candidate).exclude(pk=self.pk).update(is_primary=False)


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWED = "reviewed", "Reviewed"
        SHORTLISTED = "shortlisted", "Shortlisted"
        INTERVIEW = "interview", "Interview"
        REJECTED = "rejected", "Rejected"
        ACCEPTED = "accepted", "Accepted"

    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(
        "accounts.CandidateProfile", on_delete=models.CASCADE, related_name="applications"
    )
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, related_name="applications")
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        unique_together = ["job", "candidate"]

    def __str__(self):
        return f"{self.candidate} -> {self.job.title} ({self.status})"
