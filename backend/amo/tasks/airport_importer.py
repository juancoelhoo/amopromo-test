import requests
import logging
import json
from amo.models import Airport
logger = logging.getLogger(__name__)


class AirportImporter():

    def __init__(self) -> None:
        self.airports_request = {}
        self.airports_database = {}
        self.airports_to_create = []
        self.airports_to_update = []
    
    API_URL = "https://stub-850169372117.us-central1.run.app/air/airports/pzrvlDwoCwlzrWJmOzviqvOWtm4dkvuc"
    API_AUTH = ("demo", "swnvlD")
    BATCH_SIZE = 1000

    def run(self, file_path=None) -> bool:
        if not self.fetch_airports(file_path):
            print("No airport data to process.")
            return False

        self.airports_database = Airport.objects.in_bulk(field_name="iata")
        self.process_airports()
        self.bulk_write()
        self.log_summary()
        return True


    def fetch_airports(self, file_path=None) -> bool:
        """Retrieve airport data from an external API or a JSON file."""
        if file_path is not None:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.airports_request = json.load(f)
                return True
            except Exception as e:
                print(f"Failed to load file {file_path}: {e}")
                return False

        try:
            response = requests.get(self.API_URL, auth=self.API_AUTH, timeout=10)
            response.raise_for_status()
            self.airports_request = response.json()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch airports from API: {e}")
            return False

    def process_airports(self) -> None:
        """Compare incoming data with DB records to identify new or changed airports."""
        fields = ["city", "state", "lat", "lon"]

        for airport_data in self.airports_request.values():
            obj = self.airports_database.get(airport_data["iata"])

            if obj:
                has_changed = False
                for f in fields:
                    new_val = airport_data[f]
                    current_val = float(getattr(obj, f)) if f in ("lat", "lon") else getattr(obj, f)
                    
                    if current_val != (float(new_val) if f in ("lat", "lon") else new_val):
                        setattr(obj, f, new_val)
                        has_changed = True
                
                if has_changed:
                    self.airports_to_update.append(obj)
            else:
                self.airports_to_create.append(Airport(**airport_data))

    def bulk_write(self) -> None:
        """Execute batch inserts and updates in the database for optimal performance."""
        if self.airports_to_create:
            Airport.objects.bulk_create(
                self.airports_to_create,
                batch_size=1000
            )

        if self.airports_to_update:
            Airport.objects.bulk_update(
                self.airports_to_update,
                ["city", "state", "lat", "lon"],
                batch_size=1000
            )

    def log_summary(self) -> None:
        """Display a final count and the IATA codes of inserted and updated records."""
        created_iatas = [obj.iata for obj in self.airports_to_create]
        updated_iatas = [obj.iata for obj in self.airports_to_update]

        n_inserted = len(created_iatas)
        n_updated = len(updated_iatas)

        print(f"Airports import finished | inserted={n_inserted} updated={n_updated}")
        
        if n_inserted > 0:
            print(f"  Inserted IATAs: {', '.join(created_iatas)}")
        
        if n_updated > 0:
            print(f"  Updated IATAs: {', '.join(updated_iatas)}")