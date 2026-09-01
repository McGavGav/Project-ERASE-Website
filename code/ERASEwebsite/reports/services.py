from datetime import datetime
from django.db.models import Sum
from .models import FundingEntry, WorkshopAttendance, StudentSupport, SocialMediaMetric


class ReportsAnalyticsService:
    """Service class encapsulating metric aggregations and query operations for reports."""

    @staticmethod
    def get_fundraising_data(year_filter='', type_filter=''):
        funding_entries = FundingEntry.objects.all()
        if year_filter:
            funding_entries = funding_entries.filter(date__year=year_filter)
        if type_filter:
            funding_entries = funding_entries.filter(fund_type=type_filter)

        funding_total = funding_entries.aggregate(total=Sum('amount'))['total'] or 0
        donations_total = funding_entries.filter(fund_type='donation').aggregate(total=Sum('amount'))['total'] or 0
        grants_total = funding_entries.filter(fund_type='grant').aggregate(total=Sum('amount'))['total'] or 0

        funding_years = sorted(
            set(FundingEntry.objects.values_list('date__year', flat=True)),
            reverse=True
        )

        return {
            'funding_entries': funding_entries,
            'year_filter': year_filter,
            'type_filter': type_filter,
            'funding_years': funding_years,
            'funding_total': funding_total,
            'donations_total': donations_total,
            'grants_total': grants_total,
        }

    @staticmethod
    def get_workshops_data():
        workshops = WorkshopAttendance.objects.all()
        workshop_count = workshops.count()
        total_attendees = workshops.aggregate(total=Sum('attendee_count'))['total'] or 0
        avg_attendees = round(total_attendees / workshop_count, 1) if workshop_count else 0

        return {
            'workshops': workshops,
            'workshop_count': workshop_count,
            'total_attendees': total_attendees,
            'avg_attendees': avg_attendees,
        }

    @staticmethod
    def get_student_support_data():
        student_entries = StudentSupport.objects.all()
        current_year = datetime.now().year
        current_year_students = (
            StudentSupport.objects.filter(year=current_year)
            .aggregate(total=Sum('student_count'))['total'] or 0
        )
        all_time_students = StudentSupport.objects.aggregate(total=Sum('student_count'))['total'] or 0

        return {
            'student_entries': student_entries,
            'current_year': current_year,
            'current_year_students': current_year_students,
            'all_time_students': all_time_students,
        }

    @staticmethod
    def get_social_media_data(platform_filter=''):
        social_entries = SocialMediaMetric.objects.all()
        if platform_filter:
            social_entries = social_entries.filter(platform=platform_filter)

        return {
            'social_entries': social_entries,
            'platform_filter': platform_filter,
            'platform_choices': SocialMediaMetric.PLATFORM_CHOICES,
        }

