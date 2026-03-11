from amo.models import Airport
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

class TestMockAirlinesApi(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = baker.make(User)
        self.client.force_authenticate(user=self.user)
        
        self.origin_airport = baker.make(
            Airport, 
            iata="POA", 
            city="Porto Alegre",
            state="RS",
            lat=-29.99,
            lon=-51.17,
        )
        self.destination_airport = baker.make(
            Airport, 
            iata="MAO", 
            city="Manaus",
            state="AM",
            lat=-3.03,
            lon=-60.05,
        )
        self.departure_date = "2026-06-12"
        self.return_date = "2026-06-13"

    def test_get_flight_search(self):
        endpoint = (
            f"{reverse('mock-airlines')}?"
            f"from={self.origin_airport.iata}&"
            f"to={self.destination_airport.iata}&"
            f"departure_date={self.departure_date}&"
            f"return_date={self.return_date}"
        )
        
        response = self.client.get(endpoint)
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        
        self.assertIn("options", data)
        self.assertIsInstance(data["options"], list)
        self.assertGreater(len(data["options"]), 0)

        option = data["options"][0]

        self.assertIn("outbound", option)
        self.assertIn("inbound", option)

        price = option["price"]
        self.assertIn("total", price)
        self.assertIn("fees", price)
        self.assertIn("fare", price)