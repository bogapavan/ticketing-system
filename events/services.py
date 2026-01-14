from django.db import transaction
from django.db.models import F
from .repositories import EventRepository, BookingRepository
from .models import Booking

class TicketService:

    @staticmethod
    @transaction.atomic
    def book(event_id, user_id, tickets):
        event = EventRepository.lock_event(event_id)

        booking = BookingRepository.get(event, user_id)
        already = booking.tickets_booked if booking else 0

        if already + tickets > 2:
            raise ValueError("Max 2 tickets per user")

        if event.available_tickets < tickets:
            raise ValueError("Tickets sold out")

        if booking:
            booking.tickets_booked += tickets
            booking.save()
        else:
            Booking.objects.create(
                event=event,
                user_id=user_id,
                tickets_booked=tickets
            )

        event.available_tickets = F("available_tickets") - tickets
        event.save()

    @staticmethod
    @transaction.atomic
    def cancel(event_id, user_id):
        event = EventRepository.lock_event(event_id)
        booking = BookingRepository.get(event, user_id)

        if not booking:
            raise ValueError("No booking found")

        event.available_tickets = F("available_tickets") + booking.tickets_booked
        event.save()
        booking.delete()
