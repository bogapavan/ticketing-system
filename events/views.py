from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    CreateEventSerializer,
    BookTicketSerializer,
    CancelTicketSerializer
)
from .services import TicketService
from .models import Event

class CreateEventView(APIView):
    def post(self, request):
        s = CreateEventSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        data = s.validated_data
        event = Event.objects.create(
            name=data["name"],
            total_tickets=data["total_tickets"],
            available_tickets=data["total_tickets"]
        )
        return Response({"event_id": event.id}, status=201)

class BookTicketView(APIView):
    def post(self, request, event_id):
        s = BookTicketSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        try:
            TicketService.book(
                event_id,
                s.validated_data["user_id"],
                s.validated_data.get("tickets", 1),
            )
            return Response({"success": "Booked"})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class CancelTicketView(APIView):
    def post(self, request, event_id):
        s = CancelTicketSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        try:
            TicketService.cancel(event_id, s.validated_data["user_id"])
            return Response({"success": "Cancelled"})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
