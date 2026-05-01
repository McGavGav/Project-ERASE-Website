from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
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
    path('calendar/add-event/', views.add_event, name='add_event'),
    path('calendar/rsvp/<int:event_id>/', views.rsvp_event, name='rsvp_event'),
    path('rsvp-listing/', views.rsvp_listing, name='rsvp_listing'),
    path('rsvp-listing/<int:event_id>/', views.rsvp_detail, name='rsvp_detail'),
    path('shipment-map/', views.shipment_map, name='shipment_map'),
    path('studentdb/', views.studentdb, name='studentdb'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('account/', views.account, name='account'),
    path('account/delete/', views.delete_account, name='delete_account'),
    path('admin-panel/', views.custom_admin, name='custom_admin'),
    path('reports/', views.reports, name='reports'),
    path('reports/delete-funding/<int:pk>/',  views.delete_funding,  name='delete_funding'),
    path('reports/delete-workshop/<int:pk>/', views.delete_workshop, name='delete_workshop'),
    path('reports/delete-student/<int:pk>/',  views.delete_student,  name='delete_student'),
    path('reports/delete-social/<int:pk>/',   views.delete_social,   name='delete_social'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)