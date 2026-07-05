# JobPortal — Django REST Job Board

A full-stack job portal connecting **employers** and **candidates**, built with a **Django REST Framework** backend and a **vanilla HTML/CSS/JS** frontend. Employers post and manage job listings; candidates search, upload resumes, and apply; both sides track applications through a six-stage pipeline with automatic notifications.

---

## Features

**For candidates**
- Register, build a profile (headline, skills, experience, location)
- Upload multiple resumes and mark one as primary
- Search jobs by keyword, location, job type, experience level, and salary range
- Apply with a resume + cover note, one click, no duplicates allowed
- Track every application's status (Pending → Reviewed → Shortlisted → Interview → Accepted/Rejected)
- Get notified the moment a status changes

**For employers**
- Register a company profile
- Post, edit, close, and delete job listings
- Review applicants per job, read cover notes, download resumes
- Move applicants through the pipeline with one click (auto-notifies the candidate)
- Dashboard stats: total/open jobs, total applications, status breakdown, top roles by applicant count

**Admin**
- Full Django admin for every model (users, profiles, jobs, resumes, applications, notifications)
- `/api/stats/platform/` — staff-only endpoint with platform-wide reporting numbers

---

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Django 6, Django REST Framework, SimpleJWT, django-filter, django-cors-headers |
| Database | SQLite (swap the `DATABASES` setting for Postgres in production) |
| Frontend | Vanilla HTML/CSS/JS (no build step, no framework) — talks to the API over `fetch()` |
| Auth | JWT (access + refresh tokens, stored in `localStorage`) |

---

## Project structure

```
jobportal/
├── config/            # Django project settings, root URLconf
├── accounts/          # Custom User model, Employer/Candidate profiles, auth endpoints
├── jobs/               # JobListing, Resume, Application models + API
├── notifications/     # Notification model + API
├── frontend/           # Static HTML/CSS/JS site (served separately from Django)
│   ├── css/style.css
│   ├── js/api.js       # fetch wrapper + JWT handling
│   ├── js/main.js      # nav rendering, formatting helpers
│   └── *.html
├── seed.py             # Demo data loader (3 employers, 3 candidates, 5 jobs)
├── requirements.txt
└── manage.py
```

---

## Setup

### 1. Backend

```bash
cd jobportal
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser  # or just run the seed script below

python seed.py                    # optional: loads demo employers/candidates/jobs

python manage.py runserver
```

The API is now live at `http://127.0.0.1:8000/api/`. Admin panel: `http://127.0.0.1:8000/admin/`.

**Demo accounts created by `seed.py`** (password for all: `password123`):
- Employers: `nova_tech`, `skyline_labs`, `brightpath`
- Candidates: `zeeshan_dev`, `hina_codes`, `ali_data`
- Superuser: `admin` / `admin12345`

### 2. Frontend

The frontend is plain static files — serve them with anything:

```bash
cd frontend
python -m http.server 8080
```

Open `http://127.0.0.1:8080/index.html`. By default the frontend calls the API at `http://127.0.0.1:8000`.

**If your Django server runs on a different port** (e.g. you started it with `python manage.py runserver 2000`), update the single line in `frontend/js/config.js` to match — every page loads that file first, so it's the only place you need to change it.

> Visiting `http://127.0.0.1:8000/` directly in a browser now returns a small JSON status page confirming the API is running, with links to `/admin/` and `/api/`. That's expected — the real frontend lives in `frontend/index.html`, served separately.

---

## API reference

Base URL: `/api/`

### Auth (`/api/auth/`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `register/` | Create an employer or candidate account, returns JWT tokens |
| POST | `login/` | Log in, returns JWT tokens |
| POST | `token/refresh/` | Exchange a refresh token for a new access token |
| GET | `me/` | Current user + profile |
| GET/PATCH | `profile/employer/` | Employer's company profile |
| GET/PATCH | `profile/candidate/` | Candidate's profile |

### Jobs (`/api/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `listings/` | Search/browse open jobs. Filters: `keyword`, `location`, `category`, `job_type`, `experience_level`, `is_remote`, `salary_min`, `salary_max`, `company`. Paginated. |
| POST | `listings/` | Create a job (employer only) |
| GET | `listings/<slug>/` | Job detail |
| PATCH/DELETE | `listings/<slug>/` | Edit/delete (owning employer only) |
| GET | `listings/my_jobs/` | Employer's own postings |
| GET | `listings/<slug>/applicants/` | Applicants for a job (owning employer only) |
| GET/POST | `resumes/` | List / upload resumes (candidate only) |
| DELETE | `resumes/<id>/` | Delete a resume |
| GET/POST | `applications/` | List my applications / apply to a job |
| PATCH | `applications/<id>/status_update/` | Change an application's status (owning employer only) — notifies the candidate |
| GET | `stats/employer/` | Employer dashboard stats |
| GET | `stats/platform/` | Platform-wide stats (staff only) |

### Notifications (`/api/notifications/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | My notifications |
| PATCH | `<id>/mark_read/` | Mark one as read |
| PATCH | `mark_all_read/` | Mark all as read |

All authenticated endpoints expect `Authorization: Bearer <access_token>`.

---

## Data model

- **User** (custom, `role` = employer/candidate) → one-to-one with **EmployerProfile** or **CandidateProfile**
- **EmployerProfile** → many **JobListing**
- **CandidateProfile** → many **Resume**, many **Application**
- **JobListing** → many **Application**
- **Application** links a **JobListing**, a **CandidateProfile**, and a **Resume**, and carries a `status`
- **Notification** → belongs to a **User**, created automatically when an application is submitted or its status changes

---

## Notes for deployment

- `SECRET_KEY` and `DEBUG` in `config/settings.py` are set for local development — replace before deploying.
- Swap SQLite for Postgres by changing `DATABASES` in `config/settings.py`.
- `CORS_ALLOW_ALL_ORIGINS = True` is convenient for local dev; restrict it to your real frontend domain in production.
- Media uploads (resumes, logos, photos) are served from Django in dev; use S3/Cloud Storage in production.
