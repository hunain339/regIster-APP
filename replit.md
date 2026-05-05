# Workspace

## Overview

pnpm workspace monorepo using TypeScript — plus a standalone **Django Event Registration System** at `eventregistration/`.

## Stack

### Django App (primary — `eventregistration/`)
- **Framework**: Django 5.2 + Django REST Framework 3.17
- **Database**: SQLite3 (file: `eventregistration/db.sqlite3`)
- **Authentication**: DRF Token Auth + Django Session Auth
- **Frontend**: Django templates + Tailwind CSS CDN + Vanilla JS (fetch API)
- **CORS**: django-cors-headers
- **Rate limiting**: DRF throttling (10 reg/min, 30 anon/min, 60 user/min)

### Node.js Monorepo (pre-existing)
- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)

## Key Commands

### Django
- `cd eventregistration && python manage.py runserver 0.0.0.0:8000` — run Django dev server
- `cd eventregistration && python manage.py migrate` — run all migrations
- `cd eventregistration && python manage.py makemigrations events` — create new migrations
- `cd eventregistration && python manage.py seed_events` — seed sample data
- `cd eventregistration && python manage.py createsuperuser` — create admin user

### Node.js (pnpm workspace)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec

## Django Project Structure

```
eventregistration/
├── manage.py
├── db.sqlite3                       # SQLite3 database
├── eventregistration/
│   ├── settings.py                  # Django settings
│   ├── urls.py                      # Root URL config
│   └── wsgi.py
├── events/
│   ├── models.py                    # Event, Registration models
│   ├── serializers.py               # DRF serializers
│   ├── views.py                     # API ViewSets + template views
│   ├── urls.py                      # HTML page URLs
│   ├── api_urls.py                  # REST API URLs
│   ├── admin.py                     # Admin panel config
│   └── management/commands/
│       └── seed_events.py           # Demo data seeder
├── templates/
│   ├── base.html                    # Base template + nav
│   ├── events/
│   │   ├── list.html                # Event list (infinite scroll)
│   │   ├── detail.html              # Event detail + registration form
│   │   └── my_registrations.html   # User's registrations
│   └── registration/
│       └── login.html               # Login page
└── static/
    ├── css/custom.css               # Custom styles + badge classes
    └── js/utils.js                  # Shared JS utilities
```

## API Endpoints

| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET | `/api/events/` | Paginated event list (10/page) | Public |
| GET | `/api/events/<id>/` | Event detail | Public |
| POST | `/api/registrations/` | Register for event | Required |
| GET | `/api/registrations/` | List my registrations | Required |
| DELETE | `/api/registrations/<id>/` | Cancel registration | Required |
| POST | `/api/token-auth/` | Get auth token | Public |

## Frontend Pages

| URL | Description |
|-----|-------------|
| `/events/` | Event list with infinite scroll + search |
| `/events/<id>/` | Event detail + registration form |
| `/events/my-registrations/` | My registrations + cancel |
| `/login/` | Login page |
| `/admin/` | Django admin panel |

## Demo Credentials

- **User**: `demo` / `demo1234`
- **Admin**: `admin` / `admin1234`

## Security Features

- Token-based API auth (DRF TokenAuthentication)
- Users can only cancel their own registrations (queryset filtering)
- Capacity check before registration (serializer validation)
- Duplicate registration prevention per email+event
- Email validation (Django EmailField + serializer normalisation)
- Rate limiting: 10 registrations/min, 30 anon/min, 60 user/min
- CORS configured via django-cors-headers
- Optimised queries: `select_related` + `prefetch_related` used throughout
- Admin: bulk cancel/restore actions, inline registration display
