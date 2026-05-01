from datetime import datetime
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from event_calendar.models import Event
from event_calendar.forms import EventForm
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
    
    month_events = Event.objects.filter(date__year=current_year, date__month=current_month)
    events_by_date = {}
    for event in month_events:
        events_by_date.setdefault(event.date, []).append(event)
    
    calendar_html = get_calendar_html(current_year, current_month, events_by_date)

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

    event_form = EventForm()
    event_added = request.GET.get('event_added') == '1'

    context = {
        'calendar_html': calendar_html,
        'current_month': current_month,
        'current_year': current_year,
        'display_date': date(current_year, current_month, 1),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'event_form': event_form,
        'event_added': event_added,
    }

    return render(request, 'calendar.html', context)

@login_required
def add_event(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = EventForm(request.POST)

        if form.is_valid():
            form.save()
            month = form.cleaned_data['date'].month
            year = form.cleaned_data['date'].year

            return redirect(f"{reverse('pages:calendar')}?month={month}&year={year}&event_added=1")
    
    return redirect('pages:calendar')

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

@login_required
def manage_users(request):
    """Only the master account can grant/revoke admin privileges."""
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        target_id = request.POST.get('user_id')
        action = request.POST.get('action')
        target_user = get_object_or_404(User, pk=target_id)

        # Prevents the master account from being demoted
        if not target_user.is_superuser:
            if action == 'grant':
                target_user.is_staff = True
                target_user.save()
            elif action == 'revoke':
                target_user.is_staff = False
                target_user.save()

        return redirect('pages:manage_users')

    users = User.objects.exclude(pk=request.user.pk).order_by('username')
    return render(request, 'manage_users.html', {'users': users})

def shipment_map(request):
    return render(request, "shipment_map.html")

@login_required
def custom_admin(request):
    """Custom admin dashboard — accessible to staff and superusers only."""
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied

    total_users = User.objects.count()
    staff_count = User.objects.filter(is_staff=True, is_superuser=False).count()
    superuser_count = User.objects.filter(is_superuser=True).count()

    context = {
        'total_users': total_users,
        'staff_count': staff_count,
        'superuser_count': superuser_count,
    }
    return render(request, 'custom_admin.html', context)


@login_required
def reports(request):
    """Placeholder reports view for admins."""
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied

    context = {}
    return render(request, 'reports.html', context)

@login_required
def account(request):
    """Display the current user's account details."""
    user = request.user
    groups = user.groups.values_list('name', flat=True)
    if user.is_superuser:
        role = 'Master'
    elif user.is_staff:
        role = 'Admin'
    elif groups:
        role = ', '.join(groups)
    else:
        role = 'User'
    context = {
        'role': role,
    }
    return render(request, 'account.html', context)

@login_required
def delete_account(request):
    """Allow a non-superuser to delete their own account."""
    if request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        user = request.user
        from django.contrib.auth import logout
        logout(request)
        user.delete()
        return redirect('pages:home')

    return redirect('pages:account')