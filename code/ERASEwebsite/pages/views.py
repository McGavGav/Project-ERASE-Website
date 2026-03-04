from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm

def home(request):
    """Render the homepage"""
    return render(request, 'home.html')


def about(request):
    """Render the about page"""
    return render(request, 'about.html')


def contact(request):
    """Render the contact page"""
    return render(request, 'contact.html')


def signup(request):
    """Handle user sign-up"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pages:login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'login.html'
    redirect_authenticated_user = False
