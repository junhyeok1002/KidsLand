from django.db import models

class Reservation(models.Model):
    timestamp = models.TextField()
    is_OK = models.TextField()
    child_name = models.TextField()
    child_birth = models.TextField()
    reservation_date = models.TextField()
    reservation_time = models.TextField()
    parents_number = models.TextField()
    status = models.TextField()

class LogHistory(models.Model):
    timestamp = models.TextField()
    is_OK = models.TextField()
    child_name = models.TextField()
    child_birth = models.TextField()
    reservation_date = models.TextField()
    reservation_time = models.TextField()
    parents_number = models.TextField()
    status = models.TextField()