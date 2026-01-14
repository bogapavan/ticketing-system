from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=255)
    total_tickets = models.PositiveIntegerField()
    available_tickets = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    tickets_booked = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user_id")
