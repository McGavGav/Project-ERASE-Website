from calendar import month_name
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from event_calendar.calendar_maker import get_calendar_html

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
            user = form.save()

            # users automatically into normal user perms
            normal_users_group, _ = Group.objects.get_or_create(name='normal users')
            normal_users_group.user_set.add(user)

            return redirect('pages:login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def calendar(request):
    """Render the calendar page"""
    # Get the current month and year.
    now = datetime.now()
    current_month = request.GET.get('month', now.month)
    current_year = request.GET.get('year', now.year)

    try:
        current_month = int(current_month)
        current_year = int(current_year)
    except (ValueError, TypeError):
        current_month = now.month
        current_year = now.year
    
    calendar_html = get_calendar_html(current_year, current_month)

    if current_month == 1:
        prev_month = 12
        prev_year = current_year - 1
    else:
        prev_month = current_month - 1
        prev_year = current_year
    
    if current_month == 12:
        next_month = 1
        next_year = current_year + 1
    else:
        next_month = current_month + 1
        next_year = current_year

    calendar_month = month_name[current_month]

    context = {
        'calendar_html': calendar_html,
        'current_month': current_month,
        'current_year': current_year,
        'month_name': calendar_month,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }

    return render(request, 'calendar.html', context)



def studentdb(request):
    # temp data to test database view.
    students = [
        {"name": "Anne", "gender": "Female", "school": "Washington State University", "photo": None},
        {"name": "Tim", "gender": "Male", "school": "Lincoln Primary", "photo": None},
        {"name": "Emma", "gender": "Female", "school": "Washington Middle School", "photo": None},
        {"name": "Daniel", "gender": "Male", "school": "Franklin High", "photo": None},
    ]
    
    search_query = request.GET.get("search", "")
    gender_filter = request.GET.get("gender", "")
    school_filter = request.GET.get("school", "")

    filtered_students = []

    for student in students:
        if search_query and search_query.lower() not in student["name"].lower():
            continue

        if gender_filter and student["gender"] != gender_filter:
            continue

        if school_filter and school_filter.lower() not in student["school"].lower():
            continue

        filtered_students.append(student)

    context = {
        "students": filtered_students,
        "search_query": search_query,
        "gender_filter": gender_filter,
        "school_filter": school_filter
    }

    return render(request, "studentdb.html", context)

class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'login.html'
    redirect_authenticated_user = False
