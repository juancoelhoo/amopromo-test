from django.core.management.base import BaseCommand
from amo.tasks.airport_importer import AirportImporter


class Command(BaseCommand):
    help = "Import airports from Domestic Airports API"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file_path',
            type=str,
            help='Path to a JSON file to load airports instead of calling the API'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs.get('file_path')
        importer = AirportImporter()

        if importer.run(file_path=file_path):
            self.stdout.write(self.style.SUCCESS("Airports imported successfully"))
        else:
            self.stdout.write(self.style.ERROR("Import failed. Check logs above."))

        