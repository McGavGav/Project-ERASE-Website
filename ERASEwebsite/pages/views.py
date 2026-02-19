from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    """Render the homepage"""
    return render(request, 'home.html')


def about(request):
    """Render the about page"""
    return render(request, 'about.html')


def contact(request):
    """Render the contact page"""
    return render(request, 'contact.html')
