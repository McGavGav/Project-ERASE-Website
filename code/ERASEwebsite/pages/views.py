from calendar import month_name
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from .models import FundingEntry, WorkshopAttendance, StudentSupport, SocialMediaMetric
from .forms import FundingEntryForm, WorkshopAttendanceForm, StudentSupportForm, SocialMediaMetricForm, AccountEmailForm
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
    """Reports dashboard — fundraising, workshops, students, and social media."""
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied

    funding_form  = FundingEntryForm()
    workshop_form = WorkshopAttendanceForm()
    student_form  = StudentSupportForm()
    social_form   = SocialMediaMetricForm()
    active_tab    = request.GET.get('tab', 'fundraising')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'funding':
            funding_form = FundingEntryForm(request.POST)
            if funding_form.is_valid():
                funding_form.save()
                messages.success(request, 'Funding entry added.')
                return redirect(reverse('pages:reports') + '?tab=fundraising')
            active_tab = 'fundraising'
        elif form_type == 'workshop':
            workshop_form = WorkshopAttendanceForm(request.POST)
            if workshop_form.is_valid():
                workshop_form.save()
                messages.success(request, 'Workshop record added.')
                return redirect(reverse('pages:reports') + '?tab=workshops')
            active_tab = 'workshops'
        elif form_type == 'student':
            student_form = StudentSupportForm(request.POST)
            if student_form.is_valid():
                student_form.save()
                messages.success(request, 'Student support entry added.')
                return redirect(reverse('pages:reports') + '?tab=students')
            active_tab = 'students'
        elif form_type == 'social':
            social_form = SocialMediaMetricForm(request.POST)
            if social_form.is_valid():
                social_form.save()
                messages.success(request, 'Social media entry added.')
                return redirect(reverse('pages:reports') + '?tab=social')
            active_tab = 'social'

    # --- Fundraising ---
    year_filter = request.GET.get('year', '')
    type_filter = request.GET.get('fund_type', '')
    funding_entries = FundingEntry.objects.all()
    if year_filter:
        funding_entries = funding_entries.filter(date__year=year_filter)
    if type_filter:
        funding_entries = funding_entries.filter(fund_type=type_filter)
    funding_total   = funding_entries.aggregate(total=Sum('amount'))['total'] or 0
    donations_total = funding_entries.filter(fund_type='donation').aggregate(total=Sum('amount'))['total'] or 0
    grants_total    = funding_entries.filter(fund_type='grant').aggregate(total=Sum('amount'))['total'] or 0
    # Build year list from all entries for the filter dropdown
    funding_years = sorted(
        set(FundingEntry.objects.values_list('date__year', flat=True)),
        reverse=True
    )

    # --- Workshops ---
    workshops       = WorkshopAttendance.objects.all()
    workshop_count  = workshops.count()
    total_attendees = workshops.aggregate(total=Sum('attendee_count'))['total'] or 0
    avg_attendees   = round(total_attendees / workshop_count, 1) if workshop_count else 0

    # --- Students Supported ---
    student_entries      = StudentSupport.objects.all()
    current_year         = datetime.now().year
    current_year_students = (
        StudentSupport.objects.filter(year=current_year)
        .aggregate(total=Sum('student_count'))['total'] or 0
    )
    all_time_students = StudentSupport.objects.aggregate(total=Sum('student_count'))['total'] or 0

    # --- Social Media ---
    platform_filter = request.GET.get('platform', '')
    social_entries  = SocialMediaMetric.objects.all()
    if platform_filter:
        social_entries = social_entries.filter(platform=platform_filter)

    context = {
        'funding_form':  funding_form,
        'workshop_form': workshop_form,
        'student_form':  student_form,
        'social_form':   social_form,
        'active_tab':    active_tab,
        # fundraising
        'funding_entries':  funding_entries,
        'year_filter':      year_filter,
        'type_filter':      type_filter,
        'funding_years':    funding_years,
        'funding_total':    funding_total,
        'donations_total':  donations_total,
        'grants_total':     grants_total,
        # workshops
        'workshops':        workshops,
        'workshop_count':   workshop_count,
        'total_attendees':  total_attendees,
        'avg_attendees':    avg_attendees,
        # students
        'student_entries':        student_entries,
        'current_year':           current_year,
        'current_year_students':  current_year_students,
        'all_time_students':      all_time_students,
        # social media
        'social_entries':   social_entries,
        'platform_filter':  platform_filter,
        'platform_choices': SocialMediaMetric.PLATFORM_CHOICES,
    }
    return render(request, 'reports.html', context)


@login_required
def delete_funding(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    entry = get_object_or_404(FundingEntry, pk=pk)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Funding entry deleted.')
    return redirect(reverse('pages:reports') + '?tab=fundraising')


@login_required
def delete_workshop(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    workshop = get_object_or_404(WorkshopAttendance, pk=pk)
    if request.method == 'POST':
        workshop.delete()
        messages.success(request, 'Workshop record deleted.')
    return redirect(reverse('pages:reports') + '?tab=workshops')


@login_required
def delete_student(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    entry = get_object_or_404(StudentSupport, pk=pk)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Student support entry deleted.')
    return redirect(reverse('pages:reports') + '?tab=students')


@login_required
def delete_social(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    entry = get_object_or_404(SocialMediaMetric, pk=pk)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Social media entry deleted.')
    return redirect(reverse('pages:reports') + '?tab=social')

@login_required
def account(request):
    """Display the current user's account details."""
    user = request.user

    if request.method == 'POST':
        email_form = AccountEmailForm(request.POST, instance=user)
        if email_form.is_valid():
            email_form.save()
            messages.success(request, 'Email updated successfully.')
            return redirect('pages:account')
    else:
        email_form = AccountEmailForm(instance=user)

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
        'email_form': email_form,
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