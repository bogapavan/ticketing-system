from rest_framework import serializers

class CreateEventSerializer(serializers.Serializer):
    name = serializers.CharField()
    total_tickets = serializers.IntegerField(min_value=1)

class BookTicketSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    tickets = serializers.IntegerField(min_value=1, max_value=2, required=False)

class CancelTicketSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
