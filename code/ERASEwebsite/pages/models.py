from django.db import models
import os

class StudentQuerySet(models.QuerySet):
    def search(self, query):
        if query:
            return self.filter(name__icontains=query)
        return self

    def filter_gender(self, gender):
        if gender:
            return self.filter(gender=gender)
        return self

    def filter_school(self, school):
        if school:
            return self.filter(school__icontains=school)
        return self

    def apply_filters(self, search=None, gender=None, school=None):
        return (
            self.search(search)
            .filter_gender(gender)
            .filter_school(school)
        )

class StudentManager(models.Manager):
    def get_queryset(self):
        return StudentQuerySet(self.model, using=self._db)

    def apply_filters(self, *args, **kwargs):
        return self.get_queryset().apply_filters(*args, **kwargs)

class Student(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    school = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='students', blank=True, null=True)

    objects = StudentManager() 

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        if self.photo and os.path.isfile(self.photo.path):
            os.remove(self.photo.path)
        super().delete(*args, **kwargs)


class FundingEntry(models.Model):
    FUND_TYPE_CHOICES = [
        ('donation', 'Donation'),
        ('grant',    'Grant'),
        ('other',    'Other'),
    ]

    date      = models.DateField()
    source    = models.CharField(max_length=255, help_text='Donor or grant name')
    fund_type = models.CharField(max_length=20, choices=FUND_TYPE_CHOICES, default='donation')
    amount    = models.DecimalField(max_digits=10, decimal_places=2)
    notes     = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.source} ({self.get_fund_type_display()}) – ${self.amount} ({self.date})"


class WorkshopAttendance(models.Model):
    workshop_name  = models.CharField(max_length=255)
    date           = models.DateField()
    location       = models.CharField(max_length=255, blank=True)
    attendee_count = models.PositiveIntegerField(default=0)
    notes          = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.workshop_name} ({self.date}) – {self.attendee_count} attendees"


class StudentSupport(models.Model):
    year          = models.PositiveIntegerField()
    student_count = models.PositiveIntegerField()
    notes         = models.TextField(blank=True)

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return f"{self.year} – {self.student_count} students"


class SocialMediaMetric(models.Model):
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook',  'Facebook'),
        ('twitter',   'Twitter/X'),
        ('linkedin',  'LinkedIn'),
        ('other',     'Other'),
    ]

    platform   = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    date       = models.DateField()
    followers  = models.PositiveIntegerField(null=True, blank=True)
    post_reach = models.PositiveIntegerField(null=True, blank=True)
    engagement = models.PositiveIntegerField(null=True, blank=True,
                    help_text='Total likes, shares, and comments')
    notes      = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_platform_display()} – {self.date}"
