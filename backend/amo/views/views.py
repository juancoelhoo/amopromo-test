from amo.api.serializers import AirportSerializer
from amo.models import Airport
from rest_framework.response import Response
from rest_framework.views import APIView

class AirportView(APIView):
    def get(self, request):
        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)
        return Response(serializer.data)