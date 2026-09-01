from django.urls import path
from .views import (
    ReportsDashboardView,
    DeleteFundingView,
    DeleteWorkshopAttendanceView,
    DeleteStudentSupportView,
    DeleteSocialMediaView,
)

app_name = 'reports'

urlpatterns = [
    path('reports/', ReportsDashboardView.as_view(), name='reports'),
    path('reports/delete-funding/<int:pk>/', DeleteFundingView.as_view(), name='delete_funding'),
    path('reports/delete-workshop/<int:pk>/', DeleteWorkshopAttendanceView.as_view(), name='delete_workshop'),
    path('reports/delete-student/<int:pk>/', DeleteStudentSupportView.as_view(), name='delete_student'),
    path('reports/delete-social/<int:pk>/', DeleteSocialMediaView.as_view(), name='delete_social'),
]

