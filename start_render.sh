#!/bin/bash
set -e

echo "--- Applying migrations ---"
python manage.py migrate

echo "--- Collecting static files ---"
python manage.py collectstatic --noinput

echo "--- Checking if database needs seeding ---"
python - <<'EOF'
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diary_project.settings')
django.setup()
from accounts.models import User
if not User.objects.filter(is_superuser=True).exists():
    from django.core.management import call_command
    print("Database is empty — running seed...")
    call_command('seed_data')
    print("Seed complete.")
else:
    print("Database already has data — skipping seed.")
EOF

echo "--- Starting server ---"
exec gunicorn diary_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --log-level info
