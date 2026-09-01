"""
Pages app models.

Domain models have been refactored into dedicated apps:
- Student models -> students.models
- Workshop models -> workshops.models
- Reporting & Analytics models -> reports.models
"""
from students.models import Student, StudentManager, StudentQuerySet
from workshops.models import Workshop
from reports.models import FundingEntry, WorkshopAttendance, StudentSupport, SocialMediaMetric

__all__ = [
    'Student',
    'StudentManager',
    'StudentQuerySet',
    'Workshop',
    'FundingEntry',
    'WorkshopAttendance',
    'StudentSupport',
    'SocialMediaMetric',
]
