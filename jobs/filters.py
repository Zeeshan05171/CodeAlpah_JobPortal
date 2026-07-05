import django_filters as df

from .models import JobListing


class JobListingFilter(df.FilterSet):
    keyword = df.CharFilter(method="filter_keyword")
    location = df.CharFilter(field_name="location", lookup_expr="icontains")
    category = df.CharFilter(field_name="category", lookup_expr="icontains")
    job_type = df.CharFilter(field_name="job_type")
    experience_level = df.CharFilter(field_name="experience_level")
    is_remote = df.BooleanFilter(field_name="is_remote")
    salary_min = df.NumberFilter(field_name="salary_max", lookup_expr="gte")
    salary_max = df.NumberFilter(field_name="salary_min", lookup_expr="lte")
    company = df.CharFilter(field_name="employer__company_name", lookup_expr="icontains")

    class Meta:
        model = JobListing
        fields = [
            "keyword", "location", "category", "job_type",
            "experience_level", "is_remote", "salary_min", "salary_max", "company",
        ]

    def filter_keyword(self, queryset, name, value):
        from django.db.models import Q
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value) | Q(requirements__icontains=value)
        )
