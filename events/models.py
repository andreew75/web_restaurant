from django.contrib.auth.models import User
from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Event Title")
    description = models.TextField(verbose_name="Event Description")
    date = models.DateField(verbose_name="Event Date")
    location = models.CharField(max_length=200, verbose_name="Event Location")
    start_time = models.TimeField(verbose_name="Event Start Time")
    image = models.ImageField(upload_to='event_images/', verbose_name="Event Image")
    is_active = models.BooleanField(verbose_name="Event Active", default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Event Created At")

    class Meta:
        verbose_name = "События"
        verbose_name_plural = "События"
        ordering = ['-date']

    def __str__(self):
        return self.title
