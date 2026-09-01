from django import forms
from django.contrib.auth.models import User


class AccountEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'})
        }
