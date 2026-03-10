from amo.models import Airport
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import math
from datetime import datetime
from app.validators.validators import get_flight_validation_cases

class MockAirlinesView(APIView):    
    def get(self, request):
        self.origin_airport = request.GET.get("from")
        self.destination_airport = request.GET.get("to")
        self.departure_date = request.GET.get("departure_date")
        self.return_date = request.GET.get("return_date")

        self.origin_airport_obj = None
        self.destination_airport_obj = None
        
        error_response = self.validate_request()
        if error_response:
            return error_response
        
        outbound_flights = self._get_flights(
            self.origin_airport, 
            self.destination_airport, 
            self.departure_date
        )
        
        inbound_flights = self._get_flights(
            self.destination_airport, 
            self.origin_airport, 
            self.return_date
        )

        if outbound_flights is None or (self.return_date and inbound_flights is None):
            return Response(
                {"error": "Could not fetch flights from provider."}, 
                status=status.HTTP_502_BAD_GATEWAY
            )
        
        result = self.consolidate_trip_options(outbound_flights, inbound_flights)
        return Response(result, status=status.HTTP_200_OK)
    
    def _get_flights(self, origin: str, destination: str, date: str):
        """Internal pipeline to fetch raw flight data and enrich it with price and metadata"""
        if not date:
            return None
        raw_flights = self.flight_request(origin, destination, date)
        processed_flights = self.process_flight_prices(raw_flights)
        return self.calculate_meta_info(processed_flights)

    def validate_request(self):
        """Retrieves airport objects and runs all business logic validation rules"""
        origin_airport_obj = Airport.objects.filter(iata=self.origin_airport).first()
        destination_airport_obj = Airport.objects.filter(iata=self.destination_airport).first()

        test_cases = get_flight_validation_cases(self, origin_airport_obj, destination_airport_obj)

        for test in test_cases:
            if test["condition"]:
                return Response(
                    {"error": test["error"]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        self.origin_airport_obj = origin_airport_obj
        self.destination_airport_obj = destination_airport_obj
        return None
    
    def flight_request(self, departure_airport: str, arrival_airport: str, departure_date: str) -> dict:
        """Communicates with the external Mock Airlines API using Basic Auth and dynamic URL parameters"""
        base_url = "https://stub-850169372117.us-central1.run.app"
        username = "demo"
        password = "swnvlD"
        api_key = "pzrvlDwoCwlzrWJmOzviqvOWtm4dkvuc"

        endpoint = f"/air/search/{api_key}/{departure_airport}/{arrival_airport}/{departure_date}"
        full_url = f"{base_url}{endpoint}"

        try:
            response = requests.get(
                full_url,
                auth=requests.auth.HTTPBasicAuth(username, password),
                timeout=10
            )

            if response.status_code != 200:
                self.data = {"summary": {}, "options": []}
                return self.data

            self.data: dict = json.loads(response.content)
            return self.data

        except requests.exceptions.RequestException:
            self.data = {"error": "Connection failed", "options": []}
            return self.data
        
    

    def process_flight_prices(self, flights_dict: dict) -> dict:
        """Iterates through flight options to calculate and inject 'fees' and 'total' prices"""
        if not flights_dict or "options" not in flights_dict:
            return flights_dict

        for option in flights_dict["options"]:
            fare = option["price"]["fare"]
            
            fees = self.calculate_fees(fare)
            
            option["price"]["fees"] = round(fees, 2)
            option["price"]["total"] = round(fare + fees, 2)

        return flights_dict

    def calculate_fees(self, fare: float) -> float:
        """Applies the 10% fee rule with a minimum charge of R$ 40.00"""
        return max(fare * 0.10, 40.0)
    
    def calculate_range_between_airports(self, lon1, lat1, lon2, lat2) -> float:
        """Implements the Haversine formula to find the Great-circle distance between coordinates"""
        earth_radius = 6371 
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) *  math.sin(dlambda / 2)**2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return earth_radius * c

    def calculate_flight_duration(self, departure_str: str, arrival_str: str) -> float:
        """Computes the flight time in hours by parsing departure and arrival ISO strings"""
        fmt = '%Y-%m-%dT%H:%M:%S'
        t1 = datetime.strptime(departure_str, fmt)
        t2 = datetime.strptime(arrival_str, fmt)
        
        duration = t2 - t1
        return duration.total_seconds() / 3600
    
    def calculate_meta_info(self, flight: dict = {}) -> dict:
        """Populates technical flight data such as range, cruise speed, and cost per kilometer"""
        if not flight or "options" not in flight:
            return flight

        lon1 = flight["summary"]["from"]["lon"]
        lat1 = flight["summary"]["from"]["lat"]
        lon2 = flight["summary"]["to"]["lon"]
        lat2 = flight["summary"]["to"]["lat"]

        distance_between_airports = self.calculate_range_between_airports(lon1, lat1, lon2, lat2)

        for flight_option in flight["options"]:
            flight_duration = self.calculate_flight_duration(
                flight_option["departure_time"], 
                flight_option["arrival_time"]
            )

            if "meta" not in flight_option:
                flight_option["meta"] = {}

            flight_option["meta"]["range"] = round(distance_between_airports, 2)
            
            if flight_duration > 0:
                flight_option["meta"]["cruise_speed_kmh"] = round(distance_between_airports / flight_duration, 2)
            else:
                flight_option["meta"]["cruise_speed_kmh"] = 0

            flight_option["meta"]["cost_per_km"] = round(flight_option["price"]["fare"] / distance_between_airports, 2)
        
        return flight
    
    def consolidate_trip_options(self, outbound_data: dict, inbound_data: dict) -> dict:
        result = {
            "origin": self.origin_airport,
            "destination": self.destination_airport,
            "departure_date": self.departure_date,
            "return_date": self.return_date,
            "options": []
        }

        options = []

        if not inbound_data or "options" not in inbound_data:
            for go in outbound_data.get("options", []):
                option = {
                    "outbound": go,
                    "inbound": None,
                    "price": go["price"]
                }
                options.append(option)
            
            result["options"] = sorted(options, key=lambda x: x['price']['total'])
            return result

        for go in outbound_data.get("options", []):
            for ret in inbound_data.get("options", []):
                total_fare = go["price"]["fare"] + ret["price"]["fare"]
                
                total_fees = self.calculate_fees(total_fare)
                
                option = {
                    "outbound": go,
                    "inbound": ret,
                    "price": {
                        "fare": round(total_fare, 2),
                        "fees": round(total_fees, 2),
                        "total": round(total_fare + total_fees, 2)
                    }
                }
                options.append(option)

        result["options"] = sorted(options, key=lambda x: x['price']['total'])
        return result
