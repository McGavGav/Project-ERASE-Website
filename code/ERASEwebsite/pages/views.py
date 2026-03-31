from calendar import month_name
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from event_calendar.calendar_maker import get_calendar_html
from .models import Student

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

    # admin/supers can add and delete students
    if request.method == "POST" and (request.user.is_staff or request.user.is_superuser):
        action = request.POST.get("action")

        if action == "add":
            Student.objects.create(
                name=request.POST.get("name"),
                gender=request.POST.get("gender"),
                school=request.POST.get("school"),
                photo=request.FILES.get("photo")
            )

        elif action == "delete":
            student = Student.objects.filter(
                name=request.POST.get("student_name")
            )

            for s in student:
                s.delete()

        return redirect("pages:studentdb")

    students = Student.objects.apply_filters(
        search=request.GET.get("search"),
        gender=request.GET.get("gender"),
        school=request.GET.get("school")
    )

    return render(request, "studentdb.html", {
        "students": students,
        "search_query": request.GET.get("search", ""),
        "gender_filter": request.GET.get("gender", ""),
        "school_filter": request.GET.get("school", "")
    })

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