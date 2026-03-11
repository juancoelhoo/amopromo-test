# DESCRIPTION
Exercise 1: I understood it as an ETL process where performance and data integrity are essential. To handle the synchronization between the external API and the local database, I used Django's in_bulk method to load the existing records into a dictionary keyed by IATA code. The logic iterates through the incoming data, identifying which airports are new (adding them to a bulk_create list) and which have changed fields such as city, state, or coordinates (adding them to a bulk_update list). Finally, I used Batch Processing with a BATCH_SIZE of 1000 to minimize database hits. The code for this exercise can be found on backend/amo/tasks/airport_importer.py.

Exercise 2: The required API was developed to consume the Mock Airlines provider. I used Python dicts to handle all necessary data manipulations. This helped with calculating taxes (applying the 10% fee with a R$ 40,00 minimum), flight distances via coordinates, and additional metadata. For the flight consolidation, I implemented logic to pair outbound and inbound flights, ensuring the final pricing and information meet the business requirements. The backend code for this exercise can be found on backend/amo/views/MockAirlinesView.py.
An example of the API endpoint, that can be used by Curl command or on Postman:

http://localhost:8000/search/?from=POA&to=MAO&departure_date=2026-06-12&return_date=2026-06-13

# SETUP & EXECUTION
1. Clone this repository
2. Run [make backend] to build and start the Docker environment.
3. Once the server is running, open another terminal and change to backend/ directory
4. Use the command [docker exec -it backend_container python manage.py import_airports] to run the exercise 1
5. The database is now populated, and the API is ready to receive requests.
6. Use the command [docker exec -it backend_container python manage.py test] to run the test

# TECHNOLOGIES
Python 3.11: The core programming language used for its versatility and clean syntax.

Django 5.2: High-level Web framework used for rapid and secure development.

Docker & Docker Compose: Used to containerize the application, ensuring a consistent environment across different machines.

SQLite: Chosen as a lightweight, file-based database for easy evaluation and setup.

