from django.urls import path
from .views import StudentDatabaseView

app_name = 'students'

urlpatterns = [
    path('studentdb/', StudentDatabaseView.as_view(), name='studentdb'),
]

