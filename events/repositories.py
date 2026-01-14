from .models import Event, Booking

class EventRepository:
    @staticmethod
    def lock_event(event_id):
        return Event.objects.select_for_update().get(id=event_id)

class BookingRepository:
    @staticmethod
    def get(event, user_id):
        return Booking.objects.filter(event=event, user_id=user_id).first()
