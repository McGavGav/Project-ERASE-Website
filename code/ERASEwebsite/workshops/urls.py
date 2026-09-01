from django.urls import path
from .views import ShipmentMapView

app_name = 'workshops'

urlpatterns = [
    path('shipment-map/', ShipmentMapView.as_view(), name='shipment_map'),
]

