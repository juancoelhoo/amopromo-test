from rest_framework import serializers

class AirportSerializer(serializers.Serializer):
    iata = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    lat = serializers.CharField()
    lon = serializers.CharField()