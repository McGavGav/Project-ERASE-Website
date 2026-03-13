from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='pages:home'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('calendar/', views.calendar, name='calendar'),
    path('studentdb/', views.studentdb, name='studentdb')
]
