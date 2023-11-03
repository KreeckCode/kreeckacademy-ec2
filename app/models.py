from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.db.models import Q

NEWS = "News"
EVENTS = "Event"

POST = (
    (NEWS, "News"),
    (EVENTS, "Event"),
)

FIRST = "First"
SECOND = "Second"
THIRD = "Third"

SEMESTER = (
    (FIRST, "First"),
    (SECOND, "Second"),
    (THIRD, "Third"),
)


class NewsAndEventsQuerySet(models.query.QuerySet):

    def search(self, query):
        lookups = (Q(title__icontains=query) | 
                  Q(summary__icontains=query) |
                  Q(posted_as__icontains=query)
                  )
        return self.filter(lookups).distinct()


class NewsAndEventsManager(models.Manager):
    def get_queryset(self):
        return NewsAndEventsQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id) # NewsAndEvents.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().search(query)


class NewsAndEvents(models.Model):
    title = models.CharField(max_length=200, null=True)
    summary = models.TextField(max_length=200, blank=True, null=True)
    posted_as = models.CharField(choices=POST, max_length=10)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)

    objects = NewsAndEventsManager()

    def __str__(self):
        return self.title


class Session(models.Model):
    session = models.CharField(max_length=200, unique=True)
    is_current_session = models.BooleanField(default=False, blank=True, null=True)
    next_session_begins = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.session


class Semester(models.Model):
    semester = models.CharField(max_length=10, choices=SEMESTER, blank=True)
    is_current_semester = models.BooleanField(default=False, blank=True, null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, blank=True, null=True)
    next_semester_begins = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.semester
    
class Landing(models.Model):
    body_Color = models.TextField(max_length=500, blank=True, null=True)
    Hero_Title = models.CharField(max_length=200, blank=True, null=True)
    Hero_Content = models.CharField(max_length=200, blank=True, null=True)
    Supporter_Logo = models.FileField(upload_to='LandingPage/', validators=[FileExtensionValidator(['svg', 'png'])])
    Course_Top_Card = models.FileField(upload_to='LandingPage/', validators=[FileExtensionValidator(['svg', 'png', 'jpg', 'jpeg'])])
    
    #Why Choose Us Section
    why_choose_Us = models.CharField(max_length=300, blank=True, null=True)
    why_choose_us_img = models.FileField(upload_to='LandingPage/', validators=[FileExtensionValidator(['svg', 'png', 'jpg', 'jpeg'])])