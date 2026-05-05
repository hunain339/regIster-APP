# EventHub — Event Registration System

A full-stack Django event registration platform.

## Stack
- **Backend**: Django 5.2 + Django REST Framework
- **Database**: SQLite3
- **Frontend**: Django Templates + Tailwind CSS + Vanilla JS
- **Auth**: DRF Token Authentication
- **Email**: Django email backend (HTML + plain-text)

## Features
- Browse events with infinite scroll & search
- Register for events with capacity enforcement
- Email confirmation on registration & cancellation
- My Registrations page with cancel support
- Django admin panel with bulk actions
- Rate limiting, CORS, optimised queries

## Setup
```bash
pip install -r requirements.txt
cd eventregistration
python manage.py migrate
python manage.py seed_events        # demo data
python manage.py createsuperuser    # admin account
python manage.py runserver
```

## API Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/events/` | Paginated event list |
| GET | `/api/events/<id>/` | Event detail |
| POST | `/api/registrations/` | Register for event |
| GET | `/api/registrations/` | My registrations |
| DELETE | `/api/registrations/<id>/` | Cancel registration |
| POST | `/api/token-auth/` | Get auth token |

## Demo credentials
- User: `demo` / `demo1234`
- Admin: `admin` / `admin1234`
