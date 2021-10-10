import os
import sys
from django.db import transaction
from django.core.management import call_command
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
with transaction.atomic():
    call_command('loaddata', sys.argv[1])
