from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'time', 'description', 'hasRSVP']
        labels = {
            'hasRSVP': 'Enable RSVP list?'
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'hasRSVP': forms.CheckboxInput()
        }