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
]
