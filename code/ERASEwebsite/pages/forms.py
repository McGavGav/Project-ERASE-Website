from django import forms
from django.contrib.auth.models import User
from .models import FundingEntry, WorkshopAttendance, StudentSupport, SocialMediaMetric

_date_input = {'type': 'date'}
_text_input = {'rows': 2}


class FundingEntryForm(forms.ModelForm):
    class Meta:
        model  = FundingEntry
        fields = ['date', 'source', 'fund_type', 'amount', 'notes']
        widgets = {
            'date':  forms.DateInput(attrs=_date_input),
            'notes': forms.Textarea(attrs=_text_input),
        }


class WorkshopAttendanceForm(forms.ModelForm):
    class Meta:
        model  = WorkshopAttendance
        fields = ['workshop_name', 'date', 'location', 'attendee_count', 'notes']
        widgets = {
            'date':  forms.DateInput(attrs=_date_input),
            'notes': forms.Textarea(attrs=_text_input),
        }


class StudentSupportForm(forms.ModelForm):
    class Meta:
        model  = StudentSupport
        fields = ['year', 'student_count', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs=_text_input),
        }


class SocialMediaMetricForm(forms.ModelForm):
    class Meta:
        model  = SocialMediaMetric
        fields = ['platform', 'date', 'followers', 'post_reach', 'engagement', 'notes']
        widgets = {
            'date':  forms.DateInput(attrs=_date_input),
            'notes': forms.Textarea(attrs=_text_input),
        }


class AccountEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'})
        }
