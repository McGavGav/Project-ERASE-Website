import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
from pages.models import Workshop
print('Workshops:', Workshop.objects.count())