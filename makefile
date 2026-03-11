.PHONY: backend import test

backend:
	docker build -t backend backend/
	docker run -p 8000:8000 --rm --name backend_container backend

import:
	docker exec -it backend_container python manage.py migrate
	docker exec -it backend_container python manage.py import_airports