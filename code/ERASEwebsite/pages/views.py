from calendar import month_name
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from event_calendar.calendar_maker import get_calendar_html
from .models import Workshop

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

def shipment_map(request):
    if request.method == 'POST':
        print(f"DEBUG: POST request received. User authenticated: {request.user.is_authenticated}, is_staff: {request.user.is_staff if request.user.is_authenticated else 'N/A'}")
        # Check for delete request first (AJAX)
        delete_workshop_id = request.POST.get('delete_workshop')
        print(f"DEBUG: delete_workshop_id: {delete_workshop_id}")
        if delete_workshop_id:
            print("DEBUG: Processing delete request")
            if not (request.user.is_authenticated and request.user.is_staff):
                print("DEBUG: User not authenticated or not staff")
                return JsonResponse({'success': False, 'error': 'Authentication required'})
            try:
                workshop = Workshop.objects.get(id=int(delete_workshop_id))
                print(f"DEBUG: Found workshop: {workshop.title}, deleting...")
                workshop.delete()
                print("DEBUG: Workshop deleted successfully")
                return JsonResponse({'success': True})
            except (Workshop.DoesNotExist, ValueError) as e:
                print(f"DEBUG: Error deleting workshop: {e}")
                return JsonResponse({'success': False, 'error': 'Workshop not found'})

        # Regular POST requests require authentication
        if not (request.user.is_authenticated and request.user.is_staff):
            return redirect('pages:login')

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        date = request.POST.get('date')
        city = request.POST.get('city', '').strip()
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        photo = request.FILES.get('photo')

        if title and date and latitude and longitude:
            Workshop.objects.create(
                title=title,
                description=description,
                date=date,
                city=city,
                latitude=float(latitude),
                longitude=float(longitude),
                photo=photo,
                created_by=request.user,
            )
        return redirect('pages:shipment_map')

    workshops = Workshop.objects.all()
    workshop_markers = []
    for workshop in workshops:
        marker = {
            'id': workshop.id,
            'title': workshop.title,
            'description': workshop.description,
            'date': workshop.date.strftime('%Y-%m-%d'),
            'city': workshop.city,
            'latitude': workshop.latitude,
            'longitude': workshop.longitude,
            'address': workshop.city,
            'photos': [workshop.photo.url] if workshop.photo else [],
        }
        workshop_markers.append(marker)
    return render(request, "shipment_map.html", {
        "workshop_markers_json": json.dumps(workshop_markers),
        "show_add_pin": request.user.is_authenticated and request.user.is_staff,
    })
