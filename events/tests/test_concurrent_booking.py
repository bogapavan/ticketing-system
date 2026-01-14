import threading
from django.db import connection, connections
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient
from django.db.models import Sum

from events.models import Event, Booking

# Concurrency Tests
class BookTicketConcurrencyTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.event = Event.objects.create(
            name="Coldplay Concert",
            total_tickets=1,
            available_tickets=1
        )

    def tearDown(self):
        #Ensure all DB connections are closed
        for conn in connections.all():
            conn.close()

    def _book_ticket_thread(self, user_id, results):
        client = APIClient()  # new client per thread

        response = client.post(
            f"/api/events/{self.event.id}/book/",
            {"user_id": user_id, "tickets": 1},
            format="json"
        )

        results.append(response.status_code)

        # release DB connection held by this thread
        connection.close()

    def test_only_one_booking_succeeds_for_last_ticket(self):
        threads = []
        results = []

        for user_id in range(1, 6):
            t = threading.Thread(
                target=self._book_ticket_thread,
                args=(user_id, results)
            )
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(results.count(200), 1)
        self.assertEqual(results.count(400), 4)

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_tickets, 0)
        self.assertEqual(Booking.objects.count(), 1)

    def test_user_cannot_book_more_than_two_tickets_concurrently(self):
        self.event.total_tickets = 5
        self.event.available_tickets = 5
        self.event.save()

        threads = []
        results = []

        for _ in range(3):
            t = threading.Thread(
                target=self._book_ticket_thread,
                args=(1, results)
            )
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(results.count(200), 2)
        self.assertEqual(results.count(400), 1)

        total_booked = (
            Booking.objects
            .filter(user_id=1, event=self.event)
            .aggregate(Sum("tickets_booked"))
            ["tickets_booked__sum"]
        )

        self.assertEqual(total_booked, 2)

        self.event.refresh_from_db()
        self.assertEqual(self.event.available_tickets, 3)
