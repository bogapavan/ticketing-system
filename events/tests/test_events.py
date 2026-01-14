
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient

from events.models import Event, Booking



# Functional Tests (single-threaded)

class EventViewsFunctionalTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_event_success(self):
        response = self.client.post(
            "/api/events/",
            {"name": "IPL Final", "total_tickets": 100},
            format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().available_tickets, 100)

    def test_create_event_invalid_data(self):
        response = self.client.post(
            "/api/events/",
            {"total_tickets": 10},
            format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_book_ticket_success(self):
        event = Event.objects.create(
            name="Concert",
            total_tickets=2,
            available_tickets=2
        )

        response = self.client.post(
            f"/api/events/{event.id}/book/",
            {"user_id": 1, "tickets": 1},
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        event.refresh_from_db()
        self.assertEqual(event.available_tickets, 1)
        self.assertEqual(event.booking_set.count(), 1)

    def test_book_ticket_max_limit(self):
        event = Event.objects.create(
            name="Concert",
            total_tickets=5,
            available_tickets=5
        )

        self.client.post(
            f"/api/events/{event.id}/book/",
            {"user_id": 1, "tickets": 2},
            format="json"
        )

        response = self.client.post(
            f"/api/events/{event.id}/book/",
            {"user_id": 1, "tickets": 1},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_book_ticket_sold_out(self):
        event = Event.objects.create(
            name="Concert",
            total_tickets=1,
            available_tickets=0
        )

        response = self.client.post(
            f"/api/events/{event.id}/book/",
            {"user_id": 2},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_cancel_ticket_success(self):
        event = Event.objects.create(
            name="Concert",
            total_tickets=2,
            available_tickets=1
        )

        booking = Booking.objects.create(
            event=event,
            user_id=1,
            tickets_booked=1
        )

        event.save()

        response = self.client.post(
            f"/api/events/{event.id}/cancel/",
            {"user_id": 1},
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.filter(id=booking.id).exists())

        event.refresh_from_db()
        self.assertEqual(event.available_tickets, 2)

    def test_cancel_ticket_no_booking(self):
        event = Event.objects.create(
            name="Concert",
            total_tickets=2,
            available_tickets=2
        )

        response = self.client.post(
            f"/api/events/{event.id}/cancel/",
            {"user_id": 99},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

