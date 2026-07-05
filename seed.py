import os, django, random
from datetime import timedelta
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone
from accounts.models import User, EmployerProfile, CandidateProfile
from jobs.models import JobListing, Resume, Application

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@jobportal.dev", "admin12345", role="employer")

employers_data = [
    ("nova_tech", "Nova Technologies", "Software / SaaS", "Lahore, Pakistan"),
    ("skyline_labs", "Skyline Labs", "AI & Data", "Islamabad, Pakistan"),
    ("brightpath", "BrightPath Digital", "Marketing", "Karachi, Pakistan"),
]
employers = []
for username, company, industry, location in employers_data:
    user, created = User.objects.get_or_create(
        username=username, defaults={"email": f"{username}@example.com", "role": "employer"}
    )
    if created:
        user.set_password("password123")
        user.save()
    profile, _ = EmployerProfile.objects.get_or_create(
        user=user, defaults={"company_name": company, "industry": industry, "location": location, "is_verified": True}
    )
    employers.append(profile)

candidates_data = [
    ("zeeshan_dev", "Zeeshan Ahmed", "AI / Backend Developer", "Haripur, Pakistan", "Python, Django, React, SQL"),
    ("hina_codes", "Hina Batool", "Frontend Developer", "Lahore, Pakistan", "JavaScript, React, CSS, UI Design"),
    ("ali_data", "Ali Raza", "Data Analyst", "Karachi, Pakistan", "Python, Pandas, SQL, Power BI"),
]
candidates = []
for username, full_name, headline, location, skills in candidates_data:
    user, created = User.objects.get_or_create(
        username=username, defaults={"email": f"{username}@example.com", "role": "candidate"}
    )
    if created:
        user.set_password("password123")
        user.save()
    profile, _ = CandidateProfile.objects.get_or_create(
        user=user,
        defaults={"full_name": full_name, "headline": headline, "location": location,
                  "skills": skills, "experience_years": random.randint(1, 5)},
    )
    candidates.append(profile)

jobs_data = [
    (employers[0], "Backend Engineer (Django)", "Engineering", "full_time", "mid", "Lahore, Pakistan", False, 120000, 180000,
     "We're looking for a backend engineer to build and scale our Django REST APIs.",
     "2+ years Python/Django, REST APIs, PostgreSQL, Git."),
    (employers[1], "AI/ML Intern", "Data Science", "internship", "entry", "Remote", True, 30000, 50000,
     "Join our AI team to work on real-world machine learning pipelines.",
     "Basic Python, understanding of ML fundamentals, eagerness to learn."),
    (employers[2], "Social Media Marketing Executive", "Marketing", "full_time", "entry", "Karachi, Pakistan", False, 60000, 90000,
     "Plan and execute campaigns across Instagram, TikTok and Facebook for client brands.",
     "1+ years experience, strong copywriting, Canva/Photoshop basics."),
    (employers[0], "Frontend Developer (React)", "Engineering", "full_time", "mid", "Islamabad, Pakistan", True, 100000, 160000,
     "Build delightful, responsive interfaces for our SaaS product.",
     "React, HTML/CSS, REST API integration, attention to detail."),
    (employers[1], "Data Analyst", "Data Science", "contract", "entry", "Karachi, Pakistan", False, 70000, 100000,
     "Turn raw data into actionable insights for our product and growth teams.",
     "SQL, Excel/Power BI, basic statistics."),
]

for employer, title, category, job_type, exp, location, remote, smin, smax, desc, reqs in jobs_data:
    JobListing.objects.get_or_create(
        employer=employer, title=title,
        defaults=dict(
            category=category, job_type=job_type, experience_level=exp, location=location,
            is_remote=remote, salary_min=smin, salary_max=smax, description=desc, requirements=reqs,
            status="open", deadline=timezone.now().date() + timedelta(days=30),
        ),
    )

print("Seed complete.")
print("Superuser -> username: admin / password: admin12345")
print("Employers -> nova_tech / skyline_labs / brightpath (password: password123)")
print("Candidates -> zeeshan_dev / hina_codes / ali_data (password: password123)")
