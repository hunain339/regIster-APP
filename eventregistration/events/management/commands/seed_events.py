"""
Management command: seed_events
Creates sample events and a test user for development/demo purposes.
Usage: python manage.py seed_events
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from events.models import Event, Registration


SAMPLE_EVENTS = [
    {
        "title": "Tech Conference 2025",
        "description": (
            "Join us for the premier technology conference of the year, "
            "featuring keynotes from industry leaders, hands-on workshops, "
            "and unparalleled networking opportunities. Covering AI, "
            "cloud computing, cybersecurity, and the future of software development."
        ),
        "location": "San Francisco Convention Center, CA",
        "capacity": 500,
        "days_from_now": 30,
    },
    {
        "title": "Python & Django Workshop",
        "description": (
            "A full-day intensive workshop covering Django REST Framework, "
            "async Django, testing best practices, deployment strategies, "
            "and building production-ready APIs. Bring your laptop — "
            "this is a hands-on coding session."
        ),
        "location": "Downtown Coding Hub, New York",
        "capacity": 50,
        "days_from_now": 14,
    },
    {
        "title": "UX Design Bootcamp",
        "description": (
            "Three days of deep-dive UX design training. Learn user research "
            "methodologies, Figma prototyping, design systems, accessibility "
            "standards, and how to present designs to stakeholders. "
            "Certificate awarded on completion."
        ),
        "location": "Creative Studio, Austin TX",
        "capacity": 30,
        "days_from_now": 21,
    },
    {
        "title": "Startup Pitch Night",
        "description": (
            "Watch 10 early-stage startups pitch their ideas to a panel of "
            "investors and industry veterans. Networking reception follows. "
            "Open to founders, investors, and anyone passionate about the "
            "startup ecosystem."
        ),
        "location": "Innovation Hub, Seattle WA",
        "capacity": 200,
        "days_from_now": 7,
    },
    {
        "title": "Data Science Summit",
        "description": (
            "Two days of talks and workshops on machine learning, data engineering, "
            "MLOps, large language models, and real-world data science case studies "
            "from companies like Google, OpenAI, and Stripe."
        ),
        "location": "Chicago Tech Center, IL",
        "capacity": 300,
        "days_from_now": 45,
    },
    {
        "title": "Cybersecurity Forum",
        "description": (
            "Explore the latest threats, defences, and compliance requirements "
            "in cybersecurity. Sessions on zero-trust architecture, penetration "
            "testing, incident response, and securing cloud infrastructure."
        ),
        "location": "Security Ops Center, Washington DC",
        "capacity": 150,
        "days_from_now": 60,
    },
    {
        "title": "React & Frontend Masterclass",
        "description": (
            "Level up your frontend skills with advanced React patterns, "
            "performance optimisation, state management with Zustand, "
            "server components, and building design systems with Tailwind CSS."
        ),
        "location": "Developer Hub, Los Angeles CA",
        "capacity": 40,
        "days_from_now": 10,
    },
    {
        "title": "Cloud Architecture Workshop",
        "description": (
            "Hands-on AWS and GCP workshop covering microservices architecture, "
            "serverless functions, container orchestration with Kubernetes, "
            "CI/CD pipelines, and infrastructure-as-code with Terraform."
        ),
        "location": "Cloud Campus, Denver CO",
        "capacity": 60,
        "days_from_now": 35,
    },
    {
        "title": "Open Source Hackathon",
        "description": (
            "48-hour hackathon contributing to popular open source projects. "
            "All skill levels welcome — from first PR to seasoned maintainer. "
            "Prizes, mentorship, and great vibes guaranteed."
        ),
        "location": "Hacker House, Portland OR",
        "capacity": 100,
        "days_from_now": 18,
    },
    {
        "title": "Product Management Forum",
        "description": (
            "A curated day for PMs at all levels. Talks on roadmap prioritisation, "
            "working with engineering teams, metrics-driven product development, "
            "and the future of AI-assisted product management."
        ),
        "location": "Business Innovation Center, Boston MA",
        "capacity": 80,
        "days_from_now": 25,
    },
    {
        "title": "Mobile Dev Conference (Past)",
        "description": "Annual mobile development conference covering iOS, Android, and cross-platform frameworks.",
        "location": "Tech Campus, Miami FL",
        "capacity": 250,
        "days_from_now": -10,  # Past event
    },
    {
        "title": "AI & Ethics Symposium",
        "description": (
            "Critical conversations on responsible AI development, bias in machine learning, "
            "privacy regulations, and the societal impact of autonomous systems. "
            "Featuring academics, policymakers, and practitioners."
        ),
        "location": "University Hall, Cambridge MA",
        "capacity": 5,  # Nearly full for demo
        "days_from_now": 12,
    },
]


class Command(BaseCommand):
    help = "Seeds the database with sample events and a test user."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database…")

        # ---- Create demo user ----
        if not User.objects.filter(username='demo').exists():
            user = User.objects.create_user(
                username='demo',
                password='demo1234',
                email='demo@eventhub.com',
                first_name='Demo',
                last_name='User',
            )
            self.stdout.write(self.style.SUCCESS("  Created user: demo / demo1234"))
        else:
            user = User.objects.get(username='demo')
            self.stdout.write("  User 'demo' already exists — skipping.")

        # ---- Create events ----
        now = timezone.now()
        created_count = 0

        for data in SAMPLE_EVENTS:
            if Event.objects.filter(title=data['title']).exists():
                continue

            event = Event.objects.create(
                title=data['title'],
                description=data['description'],
                date=now + timedelta(days=data['days_from_now']),
                location=data['location'],
                capacity=data['capacity'],
            )
            created_count += 1

            # Add a few sample registrations to make capacity bars non-empty
            sample_names = [
                ('Alice Johnson', 'alice@example.com'),
                ('Bob Martinez', 'bob@example.com'),
                ('Carol White', 'carol@example.com'),
            ]
            reg_count = random.randint(0, min(3, data['capacity']))
            for name, email in sample_names[:reg_count]:
                Registration.objects.get_or_create(
                    event=event,
                    email=email,
                    defaults={'name': name, 'is_cancelled': False}
                )

        self.stdout.write(self.style.SUCCESS(f"  Created {created_count} event(s)."))

        # ---- Create a sample registration for demo user ----
        first_event = Event.objects.first()
        if first_event and not Registration.objects.filter(user=user, event=first_event).exists():
            Registration.objects.create(
                event=first_event,
                user=user,
                name='Demo User',
                email='demo@eventhub.com',
                phone='+1 555 000 0000',
            )
            self.stdout.write(f"  Added demo registration for '{first_event.title}'")

        self.stdout.write(self.style.SUCCESS("\nDone! Login at /login/ with:  demo / demo1234"))
        self.stdout.write(self.style.SUCCESS("Admin panel at /admin/ (create a superuser first with createsuperuser)"))
