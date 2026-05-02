import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
from pages.models import Workshop
print('Total workshops:', Workshop.objects.count())
for workshop in Workshop.objects.all():
    print(f'ID: {workshop.id}, Title: {workshop.title}')