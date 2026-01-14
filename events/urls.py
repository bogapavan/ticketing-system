from django.urls import path
from .views import CreateEventView, BookTicketView, CancelTicketView

urlpatterns = [
    path("events/", CreateEventView.as_view()),
    path("events/<int:event_id>/book/", BookTicketView.as_view()),
    path("events/<int:event_id>/cancel/", CancelTicketView.as_view()),
]
